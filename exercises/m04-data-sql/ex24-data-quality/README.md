# ex24 · Data-quality checks framework

**Module:** m04 · **Covers:** R04 Data pipelines · **Time:** 50 min

## Learning objectives
- Express data-quality rules declaratively and run them before every refresh.
- Separate blocking errors from warnings.
- Report failures with samples so owners can fix the source.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Data-quality checks framework".
Before I write code, teach me data-quality checks (nullness, uniqueness, ranges, patterns, accepted values,
freshness, row counts) and how they gate pipelines, in the style of dbt tests and Great Expectations. Use short
Python examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a
time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m04-data-sql/ex24-data-quality/starter.py so that test_dq.py passes. README.md in that folder is
the spec: follow its names, formats, ordering and error messages exactly. Public API: `Check`, `Result`, `Report`,
`not_null`, `unique`, `in_range`, `matches`, `accepted_values`, `row_count_between`, `fresh`, `run_checks`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m04-data-sql/ex24-data-quality` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Data-quality checks framework" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Does unique() fail every duplicate occurrence? Are check names stable for dashboards?
Which check would have caught the empty policy_number incident earliest? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
