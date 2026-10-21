# Capstone 6 hints · Deployment Lead: a partner-delivered, multi-workstream engagement

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

This capstone assembles five exercises into one decision. Build the inputs first, and the decision last:

| Order | Module | Reuse |
|---|---|---|
| 1 | `plan.py` | ex81 PERT and critical path |
| 2 | `reviews.py` | ex90 design review and gate |
| 3 | `adoption.py` | ex82 funnel and diff-in-diff |
| 4 | `security.py` | ex83 questionnaire responder |
| 5 | `readiness.py` | blockers and conditions |
| 6 | `steering.py` | ex05 status report |

Each module has its own test. `test_c6_plan.py` doesn't depend on anything else, so start there.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Forecast:** the remaining duration of each task is its expected duration × (1 − reported progress). Re-run the
  same CPM schedule with those durations, starting at `as_of_day`. The slip is the forecast finish minus the baseline
  finish.
- **Workstream RAG:** for each task, planned progress today = how far through its baseline window you are (clamped to
  0–1). The variance is the effort-weighted average of actual minus planned. Thresholds are in the starter docstring.
- **Go-live:** blockers (rejected deliverables, open security questions, slip beyond the limit) mean NO_GO; otherwise
  conditions (conditional deliverables, activation under 60%, weak impact) mean GO_WITH_CONDITIONS; otherwise GO.
  Each blocker and condition is a readable sentence.
- **Steering update:** generate it entirely from those computed values. Nothing typed in by hand. Lead with
  the decisions needed (every blocker and condition), then the status line: a committee that reads only the top
  should still know what it has to decide.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `schedule` takes a `durations` override and an `offset`, so the baseline and the forecast share one implementation.
  Tasks without dependencies start at the offset.
- A workstream can look green on average while a **critical-path** task in it is behind. That bumps it to amber. This
  is why the UI, which is off the critical path, stays green.
- Security questions about physical security or model risk always go to humans, however well a rule matches.
  Questions are matched with the same stem rules as ex83.
- The partner gate reasons come straight from ex90's `gate`, in its order: reject reasons first, then conditional
  ones.
- The memo must name the rejected deliverable (`D-fe-1`) and a concrete re-review date, and the SOW needs
  **Partner responsibilities**, **Support boundaries** and **Exit criteria** sections. You set the quality bar for work you don't build.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_baseline` | Critical path not ordered by start; P90 summing standard deviations instead of variances |
| `test_forecast_and_slip` | Forecast schedule starts at day 0 instead of `as_of_day`; progress applied to the baseline |
| `test_rag` | Planned progress not clamped; variance not weighted by effort; critical-path bump missing |
| `test_next_milestone` | Milestones ordered by listing instead of baseline finish; forecast day taken from the baseline instead of the re-planned schedule; a finished milestone still returned |
| `test_cycle_rejected` | Cycle loops forever instead of raising |
| `test_partner_reviews` | Design checklist severities or gate reason order differ from ex90 |
| `test_adoption_and_impact` | Funnel or diff-in-diff arithmetic (see ex82) |
| `test_security_gate` | Physical or model-risk questions auto-answered; status not `open` when anything is unanswered |
| `test_go_live` | Conditions reported as blockers; GO returned with conditions still present |
| `test_steering_update` | Numbers typed in instead of computed; table rows differ; sections not in Section 16.3's order (decision first, next milestone last) |
| `test_steering_changes_risks_and_next_milestone` | Last week's RAG not recomputed from `last_week` with the same `workstream_rag`; closed RAID items shown; a missing owner or date hidden instead of shown as UNASSIGNED or NO DATE |
| `test_deliverable` | A required heading missing (the SOW's support boundaries and exit criteria too), a placeholder left in, `D-fe-1` or a date missing from the memo, or no percentages |
