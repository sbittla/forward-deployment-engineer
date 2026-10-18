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
        return self._value

    def __repr__(self) -> str:
        return "Secret('****')"

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
        d = {f.name: getattr(self, f.name) for f in fields(self)}
        d["api_tokens"] = f"{len(self.api_tokens)} token(s)"
        return d


def _split(v: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in (v or "").split(",") if x.strip())


def load_settings(env: Mapping[str, str]) -> Settings:
    errors, out = [], {}
    tokens = _split(env.get("PILOT_API_TOKENS", ""))
    if not tokens:
        errors.append("PILOT_API_TOKENS is required (comma-separated)")
    out["api_tokens"] = tuple(Secret(t) for t in tokens)

    endpoint = env.get("PILOT_LLM_ENDPOINT", "")
    if not endpoint.startswith("https://"):
        errors.append("PILOT_LLM_ENDPOINT must be an https:// URL")
    out["llm_endpoint"] = endpoint

    for key, name, cast, check in (("PILOT_TIMEOUT_S", "timeout_s", float, lambda v: 0 < v <= 120),
                                   ("PILOT_MAX_INPUT_CHARS", "max_input_chars", int, lambda v: 100 <= v <= 200_000)):
        if key in env:
            try:
                v = cast(env[key])
                if not check(v):
                    raise ValueError
                out[name] = v
            except ValueError:
                errors.append(f"{key} is out of range or not a number")

    for key, name in (("PILOT_MODEL", "model"), ("PILOT_FALLBACK_MODEL", "fallback_model")):
        if env.get(key):
            out[name] = env[key]
    out["egress_allowlist"] = _split(env.get("PILOT_EGRESS_ALLOWLIST", ""))
    host = urlsplit(endpoint).hostname or ""
    if out["egress_allowlist"] and host and host not in out["egress_allowlist"]:
        errors.append(f"PILOT_LLM_ENDPOINT host {host} is not in PILOT_EGRESS_ALLOWLIST")
    out["https_proxy"] = env.get("HTTPS_PROXY") or env.get("https_proxy") or None
    out["ca_bundle"] = env.get("REQUESTS_CA_BUNDLE") or env.get("SSL_CERT_FILE") or None
    if errors:
        raise ConfigError(errors)
    return Settings(**out)
