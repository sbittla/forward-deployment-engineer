# ex05 · Weekly status report generator

**Module:** m01 · **Covers:** R19 Stakeholder communication, R30 Engagement delivery · **Time:** 40 min

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
