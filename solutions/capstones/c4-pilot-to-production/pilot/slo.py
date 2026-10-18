"""SLO arithmetic for the service: SLI, burn rate and multi-window alerts."""
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
