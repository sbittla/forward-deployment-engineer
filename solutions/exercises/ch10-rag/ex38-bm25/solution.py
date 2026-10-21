import math
from collections import Counter

from fde_kit import tokenize


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b

    def fit(self, docs: list[tuple[str, str]]) -> "BM25":
        self.tf = {doc_id: Counter(tokenize(text)) for doc_id, text in docs}
        self.len = {d: sum(c.values()) for d, c in self.tf.items()}
        self.n = len(docs)
        self.avgdl = sum(self.len.values()) / self.n if self.n else 0.0
        self.df = Counter(t for c in self.tf.values() for t in c)
        return self

    def idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.n - df + 0.5) / (df + 0.5) + 1)

    def _term(self, term: str, doc_id: str) -> float:
        tf = self.tf[doc_id].get(term, 0)
        if not tf:
            return 0.0
        norm = self.k1 * (1 - self.b + self.b * self.len[doc_id] / self.avgdl)
        return self.idf(term) * tf * (self.k1 + 1) / (tf + norm)

    def explain(self, query: str, doc_id: str) -> dict[str, float]:
        out: dict[str, float] = {}
        for t in tokenize(query):
            out[t] = out.get(t, 0.0) + self._term(t, doc_id)
        return out

    def score(self, query: str, doc_id: str) -> float:
        return sum(self.explain(query, doc_id).values())

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        scored = [(d, self.score(query, d)) for d in self.tf]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda s: (-s[1], s[0]))
        return scored[:k]
