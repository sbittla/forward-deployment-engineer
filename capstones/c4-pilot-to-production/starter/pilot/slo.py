"""SLO arithmetic for the service: SLI, burn rate and multi-window alerts."""
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
