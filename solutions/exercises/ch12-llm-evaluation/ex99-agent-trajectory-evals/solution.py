"""Evaluate how an agent got its answer: tool choice, order, arguments, efficiency and reliability across runs."""
import math
from dataclasses import dataclass, field


@dataclass
class TrajectoryScore:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    efficiency: float = 1.0
    steps: int = 0


def tool_calls(trajectory: list[dict]) -> list[dict]:
    return [s for s in trajectory if s["type"] == "tool_call"]


def final_text(trajectory: list[dict]) -> str | None:
    finals = [s["text"] for s in trajectory if s["type"] == "final"]
    return finals[-1] if finals else None


def _is_subsequence(needle: list[str], haystack: list[str]) -> bool:
    it = iter(haystack)
    return all(any(x == y for y in it) for x in needle)


def score_trajectory(trajectory: list[dict], spec: dict) -> TrajectoryScore:
    calls = tool_calls(trajectory)
    names = [c["name"] for c in calls]
    final = final_text(trajectory)
    checks: dict[str, bool] = {"has_final": final is not None}
    if "required_tools" in spec:
        checks["required_tools"] = all(t in names for t in spec["required_tools"])
    if "forbidden_tools" in spec:
        checks["forbidden_tools"] = not any(t in names for t in spec["forbidden_tools"])
    if "order" in spec:
        checks["order"] = _is_subsequence(spec["order"], names)
    if "max_steps" in spec:
        checks["max_steps"] = len(calls) <= spec["max_steps"]
    if "final_contains" in spec:
        low = (final or "").lower()
        checks["final_contains"] = all(s.lower() in low for s in spec["final_contains"])
    for tool, expected in spec.get("arg_checks", {}).items():
        made = [c["arguments"] for c in calls if c["name"] == tool]
        checks[f"args:{tool}"] = any(all(a.get(k) == v for k, v in expected.items()) for a in made)
    optimal = len(spec.get("required_tools", [])) or 1
    efficiency = round(min(1.0, optimal / len(calls)), 4) if calls else (1.0 if not spec.get("required_tools") else 0.0)
    return TrajectoryScore(all(checks.values()), checks, efficiency, len(calls))


def tool_call_f1(trajectory: list[dict], expected_calls: list[dict]) -> dict:
    """Precision/recall over (name, arguments) pairs, as multisets."""
    made = [(c["name"], tuple(sorted(c["arguments"].items()))) for c in tool_calls(trajectory)]
    want = [(c["name"], tuple(sorted(c["arguments"].items()))) for c in expected_calls]
    remaining = list(want)
    tp = 0
    for m in made:
        if m in remaining:
            remaining.remove(m)
            tp += 1
    p = tp / len(made) if made else (1.0 if not want else 0.0)
    r = tp / len(want) if want else 1.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimate that at least one of k sampled runs passes, given c passes in n runs."""
    if not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("need 0 <= c <= n and 1 <= k <= n")
    if n - c < k:
        return 1.0
    return round(1 - math.comb(n - c, k) / math.comb(n, k), 4)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Estimate that all k sampled runs pass (pass^k): the reliability a customer actually experiences."""
    if not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("need 0 <= c <= n and 1 <= k <= n")
    return round(math.comb(c, k) / math.comb(n, k), 4)


def run_suite(agent, cases: list[dict], trials: int = 1, k: int = 1) -> dict:
    """agent(task, trial) -> trajectory. Reports per-case pass counts, pass@k, pass^k and the most common failures."""
    per_case, failures, steps = [], {}, []
    for case in cases:
        passes = 0
        for t in range(trials):
            s = score_trajectory(agent(case["task"], t), case["spec"])
            passes += s.passed
            steps.append(s.steps)
            for name, ok in s.checks.items():
                if not ok:
                    failures[name] = failures.get(name, 0) + 1
        per_case.append({"id": case["id"], "passes": passes, "pass_at_k": pass_at_k(trials, passes, k),
                         "pass_hat_k": pass_hat_k(trials, passes, k)})
    n = len(per_case) or 1
    return {"cases": per_case,
            "pass_at_k": round(sum(c["pass_at_k"] for c in per_case) / n, 4),
            "pass_hat_k": round(sum(c["pass_hat_k"] for c in per_case) / n, 4),
            "mean_steps": round(sum(steps) / len(steps), 2) if steps else 0.0,
            "top_failures": sorted(failures.items(), key=lambda kv: (-kv[1], kv[0]))}
