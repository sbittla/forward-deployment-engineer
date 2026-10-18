# ex05 · Weekly status report generator

**Module:** m01 · **Covers:** R19 Stakeholder communication, R30 Engagement delivery · **Time:** 40 min

## Learning objectives
- Compute a project's RAG status from tracker data instead of gut feel.
- Write a status note executives can read in three lines: status, risks, asks.
- Handle date windows and empty sections without misleading the reader.

## Scenario
Every Friday the customer's sponsor gets a status note. Hand-writing it takes an hour and drifts from reality.
Generate it from the task tracker export so the RAG status is computed, not felt.

## Your task
Tasks are dicts: `title, owner, due (YYYY-MM-DD), status (done|in_progress|blocked|not_started)`, and
optional `completed (YYYY-MM-DD)`, `ask` (a request for the customer).

1. `overall_status(tasks, today) -> "red"|"amber"|"green"`
   - **red**: any blocked task due within 7 days (or already overdue), or ≥ 3 overdue non-done tasks
   - **amber**: any overdue non-done task, or any blocked task
   - **green**: otherwise
2. `render(tasks, today, project) -> str` with sections in order:
   `# <project> — status <YYYY-MM-DD>`, `**Overall: RED|AMBER|GREEN**`, `## Done this week` (completed in the last
   7 days, inclusive), `## Next up` (not done, due in next 14 days, sorted by due), `## Risks & blockers`
   (blocked or overdue, with owner), `## Asks` (all non-empty `ask` values). Empty sections show `- none`.

## Field notes
Lead with the ask. Executives read the first three lines.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Weekly status report generator".
Before I write code, teach me how to define red/amber/green rules from task data, how to structure a weekly status
note for an executive sponsor, and why the ask should come first. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m01-engagement-discovery/ex05-status-report/starter.py so that test_status.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`overall_status`, `render`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m01-engagement-discovery/ex05-status-report` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Weekly status report generator" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are the 7-day and 14-day windows inclusive exactly as specified? Could a blocked task
appear twice? Would the sponsor understand the note without opening the tracker? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
