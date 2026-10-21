import statistics
import zlib

STATS = {"shuffles": 0}


def _partition_for(key, n: int) -> int:
    return zlib.crc32(str(key).encode()) % n


class MiniRDD:
    def __init__(self, partitions: list[list], ops: list | None = None):
        self._partitions = partitions
        self._ops = ops or []          # pending narrow ops, applied lazily per partition

    def _with(self, op) -> "MiniRDD":
        return MiniRDD(self._partitions, self._ops + [op])

    def map(self, fn) -> "MiniRDD":
        return self._with(lambda part: [fn(x) for x in part])

    def filter(self, fn) -> "MiniRDD":
        return self._with(lambda part: [x for x in part if fn(x)])

    def flat_map(self, fn) -> "MiniRDD":
        return self._with(lambda part: [y for x in part for y in fn(x)])

    def _materialize(self) -> list[list]:
        parts = self._partitions
        for op in self._ops:
            parts = [op(p) for p in parts]
        return parts

    def reduce_by_key(self, fn, num_partitions: int) -> "MiniRDD":
        STATS["shuffles"] += 1      # stage boundary: every key must meet its peers on one partition
        buckets: list[dict] = [{} for _ in range(num_partitions)]
        for part in self._materialize():
            for k, v in part:
                b = buckets[_partition_for(k, num_partitions)]
                b[k] = fn(b[k], v) if k in b else v
        return MiniRDD([list(b.items()) for b in buckets])

    def collect(self) -> list:
        return [x for part in self._materialize() for x in part]

    def count(self) -> int:
        return sum(len(p) for p in self._materialize())

    def partition_sizes(self) -> list[int]:
        return [len(p) for p in self._materialize()]


def parallelize(data, num_partitions: int) -> MiniRDD:
    parts: list[list] = [[] for _ in range(num_partitions)]
    for i, x in enumerate(data):
        parts[i % num_partitions].append(x)
    return MiniRDD(parts)


def skew_ratio(rdd: MiniRDD) -> float:
    sizes = rdd.partition_sizes()
    mean = sum(sizes) / len(sizes) if sizes else 0
    return round(max(sizes) / mean, 2) if mean else 0.0


class IncompleteBatch(Exception):
    pass


def check_batch_complete(batch_rows: int, trailing_counts: list[int], min_ratio: float = 0.5) -> None:
    """Raise IncompleteBatch unless batch_rows >= min_ratio * median(trailing_counts)."""
    if not trailing_counts:
        raise IncompleteBatch("no trailing counts to compare against")
    median = statistics.median(trailing_counts)
    if batch_rows < min_ratio * median:
        raise IncompleteBatch(f"{batch_rows} rows is below {min_ratio:.0%} of the trailing median {median:g}")


def salted_reduce_by_key(rdd: MiniRDD, fn, num_partitions: int, salts: int) -> MiniRDD:
    items = rdd.collect()
    salted = parallelize([((k, i % salts), v) for i, (k, v) in enumerate(items)], num_partitions)
    partial = salted.reduce_by_key(fn, num_partitions)
    return partial.map(lambda kv: (kv[0][0], kv[1])).reduce_by_key(fn, num_partitions)
