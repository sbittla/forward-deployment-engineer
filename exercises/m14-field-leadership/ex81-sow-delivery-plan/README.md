# ex81 · Statement of work and delivery plan with critical path

**Module:** m14 Field Leadership · **Covers:** R33 Delivery management & SOW, R30 Value, R18 Scoping · **Time:** 75 min

## Learning objectives
- Estimate tasks with PERT and schedule them with the critical path method.
- Produce P50/P90 estimates and dated milestones on working days.
- Render a SOW with deliverables and acceptance criteria.

## Scenario
OpenAI's Deployment Lead and Anthropic's Staff FDE postings both ask you to "scope the work, sequence it" and
"prepare detailed scopes of work and project plans for both proof-of-concept prototypes and full production
deployments". The customer's procurement team won't sign until they see a SOW with deliverables, acceptance
criteria, a dated timeline and an honest estimate range.

## Your task
Tasks: `Task(id, name, optimistic, likely, pessimistic, depends_on=(), owner="fde", milestone=None)` (durations in
working days).

1. `pert(task) -> (expected, stdev)` with `expected = (o + 4m + p) / 6`, `stdev = (p - o) / 6`, rounded to 2 dp.
2. `schedule(tasks) -> dict[id, Slot(start, finish, slack, critical)]` using the critical path method on
   **expected** durations (day 0 = project start): earliest start = max finish of dependencies; latest times from a
   backward pass; `slack = latest_start - earliest_start` (2 dp); `critical = slack == 0`. Unknown dependencies or
   cycles raise `ValueError`.
3. `critical_path(tasks) -> list[id]`: critical task ids ordered by start (ties by id).
4. `project_estimate(tasks) -> (p50_days, p90_days)`: P50 = sum of expected along the critical path; P90 = P50 +
   1.2816 × sqrt(sum of variances on the critical path). Round to 1 dp.
5. `to_dates(day_offset, start: date) -> date`: count working days (Mon–Fri) from `start`; offset 0 is `start`
   itself (move forward to Monday if it falls on a weekend).
6. `render_sow(engagement, tasks, start, rate_per_day)` → markdown with headings, in order: `Objectives`,
   `In scope`, `Out of scope`, `Deliverables and acceptance criteria` (table `| Milestone | Due | Acceptance
   criteria |`; every milestone in the tasks must have acceptance criteria in `engagement["acceptance"]`, otherwise
   raise `ValueError`), `Timeline` (critical path), `Assumptions`, `Customer responsibilities`, `Change control`,
   `Estimate` (`P50: N days ($X)` and `P90: N days ($Y)`, money with thousands separators, rounded to the dollar).
   Milestone due date = the finish date of the task tagged with it (finish day offset, rounded up, minus 1 → working
   day date).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Statement of work and delivery plan
with critical path". Before I write code, teach me statements of work, PERT estimation, critical path scheduling,
slack, and communicating estimate ranges to procurement. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m14-field-leadership/ex81-sow-delivery-plan/starter.py so that test_sow.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Task`, `Slot`,
`pert`, `schedule`, `critical_path`, `project_estimate`, `to_dates`, `render_sow`. Constraints: Python 3.11+, the
standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify
the tests or fde_kit. When you're done, run `pytest exercises/m14-field-leadership/ex81-sow-delivery-plan` and show
me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Statement of work and delivery plan with critical path" as a senior forward deployed engineer
would before it ships to a customer. Specifically: Are cycles and unknown dependencies rejected? Is the backward
pass correct for tasks with no successors? Would a customer sign this SOW, and what is missing? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
