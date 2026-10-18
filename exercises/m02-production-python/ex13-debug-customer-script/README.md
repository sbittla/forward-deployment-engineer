# ex13 · Triage and fix a broken customer script

**Module:** m02 · **Covers:** R29 Debugging in the customer environment, R01 Python · **Time:** 60 min

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
