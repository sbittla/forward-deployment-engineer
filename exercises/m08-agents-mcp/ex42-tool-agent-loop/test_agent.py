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
