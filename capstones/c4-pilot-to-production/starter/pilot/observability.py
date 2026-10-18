"""Prometheus-format metrics and JSON logs (stdlib only)."""
import json
import logging
import threading
import time
from datetime import datetime, timezone

DEFAULT_BUCKETS = (0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)


def _labels(labels: dict) -> str:
    raise NotImplementedError


class Counter:
    def __init__(self, name, help_text):
        self.name, self.help, self.values = name, help_text, {}

    def inc(self, labels: dict | None = None, value: float = 1.0):
        raise NotImplementedError

    def get(self, labels: dict | None = None) -> float:
        raise NotImplementedError

    def render(self) -> list[str]:
        raise NotImplementedError


class Histogram:
    def __init__(self, name, help_text, buckets=DEFAULT_BUCKETS):
        self.name, self.help, self.buckets = name, help_text, tuple(buckets)
        self.series: dict = {}

    def observe(self, value: float, labels: dict | None = None):
        raise NotImplementedError

    def render(self) -> list[str]:
        raise NotImplementedError


class Metrics:
    def __init__(self):
        self._m: dict[str, object] = {}
        self._lock = threading.Lock()

    def counter(self, name, help_text="") -> Counter:
        raise NotImplementedError

    def histogram(self, name, help_text="", buckets=DEFAULT_BUCKETS) -> Histogram:
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        raise NotImplementedError


def json_logger(name: str, stream) -> logging.Logger:
    raise NotImplementedError
