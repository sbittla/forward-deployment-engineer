import urllib.request

import pytest

ENV = {
    "HTTPS_PROXY": "http://ignored:1",
    "https_proxy": "http://proxy.bank.local:3128",
    "http_proxy": "http://proxy.bank.local:3128",
    "no_proxy": "localhost,.corp.local,vault.bank.local:8200",
    "SSL_CERT_FILE": "/etc/ssl/bank-root.pem",
    "FDE_EGRESS_ALLOWLIST": "api.anthropic.com, *.corp.local",
}


def test_from_env(impl):
    p = impl.NetworkPolicy.from_env(ENV)
    assert p.https_proxy == "http://proxy.bank.local:3128"
    assert p.no_proxy == ["localhost", ".corp.local", "vault.bank.local:8200"]
    assert p.ca_bundle == "/etc/ssl/bank-root.pem"
    assert p.allowlist == ["api.anthropic.com", "*.corp.local"]
    assert impl.NetworkPolicy.from_env({**ENV, "REQUESTS_CA_BUNDLE": "/a.pem"}).ca_bundle == "/a.pem"


@pytest.mark.parametrize("url,expected", [
    ("https://api.anthropic.com/v1/messages", "http://proxy.bank.local:3128"),
    ("https://search.corp.local/q", None),
    ("http://localhost:8080/", None),
    ("https://vault.bank.local:8200/v1", None),
    ("https://vault.bank.local/v1", "http://proxy.bank.local:3128"),
])
def test_proxy_for(impl, url, expected):
    assert impl.NetworkPolicy.from_env(ENV).proxy_for(url) == expected


def test_lowercase_proxy_wins_like_requests(impl):
    # urllib.request.getproxies() (used by requests) and curl prefer the lower-case variable when both are set
    env = {"HTTPS_PROXY": "http://upper:1", "https_proxy": "http://lower:2",
           "HTTP_PROXY": "http://upper:1", "http_proxy": "http://lower:2", "NO_PROXY": "a.corp", "no_proxy": "b.corp"}
    p = impl.NetworkPolicy.from_env(env)
    assert (p.https_proxy, p.http_proxy, p.no_proxy) == ("http://lower:2", "http://lower:2", ["b.corp"])
    only_upper = impl.NetworkPolicy.from_env({"HTTPS_PROXY": "http://upper:1", "NO_PROXY": "a.corp"})
    assert (only_upper.https_proxy, only_upper.no_proxy) == ("http://upper:1", ["a.corp"])


def test_no_proxy_star(impl):
    assert impl.NetworkPolicy.from_env({**ENV, "no_proxy": "*"}).proxy_for("https://x.com") is None


def test_egress(impl):
    p = impl.NetworkPolicy.from_env(ENV)
    p.check_egress("https://api.anthropic.com/v1/messages")
    p.check_egress("https://search.corp.local/")
    for bad in ("https://evil.com/", "https://corp.local/", "https://api.anthropic.com.evil.com/"):
        with pytest.raises(impl.EgressDenied):
            p.check_egress(bad)
    impl.NetworkPolicy.from_env({}).check_egress("https://anything.example")


def test_diagnose(impl):
    p = impl.NetworkPolicy.from_env(ENV)
    assert p.diagnose("https://evil.com") == ["egress: DENIED by allowlist", "proxy: http://proxy.bank.local:3128",
                                              "ca_bundle: /etc/ssl/bank-root.pem"]
    assert impl.NetworkPolicy.from_env({}).diagnose("https://x.com") == [
        "egress: allowed", "proxy: direct", "ca_bundle: system default"]


def test_opener(impl):
    op = impl.NetworkPolicy.from_env(ENV).opener()
    ph = [h for h in op.handlers if isinstance(h, urllib.request.ProxyHandler)]
    assert ph and ph[0].proxies["https"] == "http://proxy.bank.local:3128"
    assert "corp.local" in ph[0].proxies.get("no", "")


# Offline and air-gap tests: the tool works with no network at all, and an internal-only allowlist fails closed

@pytest.fixture
def no_network(monkeypatch):
    import socket

    def refuse(*args, **kwargs):
        raise OSError("network disabled by test")

    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket.socket, "connect", refuse)


AIR_GAP = {"FDE_EGRESS_ALLOWLIST": "*.bank.internal, pypi-mirror.bank.internal",
           "REQUESTS_CA_BUNDLE": "/etc/ssl/bank-root.pem", "NO_PROXY": ".bank.internal"}


def test_offline_policy_makes_no_network_calls(impl, no_network):
    p = impl.NetworkPolicy.from_env(AIR_GAP)
    assert p.diagnose("https://idp.bank.internal/token") == [
        "egress: allowed", "proxy: direct", "ca_bundle: /etc/ssl/bank-root.pem"]
    p.check_egress("https://pypi-mirror.bank.internal/simple/")
    assert p.proxy_for("https://idp.bank.internal/token") is None
    p.opener()


def test_air_gap_allowlist_fails_closed(impl, no_network):
    p = impl.NetworkPolicy.from_env(AIR_GAP)
    for url in ("https://api.anthropic.com/v1/messages", "https://pypi.org/simple/", "https://8.8.8.8/",
                "https://idp.bank.internal@evil.com/", "https://bank.internal/"):
        with pytest.raises(impl.EgressDenied):
            p.check_egress(url)
    assert p.diagnose("https://pypi.org/simple/")[0] == "egress: DENIED by allowlist"
