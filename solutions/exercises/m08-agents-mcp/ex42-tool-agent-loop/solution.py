import json
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Tool:
    description: str
    input_schema: dict
    fn: Callable


@dataclass
class AgentResult:
    final_text: str
    steps: int
    messages: list = field(default_factory=list)


class AgentLoopError(Exception):
    pass


def _execute(tools: dict[str, Tool], call) -> dict:
    block = {"type": "tool_result", "tool_use_id": call.id}
    tool = tools.get(call.name)
    if tool is None:
        return {**block, "content": f"unknown tool {call.name}", "is_error": True}
    try:
        result = tool.fn(**call.arguments)
    except Exception as exc:
        return {**block, "content": f"{type(exc).__name__}: {exc}", "is_error": True}
    content = result if isinstance(result, str) else json.dumps(result, default=str)
    return {**block, "content": content, "is_error": False}


def run_agent(llm, tools: dict[str, Tool], user_msg: str, system: str | None = None, max_steps: int = 8) -> AgentResult:
    specs = [{"name": n, "description": t.description, "input_schema": t.input_schema} for n, t in tools.items()]
    messages = [{"role": "user", "content": user_msg}]
    for step in range(1, max_steps + 1):
        resp = llm.complete(list(messages), system=system, tools=specs)
        if not resp.tool_calls:
            messages.append({"role": "assistant", "content": resp.text})
            return AgentResult(resp.text, step, messages)
        blocks = [{"type": "text", "text": resp.text}] if resp.text else []
        blocks += [{"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments} for c in resp.tool_calls]
        messages.append({"role": "assistant", "content": blocks})
        messages.append({"role": "user", "content": [_execute(tools, c) for c in resp.tool_calls]})
    raise AgentLoopError(f"agent still requesting tools after {max_steps} steps")
