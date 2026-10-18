import math

import pytest

DOCS = [
    ("kb1", "Error ERR4031 means the payment gateway timed out. Retry the payment."),
    ("kb2", "Reset your password from the login page."),
    ("kb3", "Payment failed? Check card details. Payment retries happen automatically."),
    ("kb4", "Gateway maintenance window is Sunday."),
]


@pytest.fixture
def bm(impl):
    return impl.BM25().fit(DOCS)


def test_idf(bm):
    # 'payment' appears in kb1 and kb3 -> df=2, N=4
    assert bm.idf("payment") == pytest.approx(math.log((4 - 2 + 0.5) / (2 + 0.5) + 1))


def test_exact_score(bm):
    # kb2 tokens (stopwords removed): reset password login page -> |d| = 4
    from fde_kit import tokenize
    lens = [len(tokenize(t)) for _, t in DOCS]
    avg = sum(lens) / 4
    idf = math.log((4 - 1 + 0.5) / (1 + 0.5) + 1)
    expected = 2 * idf * (1 * 2.5) / (1 + 1.5 * (1 - 0.75 + 0.75 * 4 / avg))
    assert bm.score("password login", "kb2") == pytest.approx(expected)


def test_search_ranking(bm):
    res = bm.search("ERR4031 payment")
    assert res[0][0] == "kb1"
    assert [d for d, _ in res] == ["kb1", "kb3"]
    assert bm.search("nothing matches zzz") == []


def test_explain_sums(bm):
    ex = bm.explain("payment gateway retry", "kb1")
    assert set(ex) == {"payment", "gateway", "retry"}
    assert sum(ex.values()) == pytest.approx(bm.score("payment gateway retry", "kb1"))


def test_k_and_ties(impl):
    bm = impl.BM25().fit([("b", "same words"), ("a", "same words"), ("c", "other")])
    assert [d for d, _ in bm.search("same", k=1)] == ["a"]
