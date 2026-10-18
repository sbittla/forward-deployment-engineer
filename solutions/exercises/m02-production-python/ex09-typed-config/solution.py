from dataclasses import asdict, dataclass, fields
from typing import Mapping

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class ConfigError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class Secret:
    def __init__(self, value: str):
        self._value = value

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "Secret('****')"

    __str__ = __repr__

    def __eq__(self, other) -> bool:
        return isinstance(other, Secret) and other._value == self._value

    def __hash__(self) -> int:
        return hash(self._value)


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    api_key: Secret
    timeout_s: float = 30.0
    max_retries: int = 3
    log_level: str = "INFO"
    allowed_tenants: tuple[str, ...] = ()

    def redacted(self) -> dict:
        d = {f.name: getattr(self, f.name) for f in fields(self)}
        d["api_key"] = "****"
        return d


def load_settings(env: Mapping[str, str]) -> Settings:
    errors: list[str] = []
    out: dict = {}

    url = env.get("FDE_API_BASE_URL", "")
    if not url:
        errors.append("FDE_API_BASE_URL is required")
    elif not url.startswith("https://"):
        errors.append("FDE_API_BASE_URL must use https://")
    out["api_base_url"] = url

    key = env.get("FDE_API_KEY", "")
    if not key:
        errors.append("FDE_API_KEY is required")
    out["api_key"] = Secret(key)

    if "FDE_TIMEOUT_S" in env:
        try:
            t = float(env["FDE_TIMEOUT_S"])
            if t <= 0:
                raise ValueError
            out["timeout_s"] = t
        except ValueError:
            errors.append("FDE_TIMEOUT_S must be a number > 0")

    if "FDE_MAX_RETRIES" in env:
        try:
            r = int(env["FDE_MAX_RETRIES"])
            if not 0 <= r <= 10:
                raise ValueError
            out["max_retries"] = r
        except ValueError:
            errors.append("FDE_MAX_RETRIES must be an integer 0-10")

    if "FDE_LOG_LEVEL" in env:
        lvl = env["FDE_LOG_LEVEL"].upper()
        if lvl not in LEVELS:
            errors.append(f"FDE_LOG_LEVEL must be one of {', '.join(LEVELS)}")
        out["log_level"] = lvl

    if "FDE_ALLOWED_TENANTS" in env:
        out["allowed_tenants"] = tuple(t.strip() for t in env["FDE_ALLOWED_TENANTS"].split(",") if t.strip())

    if errors:
        raise ConfigError(errors)
    return Settings(**out)
