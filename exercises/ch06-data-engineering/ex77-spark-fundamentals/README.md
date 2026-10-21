# ex77 · Spark fundamentals: partitions, shuffles, skew, and a PySpark/Delta job

**Chapter:** 6 · Data Engineering (`exercises/ch06-data-engineering/`) · **Covers:** R04 Pipelines, R31 Data platforms, R27 Performance · **Hands-on:** Spark, Databricks ·
**Time:** 75 min

## Learning objectives
- See partitions, narrow vs wide transformations and shuffles in a mini engine.
- Diagnose and fix key skew with salting.
- Write the equivalent PySpark/Delta job for Databricks, guarded by blocking input checks before it overwrites.

## Scenario
Databricks, Palantir and Snowflake-adjacent FDE roles assume you can reason about distributed execution: why a job
with one hot key runs for hours, why `collect()` crashed the driver, and where the shuffle happens. Part A builds a
tiny partitioned engine so you can *see* those mechanics. Part B is the real PySpark job you'd hand the customer.

## Part A: `MiniRDD` (in `starter.py`)
- `parallelize(data, num_partitions)` splits data round-robin into partitions (item *i* → partition `i % n`).
- Narrow, lazy transformations: `map`, `filter`, `flat_map`. They run nothing until an action.
- `reduce_by_key(fn, num_partitions)`: a **wide** transformation. Shuffle pairs to partition
  `zlib.crc32(str(key).encode()) % num_partitions`, then reduce within each partition. Each shuffle increments the
  module-level counter `STATS["shuffles"]`.
- Actions: `collect()` (partition order, then item order), `count()`, `partition_sizes()`.
- `skew_ratio(rdd)` → `max(partition_sizes) / mean(partition_sizes)` rounded to 2 dp (0.0 for empty).
- `salted_reduce_by_key(rdd, fn, num_partitions, salts)` fixes a hot key: append salt `i % salts` (by item position)
  to each key, `reduce_by_key`, strip the salt, `reduce_by_key` again. The result equals a plain `reduce_by_key`.

## Part B: `spark_job.py`
Write a PySpark job, the code you'd run on Databricks, as `build(spark, min_rows, max_age_hours)`, that:
1. reads `transactions` (Delta) with `spark.read.table("bronze.transactions")`
2. **blocks** before any write: counts the input rows (`count`) and measures the age of the newest `ingested_at`, and
   raises if there are fewer than `min_rows` rows or the newest row is older than `max_age_hours`. An overwrite
   trusts its input completely; a partial bronze must fail the job, not replace correct totals
3. keeps `amount > 0`, groups by `merchant`, and sums `amount` as `total` using `pyspark.sql.functions`
4. writes the result with `.write.format("delta").mode("overwrite").saveAsTable("gold.merchant_totals")`
5. never calls `.collect()` or `.toPandas()` on the un-aggregated data (the test checks there are none at all)

`spark_job.py` isn't executed by the tests (no Spark cluster needed); it's parsed and checked statically: the
`count` call and a `raise` must come before the `saveAsTable` line. For the
Scala API, the same job is `df.filter($"amount" > 0).groupBy("merchant").agg(sum("amount").as("total"))`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch06-data-engineering/ex77-spark-fundamentals`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch06-data-engineering/ex77-spark-fundamentals`: all
  6 pass.
- **Tests:** `test_spark.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** `MiniRDD` runs in one process and only models partitioning and shuffles; the PySpark job is
  checked statically, not run on a cluster. Before production, run the job on representative data, read its plan and
  Spark UI, tune the input-check thresholds with the data owner, and rely on Delta table history so a bad overwrite
  can be restored.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Spark fundamentals: partitions,
shuffles, skew, and a PySpark/Delta job". Before I write code, teach me Spark execution: lazy evaluation,
partitions, shuffles, skew, salting, and Delta table reads/writes. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch06-data-engineering/ex77-spark-fundamentals/starter.py so that test_spark.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `MiniRDD`,
`parallelize`, `skew_ratio`, `salted_reduce_by_key`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch06-data-engineering/ex77-spark-fundamentals` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Spark fundamentals: partitions, shuffles, skew, and a PySpark/Delta job" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Does salting produce exactly the same result as
a plain reduce? Is the shuffle counter incremented once per wide transformation? Would the PySpark job push the
filter down before the shuffle? Rank findings by customer impact, quote the line for each, and say which ones a test
should catch.
```
