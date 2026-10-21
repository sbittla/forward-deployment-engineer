import zlib

STATS = {"shuffles": 0}


class MiniRDD:
    def __init__(self, partitions: list[list], ops: list | None = None):
        self._partitions = partitions
        self._ops = ops or []

    def map(self, fn) -> "MiniRDD":
        raise NotImplementedError

    def filter(self, fn) -> "MiniRDD":
        raise NotImplementedError

    def flat_map(self, fn) -> "MiniRDD":
        raise NotImplementedError

    def reduce_by_key(self, fn, num_partitions: int) -> "MiniRDD":
        raise NotImplementedError

    def collect(self) -> list:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

    def partition_sizes(self) -> list[int]:
        raise NotImplementedError


def parallelize(data, num_partitions: int) -> MiniRDD:
    raise NotImplementedError


def skew_ratio(rdd: MiniRDD) -> float:
    raise NotImplementedError


def salted_reduce_by_key(rdd: MiniRDD, fn, num_partitions: int, salts: int) -> MiniRDD:
    raise NotImplementedError
