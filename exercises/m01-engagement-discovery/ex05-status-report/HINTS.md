# ex05 hints · Weekly status report generator

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write two small helpers before anything else: one that turns `"YYYY-MM-DD"` into a `date`, and one that says whether a
task is overdue (not done, and due before today). Both functions use them over and over.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **overall_status:** build the overdue list and the blocked list, then check red, then amber, then green, in that
  order. Red means a blocked task due on or before `today + 7 days`, or three or more overdue tasks.
- **render:** build each section as a list of lines, then join them. A small helper that returns the heading plus
  the items, or `- none` when the list is empty, keeps the four sections consistent.
- "Done this week" is an inclusive window from `today - 7 days` to `today` on `completed`, not on `due`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A blocked task that is already overdue is due *before* today, so the "due within 7 days" check covers it: use
  `due <= today + 7`, with no lower bound.
- "Next up" sorts by due date. ISO date strings sort correctly as strings, so you can sort on the raw `due` value.
- The title line uses an em dash: `# Claims Copilot — status 2026-10-16`.
- A done task with no `completed` date is never "done this week".
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_green` | Counting the done task as overdue because its due date has passed |
| `test_amber_blocked_far_out` | Every blocked task treated as red, ignoring the 7-day window |
| `test_amber_one_overdue` | Overdue check uses `<=` instead of `<` |
| `test_red_blocked_soon` | Window computed from the creation date or with the wrong sign |
| `test_red_three_overdue` | Threshold off by one (`> 3` instead of `>= 3`) |
| `test_render` | Sections out of order; "Done this week" filtered on `due`; "Next up" includes tasks more than 14 days out |
| `test_render_empty_sections` | Empty sections omitted instead of showing `- none` |
| `test_no_tasks_is_green` | Code parses `today` or touches tasks before checking there are any |
