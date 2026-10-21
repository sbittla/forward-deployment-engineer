# ex33 hints · Token budgeting and context packing

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `_render_system(system, docs)`, which builds the final system text including the `<documents>` wrapper. Then
write a `used(docs, messages)` helper that counts tokens on exactly what would be sent. Every "does it fit?" question
becomes `used(...) <= available`, so you never have to count the wrapper overhead by hand.
</details>

<details>
<summary>Hint 2 · The approach</summary>

1. Check that system plus question fits, or raise.
2. Docs, by score descending: if the whole doc fits, add it. If not, work out what's left *with an empty doc in its
   place* (so the tags are counted). If that's at least 50, add a truncated prefix; either way, stop. Every later doc
   is dropped.
3. History: group it into pairs `[0:2], [2:4], …`, walk the pairs from the newest, and add each pair to the front of
   the kept list while everything still fits. Stop at the first pair that doesn't fit.
4. Messages are the kept pairs (oldest first) plus the question.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Counting doc tokens by themselves underestimates the total: the header, footer and `<doc id="…">` tags cost tokens
  too. Measure the rendered system text.
- Docs come before history. History only gets what's left after the docs.
- Don't skip a pair that doesn't fit and try an older one. A conversation with a gap in the middle confuses the
  model.
- With no included docs, the system text is the original system prompt with no wrapper at all.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_count` | Using `//` instead of a ceiling, so `"abcde"` gives 1 |
| `test_everything_fits` | Docs not sorted by score; history order reversed in the output |
| `test_truncation_and_history_priority` | Wrapper tokens ignored, so the total exceeds 700; docs after the truncated one not dropped |
| `test_history_recent_pairs_first` | Oldest pair kept instead of the newest; empty `<documents>` block rendered |
| `test_mandatory_overflow` | No check that system and question fit before packing |
