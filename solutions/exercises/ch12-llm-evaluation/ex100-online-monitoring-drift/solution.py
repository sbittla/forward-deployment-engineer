"""Online quality monitoring for a deployed LLM feature: input drift, live judge scores, and review sampling."""
import hashlib
import math
from dataclasses import dataclass

EPS = 1e-4


def _psi_terms(expected: list[float], actual: list[float]) -> float:
    return sum((a - e) * math.log(a / e) for e, a in zip(expected, actual))


def quantile_edges(values: list[float], bins: int) -> list[float]:
    s = sorted(values)
    return [s[min(len(s) - 1, int(len(s) * i / bins))] for i in range(1, bins)]


def _bucket(x: float, edges: list[float]) -> int:
    return sum(x >= e for e in edges)


def psi(baseline: list[float], current: list[float], bins: int = 10) -> float:
    """Population stability index of a numeric feature, binned at the baseline's quantiles."""
    if not baseline or not current:
        raise ValueError("need data in both windows")
    edges = quantile_edges(baseline, bins)
    nb = len(edges) + 1

    def shares(xs):
        counts = [0] * nb
        for x in xs:
            counts[_bucket(x, edges)] += 1
        return [max(c / len(xs), EPS) for c in counts]

    return round(_psi_terms(shares(baseline), shares(current)), 4)


def category_psi(baseline: dict[str, int], current: dict[str, int]) -> float:
    cats = sorted(set(baseline) | set(current))
    tb, tc = sum(baseline.values()), sum(current.values())
    if not tb or not tc:
        raise ValueError("need data in both windows")
    exp = [max(baseline.get(c, 0) / tb, EPS) for c in cats]
    act = [max(current.get(c, 0) / tc, EPS) for c in cats]
    return round(_psi_terms(exp, act), 4)


def drift_level(value: float) -> str:
    return "drift" if value >= 0.25 else "watch" if value >= 0.1 else "stable"


def p95(values: list[float]) -> float:
    s = sorted(values)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]


@dataclass
class Thresholds:
    min_samples: int = 50
    judge_drop: float = 0.05          # absolute drop in judge pass rate vs baseline
    refusal_rate: float = 0.05
    p95_latency_ms: float = 4000
    cost_per_conv: float = 0.10


def check_window(baseline: dict, window: list[dict], t: Thresholds = Thresholds()) -> list[dict]:
    """baseline: {"input_len": [...], "intents": {...}, "judge_pass": float}.
    window records: {"input_len", "intent", "judge_pass": bool | None, "refused", "latency_ms", "cost"}."""
    alerts = []
    if len(window) < t.min_samples:
        return [{"metric": "samples", "level": "info", "value": len(window),
                 "message": f"only {len(window)} records; need {t.min_samples} before alerting"}]
    v = psi(baseline["input_len"], [r["input_len"] for r in window])
    if drift_level(v) != "stable":
        alerts.append({"metric": "input_len_psi", "level": drift_level(v), "value": v})
    intents: dict[str, int] = {}
    for r in window:
        intents[r["intent"]] = intents.get(r["intent"], 0) + 1
    v = category_psi(baseline["intents"], intents)
    if drift_level(v) != "stable":
        alerts.append({"metric": "intent_psi", "level": drift_level(v), "value": v})
    judged = [r["judge_pass"] for r in window if r.get("judge_pass") is not None]
    if len(judged) >= t.min_samples:
        rate = round(sum(judged) / len(judged), 4)
        if rate < baseline["judge_pass"] - t.judge_drop:
            alerts.append({"metric": "judge_pass", "level": "page", "value": rate})
    refusal = round(sum(r["refused"] for r in window) / len(window), 4)
    if refusal > t.refusal_rate:
        alerts.append({"metric": "refusal_rate", "level": "page", "value": refusal})
    lat = p95([r["latency_ms"] for r in window])
    if lat > t.p95_latency_ms:
        alerts.append({"metric": "p95_latency_ms", "level": "page", "value": lat})
    cost = round(sum(r["cost"] for r in window) / len(window), 4)
    if cost > t.cost_per_conv:
        alerts.append({"metric": "cost_per_conv", "level": "watch", "value": cost})
    return alerts


def sample_for_review(records: list[dict], rate: float, always=lambda r: False) -> list[str]:
    """Deterministic hash sampling (stable across reruns and machines) plus everything `always` flags."""
    if not 0 <= rate <= 1:
        raise ValueError("rate must be within [0, 1]")
    picked = []
    for r in records:
        h = int(hashlib.sha256(r["id"].encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        if always(r) or h < rate:
            picked.append(r["id"])
    return picked
