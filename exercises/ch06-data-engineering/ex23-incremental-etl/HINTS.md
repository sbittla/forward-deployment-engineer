# ex23 hints · Incremental ETL with watermarks and upserts

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the four SQL statements as constants first: the `CREATE TABLE IF NOT EXISTS` DDL, the "changed rows" select, the
upsert into `dw_orders`, and the upsert into `etl_state`. Then read the current watermark, defaulting to `("", -1)` on
the first run so every row qualifies.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Run the select once on the source with the watermark as parameters, then pull rows with
  `cursor.fetchmany(batch_size)` until it returns nothing.
- For each batch, open one transaction on the destination. In Python's `sqlite3`, `with dst:` commits on success and
  rolls back on an exception. Inside it, `executemany` the upsert, then save the watermark from the batch's **last**
  row.
- Count loaded rows as you go and return the total.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Watermarking on `updated_at` alone misses rows that share the watermark's timestamp but arrived later. That's why
  the predicate is `updated_at > ts OR (updated_at = ts AND id > last_id)`, and the order must be
  `updated_at, id` to match.
- The watermark write must sit **inside** the same `with dst:` block as the rows. Otherwise a failure can leave the
  watermark ahead of the data, and those rows are never loaded.
- Let the `IntegrityError` propagate after the rollback. Don't catch it; the caller needs to know.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_initial_and_idempotent` | Watermark not saved, so the second run reloads everything; or saved from the first row of the batch |
| `test_ties_and_updates` | Timestamp-only watermark misses id 4; plain `INSERT` fails on the updated row instead of upserting |
| `test_failed_batch_rolls_back` | Watermark committed separately from the rows, or the whole run in one transaction (so batch 1 is lost too) |
| `test_boundary_late_arriving_row_is_missed` | Selection isn't the composite `(updated_at, id)` predicate (e.g. a full rescan); this pins the documented limit |
| `test_boundary_replay_after_watermark_reset` | Missing `etl_state` row not treated as `("", -1)`; plain `INSERT` duplicates or fails on replayed ids |
| `test_duplicate_source_rows_keep_latest` | Plain `INSERT` fails on the repeated id; or the upsert keeps the first version instead of the last |
| `test_reconcile_deletes_removes_hard_deleted_rows` | `reconcile_deletes` compares against the watermark instead of the source ids; or a rerun deletes again |
| `test_boundary_reconcile_refuses_mass_delete` | No `max_fraction` guard, or the check runs after the `DELETE` instead of before it |
| `test_backfill_100k_rows` | One transaction per row (slow); watermark taken from the wrong row; replay inserts duplicates |
