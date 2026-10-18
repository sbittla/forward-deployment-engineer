import threading
import time


class CircuitOpenError(Exception):
    pass


class BulkheadFull(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=30.0, clock=time.monotonic):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.clock = clock

    @property
    def state(self) -> str:
        raise NotImplementedError

    def call(self, fn, *args, **kwargs):
        raise NotImplementedError


class Bulkhead:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc):
        raise NotImplementedError
