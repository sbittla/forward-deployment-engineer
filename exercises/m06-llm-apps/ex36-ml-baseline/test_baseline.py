import itertools

import pytest

from fde_kit import FakeLLM

TEMPLATES = {
    "billing": ["charged twice on my invoice", "refund for the duplicate payment", "invoice amount is wrong",
                "update credit card for billing", "why was my card charged", "billing statement missing"],
    "login": ["cannot log in to my account", "password reset email never arrives", "locked out after 2fa",
              "login page says invalid password", "sso sign in fails", "forgot my username"],
    "outage": ["site is down for everyone", "api returns 503 errors", "service unavailable since morning",
               "dashboard not loading outage", "everything timing out down", "status page shows outage"],
}
SUFFIXES = ["", " please help", " urgent", " asap", " thanks", " again today", " since yesterday"]
ROWS = [(t + s, lab) for lab, ts in TEMPLATES.items() for t, s in itertools.product(ts, SUFFIXES)]


def test_split_stratified_deterministic(impl):
    tr1, te1 = impl.train_test_split(ROWS, 0.25, seed=7)
    tr2, te2 = impl.train_test_split(ROWS, 0.25, seed=7)
    assert te1 == te2 and len(tr1) + len(te1) == len(ROWS)
    for lab in TEMPLATES:
        assert sum(1 for _, l in te1 if l == lab) == round(42 * 0.25)
    assert set(te1).isdisjoint(set(tr1)) or len(set(te1) & set(tr1)) == 0


def test_naive_bayes(impl):
    tr, te = impl.train_test_split(ROWS, 0.25, seed=1)
    nb = impl.NaiveBayes().fit([t for t, _ in tr], [l for _, l in tr])
    p = nb.predict_proba("my invoice shows a duplicate charge")
    assert abs(sum(p.values()) - 1) < 1e-9 and max(p, key=p.get) == "billing"
    preds = [nb.predict(t) for t, _ in te]
    m = impl.metrics([l for _, l in te], preds)
    assert m["accuracy"] >= 0.9 and m["macro_f1"] >= 0.9


def test_metrics_exact(impl):
    y_true = ["a", "a", "b", "b", "c"]
    y_pred = ["a", "b", "b", "b", "a"]
    m = impl.metrics(y_true, y_pred)
    assert m["accuracy"] == 0.6
    assert m["per_class"]["a"] == {"precision": 0.5, "recall": 0.5, "f1": 0.5}
    assert m["per_class"]["b"] == {"precision": 0.667, "recall": 1.0, "f1": 0.8}
    assert m["per_class"]["c"] == {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    assert m["macro_f1"] == 0.433
    assert m["confusion"][("c", "a")] == 1


def test_llm_classify(impl):
    llm = FakeLLM([" Billing.", "LOGIN", "I think it's a hardware issue"])
    labels = ["billing", "login", "outage"]
    assert impl.llm_classify(llm, "x", labels) == "billing"
    assert impl.llm_classify(llm, "x", labels) == "login"
    assert impl.llm_classify(llm, "x", labels) == "unknown"
    prompt = llm.calls[0]["system"] or llm.calls[0]["messages"][0]["content"]
    assert all(l in prompt for l in labels)


def test_recommend(impl):
    assert impl.recommend({"macro_f1": 0.93}, {"macro_f1": 0.95}, 500_000, 0.002) == ("baseline", 1000.0)
    assert impl.recommend({"macro_f1": 0.80}, {"macro_f1": 0.95}, 500_000, 0.002) == ("llm", 1000.0)
