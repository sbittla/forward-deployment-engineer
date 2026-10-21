# ex24 hints · Data-quality checks framework

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Settle on one shape for every check's function: it takes `rows` and returns `(passed, failing_row_indices)`. Dataset
checks return an empty index list. Once every check has that shape, `run_checks` is a three-line loop and `Result` is
built the same way for all of them.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Most row checks are "fail the rows where this predicate is true". Write one helper that takes a name, a predicate and
a severity and builds the `Check`, then make `not_null`, `in_range`, `matches` and `accepted_values` one-liners on top
of it. `unique` needs the whole column first: count values with `collections.Counter`, then fail every row whose value
has a count above 1.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Names are tested exactly: `in_range(premium,0,100000)` with no spaces, and `matches` includes the raw pattern.
  `accepted_values(state)` shows only the column.
- `matches` needs `re.fullmatch`: `pn-9` must fail `PN-\d{4}`, and `re.match` would also accept `PN-00012`.
- `in_range` and `matches` skip `None` (that's `not_null`'s job), but `accepted_values` does not.
- `sample_rows` is capped at 5, but `failed_count` is the full count.
- `Report.ok` ignores failed checks whose severity is `warn`.
- `pseudonymise` normalizes first (`strip().lower()`), then `hmac.new(key, ..., hashlib.sha256)`. Encode the value,
  not the key: `key` is already bytes.
- `checks_from_contract` builds every check with the factories you already have, then sets each one's severity from
  `checks_blocking` by name. Only the names the factories produce will match.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_row_checks` | `unique` fails only the second occurrence; `matches` uses `re.match`; check names contain spaces |
| `test_warn_only_does_not_block` | `ok` counts warn-severity failures |
| `test_dataset_checks` | `fresh` compares strings instead of parsed datetimes, or returns row indices |
| `test_sample_cap` | `failed_count` uses the capped list's length |
| `test_pseudonymise_is_keyed_and_stable` | Plain `sha256` without the key; no normalization; full 64-char digest returned |
| `test_checks_from_contract` | Checks built in a different order; severity left at `error` for unlisted checks |
| `test_contract_rejects_unknown_blocking_check` | Unknown names silently ignored instead of raising `ValueError` |
| `test_markdown` | Header or row spacing differs from `\| name \| severity \| PASS/FAIL \| n \|` |
| `test_pseudonymise_rejects_weak_key` | No key check, so an empty key quietly yields a guessable token; or the message differs |
