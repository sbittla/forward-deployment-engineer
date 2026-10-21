import random

import pytest

LABELS = {"refund": "billing", "invoice": "billing", "charge": "billing", "password": "account", "login": "account",
          "crash": "bug", "error": "bug"}


def model(prompt, text):
    """A deterministic stand-in whose behaviour depends on prompt wording, like a real model's."""
    label = next((v for k, v in LABELS.items() if k in text.lower()), "other")
    if "urgent" in text.lower() and "Escalate" not in prompt:
        label = "other"
    if "label only" not in prompt:
        return f"The category is {label}."
    if "lowercase" not in prompt:
        return label.upper() if len(text) % 2 else label
    return label


CASES = [{"input": t, "expected": e} for t, e in [
    ("Refund please", "billing"), ("Invoice wrong", "billing"), ("Double charge on card", "billing"),
    ("Password reset fails", "account"), ("Login loop", "account"), ("App crash on save", "bug"),
    ("Error 500 on export", "bug"), ("URGENT refund now", "billing"), ("urgent: login broken", "account"),
    ("Where is the office", "other"), ("Crash after update", "bug"), ("Invoice missing VAT", "billing"),
    ("urgent crash in prod", "bug"), ("Change my password", "account"), ("Hello there", "other"),
    ("Charge disputed", "billing"), ("Login with SSO", "account"), ("Weird error toast", "bug"),
    ("urgent invoice overdue", "billing"), ("Feature idea", "other")]]
EDITS = {
    "label_only": lambda p: p + "\nReply with the label only.",
    "lowercase": lambda p: p + "\nUse lowercase.",
    "escalate": lambda p: p + "\nEscalate means: urgent tickets keep their topic label.",
    "verbose_role": lambda p: "You are a world-class expert.\n" + p,
}
BASE = "Classify the ticket."


def grader(out, exp):
    return out == exp


def test_split_is_deterministic_and_disjoint(impl):
    train, test = impl.split(CASES, 0.3, seed=7)
    assert len(train) == 14 and len(test) == 6
    assert [CASES.index(c) for c in test] == [17, 15, 11, 18, 7, 6]
    assert impl.split(CASES, 0.3, seed=7) == (train, test)
    assert not {id(c) for c in train} & {id(c) for c in test}
    assert len(impl.split(CASES[:2], 0.1)[1]) == 1
    with pytest.raises(ValueError):
        impl.split(CASES, 1.0)


def test_evaluate(impl):
    assert impl.evaluate(BASE, CASES, model, grader) == 0.0
    assert impl.run(BASE + "\nReply with the label only.", CASES[:5], model, grader) == [False, False, False, True, True]
    assert impl.evaluate(BASE, [], model, grader) == 0.0


def test_hill_climb_greedy_path(impl):
    train, test = impl.split(CASES, 0.3, seed=7)
    r = impl.hill_climb(BASE, EDITS, train, test, model, grader)
    assert [h["edit"] for h in r.history] == [None, "label_only", "lowercase", "escalate"]
    assert [h["train"] for h in r.history] == [0.0, 0.4286, 0.8571, 1.0]
    assert [h["round"] for h in r.history] == [0, 1, 2, 3]
    assert "world-class" not in r.prompt            # edits that don't help are never applied
    assert r.prompt.endswith("Escalate means: urgent tickets keep their topic label.")
    assert r.train == 1.0 and r.test == 1.0 and r.overfit_gap == 0.0


def test_round_limit_and_min_gain(impl):
    train, test = impl.split(CASES, 0.3, seed=7)
    assert len(impl.hill_climb(BASE, EDITS, train, test, model, grader, max_rounds=1).history) == 2
    stuck = impl.hill_climb(BASE, EDITS, train, test, model, grader, min_gain=0.5)
    assert stuck.prompt == BASE and len(stuck.history) == 1
    assert impl.hill_climb(BASE, {}, train, test, model, grader).prompt == BASE


def test_test_split_scored_once(impl):
    train, test = impl.split(CASES, 0.3, seed=7)
    seen = []

    def spy(prompt, text):
        seen.append(text)
        return model(prompt, text)

    impl.hill_climb(BASE, EDITS, train, test, spy, grader)
    test_inputs = {c["input"] for c in test}
    assert sum(t in test_inputs for t in seen) == len(test)


def test_overfit_gap(impl):
    assert impl.ClimbResult("p", 0.95, 0.7).overfit_gap == 0.25


