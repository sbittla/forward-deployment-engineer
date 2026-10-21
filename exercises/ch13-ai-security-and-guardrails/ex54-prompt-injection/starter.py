from dataclasses import dataclass


@dataclass
class Decision:
    allowed: bool
    needs_confirmation: bool
    reason: str


def wrap_untrusted(content: str, source: str) -> str:
    raise NotImplementedError


def injection_signals(text: str) -> list[str]:
    raise NotImplementedError


class ToolGate:
    def __init__(self, side_effect_tools: set[str], allowed_domains: set[str]):
        self.side_effect_tools = side_effect_tools
        self.allowed_domains = allowed_domains

    def authorize(self, tool: str, args: dict, tainted: bool) -> Decision:
        raise NotImplementedError
