import json
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
            cases.append(Case(d["id"], d["input"], d["expected"], d["grader"], d.get("tags", [])))
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
