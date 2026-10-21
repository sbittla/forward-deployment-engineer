# ex69 hints · Runbook and handoff doc linter

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Make one pass over the lines with a little state: whether you're inside a code fence, the previous heading level, the
current required section (if any), what each section contains, the prose lines seen outside code, and the variables
used inside code. Keep line-level issues and document-level issues in two lists and join them at the end.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- A line whose stripped text starts with three backticks toggles the "in code" flag. It's an *opening* fence if you
  weren't in code; flag `code-lang` only when an opening fence is bare, and mark the current section as having code.
- Inside code, collect `<UPPER_CASE>` variables in first-use order and skip every other check.
- Outside code: check placeholders, then headings (level from the number of `#`s, skip detection against the previous
  level). A heading starts a required section if its lowercased text *contains* one of the required names.
- At the end: missing sections, the rollback code block, the escalation contact, then undocumented variables.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Headings and `TODO`s inside code blocks don't count, which is why the code check comes first.
- `## Rollback procedure` still counts as the Rollback section: match on a substring, case-insensitively.
- A code block in **another** section doesn't satisfy `rollback-command`. Record code per section.
- A variable is documented if its name appears as a whole word anywhere outside code. `<NAMESPACE>` in a command is
  explained by "Set NAMESPACE to…" in the prose.
- Then write `RUNBOOK.md` and run your own linter on it.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_good` | Closing fences flagged as `code-lang`; phone or email regex too strict |
| `test_bad` | Issues not in the required order (line issues first, then sections in the listed order); wrong line numbers (must be 1-based) |
| `test_heading_with_extra_words` | Section headings matched exactly instead of by substring |
| `test_fence_in_wrong_section_doesnt_count` | Any code block in the document satisfies the rollback rule |
| `test_your_runbook` | Your `RUNBOOK.md` misses a section, leaves a placeholder, or uses an unexplained variable |
