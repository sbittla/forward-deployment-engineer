"""Typed, validated settings. All problems are reported at start-up, and secrets never print."""
from dataclasses import dataclass, fields
from typing import Mapping
from urllib.parse import urlsplit


class ConfigError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class Secret:
    def __init__(self, value: str):
        self._value = value

    def reveal(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    __str__ = __repr__


@dataclass(frozen=True)
class Settings:
    api_tokens: tuple[Secret, ...]
    llm_endpoint: str
    model: str = "claude-sonnet-5-5"
    fallback_model: str = "claude-haiku-5-5"
    timeout_s: float = 20.0
    max_input_chars: int = 20000
    egress_allowlist: tuple[str, ...] = ()
    https_proxy: str | None = None
    ca_bundle: str | None = None

    def redacted(self) -> dict:
        raise NotImplementedError


def _split(v: str) -> tuple[str, ...]:
    raise NotImplementedError


def load_settings(env: Mapping[str, str]) -> Settings:
    raise NotImplementedError
