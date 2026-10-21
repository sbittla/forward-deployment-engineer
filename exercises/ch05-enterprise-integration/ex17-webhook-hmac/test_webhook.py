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


def test_raw_body_bytes_are_signed(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk)
    raw = '{"id":"evt_b","name":"Zoë"}'.encode()
    assert impl.sign(raw, SECRET, clk.t) == impl.sign(raw.decode(), SECRET, clk.t)
    assert r.handle({"X-Signature": impl.sign(raw, SECRET, clk.t)}, raw) == (202, "accepted")


def test_non_ascii_signature_is_401_not_a_crash(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk)
    body = '{"id":"evt_u"}'
    assert r.handle({"X-Signature": f"t={clk.t},v1=é"}, body) == (401, "bad signature")
    assert r.handle({"X-Signature": f"t={clk.t},v1=é"}, body.encode()) == (401, "bad signature")


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


# Part B · version-ordered updates and reconciliation

CASES = [{"id": "c1", "version": v, "status": s} for v, s in [(1, "open"), (2, "pending"), (3, "closed")]] + \
        [{"id": "c2", "version": v, "status": s} for v, s in [(1, "open"), (2, "closed")]]
LATEST = {"c1": CASES[2], "c2": CASES[4]}


def test_apply_update_rejects_stale_and_duplicate(impl):
    store = {}
    assert impl.apply_update(store, CASES[1]) is True
    assert impl.apply_update(store, CASES[1]) is False  # duplicate
    assert impl.apply_update(store, CASES[0]) is False  # older version
    assert impl.apply_update(store, CASES[2]) is True
    assert store == {"c1": CASES[2]}


def test_shuffled_and_duplicated_deliveries_converge(impl):
    import random
    for seed in range(20):
        deliveries = CASES * 2
        random.Random(seed).shuffle(deliveries)
        store = {}
        for record in deliveries:
            impl.apply_update(store, record)
        assert store == LATEST, f"seed {seed}"


class FakeClient:
    def __init__(self, records):
        self.records, self.calls = records, []

    def list_all(self, path, params):
        self.calls.append((path, params))
        yield from self.records


def test_reconcile_uses_the_same_path(impl):
    store = {"c1": CASES[2]}  # webhook already delivered the newest c1
    client = FakeClient([CASES[1], CASES[4]])
    assert impl.reconcile(client, store, "2026-01-01T00:00:00Z") == 1
    assert client.calls == [("/cases", {"updated_since": "2026-01-01T00:00:00Z"})]
    assert store == LATEST


def test_receiver_ignores_stale_redelivery(impl):
    clk = Clock()
    store = {}
    r = impl.WebhookReceiver(SECRET, clock=clk, store=store)
    events = [("evt_new", CASES[2]), ("evt_old_1", CASES[0]), ("evt_old_2", CASES[1])]
    for event_id, record in events:  # distinct ids, so dedupe lets the stale ones through
        body = json.dumps({"id": event_id, "type": "case.updated", "data": record})
        assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t)}, body) == (202, "accepted")
    assert store == {"c1": CASES[2]}


# Boundary tests: pin what the timestamp window and the in-memory dedupe store do and don't cover

def test_boundary_replay_outside_window_is_stale(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk, tolerance=300, dedupe_ttl=60)
    body = '{"id":"evt_replay"}'
    captured = {"X-Signature": impl.sign(body, SECRET, clk.t)}
    assert r.handle(captured, body) == (202, "accepted")
    clk.t += 301  # the seen id has expired; only the timestamp window stops the replay
    assert r.handle(captured, body) == (400, "stale")
    assert len(r.processed) == 1


def test_boundary_dedupe_is_per_process(impl):
    clk = Clock()
    body = '{"id":"evt_1"}'
    captured = {"X-Signature": impl.sign(body, SECRET, clk.t)}
    first = impl.WebhookReceiver(SECRET, clock=clk)
    assert first.handle(captured, body) == (202, "accepted")
    restarted = impl.WebhookReceiver(SECRET, clock=clk)  # a restart or another replica
    assert restarted.handle(captured, body) == (202, "accepted")


# Negative tests: rewritten timestamps, future timestamps and secret rotation

def test_rewritten_timestamp_is_rejected(impl):
    # An attacker replays a captured delivery but rewrites t to "now" to pass the window: t is signed, so 401.
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk, tolerance=300)
    body = '{"id":"evt_old"}'
    captured_sig = impl.sign(body, SECRET, clk.t - 3600).split(",v1=")[1]
    assert r.handle({"X-Signature": f"t={clk.t},v1={captured_sig}"}, body) == (401, "bad signature")
    assert r.processed == []


def test_future_timestamp_is_stale(impl):
    clk = Clock()
    r = impl.WebhookReceiver(SECRET, clock=clk, tolerance=300)
    body = '{"id":"evt_future"}'
    assert r.handle({"X-Signature": impl.sign(body, SECRET, clk.t + 301)}, body) == (400, "stale")
    assert r.processed == []


def test_rotation_accepts_either_secret_during_overlap(impl):
    clk = Clock()
    new, old = "whsec_new", SECRET
    during = impl.WebhookReceiver([new, old], clock=clk)
    for i, secret in enumerate((new, old)):
        body = json.dumps({"id": f"evt_{i}"})
        assert during.handle({"X-Signature": impl.sign(body, secret, clk.t)}, body) == (202, "accepted")
    after = impl.WebhookReceiver([new], clock=clk)  # old secret dropped once the redelivery horizon has passed
    body = '{"id":"evt_late"}'
    assert after.handle({"X-Signature": impl.sign(body, old, clk.t)}, body)[0] == 401
    assert impl.WebhookReceiver([], clock=clk).handle({"X-Signature": impl.sign(body, old, clk.t)}, body)[0] == 401
