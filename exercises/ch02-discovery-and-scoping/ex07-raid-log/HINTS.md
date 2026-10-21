# ex07 hints · RAID log: risks, assumptions, issues, decisions

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Define `RaidItem` as a dataclass whose optional fields all have defaults (`owner=""`, `probability=None`,
`status="open"`, `id=""` and so on), because the tests construct items with only a few keywords. Then write `add`:
validate, assign the id, append.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **IDs** use one global counter across all kinds: the next id is the kind letter plus `len(items) + 1`.
- **Validation** raises `ValueError` for each rule. For risks, check that probability and impact are ints from 1 to
  5 *and* that there's a mitigation.
- A private helper that returns open items, optionally filtered by kind, makes `top_risks`, `overdue` and
  `escalations` one-liners.
- `top_risks` sorts by `(-score, created)`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `escalations` must not list an item twice. Collect into a dict keyed by id, then sort.
- Sort escalations by the **number** after the dash. As strings, `"R-10"` sorts before `"R-2"`.
- "More than 3 days overdue" means `today - due > timedelta(days=3)`: an issue due on the 10th escalates on the 16th
  but not on the 12th.
- Closed items never appear in `top_risks`, `overdue` or `escalations`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_ids` | Separate counter per kind (`R-1, A-1…`) instead of one global counter |
| `test_validation` | A rule missing: probability out of range, missing mitigation, decision without `decided_by`, or no owner |
| `test_top_risks` | `score` returns `None` for non-risks instead of 0, or the sort is ascending |
| `test_overdue_and_escalations` | Closed risk still escalated; boundary uses `>=` 3 days; ids sorted as strings |
| `test_markdown` | Type column shows `R` instead of `Risk`, or rows aren't in id order |
