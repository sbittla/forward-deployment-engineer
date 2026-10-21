"""Service levels for the copilot: SLO, multi-window burn-rate alerts, the canary decision and a staged rollout.

Events are (timestamp_s, ok, latency_ms). A request is good when it succeeded and answered within the latency
threshold. The canary is judged on reliability *and* on what the business cares about: answering unanswerable
questions or leaking a forbidden document is never tolerated, whatever the error rate says.
"""
from dataclasses import dataclass

HOUR = 3600
ROLLOUT_STAGES = (10, 50, 100)


@dataclass
class SLO:
    target: float = 0.995
    latency_threshold_ms: float = 4000

    @property
    def error_budget(self) -> float:
        return 1 - self.target

    def burn_rate(self, events, now: float, window_s: float) -> float:
        w = [e for e in events if now - window_s < e[0] <= now]
        if not w:
            return 0.0
        bad = sum(not (ok and ms <= self.latency_threshold_ms) for _, ok, ms in w) / len(w)
        return round(bad / self.error_budget, 2)

    def alerts(self, events, now: float) -> list[str]:
        """Page on a fast burn (14.4x over 1 hour and 5 minutes); ticket on a slow burn (6x over 6 h and 30 min)."""
        if self.burn_rate(events, now, HOUR) >= 14.4 and self.burn_rate(events, now, 300) >= 14.4:
            return ["page"]
        if self.burn_rate(events, now, 6 * HOUR) >= 6 and self.burn_rate(events, now, 1800) >= 6:
            return ["ticket"]
        return []


def canary_decision(base: dict, canary: dict, min_requests: int = 500) -> tuple[str, list[str]]:
    """Return ("wait" | "rollback" | "promote", reasons).

    Wait below `min_requests`. Roll back when: the canary leaked any forbidden document; it answered any
    unanswerable question when the base didn't; its error rate exceeds 1.5x the base's plus 0.001; its p95 exceeds
    1.2x the base's; its pass rate is more than 0.03 below the base's; or its cost per successful answer exceeds
    1.2x the base's.
    """
    if canary["requests"] < min_requests:
        return "wait", [f"{canary['requests']} requests (need {min_requests})"]
    reasons = []
    if canary.get("leaks", 0) > 0:
        reasons.append(f"permission leaks {canary['leaks']}")
    if canary["false_answer_rate"] > base["false_answer_rate"]:
        reasons.append(f"false_answer_rate {canary['false_answer_rate']} > {base['false_answer_rate']}")
    if canary["error_rate"] > base["error_rate"] * 1.5 + 0.001:
        reasons.append(f"error_rate {canary['error_rate']} vs {base['error_rate']}")
    if canary["p95_ms"] > base["p95_ms"] * 1.2:
        reasons.append(f"p95_ms {canary['p95_ms']} vs {base['p95_ms']}")
    if canary["pass_rate"] < base["pass_rate"] - 0.03:
        reasons.append(f"pass_rate {canary['pass_rate']} vs {base['pass_rate']}")
    if canary["cost_per_success_usd"] > base["cost_per_success_usd"] * 1.2:
        reasons.append(f"cost_per_success_usd {canary['cost_per_success_usd']} vs {base['cost_per_success_usd']}")
    return ("rollback", reasons) if reasons else ("promote", [])


def run_rollout(base: dict, observe, stages=ROLLOUT_STAGES, min_requests: int = 500) -> dict:
    """Walk the stages (percent of adjusters). `observe(percent)` returns the canary's metrics at that stage.

    The first "rollback" sends traffic back to 0% automatically; a "wait" stops the rollout where it is.
    """
    history = []
    for pct in stages:
        decision, reasons = canary_decision(base, observe(pct), min_requests)
        history.append((pct, decision))
        if decision == "rollback":
            return {"decision": "rolled_back", "stage": pct, "traffic_percent": 0, "reasons": reasons,
                    "history": history}
        if decision == "wait":
            return {"decision": "waiting", "stage": pct, "traffic_percent": pct, "reasons": reasons,
                    "history": history}
    return {"decision": "promoted", "stage": stages[-1], "traffic_percent": 100, "reasons": [], "history": history}
