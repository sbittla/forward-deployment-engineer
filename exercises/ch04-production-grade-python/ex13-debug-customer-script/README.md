# ex13 · Triage and fix a broken customer script

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R29 Debugging in the customer environment, R01 Python

## Learning objectives
- Reproduce and fix a customer's bugs from their verbatim reports.
- Use Decimal for money, aware datetimes, and explicit error handling.
- Document each root cause in language the customer can read.

## Scenario
On day two on site, the finance team hands you `starter.py`, the invoice report a contractor wrote last year.
It "mostly works". Their bug reports, verbatim:

1. *"It crashes on big invoices."* (amounts like `"1,234.50"`)
2. *"The report is always missing the last page of invoices."*
3. *"Tags from one invoice show up on other invoices!"*
4. *"Since we moved to the EU data center, the overdue check throws a TypeError."*
5. *"Totals are off by a cent sometimes."*
6. *"Cleaning paid invoices crashes with 'dictionary changed size during iteration'."*
7. *"When the config file is corrupted, the report silently uses defaults and emails garbage to the CFO."*

## Your task
Fix **every** bug in `starter.py` without changing function signatures. For each fix, add a one-line comment
`# FIX(n): ...` explaining the root cause, as you would in a customer-facing change log.

Rules for the fixed behaviour:
- Money uses `decimal.Decimal`, rounded half-up to cents.
- `is_overdue` treats naive datetimes as UTC.
- `load_config` raises `ValueError` mentioning the path when JSON is invalid; a **missing** file still returns `{}`.

## Field notes
Reproduce first, then fix. Write the failing test for each report before touching the code — it is also your
proof to the customer that the bug is gone.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch04-production-grade-python/ex13-debug-customer-script`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch04-production-grade-python/ex13-debug-customer-script`: all 8 pass.
- **Tests:** `test_fixes.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The fixes are proved by seven unit tests on synthetic invoices. Before shipping to the
  customer, run the fixed script against a copy of their real data, compare totals with the old report, and add the
  tests to their CI so the next change can't silently reintroduce a bug.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Triage and fix a broken customer
script". Before I write code, teach me a systematic debugging method for unfamiliar code: reproduce, isolate, write
the failing test, fix, explain, using the classic Python bugs (mutable defaults, float money, naive datetimes,
off-by-one pagination, mutating while iterating). Use short Python examples that are not the exercise solution. Then
ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Fix every reported bug in exercises/ch04-production-grade-python/ex13-debug-customer-script/starter.py so that
test_fixes.py passes. README.md in that folder is the spec: follow its names, formats, ordering and error messages
exactly. Public API: `parse_amount`, `fetch_all`, `add_tag`, `is_overdue`, `total_by_customer`, `remove_paid`,
`load_config`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch04-production-grade-python/ex13-debug-customer-script` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Triage and fix a broken customer script" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Does each FIX comment name the root cause rather than the symptom? Is there a
test that fails before each fix? Did any fix change a public signature or behaviour the customer relies on? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
