import pytest

DOCS = {
    "a": "how to reset a forgotten password",
    "b": "error code ERR4031 payment gateway timeout",
    "c": "password requirements and complexity rules",
    "d": "payment methods accepted credit card invoice",
}


def test_vector_index(impl):
    vi = impl.VectorIndex()
    for k, v in DOCS.items():
        vi.add(k, v)
    res = vi.search("reset password", k=2)
    assert res[0][0] == "a" and len(res) == 2 and res[0][1] > res[1][1]
    assert vi.search("zzzz qqqq", k=3) == []


def test_rrf_math(impl):
    fused = impl.rrf([["a", "b", "c"], ["b", "d"]], k=60)
    scores = dict(fused)
    assert scores["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert scores["a"] == pytest.approx(1 / 61)
    assert scores["d"] == pytest.approx(1 / 62)
    assert [d for d, _ in fused] == ["b", "a", "d", "c"]


def test_rrf_tie_break(impl):
    assert [d for d, _ in impl.rrf([["y"], ["x"]])] == ["x", "y"]


def test_hybrid(impl):
    kw = lambda q, n: ["b", "d"][:n]
    vec = lambda q, n: ["d", "a", "b"][:n]
    out = impl.hybrid_search("payment error", kw, vec, k=2)
    # d: 1/62 + 1/61 beats b: 1/61 + 1/63 - consistent mid ranks beat one top rank
    assert [d for d, _ in out] == ["d", "b"]
    assert impl.explain_fusion("payment error", kw, vec, "a") == {"keyword_rank": None, "vector_rank": 2}


def test_hybrid_calls_with_depth(impl):
    seen = []

    def kw(q, n):
        seen.append(n)
        return []

    impl.hybrid_search("q", kw, kw, k=3, depth=7)
    assert seen == [7, 7]
