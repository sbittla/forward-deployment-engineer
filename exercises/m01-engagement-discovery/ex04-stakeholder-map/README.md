# ex04 · Stakeholder map, RACI and comms plan

**Module:** m01 · **Covers:** R19 Stakeholder communication, R20 Ownership · **Time:** 40 min

## Learning objectives
- Classify stakeholders by influence and interest and plan communication cadence.
- Validate a RACI so every workstream has exactly one accountable owner.
- Spot unowned work early and raise it before it becomes a surprise review.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Stakeholder map, RACI and comms
plan". Before I write code, teach me power/interest stakeholder mapping, RACI rules (exactly one A, at least one R),
and how an FDE uses a comms plan to avoid late surprises from Legal, Security or Procurement. Use short Python
examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a time,
and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m01-engagement-discovery/ex04-stakeholder-map/starter.py so that test_stakeholders.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Stakeholder`, `quadrant`, `validate_raci`, `comms_plan`. Constraints: Python 3.11+, the standard library and the
repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When
you're done, run `pytest exercises/m01-engagement-discovery/ex04-stakeholder-map` and show me the output. If the
README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Stakeholder map, RACI and comms plan" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does RACI validation catch a workstream with two A's and one with none in the
same run? Is the comms plan ordering deterministic? Which real stakeholder situation does this model miss? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
