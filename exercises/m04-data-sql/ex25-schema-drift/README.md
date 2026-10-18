# ex25 · Schema drift detection

**Module:** m04 · **Covers:** R04 Data pipelines, R03 Data modeling · **Time:** 45 min

## Learning objectives
- Infer a schema from records and detect drift before loading.
- Classify drift by severity: additive, widening, breaking.
- Propose a migration and flag changes that need a human.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Schema drift detection". Before I
write code, teach me schema inference, schema evolution, type widening vs breaking changes, and nullability drift.
Use short Python examples that are not the exercise solution. Then ask me three questions to check my understanding,
one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m04-data-sql/ex25-schema-drift/starter.py so that test_drift.py passes. README.md in that folder
is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Change`, `infer_type`,
`infer_schema`, `diff`, `migration_sql`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/m04-data-sql/ex25-schema-drift` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Schema drift detection" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Is bool correctly distinguished from int? Does a column missing from some records count as
nullable? Which drift should block the pipeline versus only warn? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
