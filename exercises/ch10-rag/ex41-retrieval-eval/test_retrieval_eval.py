import math

import pytest

from fde_kit import tokenize

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


# --- A fixed, reproducible benchmark (exercise data) ---------------------------------------------------------------
# Twelve Northwind chunks plus traps: a superseded policy version, another tenant's chunk and an upload with no
# tenant. The baseline ranks every chunk; the candidate ranks only current, same-tenant chunks (fail closed on a
# missing tenant). Same ranker, so the delta is the filter's alone.
BENCH_CORPUS = [
    # (doc_id, tenant, superseded, text)
    ("pol-7.2-v1", "northwind", True, "Burst pipe water damage is covered."),
    ("pol-7.2-v2", "northwind", False, "Burst pipe water damage is covered unless the home was unoccupied for more "
                                       "than 30 days."),
    ("pol-9.1", "northwind", False, "Flood damage from rising surface water is excluded."),
    ("pol-4.3", "northwind", False, "Theft of contents is covered when there are signs of forced entry."),
    ("pol-12.4", "northwind", False, "Mold remediation is covered only when caused by a covered water loss."),
    ("pol-15.1", "northwind", False, "Roof damage from hail is covered at actual cash value."),
    ("faq-3-v1", "northwind", True, "Claims must be filed within 60 days of the loss."),
    ("faq-3-v2", "northwind", False, "Claims must be filed within 30 days of the loss."),
    ("faq-5", "northwind", False, "Adjusters may request photos of the damage and repair estimates."),
    ("faq-8", "northwind", False, "A rental car is covered for up to 14 days after a covered auto loss."),
    ("acme-claims", "acme", False, "Claims must be filed within 30 days of the loss or the premium pricing tier "
                                   "is lost."),
    ("imp-77", None, False, "Theft of contents is covered for all customers."),
]
BENCH_QRELS = {
    "b1": {"query": "is burst pipe water damage covered", "relevant": {"pol-7.2-v2": 2}},
    "b2": {"query": "how many days to file claims after a loss", "relevant": {"faq-3-v2": 2}},
    "b3": {"query": "is theft of contents covered", "relevant": {"pol-4.3": 2}},
    "b4": {"query": "flood damage surface water", "relevant": {"pol-9.1": 2}},
    "b5": {"query": "mold remediation water loss", "relevant": {"pol-12.4": 2, "pol-7.2-v2": 1}},
    "b6": {"query": "hail roof damage", "relevant": {"pol-15.1": 2}},
    "b7": {"query": "photos repair estimates", "relevant": {"faq-5": 2}},
    "b8": {"query": "rental car after auto loss", "relevant": {"faq-8": 2}},
}
BENCH_UNANSWERABLE = ["earthquake damage cover limits", "premium pricing for pets"]
TENANT, BENCH_K, MIN_SCORE = "northwind", 3, 0.5


def _ranker(chunks):
    """Share of query terms found in the chunk; ties by doc id. Returns [(doc_id, score)] with score > 0."""
    def retrieve(query, k):
        q = set(tokenize(query))
        scored = [(d, len(q & set(tokenize(text))) / len(q)) for d, _, _, text in chunks]
        scored = sorted((s for s in scored if s[1] > 0), key=lambda s: (-s[1], s[0]))
        return scored[:k]
    return retrieve


BASELINE = _ranker(BENCH_CORPUS)
CANDIDATE = _ranker([c for c in BENCH_CORPUS if c[1] == TENANT and not c[2]])  # None tenant: excluded
STALE = {d for d, _, superseded, _ in BENCH_CORPUS if superseded}
FOREIGN = {d for d, tenant, _, _ in BENCH_CORPUS if tenant != TENANT}


def _ids(retrieve):
    return lambda q, k: [d for d, _ in retrieve(q, k)]


def _leaks(retrieve, ids):
    return sum(1 for q in BENCH_QRELS.values() if ids & set(_ids(retrieve)(q["query"], BENCH_K)))


def _abstained(retrieve, query):
    hits = retrieve(query, BENCH_K)
    return not hits or hits[0][1] < MIN_SCORE


def _cites_top(retrieve):
    # Simulated answers: each answerable question's reply cites its top retrieved chunk.
    return [{"citations": _ids(retrieve)(q["query"], 1), "supporting": list(q["relevant"])}
            for q in BENCH_QRELS.values()]


def test_citation_precision_and_abstention_report(impl):
    answers = [{"citations": ["d1", "d2"], "supporting": ["d1"]}, {"citations": [], "supporting": ["d3"]},
               {"citations": ["d3"], "supporting": ["d3", "d4"]}]
    assert impl.citation_precision(answers) == pytest.approx(0.6667)
    assert impl.citation_precision([{"citations": [], "supporting": ["d1"]}]) == 0.0
    report = impl.abstention_report([{"answerable": True, "abstained": True}, {"answerable": True, "abstained": False},
                                     {"answerable": False, "abstained": False}])
    assert report == {"answerable": 2, "abstained_answerable": 1, "unanswerable": 1, "answered_unanswerable": 1}


def test_benchmark_baseline_vs_candidate(impl):
    base = impl.evaluate(_ids(BASELINE), BENCH_QRELS, BENCH_K)
    cand = impl.evaluate(_ids(CANDIDATE), BENCH_QRELS, BENCH_K)
    assert base["mean"] == {"recall": 0.9375, "precision": 0.3333, "mrr": 0.7917, "ndcg": 0.8235}
    assert cand["mean"] == {"recall": 0.9375, "precision": 0.3333, "mrr": 1.0, "ndcg": 0.9783}
    table = impl.compare(base, cand, names=("baseline", "candidate"))
    assert "| mrr | 0.7917 | 1.0000 | +0.2083 |" in table and "| recall | 0.9375 | 0.9375 | +0.0000 |" in table


def test_benchmark_stale_and_foreign_never_cited(impl):
    assert (_leaks(BASELINE, STALE), _leaks(BASELINE, FOREIGN)) == (6, 4)  # queries with a trap in the top 3
    assert (_leaks(CANDIDATE, STALE), _leaks(CANDIDATE, FOREIGN)) == (0, 0)
    assert impl.citation_precision(_cites_top(BASELINE)) == 0.625
    assert impl.citation_precision(_cites_top(CANDIDATE)) == 1.0
    assert not {d for a in _cites_top(CANDIDATE) for d in a["citations"]} & (STALE | FOREIGN)


def test_benchmark_abstention(impl):
    def report(retrieve):
        return impl.abstention_report(
            [{"answerable": True, "abstained": _abstained(retrieve, q["query"])} for q in BENCH_QRELS.values()]
            + [{"answerable": False, "abstained": _abstained(retrieve, q)} for q in BENCH_UNANSWERABLE])
    # The baseline "answers" one unanswerable question from another tenant's chunk.
    assert report(BASELINE) == {"answerable": 8, "abstained_answerable": 0, "unanswerable": 2,
                                "answered_unanswerable": 1}
    assert report(CANDIDATE)["answered_unanswerable"] == 0 and report(CANDIDATE)["abstained_answerable"] == 0
