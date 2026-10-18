"""Output guardrails: banned promises block the answer; unsupported sentences are dropped."""
import re
from dataclasses import dataclass, field

from fde_kit import tokenize

BANNED = ("guaranteed", "always approved", "100% covered", "you should sue")
CITE = re.compile(r"\[\d+\]")


@dataclass
class GuardResult:
    blocked: bool
    text: str
    dropped: list[str] = field(default_factory=list)


def check(answer: str, sources: list[str], min_support: float = 0.5) -> GuardResult:
    raise NotImplementedError
