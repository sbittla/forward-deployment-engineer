# ex22 · SQL analytics on a support-ticket database

**Chapter:** 6 · Data Engineering (`exercises/ch06-data-engineering/`) · **Covers:** R03 SQL & data modeling

## Learning objectives
- Answer baseline business questions in SQL the customer's analysts can re-run.
- Use window boundaries, conditional aggregation and UNION ALL correctly.
- Produce numbers a CFO will trust before proposing an AI solution.

## Scenario
Before proposing an AI support copilot, you need a baseline the CFO trusts: where tickets pile up, how long they
take, which categories reopen. The customer gives you read-only access to a replica. Answer in SQL — the customer's
analysts will re-run your queries, so no pandas.

## Schema (SQLite)
```
agents(id INTEGER PK, name TEXT, team TEXT)
customers(id INTEGER PK, name TEXT, tier TEXT)
tickets(id INTEGER PK, customer_id INT, agent_id INT NULL, category TEXT, priority TEXT,
        status TEXT, created_at TEXT, resolved_at TEXT NULL, reopened INT)   -- ISO-8601 timestamps
```

## Your task
Each function takes a `sqlite3.Connection` and must run **one SQL query** (put the SQL in a module-level
constant so the customer's analysts can copy it):

1. `tickets_per_status(conn)` → `[(status, count)]` ordered by count desc, then status.
2. `avg_resolution_hours(conn)` → `[(priority, hours)]` for resolved tickets, hours rounded to 1 dp, ordered by
   priority in the order `urgent, high, normal, low`.
3. `top_agents(conn, as_of, days=30, n=3)` → `[(agent_name, resolved_count)]` resolved within `days` before
   `as_of` (an ISO date string, inclusive window `[as_of - days, as_of)`), ties broken by name.
4. `reopen_rate(conn)` → `[(category, pct)]` percentage of tickets reopened, 1 dp, ordered by pct desc then category.
5. `customers_without_tickets(conn)` → sorted list of customer names with no tickets.
6. `weekly_flow(conn)` → `[(week, created, resolved)]` where week is `strftime('%Y-%W', ...)`; include weeks that
   only have resolutions; order by week.

## Hints
`julianday(b) - julianday(a)` gives days. A `UNION ALL` of created and resolved events makes `weekly_flow` easy.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch06-data-engineering/ex22-sql-analytics`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch06-data-engineering/ex22-sql-analytics`: all 8
  pass.
- **Tests:** `test_sql.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The queries run on a small SQLite fixture with timestamps stored as text. Against the
  customer's replica, port them to its dialect (the book's SQLite-to-Postgres table in Chapter 6), keep windows
  half-open in the reporting time zone the data contract defines, and check the query plans on the full table before
  you hand them over.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "SQL analytics on a support-ticket
database". Before I write code, teach me analytical SQL in SQLite: grouping, date arithmetic with julianday,
half-open time windows, custom ordering with CASE, anti-joins, and combining event streams with UNION ALL. Use short
Python examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a
time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch06-data-engineering/ex22-sql-analytics/starter.py so that test_sql.py passes. README.md in that folder
is the spec: follow its names, formats, ordering and error messages exactly. Public API: `tickets_per_status`,
`avg_resolution_hours`, `top_agents`, `reopen_rate`, `customers_without_tickets`, `weekly_flow`. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/ch06-data-engineering/ex22-sql-analytics` and show
me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "SQL analytics on a support-ticket database" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Is each window half-open exactly as specified? Do NULL agent ids or
unresolved tickets distort averages? Would an analyst understand each query without comments? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
