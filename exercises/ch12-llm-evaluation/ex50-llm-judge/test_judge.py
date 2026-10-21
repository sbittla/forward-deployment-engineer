import pytest

from fde_kit import FakeLLM

RUBRIC = "5 = accurate, complete, cites policy; 3 = partially correct; 1 = wrong or unsafe"


def test_judge_parses(impl):
    llm = FakeLLM(['Here is my verdict: {"reasoning": "Accurate but no citation.", "score": 4}'])
    v = impl.judge(llm, "Is flood covered?", "No, flood is excluded.", "Flood excluded (sec 9.1)", RUBRIC)
    assert v == impl.Verdict(4, "Accurate but no citation.")
    call = llm.calls[0]
    assert RUBRIC in call["system"] and "reasoning" in call["system"]
    user = call["messages"][0]["content"]
    assert "Is flood covered?" in user and "No, flood is excluded." in user and "sec 9.1" in user


@pytest.mark.parametrize("reply", ["no json", '{"reasoning": "x", "score": 9}', '{"reasoning": "x", "score": "4"}',
                                   '{"reasoning": "x", "score": 3.5}'])
def test_judge_rejects(impl, reply):
    with pytest.raises(ValueError):
        impl.judge(FakeLLM([reply]), "q", "a", "r", RUBRIC)


def test_agreement(impl):
    j = [5, 4, 2, 1, 3, 4]
    h = [5, 3, 2, 2, 5, 4]
    a = impl.agreement(j, h)
    assert a["exact"] == 0.5 and a["within_1"] == round(5 / 6, 3)
    # pass/fail j: P P F F F P ; h: P F F F P P -> po = 4/6 ; pe = .5*.5 + .5*.5 = .5 ; kappa = (0.667-.5)/.5
    assert a["kappa"] == round((4 / 6 - 0.5) / 0.5, 3)


def test_agreement_perfect(impl):
    assert impl.agreement([5, 5], [5, 5])["kappa"] == 1.0


def test_pairwise(impl):
    # B is better: shown second -> "2"; shown first -> "1"
    assert impl.pairwise(FakeLLM(["2", "1"]), "q", "weak", "strong") == "B"
    assert impl.pairwise(FakeLLM(["1", "2"]), "q", "strong", "weak") == "A"
    # always picks first position -> inconsistent
    llm = FakeLLM(["1", "1"])
    assert impl.pairwise(llm, "q", "x", "y") == "tie"
    first, second = (c["messages"][0]["content"] for c in llm.calls)
    assert first.index("x") < first.index("y") and second.index("y") < second.index("x")


def test_boundary_consistent_bias_passes_through(impl):
    # Order-swapping cancels only position bias. A judge that prefers the longer answer
    # in both orders (verbosity bias) still produces a winner: calibrate for that separately.
    long_wrong = (
        "Yes, burst pipes are covered in full under every policy, "
        "whatever the circumstances."
    )
    short_right = "Not covered: the house was unoccupied."
    assert impl.pairwise(FakeLLM(["1", "2"]), "q", long_wrong, short_right) == "A"


def test_labeler_agreement(impl):
    # Two experts label the same golden-set cases independently; the judge's kappa measures them too.
    expert_1 = [5, 4, 4, 2, 1, 5, 3, 4]
    expert_2 = [5, 4, 3, 2, 2, 4, 3, 5]
    assert impl.agreement(expert_1, expert_2) == {"exact": 0.5, "within_1": 1.0, "kappa": 0.75}


def test_always_pass_judge_has_zero_kappa(impl):
    humans = [5] * 9 + [1]          # 90% of answers are good
    a = impl.agreement([5] * 10, humans)
    assert a["exact"] == 0.9 and a["kappa"] == 0.0
