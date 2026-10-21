import re
from dataclasses import dataclass, field

from fde_kit import tokenize

PII = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b\d{3}-\d{2}-\d{4}\b")


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


def _supported(sentence: str, source_tokens: list[set[str]], min_support: float) -> bool:
    toks = tokenize(sentence)
    if not toks:
        return True
    return any(sum(t in src for t in toks) / len(toks) >= min_support for src in source_tokens)


def check_output(answer: str, sources: list[str], policy: Policy) -> GuardResult:
    blocking: list[str] = []
    for name, keywords in policy.blocked_topics.items():
        if any(re.search(rf"\b{re.escape(k)}\b", answer, re.I) for k in keywords):
            blocking.append(f"topic:{name}")
    blocking += [f"phrase:{p}" for p in policy.banned_phrases if p.lower() in answer.lower()]
    joined = "\n".join(sources)
    if any(m not in joined for m in PII.findall(answer)):
        blocking.append("pii_leak")

    src_tokens = [set(tokenize(s)) for s in sources]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer.strip()) if s]
    keep, warnings = [], []
    for s in sentences:
        if _supported(s, src_tokens, policy.min_support):
            keep.append(s)
        else:
            warnings.append(f"ungrounded:{s}")

    violations = blocking + warnings
    if blocking:
        return GuardResult(False, violations, policy.fallback)
    return GuardResult(True, violations, " ".join(keep) if keep else policy.fallback)
