# ex77 · Spark fundamentals: partitions, shuffles, skew, and a PySpark/Delta job

**Module:** m13 · **Covers:** R04 Pipelines, R31 Data platforms, R27 Performance · **Hands-on:** Spark, Databricks ·
**Time:** 75 min

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
Write a PySpark job, the code you'd run on Databricks, that:
1. reads `transactions` (Delta) with `spark.read.table("bronze.transactions")`
2. keeps `amount > 0`, groups by `merchant`, and sums `amount` as `total` using `pyspark.sql.functions`
3. writes the result with `.write.format("delta").mode("overwrite").saveAsTable("gold.merchant_totals")`
4. never calls `.collect()` or `.toPandas()` on the un-aggregated data (the test checks there are none at all)

`spark_job.py` isn't executed by the tests (no Spark cluster needed); it's parsed and checked statically. For the
Scala API, the same job is `df.filter($"amount" > 0).groupBy("merchant").agg(sum("amount").as("total"))`.
