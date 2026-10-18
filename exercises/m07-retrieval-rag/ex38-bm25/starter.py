from fde_kit import tokenize


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b

    def fit(self, docs: list[tuple[str, str]]) -> "BM25":
        raise NotImplementedError

    def idf(self, term: str) -> float:
        raise NotImplementedError

    def score(self, query: str, doc_id: str) -> float:
        raise NotImplementedError

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        raise NotImplementedError

    def explain(self, query: str, doc_id: str) -> dict[str, float]:
        raise NotImplementedError
