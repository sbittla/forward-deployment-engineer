"""Hybrid retrieval: BM25 + hashed-vector cosine, fused with reciprocal rank fusion.

Each hit also carries `coverage`: the share of query content tokens found in the chunk
(including its section path). Coverage is easy to explain to a customer and is what the
copilot uses to decide whether to abstain.
"""
import math
from collections import Counter
from dataclasses import dataclass

from fde_kit import cosine, hash_embed, tokenize

from .ingest import Chunk


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    coverage: float


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75, rrf_k: int = 60):
        self.chunks = chunks
        self.k1, self.b, self.rrf_k = k1, b, rrf_k
        self._tokens = [tokenize(f"{c.path} {c.text}") for c in chunks]
        self._tf = [Counter(t) for t in self._tokens]
        self._len = [len(t) for t in self._tokens]
        self._avg = sum(self._len) / len(self._len) if chunks else 0.0
        self._df = Counter(tok for tf in self._tf for tok in tf)
        self._vecs = [hash_embed(f"{c.path} {c.text}") for c in chunks]

    def _bm25(self, q_tokens: list[str], i: int) -> float:
        n, s = len(self.chunks), 0.0
        for t in q_tokens:
            tf = self._tf[i].get(t, 0)
            if tf:
                idf = math.log((n - self._df[t] + 0.5) / (self._df[t] + 0.5) + 1)
                s += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * self._len[i] / self._avg))
        return s

    def search(self, query: str, k: int = 4) -> list[Hit]:
        q = tokenize(query)
        if not q or not self.chunks:
            return []
        idx = range(len(self.chunks))
        kw = sorted((i for i in idx if self._bm25(q, i) > 0), key=lambda i: -self._bm25(q, i))
        qv = hash_embed(query)
        vec = sorted((i for i in idx if cosine(qv, self._vecs[i]) > 0), key=lambda i: -cosine(qv, self._vecs[i]))
        fused: dict[int, float] = {}
        for ranking in (kw, vec):
            for r, i in enumerate(ranking, 1):
                fused[i] = fused.get(i, 0.0) + 1 / (self.rrf_k + r)
        qset = set(q)
        top = sorted(fused, key=lambda i: (-fused[i], i))[:k]
        return [Hit(self.chunks[i], round(fused[i], 6), round(len(qset & set(self._tokens[i])) / len(qset), 4))
                for i in top]
