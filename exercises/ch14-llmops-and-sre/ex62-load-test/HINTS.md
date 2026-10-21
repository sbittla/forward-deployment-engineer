# ex62 hints · Load test and latency profiling

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write a helper that times **one** call: start `time.perf_counter()`, call `fn()` inside `try/except`, and return
`(latency_ms, ok)`. Then `run_load` maps that helper over `range(total)` with a
`concurrent.futures.ThreadPoolExecutor(max_workers=concurrency)`, timing the whole run for the RPS figure.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Sort the latencies once, then take nearest-rank percentiles (`sorted[ceil(p/100 * n) - 1]`) and the maximum.
- Errors still have a latency. A failing call took time too, and leaving it out flatters your p99.
- **Little's Law:** concurrency = arrival rate × time in the system.
- **stage_breakdown:** total each stage across all traces, divide by the grand total, and sort by share descending.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `50 * 2.4` in floating point is `120.00000000000001`, and `ceil` turns that into 121. Round the product (to around
  9 dp) before taking the ceiling.
- Validate inputs. `max_rps` needs `avg_latency_s > 0` and `concurrency >= 1`, and Little's Law rejects negative
  inputs (zero is fine).
- `stage_breakdown([])` returns `[]`: guard the division by the grand total.
- The pool must actually run `concurrency` calls at once. Don't submit and wait one call at a time.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_run_load` | Failed calls dropped from the latencies; RPS computed from the sum of latencies instead of wall time |
| `test_concurrency_actually_used` | Calls run one after another (waiting on each future in turn) |
| `test_littles_law` | Floating-point error makes `ceil` return 121 |
| `test_stage_breakdown` | Shares computed per trace instead of over the totals; not sorted descending |
| `test_invalid_capacity_inputs` | Validation missing; empty traces divide by zero |
| `test_report_states_load_model` | Think time not applied between a worker's calls, or counted in latency; label not validated |
