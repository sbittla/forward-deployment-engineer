import json

import pytest

from fde_kit import FakeLLM, LLMResponse, ToolCall


def make_tools(impl, log):
    def get_order(order_id):
        log.append(("get_order", order_id))
        if order_id == "missing":
            raise LookupError("no such order")
        return {"order_id": order_id, "total": 42.0, "status": "delivered"}

    def issue_credit(order_id, amount):
        log.append(("issue_credit", order_id, amount))
        return f"credited {amount}"

    T = impl.Tool
    return {
        "get_order": T("Look up an order", {"type": "object", "properties": {"order_id": {"type": "string"}}}, get_order),
        "issue_credit": T("Issue store credit", {"type": "object"}, issue_credit),
    }


def test_multi_step(impl):
    log = []
    script = [
        LLMResponse(text="Let me check.", tool_calls=[ToolCall("t1", "get_order", {"order_id": "A1"})]),
        LLMResponse(tool_calls=[ToolCall("t2", "issue_credit", {"order_id": "A1", "amount": 10})]),
        LLMResponse(text="Done: $10 credit issued for order A1."),
    ]
    llm = FakeLLM(script)
    res = impl.run_agent(llm, make_tools(impl, log), "Order A1 arrived damaged", system="be helpful")
    assert res.final_text.startswith("Done") and res.steps == 3
    assert log == [("get_order", "A1"), ("issue_credit", "A1", 10)]
    first_call = llm.calls[0]
    assert {t["name"] for t in first_call["tools"]} == {"get_order", "issue_credit"}
    assert first_call["system"] == "be helpful"
    msgs = llm.calls[1]["messages"]
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"][0] == {"type": "text", "text": "Let me check."}
    assert msgs[1]["content"][1] == {"type": "tool_use", "id": "t1", "name": "get_order", "input": {"order_id": "A1"}}
    result = msgs[2]["content"][0]
    assert result["type"] == "tool_result" and result["tool_use_id"] == "t1" and result["is_error"] is False
    assert json.loads(result["content"])["status"] == "delivered"


def test_parallel_results_single_turn_and_errors(impl):
    script = [
        LLMResponse(tool_calls=[ToolCall("a", "get_order", {"order_id": "missing"}),
                                ToolCall("b", "teleport", {}),
                                ToolCall("c", "get_order", {"order_id": "B2"})]),
        LLMResponse(text="Order missing; B2 delivered."),
    ]
    llm = FakeLLM(script)
    impl.run_agent(llm, make_tools(impl, []), "check")
    turn = llm.calls[1]["messages"][-1]
    assert turn["role"] == "user" and len(turn["content"]) == 3
    a, b, c = turn["content"]
    assert a["is_error"] and a["content"] == "LookupError: no such order"
    assert b["is_error"] and "unknown tool teleport" in b["content"]
    assert not c["is_error"]
    assert llm.calls[1]["messages"][-2]["content"][0]["type"] == "tool_use"  # no empty text block


def test_max_steps(impl):
    loop = lambda m, s, t: LLMResponse(tool_calls=[ToolCall("x", "get_order", {"order_id": "A"})])
    with pytest.raises(impl.AgentLoopError):
        impl.run_agent(FakeLLM(loop), make_tools(impl, []), "go", max_steps=3)


def _calls(*pairs, tokens=(0, 0)):
    """One scripted response per (name, args) pair, each with fixed token usage."""
    return [LLMResponse(tool_calls=[ToolCall(f"t{i}", name, args)], input_tokens=tokens[0], output_tokens=tokens[1])
            for i, (name, args) in enumerate(pairs)]


