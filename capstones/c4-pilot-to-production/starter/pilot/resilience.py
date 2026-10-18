"""Retries with backoff, a circuit breaker and model fallback around any LLM client."""
import random
import threading
import time

RETRYABLE = {408, 429, 500, 502, 503, 504, 529}
OVERLOADED = {503, 529}


class CircuitOpen(Exception):
    pass


def _status(exc) -> int | None:
    raise NotImplementedError


class ResilientLLM:
    def __init__(self, primary, fallback=None, model: str | None = None, fallback_model: str | None = None,
                 max_retries: int = 2, base_delay: float = 0.5, max_delay: float = 8.0,
                 breaker_threshold: int = 5, reset_timeout: float = 30.0,
                 sleep=time.sleep, clock=time.monotonic, rng=random.random, metrics=None):
        self.primary, self.fallback = primary, fallback
        self.model, self.fallback_model = model, fallback_model
        self.max_retries, self.base_delay, self.max_delay = max_retries, base_delay, max_delay
        self.breaker_threshold, self.reset_timeout = breaker_threshold, reset_timeout
        self.sleep, self.clock, self.rng, self.metrics = sleep, clock, rng, metrics
        self._failures, self._opened_at, self._lock = 0, None, threading.Lock()

    @property
    def breaker_state(self) -> str:
        raise NotImplementedError

    def _count(self, outcome: str):
        raise NotImplementedError

    def _call_with_retries(self, client, model, messages, kw):
        raise NotImplementedError

    def complete(self, messages, **kw):
        raise NotImplementedError

    def _record(self, ok: bool):
        raise NotImplementedError
