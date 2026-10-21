# ex05 · Weekly status report generator

**Chapter:** 3 · Technical Communication (`exercises/ch03-technical-communication/`) · **Covers:** R19 Stakeholder communication, R30 Engagement delivery

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
   `# <project> — status <YYYY-MM-DD>`, `**Overall: RED|AMBER|GREEN**`, `## Asks` (all non-empty `ask` values), `## Done this week` (completed in
   the last 7 days, inclusive), `## Next up` (not done, due in next 14 days, sorted by due), `## Risks & blockers`
   (blocked or overdue, with owner). Empty sections show `- none`.

## Field notes
Lead with the ask. Executives read the first three lines.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch03-technical-communication/ex05-status-report`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch03-technical-communication/ex05-status-report`:
  all 8 pass.
- **Tests:** `test_status.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The tracker export is trusted and complete, and the RAG rules are fixed in code. A
  production generator reads the tracker through a read-only API token, records which version of the rules the
  sponsor agreed, and has a person check every number (above all in AI-drafted prose) before the note is sent.

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
Implement exercises/ch03-technical-communication/ex05-status-report/starter.py so that test_status.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`overall_status`, `render`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch03-technical-communication/ex05-status-report` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Weekly status report generator" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are the 7-day and 14-day windows inclusive exactly as specified? Could a blocked task
appear twice? Would the sponsor understand the note without opening the tracker? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
