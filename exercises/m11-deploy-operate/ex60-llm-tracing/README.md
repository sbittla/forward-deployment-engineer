# ex60 · Tracing and metrics for LLM calls

**Module:** m11 · **Covers:** R15 Observability, R27 Cost & latency · **Time:** 50 min

## Scenario
"Why was that answer slow?" Without traces you can't tell whether retrieval, the model, or a tool call was the
culprit. Implement a minimal OpenTelemetry-style tracer so every request is a tree of timed spans with token and
cost attributes. (In production you'd use the OpenTelemetry SDK and an exporter; the concepts are identical.)

## Your task
1. `Tracer(clock=time.perf_counter, id_gen=None)`:
   - `with tracer.span(name, **attrs) as s:` — creates a `Span(trace_id, span_id, parent_id, name, start, end,
     attrs, status)`; nested spans get the enclosing span as parent and share its `trace_id`; a root span starts a
     new trace. `s.set(key, value)` adds attributes. If the block raises, `status = "error"` and
     `attrs["error.type"]` = exception class name, then re-raise; otherwise `status = "ok"`.
   - `tracer.finished` — list of spans in the order they ended. Use `contextvars` for the current span.
   - Ids: `id_gen()` returns hex strings; default `uuid4().hex`.
2. `traced(llm, tracer, prices)` — wraps an LLM client so `complete(...)` runs inside a span `"llm.complete"` with
   attrs `llm.model`, `llm.input_tokens`, `llm.output_tokens`, `llm.cost_usd` (rounded to 6 dp, from
   `prices[model] = (in_per_mtok, out_per_mtok)`).
3. `summarize(spans) -> dict` — for spans named `llm.complete`, grouped by `llm.model`: `count`, `p50_ms`, `p95_ms`
   (nearest-rank on `(end-start)*1000`, rounded to 1 dp), `input_tokens`, `output_tokens`, `cost_usd` (6 dp).
4. `critical_path(spans, trace_id) -> list[str]` — from the root, repeatedly follow the longest-duration child;
   return the span names.
