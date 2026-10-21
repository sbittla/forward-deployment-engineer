from dataclasses import dataclass, field
from typing import Mapping


class EgressDenied(Exception):
    pass


@dataclass
class NetworkPolicy:
    https_proxy: str | None = None
    http_proxy: str | None = None
    no_proxy: list[str] = field(default_factory=list)
    ca_bundle: str | None = None
    allowlist: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "NetworkPolicy":
        raise NotImplementedError

    def proxy_for(self, url: str) -> str | None:
        raise NotImplementedError

    def check_egress(self, url: str) -> None:
        raise NotImplementedError

    def diagnose(self, url: str) -> list[str]:
        raise NotImplementedError

    def opener(self):
        raise NotImplementedError
