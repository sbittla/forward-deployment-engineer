import asyncio
import time


class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        if rate <= 0 or capacity < 1:
            raise ValueError("rate must be > 0 and capacity >= 1")
        self.rate = rate
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self):
        now = time.monotonic()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now

    async def acquire(self) -> None:
        async with self._lock:  # serialise waiters so tokens are handed out fairly
            while True:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                await asyncio.sleep((1 - self._tokens) / self.rate)


async def gather_limited(factories, concurrency: int, bucket: TokenBucket | None = None) -> list:
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")
    sem = asyncio.Semaphore(concurrency)
    results: list = [None] * len(factories)

    async def run(i, factory):
        async with sem:
            if bucket is not None:
                await bucket.acquire()
            try:
                results[i] = await factory()
            except Exception as exc:  # keep going; caller inspects the slot
                results[i] = exc

    await asyncio.gather(*(run(i, f) for i, f in enumerate(factories)))
    return results
