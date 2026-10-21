import inspect
from datetime import datetime, timezone

import pytest

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
TICKETS = [
    {"id": "T1", "priority": "P1", "opened": "2026-10-16T06:00:00+00:00"},
    {"id": "T2", "priority": "sev2", "opened": "2026-10-14T12:00:00+00:00"},
    {"id": "T3", "priority": "low", "opened": "2026-10-10T12:00:00+00:00"},
    {"id": "T4", "priority": "URGENT", "opened": "2026-10-16T10:00:00+00:00"},
    {"id": "T5", "priority": "whatever", "opened": "2026-10-15T12:00:00+00:00"},
]


def test_parity_with_legacy(impl):
    assert impl.build_report(TICKETS, impl.ACME_CONFIG, NOW) == impl.legacy_acme_report(TICKETS, NOW)
    assert impl.build_report([], impl.ACME_CONFIG, NOW) == impl.legacy_acme_report([], NOW)


def test_other_customer(impl):
    cfg = impl.ReportConfig(
        customer_name="Globex", sla_hours={"critical": 1, "standard": 8},
        priority_aliases={"crit": "critical", "critical": "critical", "normal": "standard", "std": "standard"},
        utc_offset_hours=1, escalation_contact="noc@globex.example")
    cfg.validate()
    tickets = [{"id": "G1", "priority": "CRIT", "opened": "2026-10-16T09:00:00+00:00"},
               {"id": "G2", "priority": "std", "opened": "2026-10-16T05:00:00+00:00"}]
    out = impl.build_report(tickets, cfg, NOW).splitlines()
    assert out[0] == "GLOBEX - SLA breach report"
    assert out[1] == "- G1 [critical] opened 2026-10-16 10:00 local, 2.0h over SLA"
    assert out[-2:] == ["Total breaches.".replace(".", ":") + " 1", "Escalate to: noc@globex.example"]


def test_unknown_priority_without_normal_sla_is_config_error(impl):
    cfg = impl.ReportConfig("X", {"high": 4}, {"p1": "urgent"})
    with pytest.raises(ValueError):
        cfg.validate()
    with pytest.raises(ValueError):
        impl.ReportConfig("X", {"urgent": 0}, {"p1": "urgent"}).validate()


def test_no_customer_names_in_library_code(impl):
    src = inspect.getsource(impl.build_report).lower()
    assert "acme" not in src and "support-leads" not in src
