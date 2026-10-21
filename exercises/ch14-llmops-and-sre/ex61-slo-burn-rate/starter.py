from dataclasses import dataclass

HOUR = 3600


@dataclass
class SLO:
    target: float = 0.995
    latency_threshold_ms: float = 3000

    @property
    def error_budget(self) -> float:
        raise NotImplementedError

    def sli(self, requests, now, window_s):
        raise NotImplementedError

    def burn_rate(self, requests, now, window_s) -> float:
        raise NotImplementedError

    def alerts(self, requests, now) -> list[str]:
        raise NotImplementedError

    def budget_remaining(self, requests, now, period_s=30 * 86400) -> float:
        raise NotImplementedError

    def canary_action(self, canary_requests, now, window_s=HOUR, max_burn=2.0, min_requests=500) -> str:
        raise NotImplementedError
