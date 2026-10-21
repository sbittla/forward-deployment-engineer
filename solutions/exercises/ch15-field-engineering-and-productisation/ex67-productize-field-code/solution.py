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


DEFAULT_PRIORITY = "normal"


@dataclass
class ReportConfig:
    customer_name: str
    sla_hours: dict[str, float]
    priority_aliases: dict[str, str]
    utc_offset_hours: float = 0
    escalation_contact: str = ""

    def validate(self) -> None:
        missing = sorted(set(self.priority_aliases.values()) - self.sla_hours.keys())
        if missing:
            raise ValueError(f"no SLA defined for priorities: {', '.join(missing)}")
        if any(h <= 0 for h in self.sla_hours.values()):
            raise ValueError("SLA hours must be positive")

    def canonical(self, raw: str) -> str:
        p = self.priority_aliases.get(raw.lower())
        if p is None:
            p = DEFAULT_PRIORITY if DEFAULT_PRIORITY in self.sla_hours else min(self.sla_hours, key=self.sla_hours.get)
        return p


ACME_CONFIG = ReportConfig(
    customer_name="Acme Corp",
    sla_hours={"urgent": 4, "high": 24, "normal": 72},
    priority_aliases={"p1": "urgent", "sev1": "urgent", "urgent": "urgent",
                      "p2": "high", "sev2": "high", "high": "high"},
    utc_offset_hours=-5,
    escalation_contact="support-leads@acme.example",
)


def build_report(tickets, config: ReportConfig, now: datetime) -> str:
    config.validate()
    breached = []
    for t in tickets:
        p = config.canonical(t["priority"])
        limit = config.sla_hours[p]
        opened = datetime.fromisoformat(t["opened"])
        over = (now - opened).total_seconds() / 3600 - limit
        if over > 0:
            local = opened + timedelta(hours=config.utc_offset_hours)
            breached.append((over, f"- {t['id']} [{p}] opened {local:%Y-%m-%d %H:%M} local, {over:.1f}h over SLA"))
    lines = [f"{config.customer_name.upper()} - SLA breach report"]
    lines += [line for _, line in sorted(breached, key=lambda x: -x[0])]
    lines.append(f"Total breaches: {len(breached)}")
    if breached and config.escalation_contact:
        lines.append(f"Escalate to: {config.escalation_contact}")
    return "\n".join(lines)
