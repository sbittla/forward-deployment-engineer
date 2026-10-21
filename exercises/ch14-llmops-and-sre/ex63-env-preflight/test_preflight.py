import socket
from collections import namedtuple

Usage = namedtuple("Usage", "total used free")


def ok_connect(host, port):
    return None


def refused(host, port):
    raise ConnectionRefusedError()


def test_all_pass(impl, tmp_path):
    checks = [
        impl.python_version((3, 10), current=(3, 12, 1)),
        impl.env_vars(["FDE_API_KEY"], {"FDE_API_KEY": "x"}),
        impl.disk_free("/", 5, usage=lambda p: Usage(100e9, 10e9, 90e9)),
        impl.dns("api.anthropic.com", resolve=lambda h: "1.2.3.4"),
        impl.tcp("api.anthropic.com", 443, ok_connect),
        impl.clock_skew(1_000_000, now=lambda: 1_000_010),
        impl.writable(str(tmp_path)),
    ]
    rep = impl.run_preflight(checks)
    assert rep.status == "PASS" and rep.exit_code == 0
    lines = rep.render().splitlines()
    assert lines[2] == "[PASS] disk_free(/) — 90.0 GB free"
    assert lines[-1] == "Overall: PASS"


def test_failures_and_hints(impl):
    def nxdomain(h):
        raise socket.gaierror("nope")

    checks = [
        impl.python_version((3, 11), current=(3, 9, 7), hint="install Python 3.11+"),
        impl.env_vars(["A", "B", "C"], {"B": "1"}),
        impl.dns("api.anthropic.com", resolve=nxdomain, hint="ask IT to allow DNS for api.anthropic.com"),
        impl.tcp("api.anthropic.com", 443, refused),
        impl.clock_skew(1_000_000, now=lambda: 1_000_500),
    ]
    rep = impl.run_preflight(checks)
    assert rep.status == "FAIL" and rep.exit_code == 2
    out = rep.render()
    assert "[FAIL] python_version — 3.9.7 < 3.11 (hint: install Python 3.11+)" in out
    assert "missing: A, C" in out
    assert "gaierror" in out and "(hint: ask IT" in out
    assert "ConnectionRefusedError" in out
    assert "[WARN] clock_skew — skew 500s" in out


def test_warn_only(impl):
    rep = impl.run_preflight([impl.clock_skew(0, now=lambda: 120)])
    assert rep.status == "WARN" and rep.exit_code == 1


def test_crashing_check(impl):
    def boom():
        raise PermissionError()
    rep = impl.run_preflight([impl.Check("custom", boom)])
    assert rep.status == "FAIL" and "PermissionError" in rep.render()


def test_not_writable(impl, tmp_path):
    missing = tmp_path / "does-not-exist"
    rep = impl.run_preflight([impl.writable(str(missing))])
    assert rep.status == "FAIL"
