import functools
import hashlib
import json
import random
import time

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    return getattr(exc, "status", None) in RETRYABLE_STATUS


def retry(max_attempts=4, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rng=random.random,
          deadline=None, clock=time.monotonic, on_retry=None):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            stop_at = None if deadline is None else clock() + deadline   # set once, before the first attempt
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    if not _retryable(exc) or attempt == max_attempts - 1:
                        raise
                    ra = getattr(exc, "retry_after", None)
                    if isinstance(ra, (int, float)):
                        delay = ra
                    else:
                        delay = rng() * min(max_delay, base_delay * 2 ** attempt)
                    if stop_at is not None and clock() + delay >= stop_at:
                        raise                                # fail now, not after the sleep
                    if on_retry is not None:
                        on_retry(attempt, delay, exc)
                    sleep(delay)
        return wrapper
    return deco


class IdempotencyConflict(Exception):
    pass


def _digest(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


class IdempotencyStore:
    def __init__(self):
        self._done: dict[str, tuple[str, object]] = {}

    def run(self, key: str, payload: dict, fn):
        h = _digest(payload)
        if key in self._done:
            stored_hash, result = self._done[key]
            if stored_hash != h:
                raise IdempotencyConflict(f"key {key!r} reused with a different payload")
            return result
        result = fn(payload)
        self._done[key] = (h, result)
        return result
