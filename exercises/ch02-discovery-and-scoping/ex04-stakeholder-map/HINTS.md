# ex04 hints · Stakeholder map, RACI and comms plan

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`quadrant` is four `if` statements, and the order matters: check the case where *both* thresholds hold before the
single-threshold cases. `comms_plan` then reuses it, with a dict from quadrant to `(cadence, channel)`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Validate RACI in two passes:

1. **Per stakeholder entry:** flag workstreams that aren't in the list and letters that aren't one of `R A C I`.
2. **Per workstream:** collect `s.raci.get(ws)` for every stakeholder, then count the `A`s and `R`s.

Sort the comms plan with a key of `(-influence, name)`, so you get influence descending and names ascending in one
sort.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

The test checks message wording by substring, so word your messages so they contain:

- the phrase `one A` for the accountability rule (for example, "needs exactly one A");
- the letter `R` and the workstream name for the responsibility rule;
- the bad letter in quotes, such as `'X'`;
- the unknown workstream's name.

On the sample data, exactly one issue is expected: `security` has no `R`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_quadrants` | Checking `influence >= 4` before checking both thresholds, so "manage closely" is never reached |
| `test_raci_missing_responsible` | Extra issues reported, or the message doesn't name the workstream |
| `test_raci_two_accountable_unknown_letter_unknown_ws` | Message wording: needs `one A`, the quoted letter `'X'` and the workstream `legal` |
| `test_comms_plan` | Sorting by influence ascending, or breaking ties by role instead of name |
