# ex62 · Load test and latency profiling

**Module:** m11 · **Covers:** R27 Performance & latency, R15 Monitoring · **Time:** 50 min

## Learning objectives
- Run a load test and report latency percentiles and errors.
- Use Little's Law to size concurrency for a target load.
- Identify the bottleneck stage from per-stage timings.

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

**Errors:** `littles_law_concurrency` raises `ValueError` for negative inputs; `max_rps` raises `ValueError` unless `avg_latency_s > 0` and `concurrency >= 1`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Load test and latency profiling".
Before I write code, teach me load testing, latency percentiles, throughput, Little's Law, and stage-level
profiling. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex62-load-test/starter.py so that test_load.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `LoadReport`,
`run_load`, `littles_law_concurrency`, `max_rps`, `stage_breakdown`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/m11-deploy-operate/ex62-load-test` and show me the output. If the
README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Load test and latency profiling" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Do failed calls still record latency? Is wall-clock time measured around the whole run?
Is the bottleneck conclusion valid when stages overlap? Rank findings by customer impact, quote the line for each,
and say which ones a test should catch.
```
