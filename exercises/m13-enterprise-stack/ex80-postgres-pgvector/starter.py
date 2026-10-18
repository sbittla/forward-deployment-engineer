import re


def translate_ddl(sqlite_ddl: str) -> str:
    raise NotImplementedError


def translate_query(sql: str) -> str:
    raise NotImplementedError


def vector_schema(table: str, dim: int, metric: str = "cosine", index: str = "hnsw") -> list[str]:
    raise NotImplementedError


def knn_query(table: str, k: int, metric: str = "cosine") -> str:
    raise NotImplementedError
