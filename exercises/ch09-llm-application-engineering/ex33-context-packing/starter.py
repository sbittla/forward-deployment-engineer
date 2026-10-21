import math
from dataclasses import dataclass, field

MIN_PARTIAL = 50


@dataclass
class Packed:
    system: str
    messages: list[dict]
    included_docs: list[str] = field(default_factory=list)
    truncated: list[str] = field(default_factory=list)
    dropped_docs: list[str] = field(default_factory=list)
    tokens: int = 0


def count_tokens(text: str) -> int:
    raise NotImplementedError


def pack(system: str, question: str, docs: list[tuple[str, str, float]], history: list[dict],
         budget: int, reserve_output: int) -> Packed:
    raise NotImplementedError
