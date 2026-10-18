import pytest


def call(name, **arguments):
    return {"type": "tool_call", "name": name, "arguments": arguments}


def final(text):
    return {"type": "final", "text": text}


SPEC = {"required_tools": ["lookup_order", "issue_refund"], "forbidden_tools": ["delete_account"],
        "order": ["lookup_order", "issue_refund"], "max_steps": 4, "final_contains": ["refund"],
        "arg_checks": {"issue_refund": {"order_id": "A100", "amount": 20}}}
GOOD = [call("lookup_order", order_id="A100"), call("issue_refund", order_id="A100", amount=20),
        final("Your refund of $20 is on its way.")]


def test_good_trajectory(impl):
    s = impl.score_trajectory(GOOD, SPEC)
    assert s.passed and s.efficiency == 1.0 and s.steps == 2
    assert set(s.checks) == {"has_final", "required_tools", "forbidden_tools", "order", "max_steps",
                             "final_contains", "args:issue_refund"}


def test_right_answer_wrong_path(impl):
    """The final message looks fine, but the agent refunded before checking the order."""
    traj = [call("issue_refund", order_id="A100", amount=20), call("lookup_order", order_id="A100"),
            final("Refund issued.")]
    s = impl.score_trajectory(traj, SPEC)
    assert not s.passed and s.checks["order"] is False and s.checks["final_contains"] is True


def test_forbidden_wrong_args_and_no_final(impl):
    traj = [call("lookup_order", order_id="A100"), call("delete_account", user="ana"),
            call("issue_refund", order_id="A100", amount=200)]
    s = impl.score_trajectory(traj, SPEC)
    assert {k for k, v in s.checks.items() if not v} == {"has_final", "forbidden_tools", "final_contains",
                                                         "args:issue_refund"}


def test_efficiency_and_step_budget(impl):
    traj = [call("lookup_order", order_id="A100")] * 3 + [call("issue_refund", order_id="A100", amount=20),
                                                         final("refund done")]
    s = impl.score_trajectory(traj, SPEC)
    assert s.efficiency == 0.5 and s.checks["max_steps"] is True and s.passed
    s2 = impl.score_trajectory([call("lookup_order", order_id="A100")] * 4 + GOOD, SPEC)
    assert s2.checks["max_steps"] is False and s2.efficiency == 0.3333
    assert impl.score_trajectory([final("hi")], {}).efficiency == 1.0
    assert impl.score_trajectory([final("hi")], {"required_tools": ["x"]}).efficiency == 0.0


def test_helpers(impl):
    assert impl.final_text([final("a"), final("b")]) == "b" and impl.final_text([]) is None
    assert len(impl.tool_calls(GOOD)) == 2


def test_tool_call_f1(impl):
    expected = [{"name": "lookup_order", "arguments": {"order_id": "A100"}},
                {"name": "issue_refund", "arguments": {"amount": 20, "order_id": "A100"}}]
    assert impl.tool_call_f1(GOOD, expected) == {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    noisy = [call("lookup_order", order_id="A100"), call("lookup_order", order_id="A100"),
             call("issue_refund", order_id="A100", amount=25)]
    assert impl.tool_call_f1(noisy, expected) == {"precision": 0.3333, "recall": 0.5, "f1": 0.4}
    assert impl.tool_call_f1([final("x")], []) == {"precision": 1.0, "recall": 1.0, "f1": 1.0}


def test_pass_at_k_and_pass_hat_k(impl):
    assert impl.pass_at_k(10, 3, 1) == 0.3 and impl.pass_at_k(10, 3, 5) == 0.9167 and impl.pass_at_k(10, 8, 3) == 1.0
    assert impl.pass_hat_k(10, 8, 1) == 0.8 and impl.pass_hat_k(10, 8, 3) == 0.4667 and impl.pass_hat_k(10, 2, 3) == 0.0
    for bad in [(5, 6, 1), (5, 2, 0), (5, 2, 6)]:
        with pytest.raises(ValueError):
            impl.pass_at_k(*bad)
        with pytest.raises(ValueError):
            impl.pass_hat_k(*bad)


def test_run_suite(impl):
    cases = [{"id": "refund", "task": "refund A100", "spec": SPEC},
             {"id": "lookup", "task": "status A100", "spec": {"required_tools": ["lookup_order"], "final_contains": ["shipped"]}}]

    def agent(task, trial):
        if task.startswith("refund"):
            # flaky: skips the lookup on every third trial
            return GOOD if trial % 3 else GOOD[1:]
        return [call("lookup_order", order_id="A100"), final("It shipped yesterday.")]

    r = impl.run_suite(agent, cases, trials=6, k=2)
    assert [c["passes"] for c in r["cases"]] == [4, 6]
    assert r["cases"][0]["pass_at_k"] == 0.9333 and r["cases"][0]["pass_hat_k"] == 0.4
    assert r["pass_at_k"] == 0.9667 and r["pass_hat_k"] == 0.7
    assert r["top_failures"] == [("order", 2), ("required_tools", 2)]
    assert r["mean_steps"] == 1.33
