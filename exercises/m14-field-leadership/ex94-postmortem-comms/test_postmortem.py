import re

import pytest

EVENTS = [
    {"ts": "2026-10-14T13:02:00+00:00", "type": "detected", "note": "Error-budget page fired", "affected_users": 120},
    {"ts": "2026-10-14T13:09:00+00:00", "type": "identified", "note": "Upstream model overloaded; no retries"},
    {"ts": "2026-10-14T13:20:00+00:00", "type": "mitigated", "note": "Fallback model enabled", "affected_users": 340},
    {"ts": "2026-10-14T13:48:00+00:00", "type": "resolved", "note": "Error rate back under SLO", "affected_users": 0},
]


def test_status_updates(impl):
    u = impl.status_update("investigating", "Some adjusters see errors when asking coverage questions", 30)
    assert u == (impl.TEMPLATES["investigating"] + " Impact: Some adjusters see errors when asking coverage questions."
                 " Next update in 30 minutes.")
    r = impl.status_update("resolved", "No ongoing impact", 0)
    assert "Next update" not in r and r.startswith(impl.TEMPLATES["resolved"])
    assert impl.status_update("identified", "Answers are slow", 15, eta="14:00 UTC").endswith("Expected resolution: 14:00 UTC.")


@pytest.mark.parametrize("impact", ["copilot-7f9 pod in CrashLoop", "p95 latency high", "10.0.3.17 unreachable",
                                    "Customer ana@example.com cannot log in"])
def test_status_rejects_jargon_and_pii(impl, impact):
    with pytest.raises(ValueError):
        impl.status_update("investigating", impact, 30)


def test_impact(impl):
    assert impl.impact_summary(EVENTS) == {"duration_min": 46, "time_to_mitigate_min": 18, "peak_affected_users": 340}


def test_blame_lint(impl):
    text = "The on-call engineer should have noticed. Priya forgot to enable retries. This was human error."
    assert impl.blame_lint(text) == ["should have", "Priya forgot", "human error"]
    assert impl.blame_lint("Retries were not enabled because the client library defaulted to zero.") == []


def test_postmortem(impl):
    actions = [{"action": "Enable retries with backoff in the model client", "owner": "Platform", "due": "2026-10-21",
                "priority": "P1"},
               {"action": "Alert on upstream 529 rate", "owner": "SRE", "due": "2026-10-28", "priority": "P2"}]
    md = impl.render_postmortem("Copilot outage 2026-10-14", EVENTS,
                                "The model client had retries disabled by default, so upstream overloads became user errors.",
                                ["No alert existed for upstream overload responses"], ["Fallback model switch took 2 minutes"],
                                actions)
    heads = re.findall(r"^## (.*)$", md, re.M)
    assert heads == ["Summary", "Timeline", "Root cause", "Contributing factors", "What went well", "Action items"]
    assert "46 minutes" in md and "18 minutes" in md and "340" in md
    assert "- 13:20 UTC mitigated: Fallback model enabled" in md
    assert "| Enable retries with backoff in the model client | Platform | 2026-10-21 | P1 |" in md
    with pytest.raises(ValueError):
        impl.render_postmortem("t", EVENTS, "Sam broke the config.", [], [], actions)
    with pytest.raises(ValueError):
        impl.render_postmortem("t", EVENTS, "Config default.", [], [], [{"action": "x", "owner": "", "due": "2026-11-01", "priority": "P3"}])
