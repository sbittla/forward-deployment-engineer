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
