"""Dependency-free text utilities: tokenization and hashed embeddings."""
from __future__ import annotations

import hashlib
import math
import re

_WORD = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    "a an and are as at be by for from has have how i in is it its of on or that the this to was were what "
    "when where which who why will with you your".split()
)


def tokenize(text: str, drop_stopwords: bool = True) -> list[str]:
    toks = _WORD.findall(text.lower())
    return [t for t in toks if not (drop_stopwords and t in STOPWORDS)]


def hash_embed(text: str, dim: int = 256) -> list[float]:
    """Deterministic bag-of-words embedding via feature hashing (L2-normalised).

    Not semantic like a neural embedding, but stable and good enough to teach
    vector search mechanics without network access.
    """
    vec = [0.0] * dim
    for tok in tokenize(text):
        h = int.from_bytes(hashlib.md5(tok.encode()).digest()[:4], "little")
        vec[h % dim] += 1.0 if (h >> 31) & 1 == 0 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
