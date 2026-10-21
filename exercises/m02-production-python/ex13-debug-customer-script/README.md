# ex13 · Triage and fix a broken customer script

**Module:** m02 · **Covers:** R29 Debugging in the customer environment, R01 Python · **Time:** 60 min

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
Fix every reported bug in exercises/m02-production-python/ex13-debug-customer-script/starter.py so that
test_fixes.py passes. README.md in that folder is the spec: follow its names, formats, ordering and error messages
exactly. Public API: `parse_amount`, `fetch_all`, `add_tag`, `is_overdue`, `total_by_customer`, `remove_paid`,
`load_config`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m02-production-python/ex13-debug-customer-script` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Triage and fix a broken customer script" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Does each FIX comment name the root cause rather than the symptom? Is there a
test that fails before each fix? Did any fix change a public signature or behaviour the customer relies on? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
