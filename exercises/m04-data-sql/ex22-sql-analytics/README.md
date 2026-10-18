# ex22 · SQL analytics on a support-ticket database

**Module:** m04 Data & SQL · **Covers:** R03 SQL & data modeling · **Time:** 60 min

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
