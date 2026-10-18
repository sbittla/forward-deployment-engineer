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
        raise NotImplementedError

    def fit(self, texts: list[str], labels: list[str]) -> "IntentRouter":
        raise NotImplementedError

    def proba(self, text: str) -> dict[str, float]:
        raise NotImplementedError

    def route(self, text: str) -> tuple[str, float]:
        raise NotImplementedError
