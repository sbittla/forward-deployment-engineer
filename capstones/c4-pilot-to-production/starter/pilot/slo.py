"""SLO arithmetic for the service: SLI, burn rate, multi-window alerts and the canary decision."""
from dataclasses import dataclass

HOUR = 3600


@dataclass
class SLO:
    target: float = 0.995
    latency_threshold_ms: float = 5000

    @property
    def error_budget(self) -> float:
        raise NotImplementedError

    def _good(self, r) -> bool:
        raise NotImplementedError

    def burn_rate(self, requests, now, window_s) -> float:
        raise NotImplementedError

    def alerts(self, requests, now) -> list[str]:
        raise NotImplementedError


def canary_decision(base: dict, canary: dict, min_requests: int = 500) -> str:
    """Compare the canary with the current version over the same window: "wait", "rollback" or "promote".

    Wait below `min_requests` canary requests. Roll back when the canary's error rate exceeds 1.5x the base's plus
    0.001, its p95 exceeds 1.2x the base's, its judge pass rate falls more than 0.03 below the base's, or its refusal
    rate rises more than 0.02 above the base's. Otherwise promote.
    """
    raise NotImplementedError
