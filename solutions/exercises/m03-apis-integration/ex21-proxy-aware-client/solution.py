import fnmatch
import urllib.request
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlsplit


class EgressDenied(Exception):
    pass


def _split(v: str | None) -> list[str]:
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def _first(env, *names):
    for n in names:
        if env.get(n):
            return env[n]
    return None


@dataclass
class NetworkPolicy:
    https_proxy: str | None = None
    http_proxy: str | None = None
    no_proxy: list[str] = field(default_factory=list)
    ca_bundle: str | None = None
    allowlist: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "NetworkPolicy":
        return cls(
            https_proxy=_first(env, "HTTPS_PROXY", "https_proxy"),
            http_proxy=_first(env, "HTTP_PROXY", "http_proxy"),
            no_proxy=_split(_first(env, "NO_PROXY", "no_proxy")),
            ca_bundle=_first(env, "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"),
            allowlist=_split(env.get("FDE_EGRESS_ALLOWLIST")),
        )

    def _bypass(self, host: str, port: int | None) -> bool:
        for entry in self.no_proxy:
            if entry == "*":
                return True
            e_host, _, e_port = entry.partition(":")
            if e_port and (port is None or int(e_port) != port):
                continue
            e_host = e_host.lstrip(".")
            if host == e_host or host.endswith("." + e_host):
                return True
        return False

    def proxy_for(self, url: str) -> str | None:
        u = urlsplit(url)
        if self._bypass(u.hostname or "", u.port):
            return None
        return self.https_proxy if u.scheme == "https" else self.http_proxy

    def _allowed(self, host: str) -> bool:
        if not self.allowlist:
            return True
        return any(fnmatch.fnmatchcase(host, pat) if "*" in pat else host == pat for pat in self.allowlist)

    def check_egress(self, url: str) -> None:
        host = urlsplit(url).hostname or ""
        if not self._allowed(host):
            raise EgressDenied(f"{host} is not on the egress allowlist")

    def diagnose(self, url: str) -> list[str]:
        host = urlsplit(url).hostname or ""
        proxy = self.proxy_for(url)
        return [
            "egress: allowed" if self._allowed(host) else "egress: DENIED by allowlist",
            f"proxy: {proxy}" if proxy else "proxy: direct",
            f"ca_bundle: {self.ca_bundle}" if self.ca_bundle else "ca_bundle: system default",
        ]

    def opener(self):
        proxies = {}
        if self.http_proxy:
            proxies["http"] = self.http_proxy
        if self.https_proxy:
            proxies["https"] = self.https_proxy
        if self.no_proxy:
            proxies["no"] = ",".join(self.no_proxy)
        return urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
