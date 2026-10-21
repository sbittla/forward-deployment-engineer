import json
from dataclasses import dataclass, field


@dataclass
class Reply:
    text: str
    tool_calls: list[dict] = field(default_factory=list)   # [{"id", "name", "arguments": dict}]
    stop: str = "end"                                      # end | tool_use | max_tokens


def to_anthropic(system: str, messages: list[dict], tools: list[dict]) -> dict:
    raise NotImplementedError


def to_openai(system: str, messages: list[dict], tools: list[dict]) -> dict:
    raise NotImplementedError


def to_gemini(system: str, messages: list[dict], tools: list[dict]) -> dict:
    raise NotImplementedError


def from_anthropic(resp: dict) -> Reply:
    raise NotImplementedError


def from_openai(resp: dict) -> Reply:
    raise NotImplementedError


def from_gemini(resp: dict) -> Reply:
    raise NotImplementedError


PROVIDERS: dict = {}
