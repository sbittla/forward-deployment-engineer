from fde_kit import cosine, hash_embed


class VectorIndex:
    def __init__(self, dim: int = 256):
        self.dim = dim
        self._vecs: dict[str, list[float]] = {}
        self._acls: dict[str, dict | None] = {}

    def add(self, doc_id: str, text: str, acl: dict | None = None) -> None:
        self._vecs[doc_id] = hash_embed(text, self.dim)
        self._acls[doc_id] = acl

    def _rank(self, query: str, ids, k: int) -> list[tuple[str, float]]:
        q = hash_embed(query, self.dim)
        scored = [(d, cosine(q, self._vecs[d])) for d in ids]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda s: (-s[1], s[0]))
        return scored[:k]

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        return self._rank(query, self._vecs, k)

    def search_as(self, user: dict, query: str, k: int = 10) -> list[tuple[str, float]]:
        tenant = (user or {}).get("tenant")
        if not tenant:
            raise PermissionError("user has no tenant")
        groups = set(user.get("groups") or [])

        def visible(acl) -> bool:  # fail closed: anything missing means "not visible"
            return bool(acl) and acl.get("tenant") == tenant and bool(groups & set(acl.get("groups") or []))

        # Filter before scoring, so another tenant's best match never enters the ranking.
        return self._rank(query, [d for d in self._vecs if visible(self._acls.get(d))], k)


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
