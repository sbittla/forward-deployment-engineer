import itertools

import pytest

from fde_kit import FakeLLM, LLMResponse


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def ids():
    c = itertools.count(1)
    return lambda: f"id{next(c)}"


def test_nesting_and_errors(impl):
    clk = Clock()
    tr = impl.Tracer(clock=clk, id_gen=ids())
    with tr.span("request", route="/answer") as root:
        clk.t = 0.1
        with tr.span("retrieve") as r:
            clk.t = 0.3
        with pytest.raises(ValueError):
            with tr.span("tool.lookup"):
                clk.t = 0.4
                raise ValueError("bad")
        root.set("user", "u1")
        clk.t = 1.0
    names = [s.name for s in tr.finished]
    assert names == ["retrieve", "tool.lookup", "request"]
    req = tr.finished[-1]
    assert req.parent_id is None and req.attrs == {"route": "/answer", "user": "u1"} and req.status == "ok"
    assert all(s.trace_id == req.trace_id for s in tr.finished)
    assert tr.finished[0].parent_id == req.span_id
    err = tr.finished[1]
    assert err.status == "error" and err.attrs["error.type"] == "ValueError"
    assert (tr.finished[0].start, tr.finished[0].end) == (0.1, 0.3)
    with tr.span("second"):
        pass
    assert tr.finished[-1].trace_id != req.trace_id and tr.finished[-1].parent_id is None


def test_traced_llm_and_summary(impl):
    clk = Clock()
    tr = impl.Tracer(clock=clk, id_gen=ids())
    durations = iter([0.2, 0.4, 1.0, 0.1])

    def respond(m, s, t):
        clk.t += next(durations)
        return LLMResponse(text="ok", input_tokens=1000, output_tokens=100)

    llm = impl.traced(FakeLLM(respond), tr, {"claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.1, 0.5)})
    for model in ["claude-sonnet-5-5"] * 3 + ["claude-haiku-5-5"]:
        assert llm.complete([{"role": "user", "content": "q"}], model=model).text == "ok"
    span = tr.finished[0]
    assert span.name == "llm.complete" and span.attrs["llm.model"] == "claude-sonnet-5-5"
    assert span.attrs["llm.cost_usd"] == pytest.approx(0.003)
    s = impl.summarize(tr.finished)
    assert s["claude-sonnet-5-5"] == {"count": 3, "p50_ms": 400.0, "p95_ms": 1000.0, "input_tokens": 3000,
                                      "output_tokens": 300, "cost_usd": 0.009}
    assert s["claude-haiku-5-5"]["count"] == 1


def test_critical_path(impl):
    clk = Clock()
    tr = impl.Tracer(clock=clk, id_gen=ids())
    with tr.span("request"):
        with tr.span("retrieve"):
            clk.t += 0.2
        with tr.span("generate"):
            with tr.span("llm.complete"):
                clk.t += 0.9
            with tr.span("postprocess"):
                clk.t += 0.05
    root = tr.finished[-1]
    assert impl.critical_path(tr.finished, root.trace_id) == ["request", "generate", "llm.complete"]
