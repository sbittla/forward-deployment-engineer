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


# Fault injection: an outage, a recovery and concurrent callers during the half-open trial

def test_fault_outage_load_on_dependency_is_bounded(impl):
    # The dependency is down from t=0 to t=60 and callers arrive once a second for 100 s. Without a breaker it
    # would take 60 failing calls; with one, it sees the threshold plus one trial per reset timeout.
    clk = Clock()
    cb = impl.CircuitBreaker(failure_threshold=3, reset_timeout=10, clock=clk)
    hits = []

    def dependency():
        hits.append(clk.t)
        if clk.t < 60:
            raise ConnectionError("down")
        return "ok"

    outcomes = []
    for second in range(100):
        clk.t = float(second)
        try:
            outcomes.append(cb.call(dependency))
        except impl.CircuitOpenError:
            outcomes.append("fast-fail")
        except ConnectionError:
            outcomes.append("error")
    during_outage = [t for t in hits if t < 60]
    assert len(during_outage) <= 3 + 60 // 10
    assert outcomes.count("fast-fail") >= 50
    assert cb.state == "closed" and outcomes[-30:] == ["ok"] * 30


def test_fault_half_open_admits_one_trial_under_concurrency(impl):
    # While the single trial call hangs, every other caller fails fast instead of piling onto the dependency.
    clk = Clock()
    cb = impl.CircuitBreaker(failure_threshold=1, reset_timeout=10, clock=clk)
    with pytest.raises(ConnectionError):
        cb.call(boom)
    clk.t = 10
    gate, entered, trial_calls = threading.Event(), threading.Event(), []

    def slow_trial():
        trial_calls.append(1)
        entered.set()
        gate.wait(2)
        return "ok"

    results = []
    trial = threading.Thread(target=lambda: results.append(cb.call(slow_trial)), daemon=True)
    trial.start()
    assert entered.wait(2)
    rejected = 0
    for _ in range(5):
        try:
            cb.call(slow_trial)
        except impl.CircuitOpenError:
            rejected += 1
        except Exception:
            pass
    gate.set()
    trial.join(2)
    assert rejected == 5 and trial_calls == [1] and results == ["ok"] and cb.state == "closed"
