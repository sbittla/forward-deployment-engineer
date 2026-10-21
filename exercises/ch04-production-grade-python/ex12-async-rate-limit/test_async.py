import pytest
import asyncio
import time


def test_order_and_concurrency_bound(impl):
    active = {"now": 0, "peak": 0}

    def factory(i):
        async def job():
            active["now"] += 1
            active["peak"] = max(active["peak"], active["now"])
            await asyncio.sleep(0.01 * (5 - i % 5))
            active["now"] -= 1
            return i * i
        return job

    res = asyncio.run(impl.gather_limited([factory(i) for i in range(20)], concurrency=4))
    assert res == [i * i for i in range(20)]
    assert active["peak"] == 4


def test_exceptions_in_slot(impl):
    async def ok():
        return "ok"

    async def bad():
        raise ValueError("bad row")

    res = asyncio.run(impl.gather_limited([lambda: ok(), lambda: bad(), lambda: ok()], concurrency=2))
    assert res[0] == "ok" and isinstance(res[1], ValueError) and res[2] == "ok"


def test_bucket_limits_rate(impl):
    bucket = impl.TokenBucket(rate=50, capacity=2)

    async def noop():
        return time.monotonic()

    t0 = time.monotonic()
    stamps = asyncio.run(impl.gather_limited([lambda: noop() for _ in range(12)], concurrency=12, bucket=bucket))
    elapsed = time.monotonic() - t0
    # 2 immediate + 10 more at 50/s => >= ~0.2 s
    assert elapsed >= 0.18
    assert elapsed < 1.5


def test_bucket_starts_full(impl):
    bucket = impl.TokenBucket(rate=1, capacity=3)

    async def take3():
        t0 = time.monotonic()
        for _ in range(3):
            await bucket.acquire()
        return time.monotonic() - t0

    assert asyncio.run(take3()) < 0.05


def test_invalid_limits(impl):
    with pytest.raises(ValueError):
        impl.TokenBucket(0, 5)
    with pytest.raises(ValueError):
        impl.TokenBucket(1.0, 0)
    with pytest.raises(ValueError):
        asyncio.run(impl.gather_limited([lambda: asyncio.sleep(0)], 0))
    assert asyncio.run(impl.gather_limited([], 3)) == []


def test_boundary_cancellation_propagates(impl):
    # Cancellation is not an item failure: CancelledError must propagate, never be
    # stored in a result slot (catch Exception, not BaseException).
    started = []

    def slow():
        async def job():
            started.append(1)
            await asyncio.sleep(10)
        return job()

    async def ok():
        return "ok"

    async def cancelled():
        raise asyncio.CancelledError()

    async def main():
        with pytest.raises(asyncio.CancelledError):
            await impl.gather_limited([ok, cancelled, ok], concurrency=3)
        task = asyncio.create_task(impl.gather_limited([slow] * 3, concurrency=3))
        for _ in range(100):
            if len(started) == 3:
                break
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        return task.cancelled()

    assert asyncio.run(asyncio.wait_for(main(), timeout=5))
