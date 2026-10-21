# ex24 · Data-quality checks framework

**Chapter:** 6 · Data Engineering (`exercises/ch06-data-engineering/`) · **Covers:** R04 Data pipelines

## Learning objectives
- Express data-quality rules declaratively and run them before every refresh.
- Separate blocking errors from warnings.
- Report failures with samples so owners can fix the source.
- Pseudonymise identifiers with a keyed hash, and derive checks from a data contract.

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

### Part B · Pseudonymisation and data contracts
`pseudonymise(value, key) -> str` — a keyed, stable token for joins and counts: normalise with
`value.strip().lower()`, then return the first 32 hex characters of HMAC-SHA256 under `key` (bytes). A plain hash of
an email isn't anonymous: anyone with a list of emails can hash them and match. The same value and key always give the
same token; a different key gives a different one.

`checks_from_contract(contract) -> list[Check]` turns a data contract (the dict you get from its YAML) into checks:
- for each column in `contract["schema"]`, in order: `nullable: false` → `not_null(col)`; `pattern` →
  `matches(col, pattern)`; `range: [lo, hi]` → `in_range(col, lo, hi)`; `values` → `accepted_values(col, values)`
- then each name in `contract["checks_blocking"]` not already built, which must be `unique(col)` or `not_null(col)`;
  any other name raises `ValueError("unknown blocking check: <name>")`
- a check's severity is `"error"` if its name is listed in `checks_blocking`, otherwise `"warn"`

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch06-data-engineering/ex24-data-quality`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch06-data-engineering/ex24-data-quality`: all 8
  pass.
- **Tests:** `test_dq.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Checks run in memory over a list of dicts, and `pseudonymise` takes its key as an argument.
  In production the checks run in the warehouse (dbt tests or Great Expectations) before every refresh, the HMAC key
  lives in a secrets manager outside the analytics environment with a rotation plan, and tokens are still treated as
  personal data because the same value always gives the same token.

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
Implement exercises/ch06-data-engineering/ex24-data-quality/starter.py so that test_dq.py passes. README.md in that folder is
the spec: follow its names, formats, ordering and error messages exactly. Public API: `Check`, `Result`, `Report`,
`not_null`, `unique`, `in_range`, `matches`, `accepted_values`, `row_count_between`, `fresh`, `run_checks`,
`pseudonymise`, `checks_from_contract`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch06-data-engineering/ex24-data-quality` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Data-quality checks framework" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Does unique() fail every duplicate occurrence? Are check names stable for dashboards?
Which check would have caught the empty policy_number incident earliest? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
