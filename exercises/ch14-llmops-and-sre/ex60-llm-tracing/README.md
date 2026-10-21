# ex60 · Tracing and metrics for LLM calls

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R15 Observability, R27 Cost & latency

## Learning objectives
- Trace requests as span trees with timing, tokens and cost.
- Summarise latency percentiles and spend by model.
- Find the critical path that explains a slow answer.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex60-llm-tracing`.
- **Expected output:** all 3 tests fail against the starter; when you're done, all 3 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex60-llm-tracing`: all 3 pass.
- **Tests:** `test_tracing.py` (3 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** An in-process tracer with no sampling, export or propagation between processes, pricing
  tokens from a table you supply. In production, use the OpenTelemetry SDK with its generative-AI conventions,
  context propagation over HTTP, sampling and a current price list.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Tracing and metrics for LLM calls".
Before I write code, teach me distributed tracing concepts (traces, spans, parent ids, attributes, status) and how
OpenTelemetry applies to LLM calls. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch14-llmops-and-sre/ex60-llm-tracing/starter.py so that test_tracing.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Span`, `Tracer`,
`traced`, `summarize`, `critical_path`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch14-llmops-and-sre/ex60-llm-tracing` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Tracing and metrics for LLM calls" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Do nested spans across threads keep the right parent? Is error status set before
re-raising? Is the critical path computed from durations, not end times? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
