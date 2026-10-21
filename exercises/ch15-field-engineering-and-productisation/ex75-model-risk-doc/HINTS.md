# ex75 hints · Model risk documentation for a regulated customer

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`risk_tier` and `required_controls` are a few lines each. Store the controls as a dict from tier to the controls that
tier *adds*, then build the list by walking tiers 3, 2, 1 and including each level at or above the requested risk.
`render` reuses all the other functions.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **validate:** treat required keys and the three boolean flags differently. A required key is missing if it's absent
  *or* empty (`not meta.get(k)`). A flag is missing only if it's absent, because `False` is a valid answer.
- Add the eval threshold check, then the tier-1 oversight check (the text must mention "review" or "approve").
- **render:** build a list of lines section by section, in the exact heading order. A `_bullets(items)` helper that
  returns `- none` for an empty list keeps the sections tidy.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Don't use `not meta.get(flag)` for the booleans, or `regulated_domain: False` is reported as missing.
- Automated decision with neither customer-facing nor regulated is tier **2**, not 1.
- Eval status is `PASS` when `value >= threshold`. A 0.0 safety value with a 0.0 threshold passes.
- The approval line counts every issue, so one failing eval gives `Status: BLOCKED (1 issues)`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_tiers` | Tier 1 condition doesn't require `automated_decision` |
| `test_controls` | Controls not cumulative, or out of order |
| `test_validate` | `False` flags reported as missing; empty list `limitations` not reported |
| `test_render` | A heading missing or out of order; status line wording differs |
