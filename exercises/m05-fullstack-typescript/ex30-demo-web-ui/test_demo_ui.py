import json
import threading
import urllib.error
import urllib.request

import pytest

from fde_kit import FakeLLM


def start(impl, llm, demo):
    srv = impl.make_app(llm, demo_mode=demo)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.headers.get("Content-Type"), r.read().decode()


def post(url, body):
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


@pytest.fixture
def app(impl):
    llm = FakeLLM(lambda msgs, system, tools: f"You asked: {msgs[-1]['content']}")
    srv, url = start(impl, llm, True)
    yield url, llm
    srv.shutdown()
    srv.server_close()


def test_page(app):
    url, _ = app
    status, ctype, html = get(url + "/")
    assert status == 200 and ctype.startswith("text/html")
    assert '<form id="chat-form"' in html and 'name="q"' in html and 'id="log"' in html
    assert 'fetch("/api/chat"' in html
    assert "textContent" in html and "innerHTML" not in html
    assert 'id="demo-banner"' in html and "DEMO MODE" in html


def test_no_banner_when_live(impl):
    srv, url = start(impl, FakeLLM(["x"]), False)
    try:
        assert "demo-banner" not in get(url + "/")[2]
    finally:
        srv.shutdown()
        srv.server_close()


def test_chat_api(app, impl):
    url, llm = app
    hist = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    status, body = post(url + "/api/chat", {"q": "deductible?", "history": hist})
    assert status == 200 and body["answer"] == "You asked: deductible?"
    assert body["model"] == "fake" and isinstance(body["latency_ms"], int)
    sent = llm.calls[-1]
    assert sent["messages"] == hist + [{"role": "user", "content": "deductible?"}]
    assert sent["system"] == impl.SYSTEM_PROMPT
    assert "know" in impl.SYSTEM_PROMPT.lower()


@pytest.mark.parametrize("body", [b"nope", {"history": []}, {"q": ""}, {"q": "x", "history": "bad"}])
def test_chat_validation(app, body):
    url, _ = app
    assert post(url + "/api/chat", body)[0] == 400


def test_404(app):
    url, _ = app
    with pytest.raises(urllib.error.HTTPError) as e:
        get(url + "/admin")
    assert e.value.code == 404
