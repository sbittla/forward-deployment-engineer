from datetime import datetime


def rfc3986(s: str) -> str:
    raise NotImplementedError


def encode_path(path: str) -> str:
    raise NotImplementedError


def canonical_query(query: dict[str, list[str]]) -> str:
    raise NotImplementedError


def canonical_request(method: str, path: str, query: dict, body: bytes, ts: datetime, variant: str = "java") -> str:
    raise NotImplementedError


def sign_headers(method, path, query, body, ts, key_id, secret, variant="java") -> dict:
    raise NotImplementedError
