# ex07 · RAID log: risks, assumptions, issues, decisions

**Chapter:** 2 · Discovery and Scoping (`exercises/ch02-discovery-and-scoping/`) · **Covers:** R20 Ownership, R30 Engagement delivery

## Learning objectives
- Maintain a RAID log that makes risk visible and decisions traceable.
- Score and escalate risks consistently (probability × impact, overdue issues).
- Enforce ownership and rationale at the point of entry.

## Scenario
FDEs own outcomes, not tickets. A RAID log is how you make risk visible early and decisions traceable later
("why did we pick the managed vector DB?" — six months on, someone will ask).

## Your task
Implement `RaidLog` in `starter.py`:

- `add(item)` validates and stores a `RaidItem`; raise `ValueError` when:
  - `kind` not in `R A I D`
  - a **risk** lacks `probability` and `impact` in 1–5 or lacks a `mitigation`
  - a **decision** lacks `rationale` or `decided_by`
  - any item lacks an `owner`
- `score(item)` → `probability * impact` for risks, else 0.
- `top_risks(n)` → open risks by score desc, then created asc.
- `overdue(today)` → open items with `due < today`.
- `escalations(today)` → open risks with score ≥ 15, plus open issues more than 3 days overdue; no duplicates;
  sorted by id.
- `to_markdown()` → a table `| ID | Type | Title | Owner | Score | Status |` with one row per item in id order.

IDs are assigned on `add` as `R-1, A-2, I-3, D-4…` (prefix = kind, global counter).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch02-discovery-and-scoping/ex07-raid-log`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch02-discovery-and-scoping/ex07-raid-log`: all 9
  pass.
- **Tests:** `test_raid.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The log lives in memory with no persistence, history or access control, and the escalation
  thresholds are examples. A production RAID log needs a shared, audited store, thresholds agreed with the sponsor
  and a regular review in the steering meeting.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "RAID log: risks, assumptions,
issues, decisions". Before I write code, teach me what risks, assumptions, issues and decisions are, how to score
risks, when to escalate, and why decision records need a rationale and a decider. Use short Python examples that are
not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to
re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch02-discovery-and-scoping/ex07-raid-log/starter.py so that test_raid.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `RaidItem`,
`RaidLog`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed
where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch02-discovery-and-scoping/ex07-raid-log` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "RAID log: risks, assumptions, issues, decisions" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Can an item be added without an owner through any path? Are escalations
de-duplicated and stable? What would you add so a decision can be found six months later? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
