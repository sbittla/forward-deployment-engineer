import sqlite3


def run_incremental(src: sqlite3.Connection, dst: sqlite3.Connection, job: str = "orders", batch_size: int = 1000) -> int:
    raise NotImplementedError


def reconcile_deletes(src: sqlite3.Connection, dst: sqlite3.Connection, max_fraction: float = 0.5) -> int:
    raise NotImplementedError
