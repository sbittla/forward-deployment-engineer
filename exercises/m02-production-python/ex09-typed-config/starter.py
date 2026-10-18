from dataclasses import dataclass
from typing import Mapping


class ConfigError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class Secret:
    def __init__(self, value: str):
        self._value = value

    def reveal(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    api_key: Secret
    timeout_s: float = 30.0
    max_retries: int = 3
    log_level: str = "INFO"
    allowed_tenants: tuple[str, ...] = ()

    def redacted(self) -> dict:
        raise NotImplementedError


def load_settings(env: Mapping[str, str]) -> Settings:
    raise NotImplementedError
