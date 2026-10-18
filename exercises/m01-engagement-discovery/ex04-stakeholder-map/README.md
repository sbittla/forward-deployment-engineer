# ex04 · Stakeholder map, RACI and comms plan

**Module:** m01 · **Covers:** R19 Stakeholder communication, R20 Ownership · **Time:** 40 min

## Scenario
Your pilot has 9 stakeholders across Claims, IT Security, Legal and Procurement. Two weeks in, Legal surprises
you with a review nobody scheduled. You will build the tool that would have prevented it.

## Your task
`Stakeholder(name, role, influence, interest, raci)` — influence/interest are 1–5; `raci` maps
workstream → one of `"R" "A" "C" "I"`.

1. `quadrant(s)` → `"manage closely"` (influence ≥ 4 and interest ≥ 4), `"keep satisfied"` (influence ≥ 4),
   `"keep informed"` (interest ≥ 4), else `"monitor"`.
2. `validate_raci(stakeholders, workstreams)` → list of issues: each workstream needs **exactly one** `A` and
   **at least one** `R`; unknown letters are issues; RACI entries for unknown workstreams are issues.
3. `comms_plan(stakeholders)` → list of `(name, quadrant, cadence, channel)` sorted by influence desc then name.
   Cadence: manage closely → `weekly` / `1:1`; keep satisfied → `biweekly` / `exec summary`;
   keep informed → `weekly` / `status email`; monitor → `monthly` / `newsletter`.

## Field notes
An unowned workstream (no `A`) is a risk you own until someone else does. Raise it in the next steering meeting.
