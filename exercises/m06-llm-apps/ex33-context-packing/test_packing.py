import pytest

SYSTEM = "S" * 400          # 100 tokens
QUESTION = "Q" * 40         # 10 tokens
DOCS = [("low", "L" * 800, 0.2), ("top", "T" * 800, 0.9), ("mid", "M" * 2000, 0.5)]  # 200, 200, 500 tokens
HISTORY = [
    {"role": "user", "content": "u1" * 100}, {"role": "assistant", "content": "a1" * 100},   # 50 + 50
    {"role": "user", "content": "u2" * 100}, {"role": "assistant", "content": "a2" * 100},   # 50 + 50
]


def test_count(impl):
    assert impl.count_tokens("") == 0 and impl.count_tokens("abcde") == 2


def test_everything_fits(impl):
    p = impl.pack(SYSTEM, QUESTION, DOCS, HISTORY, budget=5000, reserve_output=1000)
    assert p.included_docs == ["top", "mid", "low"] and p.truncated == [] and p.dropped_docs == []
    assert [m["content"][:2] for m in p.messages] == ["u1", "a1", "u2", "a2", "QQ"]
    assert '<doc id="top">' in p.system and p.system.startswith(SYSTEM + "\n\n<documents>\n")
    assert p.tokens == impl.count_tokens(p.system) + sum(impl.count_tokens(m["content"]) for m in p.messages)


def test_truncation_and_history_priority(impl):
    # available = 700; mandatory 110 -> 590 left; top(200 + wrapper) fits; mid truncated
    p = impl.pack(SYSTEM, QUESTION, DOCS, HISTORY, budget=1000, reserve_output=300)
    assert p.included_docs[0] == "top" and p.truncated == ["mid"]
    assert "low" in p.dropped_docs
    assert p.tokens <= 700


def test_history_recent_pairs_first(impl):
    p = impl.pack(SYSTEM, QUESTION, [], HISTORY, budget=330, reserve_output=100)
    # 230 available, 110 mandatory -> 120 left -> only the most recent pair (100) fits
    assert [m["content"][:2] for m in p.messages] == ["u2", "a2", "QQ"]
    assert "<documents>" not in p.system


def test_mandatory_overflow(impl):
    with pytest.raises(ValueError):
        impl.pack(SYSTEM, QUESTION, DOCS, HISTORY, budget=150, reserve_output=100)
