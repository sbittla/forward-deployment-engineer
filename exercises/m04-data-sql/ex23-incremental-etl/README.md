# ex23 · Incremental ETL with watermarks and upserts

**Module:** m04 · **Covers:** R04 Data pipelines, R03 SQL · **Time:** 60 min

## Learning objectives
- Load data incrementally with a composite watermark that is correct under ties.
- Make each batch atomic: data and watermark commit together or not at all.
- Keep the job idempotent so re-runs are safe.

## Scenario
Nightly full reloads of the customer's 80M-row orders table take 6 hours and lock their replica. Move to an
incremental load that is **idempotent** (safe to re-run), **atomic** (a crash leaves no half-loaded batch) and
**correct under timestamp ties** (many rows share the same `updated_at` second).

## Your task
`run_incremental(src, dst, job="orders", batch_size=1000) -> int`

- Source: `src_orders(id INTEGER, customer TEXT, amount REAL, updated_at TEXT)`.
- Destination tables (create if missing): `dw_orders(id INTEGER PRIMARY KEY, customer TEXT, amount REAL NOT NULL,
  updated_at TEXT)` and `etl_state(job TEXT PRIMARY KEY, wm_ts TEXT, wm_id INTEGER)`.
- Use a **composite watermark** `(updated_at, id)`: select rows where
  `updated_at > wm_ts OR (updated_at = wm_ts AND id > wm_id)`, ordered by `updated_at, id`.
- Upsert each row (`INSERT ... ON CONFLICT(id) DO UPDATE`), process in batches of `batch_size`, and write the new
  watermark **in the same transaction** as each batch.
- If a batch fails, roll back that batch (watermark unchanged for it) and re-raise.
- Return the number of rows loaded in this run.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Incremental ETL with watermarks and
upserts". Before I write code, teach me incremental ETL, watermarks, why a timestamp-only watermark loses rows on
ties, upserts, and transactional batch boundaries. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m04-data-sql/ex23-incremental-etl/starter.py so that test_etl.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `run_incremental`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m04-data-sql/ex23-incremental-etl` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Incremental ETL with watermarks and upserts" as a senior forward deployed engineer would
before it ships to a customer. Specifically: If the process crashes between two batches, what is re-loaded? Is the
composite comparison correct for equal timestamps? Could a long-running source transaction cause missed rows? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
