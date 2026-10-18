# ex07 · RAID log: risks, assumptions, issues, decisions

**Module:** m01 · **Covers:** R20 Ownership, R30 Engagement delivery · **Time:** 40 min

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
Implement exercises/m01-engagement-discovery/ex07-raid-log/starter.py so that test_raid.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `RaidItem`,
`RaidLog`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed
where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m01-engagement-discovery/ex07-raid-log` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "RAID log: risks, assumptions, issues, decisions" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Can an item be added without an owner through any path? Are escalations
de-duplicated and stable? What would you add so a decision can be found six months later? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
