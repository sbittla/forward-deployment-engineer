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
        raise NotImplementedError

    def burn_rate(self, events, now: float, window_s: float) -> float:
        raise NotImplementedError

    def alerts(self, events, now: float) -> list[str]:
        """Page on a fast burn (14.4x over 1 hour and 5 minutes); ticket on a slow burn (6x over 6 h and 30 min)."""
        raise NotImplementedError


def canary_decision(base: dict, canary: dict, min_requests: int = 500) -> tuple[str, list[str]]:
    """Return ("wait" | "rollback" | "promote", reasons).

    Wait below `min_requests`. Roll back when: the canary leaked any forbidden document; it answered any
    unanswerable question when the base didn't; its error rate exceeds 1.5x the base's plus 0.001; its p95 exceeds
    1.2x the base's; its pass rate is more than 0.03 below the base's; or its cost per successful answer exceeds
    1.2x the base's.
    """
    raise NotImplementedError


def run_rollout(base: dict, observe, stages=ROLLOUT_STAGES, min_requests: int = 500) -> dict:
    """Walk the stages (percent of adjusters). `observe(percent)` returns the canary's metrics at that stage.

    The first "rollback" sends traffic back to 0% automatically; a "wait" stops the rollout where it is.
    """
    raise NotImplementedError
