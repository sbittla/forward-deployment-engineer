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


# Fault injection: hung calls, partial failures and cancellation in the middle of a batch

def test_fault_hung_calls_time_out_and_free_their_slots(impl):
    # Two of eight calls hang forever. Each factory bounds its call with asyncio.timeout(); the TimeoutError lands in
    # that slot, the semaphore slot is released, and the batch finishes well inside its deadline.
    hang = {1, 4}

    def factory(i):
        async def call():
            async with asyncio.timeout(0.05):
                if i in hang:
                    await asyncio.Event().wait()  # never set: a dependency that never answers
                await asyncio.sleep(0.005)
                return i
        return call

    async def main():
        t0 = time.monotonic()
        res = await asyncio.wait_for(impl.gather_limited([factory(i) for i in range(8)], concurrency=2), timeout=2)
        return res, time.monotonic() - t0

    res, elapsed = asyncio.run(main())
    assert [isinstance(r, TimeoutError) for r in res] == [i in hang for i in range(8)]
    assert [r for r in res if not isinstance(r, Exception)] == [0, 2, 3, 5, 6, 7]
    assert elapsed < 1.0


def test_fault_partial_failures_isolated_under_rate_limit(impl):
    # A seeded 25% of 40 calls fail; every other slot still holds its own result, in order.
    import random
    rng = random.Random(3)
    failing = {i for i in range(40) if rng.random() < 0.25}
    bucket = impl.TokenBucket(rate=1000, capacity=10)

    def factory(i):
        async def call():
            if i in failing:
                raise ConnectionError(f"item {i}")
            return i
        return call

    res = asyncio.run(impl.gather_limited([factory(i) for i in range(40)], concurrency=5, bucket=bucket))
    assert {i for i, r in enumerate(res) if isinstance(r, ConnectionError)} == failing
    assert all(r == i for i, r in enumerate(res) if i not in failing)
    assert 0 < len(failing) < 40


def test_fault_cancel_midflight_cleans_up_every_started_call(impl):
    # Canceling the batch mid-flight must reach every in-flight call (its finally runs) and start no new ones.
    started, cleaned = [], []

    def factory(i):
        async def call():
            started.append(i)
            try:
                await asyncio.sleep(10)
            finally:
                cleaned.append(i)
        return call

    async def main():
        task = asyncio.create_task(impl.gather_limited([factory(i) for i in range(10)], concurrency=3))
        for _ in range(100):
            if len(started) == 3:
                break
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(asyncio.wait_for(main(), timeout=5))
    assert len(started) == 3 and sorted(cleaned) == sorted(started)
