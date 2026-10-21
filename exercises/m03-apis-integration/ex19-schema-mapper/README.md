# ex19 · CRM to canonical schema mapper

**Module:** m03 · **Covers:** R05 System integration, R03 Data modeling · **Time:** 50 min

## Learning objectives
- Map dirty CRM exports to a canonical schema without aborting the batch.
- Normalise phones to E.164, timestamps to aware UTC, and revenue to integers.
- Report every error per row so the customer's admin can fix the source.

## Scenario
Three customers, three CRMs, one product. Your product team defined a canonical `Customer` model; your job is the
adapter for a Salesforce-style export. Real exports are dirty: blank revenues, phone numbers in five formats,
timestamps with `+0000` offsets. A good mapper **never aborts the batch** for one bad row — it collects errors
with row numbers so the customer's admin can fix the source.

## Your task
`map_records(rows: list[dict]) -> (customers: list[Customer], errors: list[RowError])`

| Canonical field | Source | Rule |
|---|---|---|
| `id` | `Id` | required, stripped |
| `name` | `AccountName` | required, whitespace collapsed |
| `phone_e164` | `Phone` | US numbers → `+1XXXXXXXXXX` (accept `(415) 555-0100`, `415.555.0100`, `+1 415 555 0100`, `1-415-555-0100`); blank → `None`; anything else is an error |
| `created_at` | `CreatedDate` | e.g. `2024-03-01T10:00:00.000+0000` → aware UTC `datetime` |
| `annual_revenue` | `AnnualRevenue` | `"1,200,000"`/`"1200000.0"` → `int`; blank → `None`; non-numeric is an error |
| `segment` | derived | `enterprise` ≥ 100M, `mid_market` ≥ 10M, `smb` otherwise, `unknown` if revenue is None |

`RowError(row, field, message)` uses the 0-based row index. A row with any error is excluded from `customers`,
and **all** errors in that row are reported (not just the first).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "CRM to canonical schema mapper".
Before I write code, teach me canonical data models, defensive parsing of exports, E.164 phone normalisation, and
row-level error reporting. Use short Python examples that are not the exercise solution. Then ask me three questions
to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m03-apis-integration/ex19-schema-mapper/starter.py so that test_mapper.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Customer`,
`RowError`, `map_records`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m03-apis-integration/ex19-schema-mapper` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "CRM to canonical schema mapper" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are all errors in a row reported, not just the first? Which real phone formats would
still fail? Is the segment boundary (exactly 10M or 100M) correct? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
