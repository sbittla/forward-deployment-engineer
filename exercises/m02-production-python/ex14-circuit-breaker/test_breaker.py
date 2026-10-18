import threading
import time

import pytest


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def boom():
    raise ConnectionError("down")


def test_opens_after_threshold(impl):
    clk = Clock()
    cb = impl.CircuitBreaker(failure_threshold=3, reset_timeout=10, clock=clk)
    for _ in range(3):
        with pytest.raises(ConnectionError):
            cb.call(boom)
    assert cb.state == "open"
    calls = []
    with pytest.raises(impl.CircuitOpenError):
        cb.call(lambda: calls.append(1))
    assert calls == []


def test_success_resets_counter(impl):
    cb = impl.CircuitBreaker(failure_threshold=2, clock=Clock())
    with pytest.raises(ConnectionError):
        cb.call(boom)
    assert cb.call(lambda: "ok") == "ok"
    with pytest.raises(ConnectionError):
        cb.call(boom)
    assert cb.state == "closed"


def test_half_open_success_closes(impl):
    clk = Clock()
    cb = impl.CircuitBreaker(failure_threshold=1, reset_timeout=10, clock=clk)
    with pytest.raises(ConnectionError):
        cb.call(boom)
    clk.t = 9.9
    assert cb.state == "open"
    clk.t = 10.0
    assert cb.state == "half_open"
    assert cb.call(lambda x: x + 1, 1) == 2
    assert cb.state == "closed"


def test_half_open_failure_reopens_and_restarts_timer(impl):
    clk = Clock()
    cb = impl.CircuitBreaker(failure_threshold=1, reset_timeout=10, clock=clk)
    with pytest.raises(ConnectionError):
        cb.call(boom)
    clk.t = 15
    with pytest.raises(ConnectionError):
        cb.call(boom)
    assert cb.state == "open"
    clk.t = 24
    assert cb.state == "open"
    clk.t = 25
    assert cb.state == "half_open"


def test_bulkhead(impl):
    bh = impl.Bulkhead(2)
    with bh:
        with bh:
            with pytest.raises(impl.BulkheadFull):
                with bh:
                    pass
        with bh:  # slot freed
            pass


def test_bulkhead_threads(impl):
    bh = impl.Bulkhead(3)
    gate = threading.Event()
    results = []

    def worker():
        try:
            with bh:
                results.append("in")
                gate.wait(1)
        except impl.BulkheadFull:
            results.append("full")
        except Exception as exc:  # e.g. NotImplementedError from an unfinished starter
            results.append(type(exc).__name__)

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(6)]
    for t in ts:
        t.start()
    deadline = time.monotonic() + 2
    while results.count("full") + len([r for r in results if r not in ("in", "full")]) < 3 \
            and time.monotonic() < deadline:
        time.sleep(0.005)
    gate.set()
    for t in ts:
        t.join()
    assert results.count("in") == 3 and results.count("full") == 3
