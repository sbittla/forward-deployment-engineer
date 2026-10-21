from fde_kit import cosine, hash_embed


class VectorIndex:
    def __init__(self, dim: int = 256):
        self.dim = dim

    def add(self, doc_id: str, text: str) -> None:
        raise NotImplementedError

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        raise NotImplementedError


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    raise NotImplementedError


def hybrid_search(query, keyword_fn, vector_fn, k=5, depth=20) -> list[tuple[str, float]]:
    raise NotImplementedError


def explain_fusion(query, keyword_fn, vector_fn, doc_id, depth=20) -> dict:
    raise NotImplementedError
