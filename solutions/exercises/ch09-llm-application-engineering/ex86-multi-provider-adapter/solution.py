import json
from dataclasses import dataclass, field


@dataclass
class Reply:
    text: str
    tool_calls: list[dict] = field(default_factory=list)
    stop: str = "end"


def _groups(messages):
    """Yield (role, [messages]) with consecutive tool messages grouped together."""
    group = []
    for m in messages:
        if m["role"] == "tool":
            group.append(m)
            continue
        if group:
            yield "tool", group
            group = []
        yield m["role"], [m]
    if group:
        yield "tool", group


# ---------- request builders ----------

def to_anthropic(system: str, messages: list[dict], tools: list[dict]) -> dict:
    out = []
    for role, ms in _groups(messages):
        if role == "tool":
            out.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]} for m in ms]})
            continue
        m = ms[0]
        if m.get("tool_calls"):
            blocks = [{"type": "text", "text": m["content"]}] if m.get("content") else []
            blocks += [{"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["arguments"]}
                       for c in m["tool_calls"]]
            out.append({"role": "assistant", "content": blocks})
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return {"system": system, "messages": out,
            "tools": [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in tools]}


def to_openai(system: str, messages: list[dict], tools: list[dict]) -> dict:
    out = [{"role": "system", "content": system}]
    for m in messages:
        if m["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
        elif m.get("tool_calls"):
            out.append({"role": "assistant", "content": m.get("content") or None, "tool_calls": [
                {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                for c in m["tool_calls"]]})
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return {"messages": out, "tools": [{"type": "function", "function": t} for t in tools]}


def to_gemini(system: str, messages: list[dict], tools: list[dict]) -> dict:
    call_names = {c["id"]: c["name"] for m in messages for c in m.get("tool_calls", [])}
    contents = []
    for role, ms in _groups(messages):
        if role == "tool":
            contents.append({"role": "user", "parts": [
                {"functionResponse": {"name": call_names[m["tool_call_id"]], "response": {"content": m["content"]}}}
                for m in ms]})
            continue
        m = ms[0]
        parts = [{"text": m["content"]}] if m.get("content") else []
        parts += [{"functionCall": {"name": c["name"], "args": c["arguments"]}} for c in m.get("tool_calls", [])]
        contents.append({"role": "model" if m["role"] == "assistant" else "user", "parts": parts})
    return {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
            "tools": [{"functionDeclarations": list(tools)}]}


# ---------- response parsers ----------

def from_anthropic(resp: dict) -> Reply:
    text = "".join(b["text"] for b in resp["content"] if b["type"] == "text")
    calls = [{"id": b["id"], "name": b["name"], "arguments": b["input"]} for b in resp["content"] if b["type"] == "tool_use"]
    stop = {"tool_use": "tool_use", "max_tokens": "max_tokens"}.get(resp.get("stop_reason"), "end")
    return Reply(text, calls, stop)


def from_openai(resp: dict) -> Reply:
    choice = resp["choices"][0]
    msg = choice["message"]
    calls = [{"id": c["id"], "name": c["function"]["name"], "arguments": json.loads(c["function"]["arguments"] or "{}")}
             for c in msg.get("tool_calls") or []]
    stop = {"tool_calls": "tool_use", "length": "max_tokens"}.get(choice.get("finish_reason"), "end")
    return Reply(msg.get("content") or "", calls, stop)


def from_gemini(resp: dict) -> Reply:
    cand = resp["candidates"][0]
    parts = cand["content"].get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    fcs = [p["functionCall"] for p in parts if "functionCall" in p]
    calls = [{"id": f"gemini_call_{i}", "name": f["name"], "arguments": f.get("args", {})} for i, f in enumerate(fcs)]
    stop = "tool_use" if calls else ("max_tokens" if cand.get("finishReason") == "MAX_TOKENS" else "end")
    return Reply(text, calls, stop)


PROVIDERS = {
    "anthropic": (to_anthropic, from_anthropic),
    "openai": (to_openai, from_openai),
    "gemini": (to_gemini, from_gemini),
}
