# ex62 · Load test and latency profiling

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R27 Performance & latency, R15 Monitoring

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex62-load-test`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex62-load-test`: all 5 pass.
- **Tests:** `test_load.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** A closed-model generator (a fixed pool of workers) against a local function: it finds
  capacity but hides queueing delay, and Little's Law uses averages, not tails. For user-facing percentiles, use an
  open-model tool with scheduled arrivals, realistic prompts and bursts, plus a budgeted run against the real model
  and quota in the customer's tenant.

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
Implement exercises/ch14-llmops-and-sre/ex62-load-test/starter.py so that test_load.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `LoadReport`,
`run_load`, `littles_law_concurrency`, `max_rps`, `stage_breakdown`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex62-load-test` and show me the output. If the
README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Load test and latency profiling" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Do failed calls still record latency? Is wall-clock time measured around the whole run?
Is the bottleneck conclusion valid when stages overlap? Rank findings by customer impact, quote the line for each,
and say which ones a test should catch.
```
