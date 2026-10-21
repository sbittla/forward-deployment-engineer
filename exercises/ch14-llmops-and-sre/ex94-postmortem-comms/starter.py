import re
from datetime import datetime

TEMPLATES = {
    "investigating": "We are investigating reports that the claims copilot is unavailable or slow.",
    "identified": "We have identified the cause and are applying a fix.",
    "monitoring": "A fix is in place and we are monitoring to confirm full recovery.",
    "resolved": "The issue is resolved and the claims copilot is operating normally.",
}
JARGON = ("pod", "k8s", "kubernetes", "oom", "crashloop", "p95", "hpa", "sev1", "sev2", "rca")


def status_update(stage: str, impact: str, next_update_min: int, eta: str | None = None) -> str:
    raise NotImplementedError


def impact_summary(events: list[dict]) -> dict:
    raise NotImplementedError


def blame_lint(text: str) -> list[str]:
    raise NotImplementedError


def render_postmortem(title, events, root_cause, contributing, went_well, actions) -> str:
    raise NotImplementedError
