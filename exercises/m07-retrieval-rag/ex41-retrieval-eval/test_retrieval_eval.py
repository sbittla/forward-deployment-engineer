import math

import pytest

REL = {"d1": 3, "d4": 1}


def test_recall_precision(impl):
    assert impl.recall_at_k(["d2", "d1", "d3"], REL, 3) == 0.5
    assert impl.precision_at_k(["d2", "d1", "d3"], REL, 3) == pytest.approx(1 / 3)
    assert impl.recall_at_k(["d1"], {}, 3) == 0.0


def test_mrr(impl):
    assert impl.mrr(["d2", "d3", "d4"], REL) == pytest.approx(1 / 3)
    assert impl.mrr(["x"], REL) == 0


def test_ndcg(impl):
    ranked = ["d4", "d2", "d1"]
    dcg = (2 ** 1 - 1) / math.log2(2) + (2 ** 3 - 1) / math.log2(4)
    idcg = (2 ** 3 - 1) / math.log2(2) + (2 ** 1 - 1) / math.log2(3)
    assert impl.ndcg_at_k(ranked, REL, 3) == pytest.approx(dcg / idcg)
    assert impl.ndcg_at_k(["d1", "d4"], REL, 2) == pytest.approx(1.0)
    assert impl.ndcg_at_k(["d1"], {}, 3) == 0.0


QRELS = {
    "q1": {"query": "flood", "relevant": {"d1": 2}},
    "q2": {"query": "pipes", "relevant": {"d2": 1, "d3": 1}},
}


def test_evaluate_and_compare(impl):
    good = {"flood": ["d1", "d9"], "pipes": ["d2", "d3"]}
    bad = {"flood": ["d9", "d1"], "pipes": ["d9", "d8"]}
    a = impl.evaluate(lambda q, k: good[q][:k], QRELS, 2)
    b = impl.evaluate(lambda q, k: bad[q][:k], QRELS, 2)
    assert a["mean"]["recall"] == 1.0 and a["mean"]["mrr"] == 1.0
    assert b["per_query"]["q1"]["mrr"] == 0.5 and b["per_query"]["q2"]["recall"] == 0.0
    assert b["mean"]["precision"] == 0.25
    table = impl.compare(b, a, names=("baseline", "new"))
    lines = table.splitlines()
    assert lines[0] == "| Metric | baseline | new | Δ |"
    assert [l.split("|")[1].strip() for l in lines[2:]] == ["recall", "precision", "mrr", "ndcg"]
    assert "| mrr | 0.2500 | 1.0000 | +0.7500 |" in table


def test_no_relevant_documents(impl):
    assert impl.recall_at_k(["a"], {}, 5) == 0.0 and impl.mrr(["a"], {}) == 0.0
    assert impl.ndcg_at_k(["a"], {}, 5) == 0.0 and impl.precision_at_k([], {"a": 1}, 3) == 0.0
