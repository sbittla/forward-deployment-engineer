from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


def legacy_acme_report(tickets, now):
    """The original on-site script. Do not modify: it is the behavioural reference."""
    lines = ["ACME CORP - SLA breach report"]
    breached = []
    for t in tickets:
        p = t["priority"].lower()
        if p in ("p1", "sev1", "urgent"):
            p = "urgent"
        elif p in ("p2", "sev2", "high"):
            p = "high"
        else:
            p = "normal"
        limit = {"urgent": 4, "high": 24, "normal": 72}[p]
        opened = datetime.fromisoformat(t["opened"])
        age_h = (now - opened).total_seconds() / 3600
        if age_h > limit:
            local = opened + timedelta(hours=-5)
            breached.append((age_h - limit, f"- {t['id']} [{p}] opened {local:%Y-%m-%d %H:%M} local, "
                                            f"{age_h - limit:.1f}h over SLA"))
    for _, line in sorted(breached, key=lambda x: -x[0]):
        lines.append(line)
    lines.append(f"Total breaches: {len(breached)}")
    if breached:
        lines.append("Escalate to: support-leads@acme.example")
    return "\n".join(lines)


@dataclass
class ReportConfig:
    customer_name: str
    sla_hours: dict[str, float]
    priority_aliases: dict[str, str]
    utc_offset_hours: float = 0
    escalation_contact: str = ""

    def validate(self) -> None:
        raise NotImplementedError


ACME_CONFIG = None  # build the ReportConfig that reproduces legacy_acme_report


def build_report(tickets, config: ReportConfig, now: datetime) -> str:
    raise NotImplementedError
