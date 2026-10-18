# ex81 · Statement of work and delivery plan with critical path

**Module:** m14 Field Leadership · **Covers:** R33 Delivery management & SOW, R30 Value, R18 Scoping · **Time:** 75 min

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
