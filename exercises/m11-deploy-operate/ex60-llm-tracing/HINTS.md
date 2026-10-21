# ex60 hints · Tracing and metrics for LLM calls

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Use one module-level `ContextVar` holding the current span (default `None`). Write `span()` as a
`@contextlib.contextmanager`: read the parent, create the new span (same trace id as the parent, or a fresh one for a
root), set it as current, yield it, then restore the parent.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- In `span()`, put `yield` inside `try/except/finally`:
  - on success, set the status to `"ok"`;
  - in `except`, set `"error"`, record `error.type`, and re-raise;
  - in `finally`, set `end`, reset the context variable, and append the span to `finished`.

  Appending in `finally` is what makes children finish before their parents.
- `traced` returns a small wrapper object whose `complete` opens an `llm.complete` span, calls the real client, and
  sets the four attributes from the response.
- `critical_path`: find the root (no parent) in the trace, then repeatedly move to the child with the longest
  duration.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Call `id_gen()` for the trace id *before* the span id on a root span. The tests use a counter, so the order is
  visible.
- Pass `**attrs` into the span as a **copy** (`dict(attrs)`), so `s.set(...)` doesn't change a dict the caller owns.
- Read the model name from the **response** for `llm.model`, and price it from the response's token counts.
- `summarize` converts durations to milliseconds before taking nearest-rank percentiles, then rounds to 1 dp.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_nesting_and_errors` | Spans appended when they start instead of when they end; parent not restored; error status not set before re-raising |
| `test_traced_llm_and_summary` | Cost not rounded or computed from the wrong model; percentile interpolated; durations left in seconds |
| `test_critical_path` | Following the first child instead of the longest; spans from other traces included |
