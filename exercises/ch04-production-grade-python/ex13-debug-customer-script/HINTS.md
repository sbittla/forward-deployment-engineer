# ex13 hints · Triage and fix a broken customer script

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>
Work like you would on site: one failing test at a time. Run `pytest -x` on the folder and read the first failure's
traceback before you touch the code. The tests are named after reports 1 to 7, in order, one per function, so each
test
leads you to one bug. Write the `# FIX(n):` comment as you fix each one, not at the end.
</details>

<details>
<summary>Hint 2 · The approach</summary>

The seven bugs fall into a few well-known classes. For each function, ask which class it falls into:

- money stored as `float`;
- an off-by-one in a loop bound;
- a mutable default argument;
- comparing a timezone-aware datetime with a naive one;
- changing a dict while iterating over it;
- a bare `except` that hides the real error.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Build `Decimal` from the **string**, after removing the thousands commas. `Decimal(float(...))` keeps the float's
  error.
- Python's `round()` uses banker's rounding, so `round(Decimal("2.675"), 2)` doesn't give `2.68`. Use
  `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- `datetime.now()` is naive. Use `datetime.now(timezone.utc)`, and give a parsed naive datetime UTC with
  `.replace(tzinfo=timezone.utc)`.
- In `load_config`, a missing file returns `{}`, but invalid JSON must raise a `ValueError` that names the path. Catch
  the two exceptions separately.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_big_invoices_do_not_crash` | Commas not stripped, or the function still returns a float |
| `test_report_includes_the_last_page` | Loop stops one page early (`<` instead of `<=`) |
| `test_tags_do_not_leak_between_invoices` | Default `tags=[]` still shared between calls |
| `test_overdue_check_survives_the_eu_move` | One side of the comparison is still naive, or `now` defaults to local time |
| `test_totals_are_not_off_by_a_cent` | Summing floats, or rounding with `round()` instead of half-up |
| `test_cleaning_paid_invoices_does_not_crash` | `RuntimeError` from deleting keys while iterating the dict itself |
| `test_corrupted_config_is_not_silently_ignored` | All exceptions still caught; or the error message doesn't include the file name |
| `test_fix_comments` | A `# FIX(n)` comment missing for one of 1 to 7 |
