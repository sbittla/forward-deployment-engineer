import asyncio
import time


class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity

    async def acquire(self) -> None:
        raise NotImplementedError


async def gather_limited(factories, concurrency: int, bucket: TokenBucket | None = None) -> list:
    raise NotImplementedError
