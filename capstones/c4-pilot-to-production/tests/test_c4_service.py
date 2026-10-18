import io
import json
import threading
import urllib.error
import urllib.request

import pytest

from fde_kit import FakeLLM

PACKAGE = "pilot"
ENV = {"PILOT_API_TOKENS": "tok", "PILOT_LLM_ENDPOINT": "https://llm.example", "PILOT_MAX_INPUT_CHARS": "200"}


class APIError(Exception):
    status = 500


def call(url, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()


@pytest.fixture
def svc(cap):
    state = {"fail": False}

    def upstream(m, s, t):
        if state["fail"]:
            raise APIError()
        return "- delayed at Rotterdam\n- ETA +2 days"

    log = io.StringIO()
    llm = cap.ResilientLLM(FakeLLM(upstream), max_retries=0, breaker_threshold=1, reset_timeout=60,
                           sleep=lambda s: None)
    metrics = cap.Metrics()
    srv = cap.make_server(cap.load_settings(ENV), llm, metrics, cap.json_logger("pilot-test", log))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", state, log
    srv.shutdown()
    srv.server_close()


def test_probes(svc):
    url, state, _ = svc
    assert call(url + "/healthz")[0] == 200
    status, _, body = call(url + "/readyz")
    assert status == 200 and json.loads(body)["llm_circuit"] == "closed"


def test_summarize_and_errors(svc):
    url, state, log = svc
    status, headers, body = call(url + "/v1/summarize", "POST", {"text": "container held"}, "tok")
    assert status == 200 and "Rotterdam" in json.loads(body)["summary"] and headers["X-Request-ID"]
    assert call(url + "/v1/summarize", "POST", {"text": "x"})[0] == 401
    assert call(url + "/v1/summarize", "POST", {"nope": 1}, "tok")[0] == 400
    assert call(url + "/v1/summarize", "POST", {"text": "x" * 201}, "tok")[0] == 413
    records = [json.loads(l) for l in log.getvalue().splitlines()]
    assert records[0]["route"] == "/v1/summarize" and records[0]["status"] == 200 and "request_id" in records[0]
    assert "container held" not in log.getvalue()     # never log customer payloads


def test_degrades_gracefully(svc):
    url, state, _ = svc
    state["fail"] = True
    assert call(url + "/v1/summarize", "POST", {"text": "x"}, "tok")[0] == 502   # upstream error, breaker trips
    status, headers, body = call(url + "/v1/summarize", "POST", {"text": "x"}, "tok")
    assert status == 503 and headers["Retry-After"] == "30"
    assert call(url + "/readyz")[0] == 503                                         # pulled from the load balancer


def test_metrics_exposition(svc):
    url, _, _ = svc
    call(url + "/v1/summarize", "POST", {"text": "x"}, "tok")
    call(url + "/healthz")
    status, headers, text = call(url + "/metrics")
    assert status == 200 and headers["Content-Type"].startswith("text/plain")
    assert "# TYPE pilot_requests_total counter" in text
    assert 'pilot_requests_total{route="/v1/summarize",status="200"} 1' in text
    assert "# TYPE pilot_request_seconds histogram" in text
    assert 'pilot_request_seconds_bucket{le="+Inf",route="/v1/summarize"} 1' in text
    assert 'pilot_request_seconds_count{route="/healthz"} 1' in text


def test_metrics_unit(cap):
    m = cap.Metrics()
    h = m.histogram("lat", "latency", buckets=(0.5, 1.0))
    for v in (0.2, 0.7, 3.0):
        h.observe(v, {"r": "a"})
    text = m.render()
    assert 'lat_bucket{le="0.5",r="a"} 1' in text and 'lat_bucket{le="1",r="a"} 2' in text
    assert 'lat_bucket{le="+Inf",r="a"} 3' in text and 'lat_count{r="a"} 3' in text
