# ex22 hints · SQL analytics on a support-ticket database

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Copy the test fixture's schema and rows into a SQLite shell (`sqlite3 :memory:`, or any SQL client) and develop each
query there, checking it against the expected rows in the test. Each Python function then becomes one line:
`conn.execute(CONSTANT, params).fetchall()`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Durations:** SQLite has no interval type. `(julianday(resolved_at) - julianday(created_at)) * 24` gives hours.
- **Custom sort order:** `ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 ... END`.
- **Date window:** `date(:as_of, '-' || :days || ' days')` gives the lower bound. Use named parameters, never string
  formatting.
- **Anti-join:** `LEFT JOIN ... WHERE right.id IS NULL` finds customers with no tickets.
- **Two event streams in one series:** `UNION ALL` the created events and the resolved events (each with a 1 in its
  own column), then `GROUP BY week`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The top-agents window is half-open, `[as_of - days, as_of)`: use `>=` on the lower bound and `<` on the upper.
  ISO strings with a time part still compare correctly against a plain date.
- `SUM(reopened) / COUNT(*)` is integer division in SQLite. Multiply by `100.0` first.
- Weeks with only resolutions disappear if you group the tickets table by `created_at`. That's why the union is
  needed.
- Each function must return `[]` on an empty database, so avoid queries that return a single row of NULLs.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_status` | Tie-break on status missing, or ordering by count ascending |
| `test_avg_resolution` | Averaging days instead of hours; alphabetical priority order |
| `test_top_agents` | Inclusive upper bound; ties not broken by name; `LIMIT` not parameterised |
| `test_reopen_rate` | Integer division gives 0; ordering by category before pct |
| `test_customers_without_tickets` | Inner join instead of a left join; unsorted names |
| `test_weekly_flow` | Weeks with only resolutions missing; wrong `strftime` format (must be `%Y-%W`) |
| `test_sql_constants_filled` | SQL built inline inside the function instead of in the named module constants |
| `test_empty_database` | A query that returns `[(None,)]` or similar on empty tables |
