# ex62 · Load test and latency profiling

**Module:** m11 · **Covers:** R27 Performance & latency, R15 Monitoring · **Time:** 50 min

## Scenario
Go-live is Monday with 400 agents. Will the service hold? You'll write a small load generator, then use Little's
Law and per-stage timings to explain capacity to the customer's platform team in numbers.

## Your task
1. `run_load(fn, total, concurrency) -> LoadReport` — call `fn()` `total` times using a thread pool of
   `concurrency` workers. Record per-call latency (ms, `time.perf_counter`) and count exceptions as errors (errors
   still record latency). Report: `count`, `errors`, `error_rate` (4 dp), `rps` (count / wall seconds, 1 dp),
   `p50`, `p95`, `p99`, `max` (ms, nearest-rank, 1 dp).
2. `littles_law_concurrency(target_rps, avg_latency_s) -> int` — `ceil(target_rps * avg_latency_s)`.
3. `max_rps(concurrency, avg_latency_s) -> float` — `concurrency / avg_latency_s`, 1 dp.
4. `stage_breakdown(traces) -> list[(stage, share)]` — `traces` is a list of `{stage: ms}` dicts; return each
   stage's share of total time across all traces (3 dp), sorted by share desc. The first item is your bottleneck.
