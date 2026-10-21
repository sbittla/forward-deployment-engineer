import hashlib
import json
import time
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


class BudgetExceeded(AgentLoopError):
    pass


class RepeatedCallError(AgentLoopError):
    pass


@dataclass
class RunBudget:
    max_steps: int = 8
    max_tokens: int = 200_000
    max_seconds: float = 120.0
    max_usd: float = 2.0
    steps: int = 0
    tokens: int = 0
    usd: float = 0.0

    def charge(self, tokens: int, usd: float, elapsed_s: float) -> None:
        self.steps += 1
        self.tokens += tokens
        self.usd += usd
        for name, used, limit in (("steps", self.steps, self.max_steps),
                                  ("tokens", self.tokens, self.max_tokens),
                                  ("seconds", elapsed_s, self.max_seconds),
                                  ("usd", self.usd, self.max_usd)):
            if used > limit:
                raise BudgetExceeded(f"{name}: {used} > {limit}")


def call_fingerprint(name: str, arguments: dict) -> str:
    return hashlib.sha256(json.dumps([name, arguments], sort_keys=True, default=str).encode()).hexdigest()


def _execute(tools: dict[str, Tool], call) -> dict:
    block = {"type": "tool_result", "tool_use_id": call.id}
    tool = tools.get(call.name)
    if tool is None:
        return {**block, "content": f"unknown tool {call.name}", "is_error": True}
    try:
        result = tool.fn(**call.arguments)
    except TimeoutError:
        text = f"outcome unknown: {call.name} timed out; check the current state before retrying"
        return {**block, "content": text, "is_error": False}
    except Exception as exc:
        return {**block, "content": f"{type(exc).__name__}: {exc}", "is_error": True}
    content = result if isinstance(result, str) else json.dumps(result, default=str)
    return {**block, "content": content, "is_error": False}


def run_agent(llm, tools: dict[str, Tool], user_msg: str, system: str | None = None, max_steps: int = 8, *,
              budget: RunBudget | None = None, usd_per_mtok: tuple[float, float] = (0.0, 0.0),
              tool_caps: dict[str, int] | None = None, max_repeats: int = 3,
              clock: Callable[[], float] = time.monotonic) -> AgentResult:
    specs = [{"name": n, "description": t.description, "input_schema": t.input_schema} for n, t in tools.items()]
    messages = [{"role": "user", "content": user_msg}]
    caps, tool_counts, seen = tool_caps or {}, {}, {}
    started = clock()
    for step in range(1, max_steps + 1):
        resp = llm.complete(list(messages), system=system, tools=specs)
        if budget is not None:
            usd = (resp.input_tokens * usd_per_mtok[0] + resp.output_tokens * usd_per_mtok[1]) / 1_000_000
            budget.charge(resp.input_tokens + resp.output_tokens, usd, clock() - started)
        if not resp.tool_calls:
            messages.append({"role": "assistant", "content": resp.text})
            return AgentResult(resp.text, step, messages)
        blocks = [{"type": "text", "text": resp.text}] if resp.text else []
        blocks += [{"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments} for c in resp.tool_calls]
        messages.append({"role": "assistant", "content": blocks})
        for c in resp.tool_calls:
            fp = call_fingerprint(c.name, c.arguments)
            seen[fp] = seen.get(fp, 0) + 1
            if seen[fp] >= max_repeats:
                raise RepeatedCallError(f"{c.name} called {seen[fp]} times with the same arguments")
        results = []
        for c in resp.tool_calls:
            if c.name in caps and tool_counts.get(c.name, 0) >= caps[c.name]:
                results.append({"type": "tool_result", "tool_use_id": c.id, "is_error": True,
                                "content": f"cap reached: {c.name} allows {caps[c.name]} call(s) per run"})
                continue
            tool_counts[c.name] = tool_counts.get(c.name, 0) + 1
            results.append(_execute(tools, c))
        messages.append({"role": "user", "content": results})
    raise AgentLoopError(f"agent still requesting tools after {max_steps} steps")
