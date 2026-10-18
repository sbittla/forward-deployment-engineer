"""A tiny, provider-neutral LLM interface used across the course.

Messages use the Anthropic Messages API shape:
    [{"role": "user" | "assistant", "content": str | list[block]}]
Tools are dicts: {"name", "description", "input_schema"}.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = "end_turn"
    model: str = "fake"


def _approx_tokens(obj: Any) -> int:
    s = obj if isinstance(obj, str) else json.dumps(obj, default=str)
    return max(1, len(s) // 4)


Responder = Callable[[list, str | None, list | None], "LLMResponse | str"]


class FakeLLM:
    """Deterministic stand-in for a model.

    Pass either a list of scripted replies (consumed in order) or a callable
    `(messages, system, tools) -> LLMResponse | str`. Every call is recorded in
    `self.calls` so tests can assert on prompts.
    """

    def __init__(self, script: Iterable["LLMResponse | str"] | Responder = (), model: str = "fake"):
        self.model = model
        self.calls: list[dict] = []
        if callable(script):
            self._fn, self._queue = script, None
        else:
            self._fn, self._queue = None, list(script)

    def complete(self, messages, system=None, tools=None, max_tokens=1024, model=None, **_) -> LLMResponse:
        self.calls.append(dict(messages=messages, system=system, tools=tools, model=model or self.model))
        if self._fn is not None:
            out = self._fn(messages, system, tools)
        elif self._queue:
            out = self._queue.pop(0)
        else:
            raise RuntimeError("FakeLLM script exhausted")
        if isinstance(out, str):
            out = LLMResponse(text=out)
        out.model = model or self.model
        if not out.input_tokens:
            out.input_tokens = _approx_tokens([system, messages, tools])
        if not out.output_tokens:
            out.output_tokens = _approx_tokens(out.text or [t.arguments for t in out.tool_calls])
        if out.tool_calls and out.stop_reason == "end_turn":
            out.stop_reason = "tool_use"
        return out


class AnthropicLLM:
    """Thin adapter over the official `anthropic` SDK (optional dependency).

    Server-side refusal fallbacks are enabled by default so a policy decline
    is retried on a fallback model instead of returning empty.
    """

    def __init__(self, model: str = "claude-opus-5-5", client=None, fallbacks: bool = True):
        import anthropic  # imported lazily so the course runs without it

        self.model = model
        self.client = client or anthropic.Anthropic()
        self.fallbacks = fallbacks

    def complete(self, messages, system=None, tools=None, max_tokens=16000, model=None, **kw) -> LLMResponse:
        params: dict[str, Any] = dict(model=model or self.model, max_tokens=max_tokens, messages=messages, **kw)
        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools
        if self.fallbacks:
            resp = self.client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **params)
        else:
            resp = self.client.messages.create(**params)
        text = "".join(b.text for b in resp.content if b.type == "text")
        calls = [ToolCall(b.id, b.name, dict(b.input)) for b in resp.content if b.type == "tool_use"]
        return LLMResponse(text=text, tool_calls=calls, input_tokens=resp.usage.input_tokens,
                           output_tokens=resp.usage.output_tokens, stop_reason=resp.stop_reason,
                           model=resp.model)


def get_llm(fake_script=None):
    """Return a real client when FDE_LIVE=1 and credentials exist, else a FakeLLM."""
    if os.environ.get("FDE_LIVE") == "1":
        return AnthropicLLM()
    return FakeLLM(fake_script or ["(fake response)"])
