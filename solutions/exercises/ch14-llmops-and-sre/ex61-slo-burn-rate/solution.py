from dataclasses import dataclass

HOUR = 3600


@dataclass
class SLO:
    target: float = 0.995
    latency_threshold_ms: float = 3000

    @property
    def error_budget(self) -> float:
        return 1 - self.target

    def _good(self, req) -> bool:
        _, status, latency = req
        return status < 500 and latency <= self.latency_threshold_ms

    def _window(self, requests, now, window_s):
        return [r for r in requests if now - window_s < r[0] <= now]

    def sli(self, requests, now, window_s):
        w = self._window(requests, now, window_s)
        if not w:
            return None
        return sum(self._good(r) for r in w) / len(w)

    def burn_rate(self, requests, now, window_s) -> float:
        s = self.sli(requests, now, window_s)
        if s is None:
            return 0.0
        return round((1 - s) / self.error_budget, 2)

    def alerts(self, requests, now) -> list[str]:
        def burning(long_w, short_w, threshold):
            return (self.burn_rate(requests, now, long_w) >= threshold
                    and self.burn_rate(requests, now, short_w) >= threshold)

        if burning(HOUR, 5 * 60, 14.4):
            return ["page"]
        if burning(6 * HOUR, 30 * 60, 6):
            return ["ticket"]
        return []

    def budget_remaining(self, requests, now, period_s=30 * 86400) -> float:
        w = self._window(requests, now, period_s)
        if not w:
            return 1.0
        bad = sum(not self._good(r) for r in w)
        return round(1 - bad / (len(w) * self.error_budget), 4)

    def canary_action(self, canary_requests, now, window_s=HOUR, max_burn=2.0, min_requests=500) -> str:
        w = self._window(canary_requests, now, window_s)
        bad = sum(not self._good(r) for r in w)
        if bad > max_burn * self.error_budget * min_requests:
            return "rollback"          # the canary has already spent more than its minimum sample may
        if len(w) < min_requests:
            return "wait"
        return "rollback" if self.burn_rate(canary_requests, now, window_s) > max_burn else "promote"
