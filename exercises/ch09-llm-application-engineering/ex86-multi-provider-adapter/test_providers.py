import json

SYSTEM = "You are a claims assistant."
TOOLS = [{"name": "get_claim", "description": "Look up a claim", "parameters": {"type": "object", "properties": {"id": {"type": "string"}}}}]
MSGS = [
    {"role": "user", "content": "Status of CL-1 and CL-2?"},
    {"role": "assistant", "content": "Checking both.", "tool_calls": [
        {"id": "t1", "name": "get_claim", "arguments": {"id": "CL-1"}},
        {"id": "t2", "name": "get_claim", "arguments": {"id": "CL-2"}}]},
    {"role": "tool", "tool_call_id": "t1", "content": "open"},
    {"role": "tool", "tool_call_id": "t2", "content": "closed"},
    {"role": "assistant", "content": "CL-1 is open, CL-2 closed."},
]


def test_anthropic_request(impl):
    r = impl.to_anthropic(SYSTEM, MSGS, TOOLS)
    assert r["system"] == SYSTEM and r["tools"][0]["input_schema"]["properties"]["id"]["type"] == "string"
    m = r["messages"]
    assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
    assert m[1]["content"][0] == {"type": "text", "text": "Checking both."}
    assert m[1]["content"][2] == {"type": "tool_use", "id": "t2", "name": "get_claim", "input": {"id": "CL-2"}}
    assert m[2]["content"] == [{"type": "tool_result", "tool_use_id": "t1", "content": "open"},
                               {"type": "tool_result", "tool_use_id": "t2", "content": "closed"}]


def test_openai_request(impl):
    r = impl.to_openai(SYSTEM, MSGS, TOOLS)
    m = r["messages"]
    assert m[0] == {"role": "system", "content": SYSTEM}
    assert r["tools"][0] == {"type": "function", "function": TOOLS[0]}
    tc = m[2]["tool_calls"][0]
    assert tc == {"id": "t1", "type": "function", "function": {"name": "get_claim", "arguments": json.dumps({"id": "CL-1"})}}
    assert m[3] == {"role": "tool", "tool_call_id": "t1", "content": "open"} and m[4]["tool_call_id"] == "t2"
    no_text = impl.to_openai(SYSTEM, [{"role": "assistant", "content": "", "tool_calls": MSGS[1]["tool_calls"]}], TOOLS)
    assert no_text["messages"][1]["content"] is None


def test_gemini_request(impl):
    r = impl.to_gemini(SYSTEM, MSGS, TOOLS)
    assert r["systemInstruction"] == {"parts": [{"text": SYSTEM}]}
    assert r["tools"] == [{"functionDeclarations": TOOLS}]
    c = r["contents"]
    assert [x["role"] for x in c] == ["user", "model", "user", "model"]
    assert c[1]["parts"] == [{"text": "Checking both."}, {"functionCall": {"name": "get_claim", "args": {"id": "CL-1"}}},
                             {"functionCall": {"name": "get_claim", "args": {"id": "CL-2"}}}]
    assert c[2]["parts"][1] == {"functionResponse": {"name": "get_claim", "response": {"content": "closed"}}}


def test_parsers(impl):
    a = impl.from_anthropic({"content": [{"type": "text", "text": "Let me check."},
                                         {"type": "tool_use", "id": "tu_1", "name": "get_claim", "input": {"id": "CL-9"}}],
                             "stop_reason": "tool_use"})
    assert a == impl.Reply("Let me check.", [{"id": "tu_1", "name": "get_claim", "arguments": {"id": "CL-9"}}], "tool_use")
    o = impl.from_openai({"choices": [{"message": {"content": None, "tool_calls": [
        {"id": "call_1", "type": "function", "function": {"name": "get_claim", "arguments": "{\"id\": \"CL-9\"}"}}]},
        "finish_reason": "tool_calls"}]})
    assert o == impl.Reply("", [{"id": "call_1", "name": "get_claim", "arguments": {"id": "CL-9"}}], "tool_use")
    g = impl.from_gemini({"candidates": [{"content": {"role": "model", "parts": [
        {"functionCall": {"name": "get_claim", "args": {"id": "CL-9"}}},
        {"functionCall": {"name": "get_claim", "args": {"id": "CL-8"}}}]}, "finishReason": "STOP"}]})
    assert g.stop == "tool_use" and [c["id"] for c in g.tool_calls] == ["gemini_call_0", "gemini_call_1"]
    assert impl.from_openai({"choices": [{"message": {"content": "Hi"}, "finish_reason": "length"}]}).stop == "max_tokens"
    assert impl.from_gemini({"candidates": [{"content": {"parts": [{"text": "Hi"}]}, "finishReason": "STOP"}]}) == impl.Reply("Hi")
    assert impl.from_anthropic({"content": [{"type": "text", "text": "x"}], "stop_reason": "max_tokens"}).stop == "max_tokens"


def test_registry_roundtrip(impl):
    assert set(impl.PROVIDERS) == {"anthropic", "openai", "gemini"}
    for name, (build, parse) in impl.PROVIDERS.items():
        assert callable(build) and callable(parse)
