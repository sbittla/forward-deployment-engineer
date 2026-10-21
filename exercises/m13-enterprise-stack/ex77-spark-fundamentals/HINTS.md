# ex77 hints · Spark fundamentals: partitions, shuffles, skew, and a PySpark/Delta job

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Laziness is the core idea. A `MiniRDD` holds its source partitions plus a list of **pending** per-partition
operations. `map`, `filter` and `flat_map` don't compute anything: they return a *new* `MiniRDD` with one more
operation appended. Write a `_materialize()` that applies the pending operations to each partition; every action calls
it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **parallelize:** item *i* goes to partition `i % n`.
- **reduce_by_key** is the wide operation:
  1. increment `STATS["shuffles"]`;
  2. materialise;
  3. route every pair to bucket `crc32(str(key)) % num_partitions`, reducing as you go;
  4. return a new RDD whose partitions are the buckets' items.
- **Salting:** collect the items, make each key `(key, i % salts)` by position, reduce once (the hot key now spreads
  over several buckets), drop the salt, and reduce again. That's exactly two shuffles.
- **Part B:** a chain of `spark.read.table(...)`, `.filter(...)`, `.groupBy("merchant")`,
  `.agg(F.sum("amount").alias("total"))` and `.write.format("delta").mode("overwrite").saveAsTable(...)`. Before
  that chain, aggregate the input once (`F.count("*")` and `F.max("ingested_at")`), take `.first()` and raise if
  either check fails.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Use `zlib.crc32`, not `hash()`. Python's string hash changes from run to run (hash randomisation), so partitioning
  wouldn't be reproducible, and Spark executors need the same answer on every machine.
- Each lazy operation must capture its own function, so build each pending operation as a closure (or lambda) over the
  `fn` that was passed in.
- The static test parses `spark_job.py` and fails if `collect` or `toPandas` appears **anywhere**, even in a comment
  that becomes code. Keep all the work on the cluster.
- `.first()` on a one-row aggregate is fine: it returns the check's numbers, not the data. Compute the age on the
  cluster (`current_timestamp()` minus the newest `ingested_at`) to avoid mixing time zones on the driver.
- `skew_ratio` is `max / mean` of the partition sizes, and 0.0 when everything is empty.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_parallelize_and_lazy_narrow_ops` | Transformations run straight away (calls recorded before `collect`); partitioning not round-robin |
| `test_reduce_by_key_shuffles_by_stable_hash` | `hash()` used instead of `crc32`; shuffle counter not incremented |
| `test_skew_and_salting` | Salt taken from the key instead of the item position; more than two shuffles |
| `test_skew_ratio_values` | Empty partitions divide by zero |
| `test_spark_job_static` | `collect`/`toPandas` present; Delta format or table names missing; no `pyspark.sql` import |
| `test_spark_job_guards_overwrite` | `build` lacks `min_rows`/`max_age_hours`; checks placed after the write, or they log instead of raising |
