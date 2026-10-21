# ex72 · Regulated data: de-identification and retention

**Chapter:** 15 · Field Engineering and Productisation (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R25 Regulated industry context, R17 Compliance

## Learning objectives
- De-identify health records with a Safe Harbor-style subset of rules.
- Enforce retention with legal holds.
- Log access by purpose without logging record contents.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Regulated data: de-identification
and retention". Before I write code, teach me HIPAA Safe Harbor de-identification concepts, generalising dates and
ZIP codes, age bands, retention policies and purpose-based access logging. Use short Python examples that are not
the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to
re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch15-field-engineering-and-productisation/ex72-phi-deidentify/starter.py so that test_phi.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `deidentify`,
`apply_retention`, `access_log_entry`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch15-field-engineering-and-productisation/ex72-phi-deidentify` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Regulated data: de-identification and retention" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Is replacement order correct so a name inside an email isn't
half-redacted? Are ages computed correctly around birthdays? Which identifiers from the full list of 18 are still
missing? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