def test_mcnemar(impl):
    base = impl.run(BASE + "\nReply with the label only.", CASES, model, grader)
    train, test = impl.split(CASES, 0.3, seed=7)
    best = impl.hill_climb(BASE, EDITS, train, test, model, grader).prompt
    assert impl.mcnemar_p(base, impl.run(best, CASES, model, grader)) == 0.000122
    assert impl.mcnemar_p([True] * 5 + [False] * 5, [False] * 5 + [True] * 5) == 1.0
    assert impl.mcnemar_p([False] * 10, [True] * 10) == 0.001953
    assert impl.mcnemar_p([True, False], [True, False]) == 1.0
    with pytest.raises(ValueError):
        impl.mcnemar_p([True], [])


V1 = BASE + "\nReply with the label only."


def test_prompt_version_and_dataset_hash(impl):
    assert impl.prompt_version(BASE) == "1ca21bd17d9e" and impl.prompt_version(V1) == "c243f7b249ac"
    assert impl.dataset_hash(CASES) == "4f02d43fe161"
    assert impl.dataset_hash(CASES[::-1]) != impl.dataset_hash(CASES)          # reordering is a new set
    edited = [dict(c) for c in CASES]
    edited[0]["expected"] = "other"
    assert impl.dataset_hash(edited) != impl.dataset_hash(CASES)                # so is a relabeled case


def test_repeat_evaluate_reports_spread(impl):
    rng = random.Random(3)

    def sampled(prompt, text):                    # a "temperature > 0" model: wrong 20% of the time, seeded
        out = model(prompt, text)
        return "other" if rng.random() < 0.2 else out

    best = "\n".join([V1, "Use lowercase.", "Escalate means: urgent tickets keep their topic label."])
    r = impl.repeat_evaluate(best, CASES, sampled, grader, runs=5)
    assert r == {"runs": 5, "scores": [0.85, 0.8, 0.95, 0.75, 0.75], "mean": 0.82, "spread": 0.2}
    assert impl.repeat_evaluate(best, CASES, model, grader, runs=3)["spread"] == 0.0
    with pytest.raises(ValueError):
        impl.repeat_evaluate(best, CASES, model, grader, runs=0)


def test_wilson_interval(impl):
    assert impl.wilson_interval(0, 6) == (0.0, 0.3903)
    assert impl.wilson_interval(6, 6) == (0.6097, 1.0)
    assert impl.wilson_interval(164, 200) == (0.7609, 0.8671)
    assert impl.wilson_interval(172, 200) == (0.8051, 0.9013)
    for bad in ((1, 0), (7, 6), (-1, 6)):
        with pytest.raises(ValueError):
            impl.wilson_interval(*bad)


def test_regression_gate(impl):
    base, cand = [True, True, False, True], [True, False, True, True]
    assert impl.regression_gate(base, cand) == {"passed": True, "broken": [1], "reasons": []}
    blocked = impl.regression_gate(base, cand, protected=frozenset({1}))
    assert blocked["passed"] is False and blocked["reasons"] == ["protected case 1 regressed"]
    worse = impl.regression_gate([True, True], [True, False])
    assert worse["passed"] is False and "below baseline" in worse["reasons"][0]
    assert impl.regression_gate([True, True], [True, False], max_drop=0.5)["passed"] is True
    with pytest.raises(ValueError):
        impl.regression_gate([True], [])


def test_experiment_record(impl):
    train, test = impl.split(CASES, 0.3, seed=7)
    best = impl.hill_climb(BASE, EDITS, train, test, model, grader).prompt
    rec = impl.experiment_record("EXP-1", V1, best, CASES, model, grader, seed=7)
    assert rec["dataset"] == "4f02d43fe161" and rec["seed"] == 7 and rec["n_test"] == 6
    assert rec["baseline"] == {"prompt": "c243f7b249ac", "passes": 0, "rate": 0.0, "ci95": (0.0, 0.3903)}
    assert rec["candidate"] == {"prompt": "bf733e7f0523", "passes": 6, "rate": 1.0, "ci95": (0.6097, 1.0)}
    assert rec["mcnemar_p"] == 0.03125 and rec["gate"]["passed"] is True
    reverted = impl.experiment_record("EXP-2", best, V1, CASES, model, grader, seed=7, protected=frozenset({0}))
    assert reverted["gate"]["passed"] is False and "protected case 0 regressed" in reverted["gate"]["reasons"]
