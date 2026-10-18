# ex19 · CRM to canonical schema mapper

**Module:** m03 · **Covers:** R05 System integration, R03 Data modeling · **Time:** 50 min

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
