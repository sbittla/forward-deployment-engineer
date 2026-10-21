import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS dw_orders(id INTEGER PRIMARY KEY, customer TEXT, amount REAL NOT NULL, updated_at TEXT);
CREATE TABLE IF NOT EXISTS etl_state(job TEXT PRIMARY KEY, wm_ts TEXT, wm_id INTEGER);
"""

SELECT_CHANGED = """
SELECT id, customer, amount, updated_at FROM src_orders
WHERE updated_at > :ts OR (updated_at = :ts AND id > :id)
ORDER BY updated_at, id
"""

UPSERT = """
INSERT INTO dw_orders(id, customer, amount, updated_at) VALUES (?,?,?,?)
ON CONFLICT(id) DO UPDATE SET customer=excluded.customer, amount=excluded.amount, updated_at=excluded.updated_at
"""

SAVE_WM = """
INSERT INTO etl_state(job, wm_ts, wm_id) VALUES (?,?,?)
ON CONFLICT(job) DO UPDATE SET wm_ts=excluded.wm_ts, wm_id=excluded.wm_id
"""


def run_incremental(src: sqlite3.Connection, dst: sqlite3.Connection, job: str = "orders", batch_size: int = 1000) -> int:
    dst.executescript(DDL)
    row = dst.execute("SELECT wm_ts, wm_id FROM etl_state WHERE job=?", (job,)).fetchone()
    ts, last_id = row if row else ("", -1)
    cur = src.execute(SELECT_CHANGED, {"ts": ts, "id": last_id})
    loaded = 0
    while True:
        batch = cur.fetchmany(batch_size)
        if not batch:
            return loaded
        # One transaction per batch: rows and watermark commit together or roll back together.
        with dst:
            dst.executemany(UPSERT, batch)
            dst.execute(SAVE_WM, (job, batch[-1][3], batch[-1][0]))
        loaded += len(batch)


def reconcile_deletes(src: sqlite3.Connection, dst: sqlite3.Connection, max_fraction: float = 0.5) -> int:
    """Delete warehouse rows whose id no longer exists at the source, in one transaction.

    Fails closed: if more than max_fraction of the warehouse would go, the source extract is more likely empty or
    truncated than the deletes real, so nothing is deleted and ValueError is raised.
    """
    dst.executescript(DDL)
    source_ids = [(r[0],) for r in src.execute("SELECT DISTINCT id FROM src_orders")]
    with dst:
        dst.execute("CREATE TEMP TABLE IF NOT EXISTS _src_ids(id INTEGER PRIMARY KEY)")
        dst.execute("DELETE FROM _src_ids")
        dst.executemany("INSERT INTO _src_ids VALUES (?)", source_ids)
        total = dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0]
        gone = dst.execute("SELECT COUNT(*) FROM dw_orders WHERE id NOT IN (SELECT id FROM _src_ids)").fetchone()[0]
        if total and gone / total > max_fraction:
            raise ValueError(f"refusing to delete {gone} of {total} rows (max_fraction={max_fraction})")
        dst.execute("DELETE FROM dw_orders WHERE id NOT IN (SELECT id FROM _src_ids)")
    return gone
