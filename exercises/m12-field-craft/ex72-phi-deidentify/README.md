# ex72 · Regulated data: de-identification and retention

**Module:** m12 · **Covers:** R25 Regulated industry context, R17 Compliance · **Time:** 60 min

## Scenario
A health system wants to use LLMs to summarise intake notes for research dashboards. Their privacy officer
requires a HIPAA Safe Harbor-style de-identification step (this exercise implements a teaching subset — real
programmes need the full 18 identifiers, an expert review, and legal sign-off) plus enforced retention.

## Your task
`deidentify(record, today) -> dict` where `record = {"patient_name", "dob", "mrn", "zip", "phone", "email",
"note", "visit_date"}`:
- drop `patient_name`, `mrn`, `phone`, `email` keys entirely
- `dob` → `birth_year` (int); if age at `today` ≥ 90 → `birth_year = None` and `age_group = "90+"`, else
  `age_group` = decade band like `"40-49"`
- `zip` → first 3 digits (`zip3`); if the 3-digit prefix is in `RESTRICTED_ZIP3` → `"000"`
- `visit_date` → year only (`visit_year`)
- in `note`: first replace MRNs (`MRN[:#\s]*\d+`) → `[MRN]`, emails → `[EMAIL]`, dates (`YYYY-MM-DD` or
  `MM/DD/YYYY`) → `[DATE]` and phones → `[PHONE]`; then replace each part of the patient's name
  (case-insensitive, whole word) with `[NAME]` (so `Maria Lopez` becomes `[NAME] [NAME]`)

`apply_retention(records, today, retention_days, legal_holds: set) -> (kept, purged_ids)` — records have `id` and
`created` (ISO date). Purge records older than `retention_days` unless their id is on legal hold. `purged_ids` sorted.

`access_log_entry(user, purpose, record_ids, today) -> dict` — `{"user", "purpose", "record_count", "date"}`
(never the record contents); raise `ValueError` if `purpose` is not in `ALLOWED_PURPOSES`.
