# Capstone 3 hints · Lakehouse ETL + NL-to-SQL analyst (financial services)

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start with the data, because every later number depends on it. `etl.py` is ex26 (bronze/silver/gold) applied to a
bank's transactions:

| Module | Reuse |
|---|---|
| `etl.py` | ex26 medallion, ex19 field converters, ex24 quality checks, ex23 latest-wins |
| `sqlguard.py` | small, pure and security-critical, so test it hard |
| `semantic.py` | metric definitions and schema prompt |
| `analyst.py` | ex32 repair loop |
| `evals.py` | ex49 harness, result-set comparison |

Get `test_c3_etl_semantic.py` green first, then `test_c3_sqlguard.py`. Neither needs a model.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Silver rules, one converter per field:** dates in several formats → ISO; amounts with thousands separators →
  float; SEK → USD at the given rate, keeping the original amount and currency. A row whose conversion fails, or
  whose account is unknown, goes to quarantine with a reason that names the field.
- **Duplicates:** the same `txn_id` with a later `updated_at` replaces the earlier row, and is counted in
  `duplicates`.
- **Gold:** `monthly_spend` is a SQL **view** over the silver table, grouped by account, category and month.
- **guard_sql:** strip comments, then allow a single statement only, `SELECT`/`WITH` only, no forbidden keywords, and
  only allowed tables (CTE names count as allowed). Then enforce the row limit.
- **Analyst:** prompt with the schema and the rules, extract the SQL from the reply, guard it, execute it. On any
  error, feed the error text back as the next user message and retry. `CANNOT_ANSWER` is a refusal, not an error.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Strip comments **before** checking for multiple statements. `-- ; DROP TABLE` inside a comment is harmless and
  should be allowed; `/* harmless */ ; DELETE` is two statements and must be blocked.
- Block system tables and table functions (`sqlite_master`, `pragma_table_info`) and `EXPLAIN` / `ATTACH`, not just
  data-changing verbs.
- Row limit: keep a smaller existing `LIMIT`, cap a larger one at 1000, append one if missing, and remove a trailing
  `;`.
- Make the error messages actionable for the model: name the rejected table *and* list the allowed ones, so the next
  attempt can succeed.
- Narratives are computed from the result rows, never written by the model (`total: <value>` for a single value,
  `N rows. First row: …` otherwise). That's how "never invent numbers" is enforced.
- Order-aware comparison only when the gold SQL has `ORDER BY`. Otherwise compare as multisets.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_load_report` | A bad row raises instead of being quarantined; the duplicate counted as loaded; quarantine reason lacks the field name |
| `test_silver_rules` | Earliest update kept instead of the latest; MM/DD/YYYY misread; FX not applied, or original amount not kept |
| `test_gold_view` | View sums the original currency instead of USD; month key format differs |
| `test_schema_prompt_and_dictionary` | Prompt lacks column types or metric names; dictionary table format differs |
| `test_blocks` | System tables, `pragma_` functions, `EXPLAIN` or `ATTACH` not blocked; multi-statement check before stripping comments |
| `test_allows_and_limits` | Trailing `;` kept; smaller limit overwritten; CTE names treated as unknown tables |
| `test_comments_cannot_smuggle` | Comments not stripped, or stripped after the statement check |
| `test_error_messages_are_actionable` | Error doesn't name the bad table and the allowed ones |
| `test_repair_loop` | SQL fences not stripped; database error not fed back to the model |
| `test_system_prompt_has_schema_and_rules` | `CANNOT_ANSWER` counted as a failed attempt instead of a refusal |
| `test_refuses_after_unsafe_attempts` | Unsafe SQL executed, or errors not recorded with `UnsafeSQL` |
| `test_narrative_multi_row` | Narrative wording differs from `N rows. First row: col=value, ….` |
| `test_question_suite` | Read `m["failures"]`; usually ordering or rounding differences against the gold results |
| `test_deliverable` | A required heading missing, a placeholder left in, or no measured percentage in the readout |
