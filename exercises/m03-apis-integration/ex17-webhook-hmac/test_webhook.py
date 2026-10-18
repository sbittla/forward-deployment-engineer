import hashlib
import hmac
import json

SECRET = "whsec_test"


class Clock:
    t = 1_700_000_000

    def __call__(self):
        return self.t


def test_sign_format(impl):
    body = '{"id":"evt_1"}'
    expected = hmac.new(SECRET.encode(), f"1700000000.{body}".encode(), hashlib.sha256).hexdigest()
    assert impl.sign(body, SECRET, 1700000000) == f"t=1700000000,v1={expected}"


def test_accept_then_duplicate(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk)
    body = json.dumps({"id": "evt_1", "type": "case.updated"})
    h = {"x-signature": impl.sign(body, SECRET, clk.t)}
    assert r.handle(h, body) == (202, "accepted")
    assert r.handle(h, body)[0] == 200
    assert len(r.processed) == 1 and r.processed[0]["type"] == "case.updated"


def test_bad_signature_and_missing(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk)
    body = '{"id":"e"}'
    assert r.handle({"X-Signature": impl.sign(body, "wrong", clk.t)}, body)[0] == 401
    assert r.handle({}, body)[0] == 401
    assert r.handle({"X-Signature": "garbage"}, body)[0] == 401
    tampered = '{"id":"e","amount":1000}'
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t)}, tampered)[0] == 401
    assert r.processed == []


def test_stale(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk, tolerance=300)
    body = '{"id":"e"}'
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t - 301)}, body) == (400, "stale")
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t - 300)}, body)[0] == 202


def test_bad_json(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk)
    for body in ("not json", '{"type":"x"}'):
        assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t)}, body)[0] == 400


def test_dedupe_expires(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk, dedupe_ttl=60)
    body = '{"id":"e"}'
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t)}, body)[0] == 202
    clk.t += 61
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t)}, body)[0] == 202
    assert len(r.processed) == 2
