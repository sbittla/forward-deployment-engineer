# ex24 · Data-quality checks framework

**Module:** m04 · **Covers:** R04 Data pipelines · **Time:** 50 min

## Scenario
Your RAG answers went wrong for a week because an upstream job started writing empty `policy_number`s. Nobody
noticed. Add declarative data-quality checks that run before every index refresh and block it on errors.

## Your task
Check factories (each returns a `Check` with `name`, `severity` ("error" default or "warn") and a function):

| Factory | Fails rows where… |
|---|---|
| `not_null(col)` | value is `None` or `""` |
| `unique(col)` | value appears more than once (all occurrences fail) |
| `in_range(col, lo, hi)` | value is not None and outside `[lo, hi]` |
| `matches(col, pattern)` | value is not None and does not fully match the regex |
| `accepted_values(col, values)` | value is not in `values` |
| `row_count_between(lo, hi)` | dataset-level: fails (no row indices) when `len(rows)` is outside the range |
| `fresh(col, max_age: timedelta, now)` | dataset-level: fails when the max ISO timestamp in `col` is older than `now - max_age` |

`run_checks(rows, checks) -> Report`:
- `Report.results`: list of `Result(name, severity, passed, failed_count, sample_rows)` — `sample_rows` holds at most
  5 failing row indices.
- `Report.ok` is False if any **error**-severity check failed (warnings do not block).
- `Report.to_markdown()` → table `| Check | Severity | Status | Failed |` with `PASS`/`FAIL`.

All factories accept `severity="warn"`. Check names: `not_null(policy_number)`, `in_range(premium,0,100000)` etc.
— i.e. `factory(arg1,arg2)` with no spaces.
