# ex19 · CRM to canonical schema mapper

**Chapter:** 5 · Enterprise Integration (`exercises/ch05-enterprise-integration/`) · **Covers:** R05 System integration, R03 Data modeling

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch05-enterprise-integration/ex19-schema-mapper`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch05-enterprise-integration/ex19-schema-mapper`:
  all 7 pass.
- **Tests:** `test_mapper.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Phone numbers are US-only and errors are returned in memory. Production uses a maintained
  phone-number library for international formats, writes rejected rows to a quarantine table the CRM administrator
  can see, and remembers that error messages echo raw values that may be personal data.

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
Implement exercises/ch05-enterprise-integration/ex19-schema-mapper/starter.py so that test_mapper.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Customer`,
`RowError`, `map_records`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch05-enterprise-integration/ex19-schema-mapper` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "CRM to canonical schema mapper" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are all errors in a row reported, not just the first? Which real phone formats would
still fail? Is the segment boundary (exactly 10M or 100M) correct? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
