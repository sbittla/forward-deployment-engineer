import pytest


class Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def test_idempotent_enqueue_and_fifo(impl):
    q = impl.JobQueue(Clock())
    a = q.enqueue("triage", {"id": 1}, idempotency_key="msg-1")
    b = q.enqueue("triage", {"id": 1}, idempotency_key="msg-1")
    c = q.enqueue("triage", {"id": 2})
    assert a == b and a != c
    assert q.claim("w1").id == a
    assert q.claim("w2").id == c
    assert q.claim("w3") is None
    assert q.stats() == {"queued": 0, "leased": 2, "done": 0, "dead": 0}


def test_lease_expiry_and_stale_ack(impl):
    clk = Clock()
    q = impl.JobQueue(clk)
    jid = q.enqueue("triage", {})
    q.claim("w1", lease_s=10)
    clk.t += 11
    job = q.claim("w2")
    assert job.id == jid and job.attempts == 2
    with pytest.raises(impl.LeaseError):
        q.ack(jid, "w1")
    q.ack(jid, "w2")
    assert q.stats()["done"] == 1


def test_extend_keeps_lease_alive(impl):
    clk = Clock()
    q = impl.JobQueue(clk)
    jid = q.enqueue("triage", {})
    job = q.claim("w1", lease_s=10)
    clk.t += 8
    q.extend(jid, "w1", lease_s=10)  # heartbeat: lease now runs to t+18
    clk.t += 5
    assert q.claim("w2") is None
    assert job.attempts == 1  # a heartbeat is not a new attempt
    q.ack(jid, "w1")
    assert q.stats()["done"] == 1


def test_extend_requires_live_lease(impl):
    clk = Clock()
    q = impl.JobQueue(clk)
    jid = q.enqueue("triage", {})
    q.claim("w1", lease_s=10)
    with pytest.raises(impl.LeaseError):
        q.extend(jid, "w2", lease_s=10)  # not the owner
    clk.t += 11
    with pytest.raises(impl.LeaseError):
        q.extend(jid, "w1", lease_s=10)  # lease already expired
    assert q.claim("w2").attempts == 2


def test_backoff_then_dead_letter(impl):
    clk = Clock()
    q = impl.JobQueue(clk, max_attempts=3, base_backoff=2)
    jid = q.enqueue("triage", {})
    q.claim("w")
    q.fail(jid, "w", "timeout")
    assert q.claim("w") is None  # available at now + 2**1
    clk.t += 2
    q.claim("w")
    q.fail(jid, "w", "timeout")
    clk.t += 3.9
    assert q.claim("w") is None  # 2**2 = 4
    clk.t += 0.1
    q.claim("w")
    q.fail(jid, "w", "bad json")
    assert q.stats() == {"queued": 0, "leased": 0, "done": 0, "dead": 1}
    assert q.dead_letter[0].last_error == "bad json"


def test_run_worker(impl):
    clk = Clock()
    q = impl.JobQueue(clk, max_attempts=1)
    for i in range(3):
        q.enqueue("triage", {"n": i})
    q.enqueue("unknown", {})
    seen = []

    def triage(p):
        if p["n"] == 1:
            raise ValueError("model returned garbage")
        seen.append(p["n"])

    assert impl.run_worker(q, {"triage": triage}, "w", max_jobs=10) == 4
    assert seen == [0, 2]
    st = q.stats()
    assert st["done"] == 2 and st["dead"] == 2
    assert any(j.last_error == "no handler for unknown" for j in q.dead_letter)
