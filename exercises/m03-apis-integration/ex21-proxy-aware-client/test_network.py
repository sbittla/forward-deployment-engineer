import urllib.request

import pytest

ENV = {
    "HTTPS_PROXY": "http://proxy.bank.local:3128",
    "https_proxy": "http://ignored:1",
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
