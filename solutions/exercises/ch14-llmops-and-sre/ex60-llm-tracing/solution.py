import contextvars
import math
import time
import uuid
from collections import defaultdict
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


_current: contextvars.ContextVar = contextvars.ContextVar("current_span", default=None)


class Tracer:
    def __init__(self, clock=time.perf_counter, id_gen=None):
        self.clock = clock
        self.id_gen = id_gen or (lambda: uuid.uuid4().hex)
        self.finished: list[Span] = []

    @contextmanager
    def span(self, name: str, **attrs):
        parent = _current.get()
        trace_id = parent.trace_id if parent else self.id_gen()
        s = Span(trace_id, self.id_gen(), parent.span_id if parent else None, name, self.clock(), attrs=dict(attrs))
        token = _current.set(s)
        try:
            yield s
            s.status = "ok"
        except BaseException as exc:
            s.status = "error"
            s.attrs["error.type"] = type(exc).__name__
            raise
        finally:
            s.end = self.clock()
            _current.reset(token)
            self.finished.append(s)


class _TracedLLM:
    def __init__(self, llm, tracer, prices):
        self.llm, self.tracer, self.prices = llm, tracer, prices

    def complete(self, messages, **kw):
        with self.tracer.span("llm.complete") as s:
            resp = self.llm.complete(messages, **kw)
            p_in, p_out = self.prices.get(resp.model, (0.0, 0.0))
            s.set("llm.model", resp.model)
            s.set("llm.input_tokens", resp.input_tokens)
            s.set("llm.output_tokens", resp.output_tokens)
            s.set("llm.cost_usd", round(resp.input_tokens * p_in / 1e6 + resp.output_tokens * p_out / 1e6, 6))
            return resp


def traced(llm, tracer: Tracer, prices: dict):
    return _TracedLLM(llm, tracer, prices)


def _pct(vals, p):
    vals = sorted(vals)
    return vals[max(0, math.ceil(p / 100 * len(vals)) - 1)]


def summarize(spans: list[Span]) -> dict:
    groups = defaultdict(list)
    for s in spans:
        if s.name == "llm.complete":
            groups[s.attrs.get("llm.model")].append(s)
    out = {}
    for model, ss in groups.items():
        ms = [(s.end - s.start) * 1000 for s in ss]
        out[model] = {
            "count": len(ss),
            "p50_ms": round(_pct(ms, 50), 1),
            "p95_ms": round(_pct(ms, 95), 1),
            "input_tokens": sum(s.attrs.get("llm.input_tokens", 0) for s in ss),
            "output_tokens": sum(s.attrs.get("llm.output_tokens", 0) for s in ss),
            "cost_usd": round(sum(s.attrs.get("llm.cost_usd", 0) for s in ss), 6),
        }
    return out


def critical_path(spans: list[Span], trace_id: str) -> list[str]:
    in_trace = [s for s in spans if s.trace_id == trace_id]
    node = next(s for s in in_trace if s.parent_id is None)
    path = [node.name]
    while True:
        children = [s for s in in_trace if s.parent_id == node.span_id]
        if not children:
            return path
        node = max(children, key=lambda s: s.end - s.start)
        path.append(node.name)
