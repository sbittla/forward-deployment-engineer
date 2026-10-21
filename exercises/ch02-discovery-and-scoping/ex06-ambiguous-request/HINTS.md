# ex06 hints · Ambiguous request to clarifying questions and assumptions

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

This is a regular-expression exercise. Write one compiled regex per dimension (metric, users, data, deadline, volume)
and keep them in a dict whose insertion order is the README's priority order. Then `missing` is just the dimensions
whose regex finds nothing.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Find vague terms with **one** regex that alternates all the words, and use `finditer`. Running one search per
  word loses the order the words appear in.
- Put longer alternatives first (sort by length, descending) so `faster` isn't matched as `fast`.
- Questions are the dimension questions in `missing` order, then one formatted question per vague term. Assumptions
  follow `missing` order too.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `real-time` has a hyphen, and `\b` treats a hyphen as a word boundary. Use lookarounds that treat letters, digits
  *and* hyphens as part of a word, for example `(?<![\w-])` before the alternation and `(?![\w-])` after it.
- Plural forms count (`customers`, `tickets`), so use optional `s?` inside word boundaries.
- A metric needs a number *followed by* a unit; "40 support agents" is not a metric. Volume works the same way:
  "3000 tickets per day" matches, a bare number doesn't.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_vague_terms_in_order` | Searching word by word (order lost), or `real-time` missed because of `\b` |
| `test_missing_dimensions` | `users` regex misses the plural `customers`; dimensions not in priority order |
| `test_questions_and_assumptions` | Vague-term questions placed before the dimension questions, or the quote style differs |
| `test_well_specified_request` | A regex too strict for `11 min`, `2026-12-01` or `3000 tickets per day` |
| `test_quarter_and_month_count_as_deadline` | Deadline regex lacks `Q1`–`Q4` or month names, or isn't case-insensitive |
| `test_whole_words_only` | No word boundaries, so `overall` matches `all` and `smartphone` matches `smart` |
