import pytest

SOURCES = [
    "Section 9.1: Flood damage is excluded from the homeowner policy.",
    "Section 7.2: Burst pipe water damage is covered up to the dwelling limit. Contact claims@northwind.com.",
]


@pytest.fixture
def policy(impl):
    return impl.Policy(blocked_topics={"legal_advice": ["sue", "lawsuit", "attorney"], "medical": ["diagnosis"]},
                       banned_phrases=["guaranteed", "100% approved"])


def test_clean_grounded(impl, policy):
    ans = "Flood damage is excluded from your policy. Burst pipe damage is covered up to the dwelling limit."
    r = impl.check_output(ans, SOURCES, policy)
    assert r.allowed and r.violations == [] and r.safe_text == ans


def test_ungrounded_removed(impl, policy):
    ans = "Flood damage is excluded. Earthquakes trigger automatic payouts within hours!"
    r = impl.check_output(ans, SOURCES, policy)
    assert r.allowed and r.violations == ["ungrounded:Earthquakes trigger automatic payouts within hours!"]
    assert r.safe_text == "Flood damage is excluded."


def test_blocked(impl, policy):
    ans = "You should sue them. Approval is guaranteed. Email ana@example.com or claims@northwind.com."
    r = impl.check_output(ans, SOURCES, policy)
    assert not r.allowed and r.safe_text == policy.fallback
    assert r.violations[:3] == ["topic:legal_advice", "phrase:guaranteed", "pii_leak"]


def test_whole_word_topics(impl, policy):
    r = impl.check_output("Flood damage is excluded; pursue the claims process.", SOURCES, policy)
    assert "topic:legal_advice" not in r.violations


def test_all_ungrounded_falls_back(impl, policy):
    r = impl.check_output("Totally unrelated content here.", SOURCES, policy)
    assert r.allowed and r.safe_text == policy.fallback


def test_ssn_leak(impl, policy):
    r = impl.check_output("Flood damage is excluded for 123-45-6789.", SOURCES, policy)
    assert not r.allowed and "pii_leak" in r.violations
