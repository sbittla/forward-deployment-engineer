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
