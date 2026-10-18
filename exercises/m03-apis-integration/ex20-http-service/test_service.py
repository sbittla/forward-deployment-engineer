import json
import threading
import urllib.error
import urllib.request

import pytest


@pytest.fixture
def server(impl):
    def answer(q):
        if q == "explode":
            raise RuntimeError("db password is hunter2")
        return f"echo: {q}"

    srv = impl.make_server(answer, {"good-token"})
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def call(url, method="GET", body=None, headers=None):
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, dict(r.headers), json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), json.loads(e.read() or b"null")


AUTH = {"Authorization": "Bearer good-token", "Content-Type": "application/json"}


def test_health(server):
    status, headers, body = call(server + "/healthz")
    assert status == 200 and body == {"status": "ok"} and len(headers["X-Request-ID"]) == 32


def test_answer_and_request_id_echo(server):
    status, headers, body = call(server + "/v1/answer", "POST", {"question": "hi"},
                                 {**AUTH, "X-Request-ID": "abc123"})
    assert status == 200 and body["answer"] == "echo: hi" and body["request_id"] == "abc123"
    assert headers["X-Request-ID"] == "abc123"


def test_auth(server):
    assert call(server + "/v1/answer", "POST", {"question": "hi"})[0] == 401
    bad = {**AUTH, "Authorization": "Bearer nope"}
    assert call(server + "/v1/answer", "POST", {"question": "hi"}, bad)[0] == 401


@pytest.mark.parametrize("body", [b"not json", {"q": "x"}, {"question": 5}, {"question": ""},
                                  {"question": "x" * 2001}])
def test_validation(server, body):
    status, _, resp = call(server + "/v1/answer", "POST", body, AUTH)
    assert status == 400 and "error" in resp


def test_too_large(server):
    status, _, resp = call(server + "/v1/answer", "POST", b"x" * 70000, AUTH)
    assert status == 413


def test_method_and_path(server):
    assert call(server + "/v1/answer", "GET", headers=AUTH)[0] == 405
    assert call(server + "/nope")[0] == 404


def test_internal_error_does_not_leak(server):
    status, _, body = call(server + "/v1/answer", "POST", {"question": "explode"}, AUTH)
    assert status == 500 and body["error"] == "internal error" and "hunter2" not in json.dumps(body)
