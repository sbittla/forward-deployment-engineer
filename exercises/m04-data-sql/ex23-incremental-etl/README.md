# ex23 · Incremental ETL with watermarks and upserts

**Module:** m04 · **Covers:** R04 Data pipelines, R03 SQL · **Time:** 60 min

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
