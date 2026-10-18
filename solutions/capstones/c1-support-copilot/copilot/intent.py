"""Intent routing with a classical baseline (multinomial Naive Bayes) plus one deterministic rule.

A cheap, explainable router in front of the LLM keeps claim-status and escalation traffic
off the RAG path entirely.
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

from fde_kit import tokenize

CLAIM_ID = re.compile(r"\bCL-\d{4,}\b", re.I)


class IntentRouter:
    def __init__(self, alpha: float = 1.0, min_confidence: float = 0.5, fallback: str = "policy_question"):
        self.alpha = alpha
        self.min_confidence = min_confidence
        self.fallback = fallback

    @classmethod
    def from_jsonl(cls, path, **kw) -> "IntentRouter":
        rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
        return cls(**kw).fit([r["text"] for r in rows], [r["intent"] for r in rows])

    def fit(self, texts: list[str], labels: list[str]) -> "IntentRouter":
        self.labels = sorted(set(labels))
        self.prior = {l: math.log(labels.count(l) / len(labels)) for l in self.labels}
        self.counts = {l: Counter() for l in self.labels}
        for t, l in zip(texts, labels):
            self.counts[l].update(tokenize(t))
        self.vocab = set().union(*self.counts.values())
        self.totals = {l: sum(c.values()) for l, c in self.counts.items()}
        return self

    def proba(self, text: str) -> dict[str, float]:
        v = len(self.vocab)
        scores = {}
        for l in self.labels:
            s = self.prior[l]
            for tok in tokenize(text):
                if tok in self.vocab:
                    s += math.log((self.counts[l][tok] + self.alpha) / (self.totals[l] + self.alpha * v))
            scores[l] = s
        top = max(scores.values())
        exp = {l: math.exp(s - top) for l, s in scores.items()}
        z = sum(exp.values())
        return {l: e / z for l, e in exp.items()}

    def route(self, text: str) -> tuple[str, float]:
        if CLAIM_ID.search(text):
            return "claim_status", 1.0
        p = self.proba(text)
        label = max(p, key=p.get)
        if p[label] < self.min_confidence:
            return self.fallback, round(p[label], 3)
        return label, round(p[label], 3)
