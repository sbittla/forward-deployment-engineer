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
        raise NotImplementedError

    def search(self, query: str, k: int = 4) -> list[Hit]:
        raise NotImplementedError
