"""SLO arithmetic for the service: SLI, burn rate, multi-window alerts and the canary decision."""
from dataclasses import dataclass

HOUR = 3600


@dataclass
class SLO:
    target: float = 0.995
    latency_threshold_ms: float = 5000

    @property
    def error_budget(self) -> float:
        return 1 - self.target

    def _good(self, r) -> bool:
        return r[1] < 500 and r[2] <= self.latency_threshold_ms

    def burn_rate(self, requests, now, window_s) -> float:
        w = [r for r in requests if now - window_s < r[0] <= now]
        if not w:
            return 0.0
        bad = sum(not self._good(r) for r in w) / len(w)
        return round(bad / self.error_budget, 2)

    def alerts(self, requests, now) -> list[str]:
        if self.burn_rate(requests, now, HOUR) >= 14.4 and self.burn_rate(requests, now, 300) >= 14.4:
            return ["page"]
        if self.burn_rate(requests, now, 6 * HOUR) >= 6 and self.burn_rate(requests, now, 1800) >= 6:
            return ["ticket"]
        return []


def canary_decision(base: dict, canary: dict, min_requests: int = 500) -> str:
    """Compare the canary with the current version over the same window: "wait", "rollback" or "promote".

    Wait below `min_requests` canary requests. Roll back when the canary's error rate exceeds 1.5x the base's plus
    0.001, its p95 exceeds 1.2x the base's, its judge pass rate falls more than 0.03 below the base's, or its refusal
    rate rises more than 0.02 above the base's. Otherwise promote.
    """
    if canary["requests"] < min_requests:
        return "wait"                              # too little data to judge
    if canary["error_rate"] > base["error_rate"] * 1.5 + 0.001:
        return "rollback"
    if canary["p95_ms"] > base["p95_ms"] * 1.2:
        return "rollback"
    if canary["judge_pass"] < base["judge_pass"] - 0.03:
        return "rollback"                          # quality regressed
    if canary["refusal_rate"] > base["refusal_rate"] + 0.02:
        return "rollback"                          # over-refusing is a regression too
    return "promote"
