# ex07 · RAID log: risks, assumptions, issues, decisions

**Module:** m01 · **Covers:** R20 Ownership, R30 Engagement delivery · **Time:** 40 min

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
