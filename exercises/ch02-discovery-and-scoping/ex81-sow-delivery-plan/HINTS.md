# ex81 hints · Statement of work and delivery plan with critical path

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Before scheduling anything, put the tasks in dependency order. Validate the dependencies (unknown ids raise
`ValueError`), then repeatedly take every task whose dependencies are all done. If a round finds nothing ready, there's
a cycle. Both passes of the critical path method walk this ordered list: forwards, then backwards.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Forward pass:** a task's earliest start is the latest earliest-finish of its dependencies (0 if it has none).
  Earliest finish = start + expected duration.
- **Backward pass:** project end = the largest earliest finish. Walking the order in reverse, a task's latest finish is
  the smallest latest-start among its successors (or the project end if it has none). Latest start = latest finish −
  duration.
- `slack = latest start - earliest start`, and critical means a slack of 0. Compare with a small tolerance, because
  the durations are floats.
- **P90:** add up the *variances* (stdev squared) along the critical path, take the square root, and multiply by 1.2816.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Use unrounded expected durations inside the passes, and round only the reported slots. Rounding each step adds
  drift.
- `to_dates`: first move a weekend start forward to Monday, then step one calendar day at a time, counting only
  weekdays, until you've counted the offset.
- Milestone due date = working day `ceil(finish) - 1`, so a task finishing at day 3.0 is due on working day 2.
- Check that every milestone has acceptance criteria **before** rendering anything, and raise if one doesn't.
- Money uses `f"${round(x):,}"`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_pert` | Weights wrong (the formula is `o + 4m + p` over 6), or not rounded |
| `test_schedule_and_critical_path` | Backward pass uses successors' earliest starts; slack compared with `== 0` on unrounded floats |
| `test_estimate` | Standard deviations summed instead of variances |
| `test_cycles_and_unknown` | A cycle loops forever; unknown dependency raises `KeyError` instead of `ValueError` |
| `test_working_days` | Weekend start not moved to Monday; weekends counted |
| `test_render_sow` | Headings out of order; due-date offset off by one; money not formatted with commas |
| `test_missing_acceptance` | Missing criteria detected too late or silently skipped |
| `test_render_sow_rejects_unmeasurable_acceptance_criteria` | Vague words matched as substrings, or a criterion with a number rejected; the error doesn't name the milestone |
