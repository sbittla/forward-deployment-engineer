import math


def recall_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    raise NotImplementedError


def precision_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    raise NotImplementedError


def mrr(ranked: list[str], relevant: dict[str, int]) -> float:
    raise NotImplementedError


def ndcg_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    raise NotImplementedError


def evaluate(retrieve, qrels: dict, k: int) -> dict:
    raise NotImplementedError


def compare(a: dict, b: dict, names=("A", "B")) -> str:
    raise NotImplementedError


def citation_precision(answers: list[dict]) -> float:
    raise NotImplementedError


def abstention_report(results: list[dict]) -> dict:
    raise NotImplementedError


def rag_scorecard(results: list[dict]) -> dict:
    raise NotImplementedError


def rewrite_followup(question: str, history: list[str]) -> str:
    raise NotImplementedError
