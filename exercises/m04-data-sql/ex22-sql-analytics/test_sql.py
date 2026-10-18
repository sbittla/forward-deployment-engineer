import sqlite3

import pytest

SCHEMA = """
CREATE TABLE agents(id INTEGER PRIMARY KEY, name TEXT, team TEXT);
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, tier TEXT);
CREATE TABLE tickets(id INTEGER PRIMARY KEY, customer_id INT, agent_id INT, category TEXT, priority TEXT,
  status TEXT, created_at TEXT, resolved_at TEXT, reopened INT);
"""
AGENTS = [(1, "Ana", "T1"), (2, "Ben", "T1"), (3, "Cy", "T2"), (4, "Dee", "T2")]
CUSTOMERS = [(1, "Acme", "gold"), (2, "Globex", "silver"), (3, "Initech", "bronze"), (4, "Hooli", "gold")]
TICKETS = [
    # id, cust, agent, category, priority, status, created, resolved, reopened
    (1, 1, 1, "billing", "urgent", "resolved", "2026-09-01T09:00:00", "2026-09-01T11:00:00", 0),
    (2, 1, 1, "billing", "high", "resolved", "2026-09-02T09:00:00", "2026-09-02T15:00:00", 1),
    (3, 2, 2, "login", "normal", "resolved", "2026-09-03T09:00:00", "2026-09-04T09:00:00", 0),
    (4, 2, 2, "login", "normal", "resolved", "2026-09-20T09:00:00", "2026-09-20T21:00:00", 0),
    (5, 1, 3, "outage", "urgent", "resolved", "2026-09-21T10:00:00", "2026-09-21T11:30:00", 1),
    (6, 2, None, "billing", "low", "open", "2026-09-25T10:00:00", None, 0),
    (7, 1, 3, "login", "high", "pending", "2026-09-26T10:00:00", None, 0),
    (8, 2, 4, "outage", "urgent", "resolved", "2026-08-30T10:00:00", "2026-09-08T10:00:00", 0),
    (9, 1, 2, "billing", "normal", "open", "2026-09-27T10:00:00", None, 1),
]


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    c.executemany("INSERT INTO agents VALUES (?,?,?)", AGENTS)
    c.executemany("INSERT INTO customers VALUES (?,?,?)", CUSTOMERS)
    c.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?)", TICKETS)
    yield c
    c.close()


def test_status(impl, conn):
    assert impl.tickets_per_status(conn) == [("resolved", 6), ("open", 2), ("pending", 1)]


def test_avg_resolution(impl, conn):
    # urgent: 2h, 1.5h, 216h -> 73.2 ; high: 6 ; normal: 24, 12 -> 18
    assert impl.avg_resolution_hours(conn) == [("urgent", 73.2), ("high", 6.0), ("normal", 18.0)]


def test_top_agents(impl, conn):
    assert impl.top_agents(conn, "2026-09-30", days=30, n=3) == [("Ana", 2), ("Ben", 2), ("Cy", 1)]
    assert impl.top_agents(conn, "2026-09-10", days=7, n=5) == [("Ben", 1), ("Dee", 1)]


def test_reopen_rate(impl, conn):
    assert impl.reopen_rate(conn) == [("billing", 50.0), ("outage", 50.0), ("login", 0.0)]


def test_customers_without_tickets(impl, conn):
    assert impl.customers_without_tickets(conn) == ["Hooli", "Initech"]


def test_weekly_flow(impl, conn):
    rows = impl.weekly_flow(conn)
    assert rows[0] == ("2026-34", 1, 0)
    weeks = [r[0] for r in rows]
    assert weeks == sorted(weeks)
    assert sum(r[1] for r in rows) == 9 and sum(r[2] for r in rows) == 6
    assert dict((w, (c, r)) for w, c, r in rows)["2026-36"] == (0, 1)


def test_sql_constants_filled(impl):
    for name in ("TICKETS_PER_STATUS", "AVG_RESOLUTION_HOURS", "TOP_AGENTS", "REOPEN_RATE",
                 "CUSTOMERS_WITHOUT_TICKETS", "WEEKLY_FLOW"):
        assert "select" in getattr(impl, name).lower()


def test_empty_database(impl):
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE agents(id INTEGER PRIMARY KEY, name TEXT, team TEXT);"
                    "CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, tier TEXT);"
                    "CREATE TABLE tickets(id INTEGER PRIMARY KEY, customer_id INT, agent_id INT, category TEXT,"
                    " priority TEXT, status TEXT, created_at TEXT, resolved_at TEXT, reopened INT);")
    for fn in (impl.tickets_per_status, impl.avg_resolution_hours, impl.reopen_rate,
               impl.customers_without_tickets, impl.weekly_flow):
        assert fn(c) == []
    assert impl.top_agents(c, "2026-01-01") == []
