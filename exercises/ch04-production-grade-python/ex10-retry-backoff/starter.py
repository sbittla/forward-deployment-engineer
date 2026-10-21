import random
import time

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


def retry(max_attempts=4, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rng=random.random,
          deadline=None, clock=time.monotonic, on_retry=None, attempt_timeout=None):
    raise NotImplementedError


class IdempotencyConflict(Exception):
    pass


class IdempotencyStore:
    def run(self, key: str, payload: dict, fn):
        raise NotImplementedError
