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
        self._failures = 0
        self._opened_at: float | None = None
        self._trial_in_flight = False
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        if self._opened_at is None:
            return "closed"
        if self.clock() - self._opened_at >= self.reset_timeout:
            return "half_open"
        return "open"

    def _trip(self):
        self._opened_at = self.clock()

    def call(self, fn, *args, **kwargs):
        with self._lock:
            state = self.state
            if state == "open" or (state == "half_open" and self._trial_in_flight):
                raise CircuitOpenError("circuit open; failing fast")
            if state == "half_open":
                self._trial_in_flight = True
        try:
            result = fn(*args, **kwargs)
        except Exception:
            with self._lock:
                self._trial_in_flight = False
                if state == "half_open":
                    self._trip()
                else:
                    self._failures += 1
                    if self._failures >= self.failure_threshold:
                        self._trip()
            raise
        with self._lock:
            self._trial_in_flight = False
            self._failures = 0
            self._opened_at = None
        return result


class Bulkhead:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self._sem = threading.BoundedSemaphore(max_concurrent)

    def __enter__(self):
        if not self._sem.acquire(blocking=False):
            raise BulkheadFull(f"more than {self.max_concurrent} concurrent callers")
        return self

    def __exit__(self, *exc):
        self._sem.release()
        return False
