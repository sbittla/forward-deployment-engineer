# ex95 hints · Prompt linter for CI

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Get the placeholder regex right before anything else, because seven of the nine rules depend on it. A placeholder is
`{name}` that is **not** part of `{{…}}`: lookarounds such as `(?<!\{)\{([a-z_][a-z0-9_]*)\}(?!\})` do it.
`placeholders` then collects unique names in first-seen order.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Check the rules one after another, appending `Finding`s, then sort once at the end by `(severity rank, rule)`.
  Python's sort is stable, so findings within one rule keep their discovery order.
- **P002:** a placeholder counts as delimited only if it sits directly inside a *matching* tag pair. A backreference
  does it: `<(tag)…>\s*\{name\}\s*</\1>`.
- **P004:** count all-caps emphasis words across the system prompt and the template together, and put the count at
  the start of the message.
- **P008:** look for a placeholder *or* a date/time pattern in the system prompt.
- **score** is pure arithmetic, floored at 0.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `<doc>{ticket_text}</ticket>` must fail P002: the closing tag must match the opening one.
- P005 produces one finding per unknown placeholder, in first-seen order. P006 produces one per unused variable, in
  **sorted** order.
- P007 checks the tool description (under 20 characters after stripping) *and* each parameter without a
  `description`. One tool can produce several findings.
- Why P008 matters: anything dynamic in the system prompt changes it on every request, which defeats prompt caching.
- `render` leaves `{{x}}` alone and raises `KeyError` listing every missing value, never sending a literal `{name}` to
  the model.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_clean_prompt` | A rule fires falsely: P003 missing "JSON" in the system prompt, or P002 not recognizing the tag pair |
| `test_placeholders_ignore_escaped_braces` | `{{literal}}` matched as a placeholder; duplicates kept |
| `test_empty_system_and_undelimited_untrusted` | Message lacks `{email_body}` with braces; score formula wrong |
| `test_mismatched_tag_is_not_delimited` | Opening and closing tag names not required to match |
| `test_format_and_shouting` | Emphasis counted only in one of the two texts; message doesn't start with the count |
| `test_variable_mismatch` | P005/P006 swapped or not one per name |
| `test_tool_descriptions` | Parameter descriptions not checked |
| `test_dynamic_system_and_contradiction` | Dates or placeholders in the system prompt not detected |
| `test_errors_sort_before_warnings` | Findings sorted by rule only, so warnings mix with errors |
| `test_render` | Escaped braces substituted; only the first missing value reported |
| `test_boundary_render_inserts_values_verbatim` | `render` escapes or strips values; the spec inserts them verbatim |
