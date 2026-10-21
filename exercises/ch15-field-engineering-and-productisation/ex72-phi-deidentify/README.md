# ex72 · Regulated data: de-identification and retention

**Chapter:** 15 · Field Engineering and Productization (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R25 Regulated industry context, R17 Compliance

## Learning objectives
- De-identify health records with a Safe Harbor-style subset of rules.
- Enforce retention with legal holds.
- Log access by purpose without logging record contents.

## Scenario
A health system wants to use LLMs to summarize intake notes for research dashboards. Their privacy officer
requires a HIPAA Safe Harbor-style de-identification step (this exercise implements a teaching subset — real
programs need the full 18 identifiers, an expert review, and legal sign-off) plus enforced retention.

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
  Only the patient's own name is replaced: other people's names (a clinician, a relative) stay in the note, a
  documented limit of this teaching subset.

`apply_retention(records, today, retention_days, legal_holds: set) -> (kept, purged_ids)` — records have `id` and
`created` (ISO date). Purge records older than `retention_days` unless their id is on legal hold. `purged_ids` sorted.

`access_log_entry(user, purpose, record_ids, today) -> dict` — `{"user", "purpose", "record_count", "date"}`
(never the record contents or ids, only their count); raise `ValueError` if `purpose` is not exactly one of
`ALLOWED_PURPOSES` (no case folding or trimming), or if `user` is missing, empty or blank (anonymous access fails
closed).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch15-field-engineering-and-productisation/ex72-phi-deidentify`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch15-field-engineering-and-productisation/ex72-phi-deidentify`: all 6 pass.
- **Tests:** `test_phi.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** A teaching subset of Safe Harbor: names other than the patient's, addresses, seven-digit
  local phone numbers and many other identifiers pass through, and the access log is a returned dictionary.
  Production needs a maintained de-identification tool with measured recall on the customer's own notes, privacy and
  legal sign-off, scheduled and logged retention jobs, and an append-only audit log.

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
