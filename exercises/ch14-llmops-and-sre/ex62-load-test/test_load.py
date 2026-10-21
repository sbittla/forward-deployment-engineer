import pytest
import itertools
import threading
import time


def test_run_load(impl):
    counter = itertools.count()
    lock = threading.Lock()

    def fn():
        with lock:
            n = next(counter)
        time.sleep(0.02)
        if n % 10 == 0:
            raise RuntimeError("503")

    rep = impl.run_load(fn, total=40, concurrency=8)
    assert rep.count == 40 and rep.errors == 4 and rep.error_rate == 0.1
    assert 18 <= rep.p50 <= 80 and rep.p50 <= rep.p95 <= rep.p99 <= rep.max
    # 40 calls * 20ms / 8 workers ~ 0.1s -> ~400 rps (allow wide margin for CI machines)
    assert 100 < rep.rps < 450


def test_concurrency_actually_used(impl):
    active = {"now": 0, "peak": 0}
    lock = threading.Lock()

    def fn():
        with lock:
            active["now"] += 1
            active["peak"] = max(active["peak"], active["now"])
        time.sleep(0.02)
        with lock:
            active["now"] -= 1

    impl.run_load(fn, total=20, concurrency=5)
    assert active["peak"] == 5


def test_littles_law(impl):
    assert impl.littles_law_concurrency(50, 2.4) == 120
    assert impl.littles_law_concurrency(10, 0.25) == 3
    assert impl.max_rps(64, 2.0) == 32.0


def test_stage_breakdown(impl):
    traces = [{"retrieve": 120, "llm": 1800, "post": 30}, {"retrieve": 80, "llm": 2200, "post": 20}]
    out = impl.stage_breakdown(traces)
    assert out[0] == ("llm", round(4000 / 4250, 3))
    assert [s for s, _ in out] == ["llm", "retrieve", "post"]


def test_invalid_capacity_inputs(impl):
    with pytest.raises(ValueError):
        impl.max_rps(4, 0)
    with pytest.raises(ValueError):
        impl.max_rps(0, 0.5)
    with pytest.raises(ValueError):
        impl.littles_law_concurrency(-1, 0.5)
    assert impl.littles_law_concurrency(0, 1.0) == 0 and impl.stage_breakdown([]) == []
