# ex46 hints · Planner/worker agents with human approval

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Split `plan` into three stages: parse the planner's JSON into `Step` objects, validate them, then order them. Write
the ordering as its own loop: repeatedly pick the first step (in the original order) whose dependencies are all
already placed.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Validation:** collect the set of ids. Raise `ValueError` if any step names a worker that isn't in `workers`, or
  depends on an id that isn't in the set.
- **Topological order (Kahn's idea, kept stable):** while steps remain, `ready` = unplaced steps whose `depends_on` is
  a subset of the placed set. If `ready` is empty, there's a cycle. Otherwise place `ready[0]`.
- **run:** walk the ordered steps, and decide each status in a fixed order: blocked (any dependency not `done`) →
  `skipped`; needs approval and not approved → `rejected`; otherwise run the worker.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Only ask for approval when the step isn't blocked. A skipped step must never reach the human, so the audit log has
  no "approval requested" line for it.
- Audit order matters: `s4: approval requested` comes before `s4: rejected`.
- The worker's context is `{dep_id: output}` for that step's dependencies only, not every output so far.
- A worker exception becomes `failed` with the output `"<ExceptionType>: <message>"`, and every step that depends on it
  is skipped.
- The system prompt must list the worker names. Sorting them keeps it deterministic.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_plan_topological_and_prompt` | Order not stable (ready steps not taken in original order); worker names missing from the system prompt |
| `test_plan_validation` | Cycle not detected, so the loop never ends or silently drops steps |
| `test_run_approved` | Context includes every output instead of only the step's dependencies; approval asked for steps that don't need it |
| `test_run_rejected_and_failure_cascade` | Skipped steps still asked for approval; audit lines out of order; exception text format differs |
| `test_boundary_approval_follows_plan_flag` | Approval asked for a step whose `requires_approval` is false, or an unasked step not run |
| `test_policy_approval_overrides_plan_flag` | Only the plan's `requires_approval` flag consulted; `always_approve` ignored |
| `test_approval_fails_closed` | Truthiness used instead of `is True`; an exception from `approve` crashes the run or approves |
| `test_failed_step_has_no_downstream_side_effects` | Dependents of a failed step run or are asked for approval; the failure's output not recorded |
