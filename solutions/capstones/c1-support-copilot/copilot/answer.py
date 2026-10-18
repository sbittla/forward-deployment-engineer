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
    lines = [f"[{i}] ({h.chunk.path}) {h.chunk.text}" for i, h in enumerate(hits, 1)]
    return "Sources:\n" + "\n".join(lines) + f"\n\nQuestion: {question}"


class Copilot:
    def __init__(self, llm, retriever: HybridRetriever, router, model: str = "claude-sonnet-5-5",
                 k: int = 4, min_coverage: float = 0.4, budget_usd: float = 0.02, prices: dict = PRICES):
        self.llm, self.retriever, self.router = llm, retriever, router
        self.model, self.k, self.min_coverage = model, k, min_coverage
        self.budget_usd, self.prices = budget_usd, prices

    def _cost(self, in_tokens: int, out_tokens: int) -> float:
        p_in, p_out = self.prices[self.model]
        return in_tokens * p_in / 1e6 + out_tokens * p_out / 1e6

    def _fit_budget(self, question: str, hits):
        """Drop the lowest-ranked sources until the worst-case request cost fits the per-request budget."""
        while hits:
            est_in = math.ceil((len(SYSTEM) + len(build_prompt(question, hits))) / 4)
            if self._cost(est_in, 1024) <= self.budget_usd:
                return hits
            hits = hits[:-1]
        return hits

    def ask(self, question: str) -> Response:
        intent, _ = self.router.route(question)
        if intent == "speak_to_human":
            return Response(intent, ESCALATE_TEXT, escalated=True)
        if intent == "claim_status":
            m = CLAIM_ID.search(question)
            text = (f"I'll pull up claim {m.group(0).upper()} in the claims system for you." if m
                    else "Please share your claim number (it looks like CL-12345).")
            return Response(intent, text)

        safe_q, mapping = pii.redact(question)
        hits = self.retriever.search(pii.strip_tokens(safe_q), self.k)
        if not hits or max(h.coverage for h in hits) < self.min_coverage:
            return Response(intent, ABSTAIN_TEXT, abstained=True, redacted=bool(mapping))
        hits = self._fit_budget(safe_q, hits)
        if not hits:
            return Response(intent, ABSTAIN_TEXT, abstained=True, redacted=bool(mapping))

        resp = self.llm.complete([{"role": "user", "content": build_prompt(safe_q, hits)}],
                                 system=SYSTEM, model=self.model, max_tokens=1024)
        cost = round(self._cost(resp.input_tokens, resp.output_tokens), 6)
        text = resp.text.strip()
        if text == MODEL_ABSTAIN:
            return Response(intent, ABSTAIN_TEXT, abstained=True, cost_usd=cost, redacted=bool(mapping))

        used: list[int] = []

        def keep_valid(m):
            nums = [int(n) for n in re.split(r"\s*,\s*", m.group(1))]
            valid = [n for n in nums if 1 <= n <= len(hits)]
            used.extend(n for n in valid if n not in used)
            return "".join(f"[{n}]" for n in valid)

        text = CITE.sub(keep_valid, text)
        checked = guard.check(text, [h.chunk.text for h in hits])
        if checked.blocked or not checked.text or not used:
            return Response(intent, ESCALATE_TEXT, escalated=True, cost_usd=cost, redacted=bool(mapping))
        cited = [hits[n - 1].chunk for n in used]
        return Response(
            intent=intent,
            text=pii.restore(checked.text, mapping),
            citations=list(dict.fromkeys(c.doc_id for c in cited)),
            chunk_ids=[c.id for c in cited],
            cost_usd=cost,
            redacted=bool(mapping),
        )
