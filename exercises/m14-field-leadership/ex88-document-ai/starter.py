import base64
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024


@dataclass
class Line:
    page: int
    y: float
    text: str
    conf: float


def group_lines(words: list[dict], y_tol: float = 5) -> list[Line]:
    raise NotImplementedError


def key_values(lines: list[Line], labels: list[str]) -> dict:
    raise NotImplementedError


def extract_table(words: list[dict], headers: list[str], page: int) -> list[dict]:
    raise NotImplementedError


def route(fields: dict, required: list[str], min_conf: float = 0.85) -> tuple[str, list[str]]:
    raise NotImplementedError


def vision_request(path, question: str) -> list[dict]:
    raise NotImplementedError
