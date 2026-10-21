from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    type: str
    start: int
    end: int
    value: str


def luhn_ok(digits: str) -> bool:
    raise NotImplementedError


def detect(text: str) -> list[Entity]:
    raise NotImplementedError


def redact(text: str, mode: str = "token") -> tuple[str, dict[str, str]]:
    raise NotImplementedError


def restore(text: str, mapping: dict[str, str]) -> str:
    raise NotImplementedError
