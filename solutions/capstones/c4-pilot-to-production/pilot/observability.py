"""Prometheus-format metrics and JSON logs (stdlib only)."""
import json
import logging
import threading
import time
from datetime import datetime, timezone

DEFAULT_BUCKETS = (0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)


def _labels(labels: dict) -> str:
    if not labels:
        return ""
    inner = ",".join(f'{k}="{str(v)}"' for k, v in sorted(labels.items()))
    return "{" + inner + "}"


class Counter:
    def __init__(self, name, help_text):
        self.name, self.help, self.values = name, help_text, {}

    def inc(self, labels: dict | None = None, value: float = 1.0):
        key = tuple(sorted((labels or {}).items()))
        self.values[key] = self.values.get(key, 0.0) + value

    def get(self, labels: dict | None = None) -> float:
        return self.values.get(tuple(sorted((labels or {}).items())), 0.0)

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} counter"]
        lines += [f"{self.name}{_labels(dict(k))} {v:g}" for k, v in sorted(self.values.items())]
        return lines


class Histogram:
    def __init__(self, name, help_text, buckets=DEFAULT_BUCKETS):
        self.name, self.help, self.buckets = name, help_text, tuple(buckets)
        self.series: dict = {}

    def observe(self, value: float, labels: dict | None = None):
        key = tuple(sorted((labels or {}).items()))
        s = self.series.setdefault(key, {"counts": [0] * len(self.buckets), "sum": 0.0, "count": 0})
        for i, b in enumerate(self.buckets):
            if value <= b:
                s["counts"][i] += 1
        s["sum"] += value
        s["count"] += 1

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} histogram"]
        for key, s in sorted(self.series.items()):
            base = dict(key)
            for b, c in zip(self.buckets, s["counts"]):
                lines.append(f"{self.name}_bucket{_labels({**base, 'le': f'{b:g}'})} {c}")
            lines.append(f"{self.name}_bucket{_labels({**base, 'le': '+Inf'})} {s['count']}")
            lines.append(f"{self.name}_sum{_labels(base)} {s['sum']:.6g}")
            lines.append(f"{self.name}_count{_labels(base)} {s['count']}")
        return lines


class Metrics:
    def __init__(self):
        self._m: dict[str, object] = {}
        self._lock = threading.Lock()

    def counter(self, name, help_text="") -> Counter:
        with self._lock:
            return self._m.setdefault(name, Counter(name, help_text))

    def histogram(self, name, help_text="", buckets=DEFAULT_BUCKETS) -> Histogram:
        with self._lock:
            return self._m.setdefault(name, Histogram(name, help_text, buckets))

    def render(self) -> str:
        lines = []
        for name in sorted(self._m):
            lines += self._m[name].render()
        return "\n".join(lines) + "\n"


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        out = {"ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(), "level": record.levelname,
               "msg": record.getMessage()}
        out.update(getattr(record, "fields", {}) or {})
        return json.dumps(out, default=str)


def json_logger(name: str, stream) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.propagate = False
    for h in list(log.handlers):
        log.removeHandler(h)
    h = logging.StreamHandler(stream)
    h.setFormatter(_JsonFormatter())
    log.addHandler(h)
    return log
