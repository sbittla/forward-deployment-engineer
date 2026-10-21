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
