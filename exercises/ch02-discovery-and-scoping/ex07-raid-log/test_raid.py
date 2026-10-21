from datetime import date

import pytest

D = date


@pytest.fixture
def log(impl):
    L = impl.RaidLog()
    I = impl.RaidItem
    L.add(I("R", "IdP integration slips", owner="Priya", created=D(2026, 10, 1), due=D(2026, 10, 20),
            probability=4, impact=4, mitigation="Fallback to local accounts for pilot"))
    L.add(I("A", "Policy PDFs are text-extractable", owner="Lee", created=D(2026, 10, 1)))
    L.add(I("I", "Staging VPN unstable", owner="Sam", created=D(2026, 10, 2), due=D(2026, 10, 10)))
    L.add(I("D", "Use managed vector DB", owner="Dana", created=D(2026, 10, 3),
            rationale="No ops headcount", decided_by="Steering committee"))
    L.add(I("R", "Low adoption", owner="Lee", created=D(2026, 10, 4), probability=2, impact=5,
            mitigation="Champions program"))
    return L


def test_ids(log):
    assert [i.id for i in log.items] == ["R-1", "A-2", "I-3", "D-4", "R-5"]


@pytest.mark.parametrize("kw", [
    dict(kind="X", title="t", owner="o"),
    dict(kind="R", title="t", owner="o", probability=3, impact=3),
    dict(kind="R", title="t", owner="o", probability=6, impact=3, mitigation="m"),
    dict(kind="D", title="t", owner="o", rationale="r"),
    dict(kind="A", title="t"),
])
def test_validation(impl, kw):
    with pytest.raises(ValueError):
        impl.RaidLog().add(impl.RaidItem(**kw))


def test_top_risks(log):
    assert [r.title for r in log.top_risks(2)] == ["IdP integration slips", "Low adoption"]
    assert log.score(log.items[0]) == 16 and log.score(log.items[1]) == 0


def test_overdue_and_escalations(log):
    today = D(2026, 10, 16)
    assert [i.id for i in log.overdue(today)] == ["I-3"]
    assert [i.id for i in log.escalations(today)] == ["R-1", "I-3"]
    log.items[0].status = "closed"
    assert [i.id for i in log.escalations(D(2026, 10, 12))] == []  # issue only 2 days overdue


def test_markdown(log):
    md = log.to_markdown()
    assert md.splitlines()[0] == "| ID | Type | Title | Owner | Score | Status |"
    assert "| R-1 | Risk | IdP integration slips | Priya | 16 | open |" in md
    assert "| D-4 | Decision | Use managed vector DB | Dana | 0 | open |" in md
