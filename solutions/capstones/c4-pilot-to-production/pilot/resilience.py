"""Retries with backoff, a circuit breaker and model fallback around any LLM client."""
import random
import threading
import time

RETRYABLE = {408, 429, 500, 502, 503, 504, 529}
OVERLOADED = {503, 529}


class CircuitOpen(Exception):
    pass


def _status(exc) -> int | None:
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return 503
    return getattr(exc, "status", None)


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
        if self._opened_at is None:
            return "closed"
        return "half_open" if self.clock() - self._opened_at >= self.reset_timeout else "open"

    def _count(self, outcome: str):
        if self.metrics:
            self.metrics.counter("pilot_llm_calls_total", "LLM calls by outcome").inc({"outcome": outcome})

    def _call_with_retries(self, client, model, messages, kw):
        for attempt in range(self.max_retries + 1):
            try:
                return client.complete(messages, model=model, **kw)
            except Exception as exc:
                status = _status(exc)
                if status not in RETRYABLE or attempt == self.max_retries:
                    raise
                self._count(f"retry_{status}")
                ra = getattr(exc, "retry_after", None)
                self.sleep(ra if isinstance(ra, (int, float)) else
                           self.rng() * min(self.max_delay, self.base_delay * 2 ** attempt))

    def complete(self, messages, **kw):
        with self._lock:
            if self.breaker_state == "open":
                self._count("short_circuit")
                raise CircuitOpen("LLM circuit is open")
        try:
            resp = self._call_with_retries(self.primary, self.model, messages, kw)
        except Exception as exc:
            if self.fallback is not None and _status(exc) in OVERLOADED:
                try:
                    resp = self.fallback.complete(messages, model=self.fallback_model, **kw)
                    self._count("fallback_ok")
                    self._record(True)
                    return resp
                except Exception:
                    pass
            self._count("failed")
            self._record(False)
            raise
        self._count("ok")
        self._record(True)
        return resp

    def _record(self, ok: bool):
        with self._lock:
            if ok:
                self._failures, self._opened_at = 0, None
            else:
                self._failures += 1
                if self._failures >= self.breaker_threshold or self.breaker_state == "half_open":
                    self._opened_at = self.clock()
