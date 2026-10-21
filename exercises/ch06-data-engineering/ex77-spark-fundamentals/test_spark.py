import ast
import operator
import zlib


def test_parallelize_and_lazy_narrow_ops(impl):
    calls = []
    rdd = impl.parallelize(range(10), 3)
    assert rdd.partition_sizes() == [4, 3, 3]
    mapped = rdd.map(lambda x: calls.append(x) or x * 2).filter(lambda x: x % 3 == 0)
    assert calls == []                                 # lazy
    assert mapped.collect() == [0, 6, 12, 18]          # only partition [0,3,6,9] survives x*2 % 3 == 0
    assert impl.parallelize(["a b", "c"], 2).flat_map(str.split).collect() == ["a", "b", "c"]


def test_reduce_by_key_shuffles_by_stable_hash(impl):
    impl.STATS["shuffles"] = 0
    pairs = [("acme", 10), ("globex", 5), ("acme", 7), ("initech", 1), ("globex", 2)]
    out = impl.parallelize(pairs, 2).reduce_by_key(operator.add, 3)
    assert sorted(out.collect()) == [("acme", 17), ("globex", 7), ("initech", 1)]
    assert impl.STATS["shuffles"] == 1
    for p, part in enumerate(out._materialize() if hasattr(out, "_materialize") else []):
        assert all(zlib.crc32(k.encode()) % 3 == p for k, _ in part)
    assert out.count() == 3


def test_skew_and_salting(impl):
    pairs = [("hot", 1)] * 90 + [(f"k{i}", 1) for i in range(10)]
    plain = impl.parallelize(pairs, 4).reduce_by_key(operator.add, 4)
    shuffled = impl.parallelize(pairs, 4).map(lambda kv: kv)
    assert impl.skew_ratio(shuffled) == 1.0
    impl.STATS["shuffles"] = 0
    salted = impl.salted_reduce_by_key(impl.parallelize(pairs, 4), operator.add, 4, salts=8)
    assert sorted(salted.collect()) == sorted(plain.collect())
    assert dict(salted.collect())["hot"] == 90
    assert impl.STATS["shuffles"] == 2


def test_skew_ratio_values(impl):
    rdd = impl.MiniRDD([[1] * 9, [1], [1], [1]])
    assert impl.skew_ratio(rdd) == 3.0
    assert impl.skew_ratio(impl.MiniRDD([[], []])) == 0.0


def test_spark_job_static(exercise_dir):
    src = (exercise_dir / "spark_job.py").read_text()
    tree = ast.parse(src)
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert {"table", "filter", "groupBy", "agg", "saveAsTable"} <= calls or \
           {"table", "where", "groupBy", "agg", "saveAsTable"} <= calls
    assert "collect" not in calls and "toPandas" not in calls
    assert 'format("delta")' in src.replace("'", '"') and "bronze.transactions" in src and "gold.merchant_totals" in src
    assert "pyspark.sql" in src and ("F.sum" in src or "sum(" in src)


def test_spark_job_guards_overwrite(exercise_dir):
    src = (exercise_dir / "spark_job.py").read_text()
    tree = ast.parse(src)
    builds = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "build"]
    assert builds, "define build(spark, batch_date, max_age_hours, min_ratio)"
    params = [a.arg for a in builds[0].args.args]
    assert params[:4] == ["spark", "batch_date", "max_age_hours", "min_ratio"]
    assert "replaceWhere" in src and "event_date" in src, "rebuild only the batch's event_date partition"
    attr_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    write_line = min(n.lineno for n in attr_calls if n.func.attr == "saveAsTable")
    assert any(n.func.attr == "count" and n.lineno < write_line for n in attr_calls), "count the input before writing"
    assert "ingested_at" in src, "check freshness on ingested_at"
    assert any(isinstance(n, ast.Raise) and n.lineno < write_line for n in ast.walk(tree)), \
        "a failed check must raise before the overwrite"


def test_completeness_check_catches_the_truncated_extract(impl):
    # The chapter's failure case: 1.1M rows for the day against a typical 9.4M. An absolute floor of 1,000,000 rows
    # passes it; a check relative to the trailing median does not.
    import pytest
    trailing = [9_400_000, 9_100_000, 9_600_000, 9_350_000, 9_500_000, 9_200_000, 9_450_000]
    with pytest.raises(impl.IncompleteBatch):
        impl.check_batch_complete(1_100_000, trailing)
    assert impl.check_batch_complete(9_000_000, trailing) is None
    assert impl.check_batch_complete(4_700_000, trailing) is None        # exactly 50% of the 9.4M median passes
    with pytest.raises(impl.IncompleteBatch):
        impl.check_batch_complete(4_699_999, trailing)
    with pytest.raises(impl.IncompleteBatch):
        impl.check_batch_complete(9_000_000, [])                         # no history: fail closed
