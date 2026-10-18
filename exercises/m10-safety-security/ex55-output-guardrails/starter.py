from dataclasses import dataclass, field

from fde_kit import tokenize


@dataclass
class Policy:
    blocked_topics: dict[str, list[str]] = field(default_factory=dict)
    banned_phrases: list[str] = field(default_factory=list)
    min_support: float = 0.5
    fallback: str = "I can't help with that here. A licensed agent will follow up."


@dataclass
class GuardResult:
    allowed: bool
    violations: list[str]
    safe_text: str


def check_output(answer: str, sources: list[str], policy: Policy) -> GuardResult:
    raise NotImplementedError
