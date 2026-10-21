# ex98 hints · System prompt from a policy spec, with traceability

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Copy the `EXPECTED` string from the test into a scratch file and build `build_system_prompt` to match it line for
line. Write the line list explicitly: the role block, a blank line, the `<policies>` opener, the policy lines, the
closer, a blank line, the conflict sentence, a blank line, and the output format block. Then join with `\n`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **load_policies:** validate in the order the README lists: id format, duplicate, kind, empty rule. Store `tests` as
  a tuple, because the dataclass is frozen.
- **Policy lines:** loop over `KINDS` in order, and within each kind over the policies in input order. The prefix comes
  from a kind → word map (`Always`, `Never`, `Hand off to a human when`).
- **run_conformance:** generate the cases, call the model once per case with the compiled prompt as the system prompt,
  and compare case-insensitively for missing and leaked strings.
- **diff_policies:** set arithmetic on ids; "changed" compares `(kind, rule)` only.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- POL-2 comes before POL-1 in the input but after it in the prompt. Grouping by kind reorders the policies, and that's
  what the exact-match test checks.
- Don't double the full stop: strip a trailing `.` from `why` before adding your own, and add ` Why: …` only when there
  is a `why`.
- Escape the rule and the why with `html.escape(..., quote=False)`, so a customer's rule can't break the XML structure.
- `by_policy` is True only if **all** of that policy's cases passed. Policies without tests go in `untested`, not in
  `by_policy`.
- A reworded `why` alone isn't a change. The rule's meaning didn't move, so its conformance tests don't need rerunning.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_load_validates` | One of the four validations missing; input order changed |
| `test_build_prompt_exact` | Policies in input order instead of grouped by kind; doubled full stop; blank lines misplaced |
| `test_rules_are_escaped` | Rule inserted without HTML escaping |
| `test_trace_and_coverage` | Trace looks for the id anywhere instead of the exact `<policy id="…">` tag |
| `test_generate_cases` | Case numbers 0-based, or global instead of per policy |
| `test_run_conformance` | Case-sensitive comparison; untested policies included in `by_policy` |
| `test_diff_policies` | Changes to `why` reported as changes; lists not sorted |
