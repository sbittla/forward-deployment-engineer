import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Case:
    id: str
    input: str
    expected: object
    grader: str
    tags: list[str] = field(default_factory=list)
    source: str = ""


SOURCES = ("production", "expert", "red_team", "synthetic")


@dataclass
class CaseResult:
    case: Case
    passed: bool
    output: str
    error: str = ""


@dataclass
class EvalReport:
    results: list[CaseResult]

    @property
    def pass_rate(self) -> float:
        return round(sum(r.passed for r in self.results) / len(self.results), 4) if self.results else 0.0

    def by_tag(self) -> dict[str, float]:
        groups = defaultdict(list)
        for r in self.results:
            for t in r.case.tags:
                groups[t].append(r.passed)
        return {t: round(sum(v) / len(v), 4) for t, v in sorted(groups.items())}

    def failures(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed]

    def to_markdown(self) -> str:
        passed = sum(r.passed for r in self.results)
        n = len(self.results)
        lines = [f"# Eval: {passed}/{n} passed ({100 * passed / n:.1f}%)", "", "| Tag | Pass rate |", "|---|---|"]
        lines += [f"| {t} | {v} |" for t, v in self.by_tag().items()]
        lines += ["", "## Failures"]
        lines += [f"- {r.case.id}: {r.error or r.output[:80]}" for r in self.failures()] or ["- none"]
        return "\n".join(lines) + "\n"

    def by_slice(self, z: float = 1.96) -> dict[str, dict]:
        groups = defaultdict(list)
        for r in self.results:
            for t in r.case.tags:
                groups[t].append(r.passed)
        out = {}
        for t, v in sorted(groups.items()):
            low, high = wilson_interval(sum(v), len(v), z)
            out[t] = {"n": len(v), "passed": sum(v), "pass_rate": round(sum(v) / len(v), 4),
                      "low": round(low, 4), "high": round(high, 4)}
        return out

    def failure_taxonomy(self, labels: dict[str, str]) -> list[tuple[str, int]]:
        counts = defaultdict(int)
        for r in self.failures():
            counts[labels.get(r.case.id, "unlabelled")] += 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def _norm(s: str) -> str:
    return " ".join(str(s).lower().split())


def _numeric(out, exp):
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", out)
    if not m:
        return False
    return abs(float(m.group(0).replace(",", "")) - exp["value"]) <= exp["tol"]


def _json_field(out, exp):
    try:
        cur = json.loads(out)
        for key in exp["path"].split("."):
            cur = cur[key]
    except (json.JSONDecodeError, KeyError, TypeError, IndexError):
        return False
    return cur == exp["value"]


GRADERS = {
    "exact": lambda out, exp: _norm(out) == _norm(exp),
    "contains": lambda out, exp: all(str(e).lower() in out.lower() for e in exp),
    "regex": lambda out, exp: re.search(exp, out) is not None,
    "numeric": _numeric,
    "json_field": _json_field,
}


def load_cases(path) -> list[Case]:
    cases = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            cases.append(Case(d["id"], d["input"], d["expected"], d["grader"], d.get("tags", []), d.get("source", "")))
    return cases


def run_eval(cases: list[Case], system) -> EvalReport:
    unknown = sorted({c.grader for c in cases} - GRADERS.keys())
    if unknown:
        raise ValueError(f"unknown graders: {unknown}")
    results = []
    for c in cases:
        try:
            out = system(c.input)
        except Exception as exc:
            results.append(CaseResult(c, False, "", f"{type(exc).__name__}: {exc}"))
            continue
        results.append(CaseResult(c, bool(GRADERS[c.grader](out, c.expected)), out))
    return EvalReport(results)


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError("need n > 0 and 0 <= successes <= n")
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def cost_per_success(cost_per_request: float, pass_rate: float) -> float:
    if pass_rate <= 0:
        raise ValueError("pass_rate must be positive")
    return cost_per_request / pass_rate


def _leak_norm(s: str) -> str:
    return " ".join(re.sub(r"[^0-9a-z]+", " ", str(s).lower()).split())


def find_leakage(cases: list[Case], examples: list[str]) -> list[str]:
    pool = [f" {_leak_norm(e)} " for e in examples]
    leaked = []
    for c in cases:
        needle = _leak_norm(c.input)
        if needle and any(f" {needle} " in e for e in pool):
            leaked.append(c.id)
    return leaked


def provenance(cases: list[Case]) -> dict[str, int]:
    counts = defaultdict(int)
    for c in cases:
        if c.source and c.source not in SOURCES:
            raise ValueError(f"unknown source {c.source!r} for case {c.id}")
        counts[c.source or "unspecified"] += 1
    return dict(sorted(counts.items()))


def mcnemar_exact(fixed: int, broken: int) -> float:
    if fixed < 0 or broken < 0:
        raise ValueError("counts must be non-negative")
    n = fixed + broken
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(fixed, broken) + 1)) / 2 ** n
    return min(1.0, 2 * tail)
