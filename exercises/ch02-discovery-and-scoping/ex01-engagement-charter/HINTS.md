# ex01 hints · Engagement charter from discovery notes

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Split the notes into sections first and parse each section separately. Every section starts with a line beginning
`## `, so a multiline split on that marker gives you (title, body) pairs. Normalize the title (strip it, lowercase it)
and dispatch on it. Bullets are the lines that start with `- `.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Stakeholders:** split each bullet on a dash *with whitespace on both sides*, at most once, so hyphenated names
  survive. Both `—` and `-` count as separators. The left part is the name and the right part is the role.
- **Metrics:** one regular expression handles the measurable form: name, colon, baseline number, an optional unit
  token, `->`, target number, then the unit. If the regex doesn't match, keep the whole bullet as the name with
  `baseline=None, target=None`. Don't drop it.
- **validate:** build the list of issues one rule at a time. A rule that passes adds nothing.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `float("11")` is `11.0`, and `render` must print `| 11 | 7 | min |`. Convert whole-number floats to `int` when you
  parse them (and keep `3.5` as a float).
- In `62 % -> 75 %` the unit appears after both numbers. Take the unit from the target side.
- `validate` is tested on keywords: the messages must contain `problem`, `sponsor`, `out-of-scope` (with hyphens) and
  the metric's name with `measurable`. The full notes must produce exactly **one** issue.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_parse_sections` | Splitting stakeholder lines on every `-`, or keeping the leading `- ` on bullets |
| `test_parse_metrics` | Regex doesn't allow a unit between the baseline and `->`; unmeasurable metric dropped instead of kept with `None` |
| `test_validate_flags_unmeasurable_metric` | A second issue raised for the sample notes, often a sponsor check that is case-sensitive |
| `test_validate_missing_sponsor_problem_scope` | Message wording: the test looks for `out-of-scope` with hyphens |
| `test_render_table` | Numbers rendered as `11.0`, or extra spaces in the table row |
