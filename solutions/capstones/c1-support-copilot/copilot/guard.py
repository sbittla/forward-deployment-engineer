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
    lowered = answer.lower()
    if any(p in lowered for p in BANNED):
        return GuardResult(True, "")
    src = [set(tokenize(s)) for s in sources]
    keep, dropped = [], []
    for sentence in re.split(r"(?<=[.!?])\s+", answer.strip()):
        if not sentence:
            continue
        toks = tokenize(CITE.sub("", sentence))
        supported = not toks or any(sum(t in s for t in toks) / len(toks) >= min_support for s in src)
        (keep if supported else dropped).append(sentence)
    return GuardResult(False, " ".join(keep), dropped)
