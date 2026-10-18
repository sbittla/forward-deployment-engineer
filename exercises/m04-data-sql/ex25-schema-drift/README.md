# ex25 · Schema drift detection

**Module:** m04 · **Covers:** R04 Data pipelines, R03 Data modeling · **Time:** 45 min

## Scenario
The customer's upstream team "just added a field" to the claims feed — and renamed another, and started sending
amounts as strings. Your pipeline should notice drift *before* loading, classify it, and propose a migration.

## Your task
1. `infer_type(value)` → one of `"null" "bool" "int" "float" "datetime" "str"` (`datetime` = ISO-8601 string
   parseable by `datetime.fromisoformat`; bools are not ints).
2. `infer_schema(records)` → `{col: {"type": t, "nullable": bool}}`. Mixed `int`/`float` → `float`; any other mix
   of non-null types → `str`. `nullable` is True if any record has `None` or lacks the column.
3. `diff(expected, observed)` → list of `Change(kind, column, detail, severity)` sorted by column:
   - `added` (warn) — in observed, not expected
   - `removed` (error)
   - `type_changed` — `int → float` is a **widening** (warn); anything else is error. detail = `"int->str"`
   - `nullability_changed` — expected non-nullable, observed nullable (error); the reverse is not reported
4. `migration_sql(table, changes, observed)` → `ALTER TABLE <table> ADD COLUMN <col> <SQLTYPE>` for each `added`
   column (types: int→INTEGER, float→REAL, bool→INTEGER, datetime→TEXT, str→TEXT, null→TEXT). Other change
   kinds produce a comment line `-- manual: <kind> <column> (<detail>)`.
