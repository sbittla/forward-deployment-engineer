import pytest


@pytest.fixture
def feats(impl):
    F = impl.Feature
    return [
        F("sso", "must", 8, 5),
        F("rag-answers", "must", 10, 8, ("ingest",)),
        F("ingest", "should", 5, 4),
        F("citations", "should", 9, 3, ("rag-answers",)),
        F("analytics", "should", 4, 4),
        F("feedback-buttons", "could", 3, 1),
        F("slack-bot", "could", 6, 6),
        F("voice", "wont", 9, 10),
    ]


def test_plan(impl, feats):
    p = impl.plan(feats, 25)
    # musts with deps: ingest(4) pulled in before rag-answers(8), sso(5) => 17
    assert p.included[:3] == ["sso", "ingest", "rag-answers"] or p.included[:3] == ["ingest", "rag-answers", "sso"]
    assert set(p.included) == {"sso", "ingest", "rag-answers", "citations", "analytics", "feedback-buttons"}
    assert p.included.index("citations") < p.included.index("analytics")
    assert p.deferred == ["slack-bot", "voice"]
    assert p.slack == 0


def test_musts_overflow(impl, feats):
    with pytest.raises(impl.ScopeError) as e:
        impl.plan(feats, 15)
    assert "17" in str(e.value) and "15" in str(e.value)


def test_dependency_not_satisfiable(impl):
    F = impl.Feature
    p = impl.plan([F("a", "must", 1, 1), F("b", "could", 9, 1, ("c",)), F("c", "wont", 1, 1)], 10)
    assert p.included == ["a"] and p.deferred == ["b", "c"] and p.slack == 9


def test_message(impl):
    p = impl.Plan(included=["a", "b"], deferred=["c"], slack=2)
    assert impl.tradeoff_message(p) == "Included: a, b. Deferred to phase 2: c. Slack: 2 days."
    p = impl.Plan(included=["a"], deferred=[], slack=0)
    assert impl.tradeoff_message(p) == "Included: a. Deferred to phase 2: none. Slack: 0 days."
