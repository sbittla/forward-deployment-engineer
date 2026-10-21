# ex72 hints · Regulated data: de-identification and retention

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start the output as a copy of the record **without** the identifying keys (a dict comprehension that skips them), so
you never change the input. Then add the generalised fields one at a time: birth year and age group, zip3, visit year,
and finally the scrubbed note.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Age:** `today.year - dob.year`, minus 1 if this year's birthday hasn't happened yet. Compare `(month, day)`
  tuples.
- **Age group:** 90 or over is `"90+"` with no birth year. Otherwise the decade band is `age // 10 * 10` to that plus 9.
- **Note scrubbing**, in this order: MRNs, emails, dates, phones, then name parts. Each step is a `re.sub`.
- **Retention:** cutoff = `today - timedelta(days=retention_days)`. Purge records created before the cutoff, unless
  they're on legal hold.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The order is deliberate. Emails go before names, so `maria@example.com` becomes `[EMAIL]` whole rather than
  `[NAME]@example.com`. Dates go before phones, because a date looks like a run of digits to a phone pattern.
- Name parts are whole-word and case-insensitive: `lopez` is replaced, but `Lopezville` isn't. Escape each part with
  `re.escape`.
- Someone born on 17 October 1936 is still 89 on 16 October 2026. Off-by-one-day errors at the 90 boundary are what
  regulators actually check.
- The access log records counts and purpose, never record contents, and rejects purposes that aren't allowed.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_deidentify` | Name scrubbed before email; substring match changes `Lopezville`; input record changed in place |
| `test_elderly_and_restricted_zip` | Age computed from years only (birthday ignored); restricted zip3 list not applied |
| `test_retention` | Legal hold ignored; boundary uses `<=` |
| `test_access_log` | Record contents included; unknown purpose accepted |
| `test_access_log_fails_closed` | Blank or `None` user accepted; purpose lower-cased or stripped before the check; record ids copied into the entry |
| `test_boundary_other_names_not_scrubbed` | Names other than the patient's replaced, or the note changed beyond the patient's name |
