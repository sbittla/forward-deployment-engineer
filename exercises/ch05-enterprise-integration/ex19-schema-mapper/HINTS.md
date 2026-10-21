# ex19 hints · CRM to canonical schema mapper

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write one small converter per field (`_phone`, `_created`, `_revenue`, `_segment`). Each takes the raw string and
either returns the clean value or raises `ValueError` with a useful message. Test them one by one in a REPL before
writing `map_records`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

For each row, keep a list of that row's errors and a dict of converted values. Run *every* converter inside its own
`try/except ValueError`, appending a `RowError(index, field, message)` on failure. Don't stop at the first error.
After all fields are done, either extend the global error list (if the row had any errors) or build the `Customer`.
Derive `segment` from the converted revenue.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- **Phone:** strip everything that isn't a digit, then drop a leading `1` if there are 11 digits. Exactly 10 digits
  are valid; anything else is an error. That handles all the listed formats.
- **Timestamp:** `%Y-%m-%dT%H:%M:%S.%f%z` parses `.000+0000` and `-0500`. Then call `.astimezone(timezone.utc)`, so
  `23:30 -0500` becomes `04:30` the next day in UTC.
- **Revenue:** remove commas, then `int(float(raw))` handles both `"1,200,000"` and `"1200000.0"`.
- **Blanks:** a blank phone or revenue is `None`, not an error. A blank `Id` is an error.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_good_rows` | Name whitespace not collapsed; timestamp left in the source offset instead of converted to UTC |
| `test_errors_collected_per_field` | Stopping at the first error in a row, or reporting the source column name instead of the canonical field |
| `test_phone_formats` | Formats handled one by one with patterns, instead of normalizing to digits |
| `test_mid_market` | Segment thresholds use `>` instead of `>=` |