def test_budget_tokens_stops_before_tools_run(impl):
    log = []
    script = _calls(("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"}), tokens=(1000, 500))
    budget = impl.RunBudget(max_tokens=2500)
    with pytest.raises(impl.BudgetExceeded, match="tokens"):
        impl.run_agent(FakeLLM(script), make_tools(impl, log), "go", budget=budget)
    assert log == [("get_order", "A1")]  # the over-budget turn's tools never ran
    assert budget.tokens == 3000 and budget.steps == 2
    assert issubclass(impl.BudgetExceeded, impl.AgentLoopError)


def test_budget_usd(impl):
    script = _calls(*[("get_order", {"order_id": f"A{i}"}) for i in range(5)], tokens=(100_000, 10_000))
    budget = impl.RunBudget(max_tokens=1_000_000, max_usd=1.0)
    with pytest.raises(impl.BudgetExceeded, match="usd"):
        impl.run_agent(FakeLLM(script), make_tools(impl, []), "go", budget=budget, usd_per_mtok=(3.0, 15.0))
    assert budget.steps == 3 and budget.usd == pytest.approx(1.35)  # 0.30 input + 0.15 output per call


def test_budget_seconds_uses_clock(impl):
    ticks = iter([0.0, 10.0, 200.0])
    script = _calls(("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"}))
    with pytest.raises(impl.BudgetExceeded, match="seconds"):
        impl.run_agent(FakeLLM(script), make_tools(impl, []), "go", budget=impl.RunBudget(),
                       clock=lambda: next(ticks))


def test_budget_within_limits(impl):
    script = _calls(("get_order", {"order_id": "A1"}), tokens=(40, 10))
    script.append(LLMResponse(text="Delivered.", input_tokens=60, output_tokens=5))
    budget = impl.RunBudget()
    res = impl.run_agent(FakeLLM(script), make_tools(impl, []), "status?", budget=budget, usd_per_mtok=(1.0, 1.0))
    assert res.final_text == "Delivered." and budget.steps == 2 and budget.tokens == 115
    assert budget.usd == pytest.approx(115 / 1_000_000)


def test_repeated_identical_call_detected(impl):
    log = []
    same = lambda m, s, t: LLMResponse(tool_calls=[ToolCall(f"x{len(m)}", "get_order", {"order_id": "A1"})])
    with pytest.raises(impl.RepeatedCallError):
        impl.run_agent(FakeLLM(same), make_tools(impl, log), "go", max_steps=10)
    assert log == [("get_order", "A1")] * 2  # the third identical call is refused, not executed
    assert issubclass(impl.RepeatedCallError, impl.AgentLoopError)
    assert impl.call_fingerprint("f", {"a": 1, "b": 2}) == impl.call_fingerprint("f", {"b": 2, "a": 1})
    assert impl.call_fingerprint("f", {"a": 1}) != impl.call_fingerprint("f", {"a": 2})


def test_per_tool_cap(impl):
    log = []
    script = _calls(("issue_credit", {"order_id": "A1", "amount": 10}),
                    ("issue_credit", {"order_id": "A1", "amount": 20}))
    script.append(LLMResponse(text="One credit issued."))
    llm = FakeLLM(script)
    impl.run_agent(llm, make_tools(impl, log), "credit", tool_caps={"issue_credit": 1})
    assert log == [("issue_credit", "A1", 10)]
    refused = llm.calls[2]["messages"][-1]["content"][0]
    assert refused["is_error"] is True
    assert refused["content"] == "cap reached: issue_credit allows 1 call(s) per run"


def test_timeout_is_outcome_unknown(impl):
    def slow_refund(order_id):
        raise TimeoutError("payment API did not answer in 30s")

    tools = {"issue_refund": impl.Tool("Refund an order", {"type": "object"}, slow_refund)}
    llm = FakeLLM(_calls(("issue_refund", {"order_id": "A1"})) + [LLMResponse(text="Checking status.")])
    impl.run_agent(llm, tools, "refund A1")
    result = llm.calls[1]["messages"][-1]["content"][0]
    assert result["is_error"] is False
    assert result["content"] == "outcome unknown: issue_refund timed out; check the current state before retrying"
