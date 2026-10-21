import sqlite3

import pytest


@pytest.fixture
def dbs():
    src, dst = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    src.execute("CREATE TABLE src_orders(id INTEGER, customer TEXT, amount REAL, updated_at TEXT)")
    src.executemany("INSERT INTO src_orders VALUES (?,?,?,?)", [
        (1, "acme", 10.0, "2026-10-01T00:00:00"),
        (2, "globex", 20.0, "2026-10-01T00:00:00"),
        (3, "acme", 30.0, "2026-10-01T00:00:01"),
    ])
    return src, dst


def wm(dst):
    return dst.execute("SELECT wm_ts, wm_id FROM etl_state WHERE job='orders'").fetchone()


def test_initial_and_idempotent(impl, dbs):
    src, dst = dbs
    assert impl.run_incremental(src, dst) == 3
    assert impl.run_incremental(src, dst) == 0
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 3
    assert wm(dst) == ("2026-10-01T00:00:01", 3)


def test_ties_and_updates(impl, dbs):
    src, dst = dbs
    impl.run_incremental(src, dst, batch_size=2)
    # a new row with the SAME timestamp as the watermark but higher id must not be missed
    src.execute("INSERT INTO src_orders VALUES (4, 'initech', 5.0, '2026-10-01T00:00:01')")
    src.execute("UPDATE src_orders SET amount=99, updated_at='2026-10-02T00:00:00' WHERE id=1")
    assert impl.run_incremental(src, dst, batch_size=2) == 2
    rows = dict(dst.execute("SELECT id, amount FROM dw_orders").fetchall())
    assert rows == {1: 99.0, 2: 20.0, 3: 30.0, 4: 5.0}


def test_failed_batch_rolls_back(impl, dbs):
    src, dst = dbs
    src.execute("INSERT INTO src_orders VALUES (5, 'bad', NULL, '2026-10-03T00:00:00')")
    with pytest.raises(sqlite3.IntegrityError):
        impl.run_incremental(src, dst, batch_size=2)
    # first batch (ids 1,2) committed; batch with id 3 and 5 rolled back
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 2
    assert wm(dst) == ("2026-10-01T00:00:00", 2)
    src.execute("UPDATE src_orders SET amount=1 WHERE id=5")
    assert impl.run_incremental(src, dst, batch_size=2) == 2


def test_boundary_late_arriving_row_is_missed(impl, dbs):
    # Known limitation: a row that lands with updated_at behind the watermark is never selected.
    src, dst = dbs
    impl.run_incremental(src, dst)
    src.execute("INSERT INTO src_orders VALUES (6, 'late', 7.0, '2026-09-30T23:59:59')")
    assert impl.run_incremental(src, dst) == 0
    assert dst.execute("SELECT COUNT(*) FROM dw_orders WHERE id=6").fetchone()[0] == 0


def test_boundary_replay_after_watermark_reset(impl, dbs):
    # Backfill: deleting the job's watermark replays every source row; the upsert adds no duplicates.
    src, dst = dbs
    impl.run_incremental(src, dst)
    src.execute("INSERT INTO src_orders VALUES (6, 'late', 7.0, '2026-09-30T23:59:59')")
    with dst:
        dst.execute("DELETE FROM etl_state WHERE job='orders'")
    assert impl.run_incremental(src, dst) == 4
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 4
    assert wm(dst) == ("2026-10-01T00:00:01", 3)


def test_duplicate_source_rows_keep_latest(impl, dbs):
    # The same order delivered twice (an exact re-send, then a later version): one row, the latest values.
    src, dst = dbs
    src.execute("INSERT INTO src_orders VALUES (3, 'acme', 30.0, '2026-10-01T00:00:01')")
    src.execute("INSERT INTO src_orders VALUES (3, 'acme', 31.0, '2026-10-01T00:00:02')")
    assert impl.run_incremental(src, dst, batch_size=2) == 5
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 3
    assert dst.execute("SELECT amount FROM dw_orders WHERE id=3").fetchone()[0] == 31.0


def test_reconcile_deletes_removes_hard_deleted_rows(impl, dbs):
    # A hard delete is invisible to the watermark; reconciliation by id removes it, and a rerun is a no-op.
    src, dst = dbs
    impl.run_incremental(src, dst)
    src.execute("DELETE FROM src_orders WHERE id=2")
    assert impl.run_incremental(src, dst) == 0
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 3
    assert impl.reconcile_deletes(src, dst) == 1
    assert [r[0] for r in dst.execute("SELECT id FROM dw_orders ORDER BY id")] == [1, 3]
    assert impl.reconcile_deletes(src, dst) == 0


def test_boundary_reconcile_refuses_mass_delete(impl, dbs):
    # Fail closed: an empty or truncated source extract must not wipe the warehouse.
    src, dst = dbs
    impl.run_incremental(src, dst)
    src.execute("DELETE FROM src_orders WHERE id IN (1, 2)")
    with pytest.raises(ValueError, match="refusing to delete 2 of 3 rows"):
        impl.reconcile_deletes(src, dst)
    assert dst.execute("SELECT COUNT(*) FROM dw_orders").fetchone()[0] == 3
    assert impl.reconcile_deletes(src, dst, max_fraction=1.0) == 2


def test_backfill_100k_rows(impl):
    # Realistic-volume backfill: 100,000 generated rows, 1,000 per timestamp (heavy ties), batches of 5,000.
    # Measured (this test, Python 3.13, Windows 11 laptop, in-memory SQLite): about 0.22 s for the load and 0.22 s for
    # the replay, 0.64 s for the whole test with data generation. The 30 s bound is generous so slow CI runners pass.
    import time
    n = 100_000
    src, dst = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    src.execute("CREATE TABLE src_orders(id INTEGER, customer TEXT, amount REAL, updated_at TEXT)")
    src.executemany("INSERT INTO src_orders VALUES (?,?,?,?)",
                    ((i, f"c{i % 997}", float(i % 500), f"2026-10-01T{i // 1000 // 60:02d}:{i // 1000 % 60:02d}:00")
                     for i in range(n)))
    t0 = time.perf_counter()
    assert impl.run_incremental(src, dst, batch_size=5000) == n
    with dst:
        dst.execute("DELETE FROM etl_state WHERE job='orders'")
    assert impl.run_incremental(src, dst, batch_size=5000) == n  # replay: every row again, no duplicates
    elapsed = time.perf_counter() - t0
    count, total = dst.execute("SELECT COUNT(*), SUM(amount) FROM dw_orders").fetchone()
    assert (count, total) == src.execute("SELECT COUNT(*), SUM(amount) FROM src_orders").fetchone()
    assert wm(dst) == ("2026-10-01T01:39:00", n - 1)
    assert elapsed < 30, f"backfill took {elapsed:.1f}s"
