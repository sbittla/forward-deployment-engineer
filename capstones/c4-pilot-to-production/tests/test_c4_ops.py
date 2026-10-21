import socket
import threading

import pytest

from fde_kit import FakeLLM

PACKAGE = "pilot"
ENV = {"PILOT_API_TOKENS": "tok", "PILOT_LLM_ENDPOINT": "https://llm-gateway.logistics.example",
       "PILOT_EGRESS_ALLOWLIST": "llm-gateway.logistics.example", "HTTPS_PROXY": "http://proxy:3128",
       "REQUESTS_CA_BUNDLE": "/etc/ssl/corp.pem"}


def test_incident_diagnosis(cap, cap_data):
    lines = (cap_data / "pilot_incident.log").read_text().splitlines()
    d = cap.diagnose(lines)
    assert d["first_error"] == "2026-10-14T13:02:11Z" and d["error_count"] == 10
    text = " ".join(f["finding"] for f in d["findings"])
    assert "4 upstream 529" in text and "surfaced to users as HTTP 500" in text
    assert "3 requests took 30 s" in text and "backlog reached 128" in text and "/healthz" in text
    assert all(f["fix"] for f in d["findings"]) and len(d["findings"]) == 4


def test_preflight_pass_warn_fail(cap):
    ok = cap.run_preflight(ENV, resolve=lambda h: "10.0.0.5", connect=lambda h, p: None, path_exists=lambda p: True)
    assert ok["status"] == "PASS" and [c[0] for c in ok["checks"]] == ["config", "dns", "egress", "allowlist", "ca_bundle"]
    warn = cap.run_preflight({k: v for k, v in ENV.items() if k != "REQUESTS_CA_BUNDLE"},
                             resolve=lambda h: "1.1.1.1", connect=lambda h, p: None)
    assert warn["status"] == "WARN" and ("ca_bundle", "WARN") in [(c[0], c[1]) for c in warn["checks"]]

    def nxdomain(h):
        raise socket.gaierror()

    bad = cap.run_preflight(ENV, resolve=nxdomain, connect=lambda h, p: None, path_exists=lambda p: False)
    assert bad["status"] == "FAIL"
    assert dict((c[0], c[1]) for c in bad["checks"]) == {"config": "PASS", "dns": "FAIL", "egress": "PASS",
                                                         "allowlist": "PASS", "ca_bundle": "FAIL"}
    assert cap.run_preflight({})["status"] == "FAIL"


def test_slo_alerts(cap):
    slo = cap.SLO(target=0.999)
    now = 10 * 3600
    healthy = [(t, 200, 800) for t in range(now - 6 * 3600 + 1, now + 1, 5)]
    burst = [(t, 529 if t % 10 == 0 else 200, 800) for t in range(now - 3600 + 1, now + 1)]
    assert slo.alerts(healthy, now) == []
    assert slo.alerts(healthy + burst, now) == ["page"]


def test_load_and_capacity(cap):
    llm = cap.ResilientLLM(FakeLLM(lambda m, s, t: "ok"))
    srv = cap.make_server(cap.load_settings(ENV), llm)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/v1/summarize"
        rep = cap.run_load(url, "tok", {"text": "hello"}, total=30, concurrency=5)
        assert rep.count == 30 and rep.errors == 0 and rep.p95_ms >= rep.p50_ms > 0 and rep.rps > 0
    finally:
        srv.shutdown()
        srv.server_close()
    assert cap.required_replicas(target_rps=20, p95_latency_s=4.0, concurrency_per_replica=16) == 7
    assert cap.required_replicas(1, 0.5, 64) == 2


def test_canary_decision(cap):
    base = {"requests": 5000, "error_rate": 0.004, "p95_ms": 3800, "judge_pass": 0.91, "refusal_rate": 0.03}
    same = dict(base, requests=600)
    assert cap.canary_decision(base, dict(same, requests=499)) == "wait"
    assert cap.canary_decision(base, same) == "promote"
    assert cap.canary_decision(base, dict(same, error_rate=0.0071)) == "rollback"
    assert cap.canary_decision(base, dict(same, error_rate=0.0069)) == "promote"
    assert cap.canary_decision(base, dict(same, p95_ms=4600)) == "rollback"
    # Same errors and latency, four points worse on quality: an error-only canary would promote this.
    assert cap.canary_decision(base, dict(same, judge_pass=0.87)) == "rollback"
    assert cap.canary_decision(base, dict(same, refusal_rate=0.06)) == "rollback"
    assert cap.canary_decision(base, dict(same, requests=100), min_requests=100) == "promote"
