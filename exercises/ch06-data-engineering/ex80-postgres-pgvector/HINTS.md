# ex80 hints · SQLite to Postgres portability and pgvector

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

For `translate_ddl`, find each `CREATE TABLE … ( … );` with one regex (DOTALL), split the inside on commas into
column definitions, translate each column with a small function, and stitch it back together. Translating column by
column keeps rules like "a TEXT column whose name ends in `_at`" simple.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Column rules:** apply the longer pattern first. `INTEGER PRIMARY KEY AUTOINCREMENT` must be replaced before
  `INTEGER PRIMARY KEY`, or the second rule eats it. Use `\b` word boundaries, and anchor the `_at` rule to the
  column name at the start of the definition.
- **Queries:** a series of `re.sub` calls, then a final pass for placeholders.
- **pgvector:** dicts from metric to operator class and from metric to distance operator, then f-strings. Validate
  `index` and `k` before building anything.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Replace `?` placeholders with a character loop that tracks whether you're inside single quotes. A regex replace
  would also change the `?` in `'why?'`.
- Do `strftime('%Y-%m-%d', …)` before `strftime('%Y-%m', …)` for the same longest-first reason.
- `INSERT OR IGNORE` needs two edits: remove `OR IGNORE` and append ` ON CONFLICT DO NOTHING` at the end (after
  stripping any trailing `;`).
- Note the ivfflat suffix ` WITH (lists = 100)` and the 1–100 range for `k`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_ddl` | `INTEGER PRIMARY KEY` rule applied before the AUTOINCREMENT rule; `_at` rule also matches other columns |
| `test_queries` | `?` inside a string literal replaced; julianday pattern not converted to EXTRACT; ON CONFLICT not appended |
| `test_vector_schema` | Wrong operator class for the metric; ivfflat suffix missing; unknown index not rejected |
| `test_knn` | Wrong distance operator; `k=0` accepted |
| `test_table_name_is_validated` | Table name interpolated unchecked; `match` instead of `fullmatch` lets `chunks; DROP ...` through; 64-character name accepted |
