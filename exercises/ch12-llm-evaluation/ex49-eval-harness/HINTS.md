# ex49 hints · Golden-set eval harness

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the five graders first, as entries in the `GRADERS` dict, and check each against `test_graders`. They're small
and independent, and `run_eval` just looks them up by name. Each grader returns a real `bool`, since the test uses
`is True` and `is False`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **exact:** lowercase both sides and collapse whitespace with `" ".join(s.split())`, then compare.
- **numeric:** find the first number with a regex that allows commas and a decimal part, remove the commas, and
  compare against `value` with `tol`.
- **json_field:** parse the output, then walk the dotted path one key at a time. Any parse or lookup error means fail.
- **run_eval:** check *every* case's grader name before running anything. Then loop, catching exceptions from
  `system` and recording them as failures.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `"1,250.40"` must parse as 1250.4. A plain `\d+` stops at the comma and gives 1.
- Unknown graders must raise `ValueError` **before** the first `system` call (the test checks that nothing was called).
- `by_tag` only counts tagged cases, and a case with two tags counts towards both. Sort the keys.
- The markdown percentage has one decimal place: `(66.7%)`. A failure line shows the error if there is one, otherwise
  the first 80 characters of the output.
- Wilson: `z * z / (4 * n * n)` has `n` squared. Clamp to `[0, 1]` so 20 of 20 reports a top of exactly `1.0`.
- `by_slice` rounds only for the report; `wilson_interval` itself returns unrounded floats.
- Leakage: pad both normalised strings with a space on each side before `in`, so only whole words match.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_load` | Blank lines not skipped; missing `tags` not defaulted to `[]` |
| `test_graders` | A grader returns a match object or `None` instead of a bool; first number ignores commas |
| `test_run_and_report` | Exception output not `""`; failure lines use the wrong fallback; tag rates not rounded |
| `test_unknown_grader` | Grader validated lazily, after `system` has already been called |
| `test_wilson_interval_matches_worked_decision` | Normal (Wald) interval instead of Wilson; `n` not squared in the `z²/4n²` term |
| `test_wilson_interval_edges` | No clamp at 0 or 1; no `ValueError` for `n == 0` or `successes > n` |
| `test_by_slice` | Keys not sorted; bounds not rounded to 4 dp; `n` and `passed` missing from each slice |
| `test_failure_taxonomy` | Passing cases counted; unlabelled failures dropped; ties not sorted by cause |
| `test_cost_per_success` | Multiplying by the pass rate instead of dividing; no `ValueError` for a zero pass rate |
| `test_find_leakage` | No normalisation of case or punctuation; plain substring match flags partial words |
| `test_provenance` | `source` not read by `load_cases`; missing source not counted as `unspecified`; unknown source accepted |
| `test_mcnemar_exact_paired_comparison` | One-sided tail; concordant cases included in `n`; no cap at 1.0 when the counts are equal |
| `test_mcnemar_rejects_negative_counts` | No `ValueError` for a negative count |
