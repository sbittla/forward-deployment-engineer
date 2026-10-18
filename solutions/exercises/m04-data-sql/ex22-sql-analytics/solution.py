import sqlite3

TICKETS_PER_STATUS = """
SELECT status, COUNT(*) AS n
FROM tickets
GROUP BY status
ORDER BY n DESC, status
"""

AVG_RESOLUTION_HOURS = """
SELECT priority, ROUND(AVG((julianday(resolved_at) - julianday(created_at)) * 24), 1) AS hours
FROM tickets
WHERE resolved_at IS NOT NULL
GROUP BY priority
ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END
"""

TOP_AGENTS = """
SELECT a.name, COUNT(*) AS resolved
FROM tickets t JOIN agents a ON a.id = t.agent_id
WHERE t.resolved_at >= date(:as_of, '-' || :days || ' days') AND t.resolved_at < date(:as_of)
GROUP BY a.id
ORDER BY resolved DESC, a.name
LIMIT :n
"""

REOPEN_RATE = """
SELECT category, ROUND(100.0 * SUM(reopened) / COUNT(*), 1) AS pct
FROM tickets
GROUP BY category
ORDER BY pct DESC, category
"""

CUSTOMERS_WITHOUT_TICKETS = """
SELECT c.name
FROM customers c LEFT JOIN tickets t ON t.customer_id = c.id
WHERE t.id IS NULL
ORDER BY c.name
"""

WEEKLY_FLOW = """
WITH events AS (
  SELECT strftime('%Y-%W', created_at) AS week, 1 AS created, 0 AS resolved FROM tickets
  UNION ALL
  SELECT strftime('%Y-%W', resolved_at), 0, 1 FROM tickets WHERE resolved_at IS NOT NULL
)
SELECT week, SUM(created), SUM(resolved)
FROM events
GROUP BY week
ORDER BY week
"""


def tickets_per_status(conn: sqlite3.Connection):
    return conn.execute(TICKETS_PER_STATUS).fetchall()


def avg_resolution_hours(conn):
    return conn.execute(AVG_RESOLUTION_HOURS).fetchall()


def top_agents(conn, as_of: str, days: int = 30, n: int = 3):
    return conn.execute(TOP_AGENTS, {"as_of": as_of, "days": days, "n": n}).fetchall()


def reopen_rate(conn):
    return conn.execute(REOPEN_RATE).fetchall()


def customers_without_tickets(conn):
    return [r[0] for r in conn.execute(CUSTOMERS_WITHOUT_TICKETS)]


def weekly_flow(conn):
    return conn.execute(WEEKLY_FLOW).fetchall()
