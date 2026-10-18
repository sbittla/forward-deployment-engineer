import contextvars
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    start: float
    end: float | None = None
    attrs: dict = field(default_factory=dict)
    status: str = "unset"

    def set(self, key, value):
        self.attrs[key] = value


class Tracer:
    def __init__(self, clock=time.perf_counter, id_gen=None):
        self.clock = clock
        self.id_gen = id_gen or (lambda: uuid.uuid4().hex)
        self.finished: list[Span] = []

    @contextmanager
    def span(self, name: str, **attrs):
        raise NotImplementedError
        yield


def traced(llm, tracer: Tracer, prices: dict):
    raise NotImplementedError


def summarize(spans: list[Span]) -> dict:
    raise NotImplementedError


def critical_path(spans: list[Span], trace_id: str) -> list[str]:
    raise NotImplementedError
