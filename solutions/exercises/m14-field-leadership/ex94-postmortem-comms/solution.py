import re
from datetime import datetime

TEMPLATES = {
    "investigating": "We are investigating reports that the claims copilot is unavailable or slow.",
    "identified": "We have identified the cause and are applying a fix.",
    "monitoring": "A fix is in place and we are monitoring to confirm full recovery.",
    "resolved": "The issue is resolved and the claims copilot is operating normally.",
}
JARGON = ("pod", "k8s", "kubernetes", "oom", "crashloop", "p95", "hpa", "sev1", "sev2", "rca")
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
BLAME = re.compile(r"should have|failed to|careless|human error|\bfault\b|\b[A-Z][a-z]+ (?:broke|caused|forgot|missed)\b")


def status_update(stage: str, impact: str, next_update_min: int, eta: str | None = None) -> str:
    low = impact.lower()
    if any(re.search(rf"\b{j}\b", low) for j in JARGON) or IP.search(impact) or EMAIL.search(impact):
        raise ValueError("customer updates must not contain internal jargon, IP addresses or email addresses")
    parts = [TEMPLATES[stage], f"Impact: {impact.rstrip('.')}."]
    if stage != "resolved":
        parts.append(f"Next update in {next_update_min} minutes.")
    if eta:
        parts.append(f"Expected resolution: {eta}.")
    return " ".join(parts)


def _t(e):
    return datetime.fromisoformat(e["ts"])


def impact_summary(events: list[dict]) -> dict:
    first = {}
    for e in sorted(events, key=_t):
        first.setdefault(e["type"], _t(e))
    minutes = lambda a, b: int((first[b] - first[a]).total_seconds() // 60) if a in first and b in first else None
    return {"duration_min": minutes("detected", "resolved"), "time_to_mitigate_min": minutes("detected", "mitigated"),
            "peak_affected_users": max((e.get("affected_users", 0) for e in events), default=0)}


def blame_lint(text: str) -> list[str]:
    return [m.group(0) for m in BLAME.finditer(text)]


def render_postmortem(title, events, root_cause, contributing, went_well, actions) -> str:
    flagged = blame_lint(" ".join([root_cause, *contributing]))
    if flagged:
        raise ValueError(f"blameful language: {flagged}")
    for a in actions:
        if not a.get("owner") or not a.get("due"):
            raise ValueError(f"action item needs an owner and a due date: {a.get('action')}")
    s = impact_summary(events)
    lines = [f"# Postmortem: {title}", "", "## Summary",
             f"Duration {s['duration_min']} minutes; mitigated after {s['time_to_mitigate_min']} minutes; "
             f"peak {s['peak_affected_users']} affected users.", "", "## Timeline"]
    lines += [f"- {_t(e):%H:%M} UTC {e['type']}: {e.get('note', '')}" for e in sorted(events, key=_t)]
    lines += ["", "## Root cause", root_cause, "", "## Contributing factors", *[f"- {c}" for c in contributing],
              "", "## What went well", *[f"- {w}" for w in went_well],
              "", "## Action items", "| Action | Owner | Due | Priority |", "|---|---|---|---|"]
    lines += [f"| {a['action']} | {a['owner']} | {a['due']} | {a.get('priority', '')} |" for a in actions]
    return "\n".join(lines) + "\n"
