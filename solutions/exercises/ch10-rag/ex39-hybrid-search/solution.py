from fde_kit import cosine, hash_embed


class VectorIndex:
    def __init__(self, dim: int = 256):
        self.dim = dim
        self._vecs: dict[str, list[float]] = {}

    def add(self, doc_id: str, text: str) -> None:
        self._vecs[doc_id] = hash_embed(text, self.dim)

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        q = hash_embed(query, self.dim)
        scored = [(d, cosine(q, v)) for d, v in self._vecs.items()]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda s: (-s[1], s[0]))
        return scored[:k]


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, 1):
            scores[doc] = scores.get(doc, 0.0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda s: (-s[1], s[0]))


def hybrid_search(query, keyword_fn, vector_fn, k=5, depth=20) -> list[tuple[str, float]]:
    return rrf([list(keyword_fn(query, depth)), list(vector_fn(query, depth))])[:k]


def explain_fusion(query, keyword_fn, vector_fn, doc_id, depth=20) -> dict:
    def rank(ids):
        ids = list(ids)
        return ids.index(doc_id) + 1 if doc_id in ids else None
    return {"keyword_rank": rank(keyword_fn(query, depth)), "vector_rank": rank(vector_fn(query, depth))}
