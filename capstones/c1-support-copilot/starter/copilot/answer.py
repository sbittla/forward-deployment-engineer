"""The copilot request path: route -> redact -> retrieve -> (abstain | generate) -> cite -> guard -> restore."""
import math
import re
from dataclasses import dataclass, field

from . import guard, pii
from .retrieval import HybridRetriever

ABSTAIN_TEXT = "I can't find that in your policy documents, so I've flagged it for a licensed agent."
ESCALATE_TEXT = "Connecting you with a licensed agent now."
MODEL_ABSTAIN = "NOT_IN_SOURCES"
CLAIM_ID = re.compile(r"\bCL-\d{4,}\b", re.I)
CITE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
PRICES = {"claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50), "claude-opus-5-5": (4.0, 20.0)}

SYSTEM = (
    "You are Northwind Insurance's support copilot for licensed claims staff.\n"
    "Answer ONLY from the numbered policy sources. After each sentence cite its source like [1].\n"
    f"If the sources do not answer the question, reply exactly {MODEL_ABSTAIN}.\n"
    "Never promise approval or payment, and never give legal advice."
)


@dataclass
class Response:
    intent: str
    text: str
    citations: list[str] = field(default_factory=list)   # doc ids
    chunk_ids: list[str] = field(default_factory=list)
    abstained: bool = False
    escalated: bool = False
    cost_usd: float = 0.0
    redacted: bool = False


def build_prompt(question: str, hits) -> str:
    raise NotImplementedError


class Copilot:
    def __init__(self, llm, retriever: HybridRetriever, router, model: str = "claude-sonnet-5-5",
                 k: int = 4, min_coverage: float = 0.4, budget_usd: float = 0.02, prices: dict = PRICES):
        self.llm, self.retriever, self.router = llm, retriever, router
        self.model, self.k, self.min_coverage = model, k, min_coverage
        self.budget_usd, self.prices = budget_usd, prices

    def _cost(self, in_tokens: int, out_tokens: int) -> float:
        raise NotImplementedError

    def _fit_budget(self, question: str, hits):
        """Drop the lowest-ranked sources until the worst-case request cost fits the per-request budget."""
        raise NotImplementedError

    def ask(self, question: str) -> Response:
        raise NotImplementedError
