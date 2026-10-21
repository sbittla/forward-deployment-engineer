import pytest


class HTTPError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(status)
        self.status = status
        if retry_after is not None:
            self.retry_after = retry_after


def make(impl, failures, **kw):
    sleeps = []
    calls = {"n": 0}

    @impl.retry(sleep=sleeps.append, rng=lambda: 1.0, **kw)
    def op():
        calls["n"] += 1
        if failures:
            raise failures.pop(0)
        return "ok"
    return op, sleeps, calls


def test_retries_then_succeeds_with_exponential_backoff(impl):
    op, sleeps, calls = make(impl, [HTTPError(503), ConnectionError(), HTTPError(429)])
    assert op() == "ok" and calls["n"] == 4
    assert sleeps == [0.5, 1.0, 2.0]


def test_caps_at_max_delay(impl):
    op, sleeps, _ = make(impl, [HTTPError(500)] * 5, max_attempts=6, base_delay=1, max_delay=3)
    op()
    assert sleeps == [1, 2, 3, 3, 3]


def test_retry_after_wins(impl):
    op, sleeps, _ = make(impl, [HTTPError(429, retry_after=7)])
    op()
    assert sleeps == [7]


def test_non_retryable_raises_immediately(impl):
    op, sleeps, calls = make(impl, [HTTPError(400)])
    with pytest.raises(HTTPError):
        op()
    assert calls["n"] == 1 and sleeps == []


def test_gives_up(impl):
    op, sleeps, calls = make(impl, [TimeoutError()] * 10, max_attempts=3)
    with pytest.raises(TimeoutError):
        op()
    assert calls["n"] == 3 and len(sleeps) == 2


def test_jitter_uses_rng(impl):
    sleeps = []

    @impl.retry(sleep=sleeps.append, rng=lambda: 0.25, base_delay=2)
    def op(_state=[HTTPError(502)]):
        if _state:
            raise _state.pop()
        return 1
    op()
    assert sleeps == [0.5]


def test_idempotency(impl):
    store = impl.IdempotencyStore()
    paid = []

    def refund(p):
        paid.append(p["amount"])
        return {"refund_id": len(paid)}

    r1 = store.run("k1", {"amount": 10, "order": "A"}, refund)
    r2 = store.run("k1", {"order": "A", "amount": 10}, refund)
    assert r1 == r2 == {"refund_id": 1} and paid == [10]
    with pytest.raises(impl.IdempotencyConflict):
        store.run("k1", {"amount": 99, "order": "A"}, refund)


def test_failed_call_not_cached(impl):
    store = impl.IdempotencyStore()
    attempts = []

    def flaky(p):
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError()
        return "done"

    with pytest.raises(ConnectionError):
        store.run("k", {}, flaky)
    assert store.run("k", {}, flaky) == "done" and len(attempts) == 2


def test_boundary_retry_after_is_not_capped_by_a_deadline(impl):
    # Pins a documented limitation: without deadline= (the default) there is no time budget, so a server's
    # Retry-After of an hour is slept in full. Production code sets a deadline.
    op, sleeps, calls = make(impl, [HTTPError(503, retry_after=3600)])
    assert op() == "ok"
    assert sleeps == [3600] and calls["n"] == 2


# Fault injection: a fake dependency that fails a fraction of calls, runs slowly, or loses its response

class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


def test_fault_partial_failures_bounded_retries(impl):
    # 200 clients against a dependency that fails a seeded 30% of calls: retries are bounded per client
    import random
    rng = random.Random(7)
    calls, sleeps, outcomes = [], [], []

    @impl.retry(max_attempts=4, sleep=sleeps.append, rng=rng.random)
    def flaky(client):
        calls.append(client)
        if rng.random() < 0.3:
            raise HTTPError(503)
        return "ok"

    for client in range(200):
        try:
            outcomes.append(flaky(client))
        except HTTPError:
            outcomes.append("failed")
    assert len(calls) <= 200 * 4 and len(sleeps) == len(calls) - 200
    assert all(calls.count(c) == 4 for c, o in enumerate(outcomes) if o == "failed")
    assert all(0 <= s <= 8.0 for s in sleeps)
    assert outcomes.count("ok") >= 190


def test_fault_retry_storm_is_bounded_during_outage(impl):
    # Full outage: every call fails. Total load is exactly clients x max_attempts, and jitter spreads the waits.
    import random
    rng = random.Random(1)
    calls, sleeps = [], []

    @impl.retry(max_attempts=3, base_delay=1, sleep=sleeps.append, rng=rng.random)
    def down():
        calls.append(1)
        raise ConnectionError("down")

    for _ in range(100):
        with pytest.raises(ConnectionError):
            down()
    assert len(calls) == 300 and len(sleeps) == 200
    assert len({round(s, 6) for s in sleeps}) > 150  # no synchronized wave


def test_fault_slow_dependency_respects_deadline(impl):
    # Each call hangs for 3 s before timing out; a 10 s budget stops the loop before the backoff would pass it
    clk = FakeClock()
    calls = []

    @impl.retry(max_attempts=10, sleep=clk.sleep, rng=lambda: 1.0, deadline=10, clock=clk)
    def slow():
        calls.append(clk.t)
        clk.t += 3
        raise TimeoutError()

    with pytest.raises(TimeoutError):
        slow()
    assert calls == [0.0, 3.5, 7.5] and clk.t == 10.5  # third backoff (2 s) would end at 12.5 > 10


def test_fault_attempt_timeout_is_capped_by_time_left(impl):
    # Each call receives timeout=min(attempt_timeout, time left before the deadline) and hangs for all of it
    clk = FakeClock()
    timeouts = []

    @impl.retry(max_attempts=10, sleep=clk.sleep, rng=lambda: 1.0, deadline=10, clock=clk, attempt_timeout=4)
    def hang(timeout):
        timeouts.append(timeout)
        clk.t += timeout
        raise TimeoutError()

    with pytest.raises(TimeoutError):
        hang()
    assert timeouts == [4, 4, 0.5] and clk.t == 10


def test_fault_retry_after_beyond_deadline_fails_fast(impl):
    clk = FakeClock()
    sleeps = []

    @impl.retry(sleep=sleeps.append, deadline=60, clock=clk)
    def throttled():
        raise HTTPError(429, retry_after=3600)

    with pytest.raises(HTTPError):
        throttled()
    assert sleeps == []


def test_fault_lost_response_retry_pays_once(impl):
    # The server applies the refund, then the network drops the response twice. The client retries with the same
    # idempotency key; the server-side store returns the stored result, so the customer is paid once.
    server = impl.IdempotencyStore()
    paid, drops = [], [ConnectionError("reset"), ConnectionError("reset")]

    def refund(p):
        paid.append(p["amount"])
        return {"refund_id": len(paid)}

    @impl.retry(sleep=lambda s: None)
    def post_refund():
        result = server.run("refund-A-10", {"order": "A", "amount": 10}, refund)
        if drops:
            raise drops.pop(0)
        return result

    assert post_refund() == {"refund_id": 1} and paid == [10]


def test_fault_each_retry_emits_one_event(impl):
    events = []

    @impl.retry(sleep=lambda s: None, rng=lambda: 1.0,
                on_retry=lambda attempt, delay, exc: events.append((attempt, delay, getattr(exc, "status", None))))
    def op(_state=[HTTPError(503), HTTPError(429, retry_after=2), HTTPError(400)]):
        raise _state.pop(0)

    with pytest.raises(HTTPError):
        op()
    assert events == [(0, 0.5, 503), (1, 2, 429)]  # no event for the non-retryable 400 that ended the loop
