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
