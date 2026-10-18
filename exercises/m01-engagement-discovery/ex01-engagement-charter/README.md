# ex01 · Engagement charter from discovery notes

**Module:** m01 Engagement & Discovery · **Covers:** R18 Customer discovery, R30 Value metrics, R19 Stakeholder communication · **Time:** 45 min

## Scenario
You just finished your first on-site discovery day with *Northwind Insurance*. Your notes are messy markdown.
Before anyone writes a line of model code, the FDE lead wants a one-page **engagement charter** that the
customer's executive sponsor can sign. Charters that lack a sponsor, vague success metrics ("make claims faster")
or an explicit out-of-scope list are the #1 cause of pilots that never reach production.

## Your task
Implement in `starter.py`:

1. `parse_notes(text) -> Charter` — parse notes with `## Customer`, `## Problem`, `## Stakeholders`,
   `## Success metrics`, `## Constraints`, `## Out of scope` sections.
   - Stakeholder lines look like `- Dana Ruiz — VP Claims (exec sponsor)` (em dash or `-` separator).
   - Metric lines look like `- Average handle time: 11 min -> 7 min`. Parse name, baseline, target, unit.
     A metric with no numbers (`- Happier adjusters`) is still captured with `baseline=None, target=None`.
2. `validate(charter) -> list[str]` — return human-readable issues:
   - missing problem statement
   - no stakeholder whose role contains "sponsor"
   - any metric without numeric baseline **and** target (`"metric 'X' is not measurable"`)
   - empty out-of-scope list
3. `render(charter) -> str` — markdown with a heading per section and a metrics table
   (`| Metric | Baseline | Target | Unit |`).

## Acceptance criteria
- `pytest exercises/m01-engagement-discovery/ex01-engagement-charter` passes.
- A charter with zero issues renders a table row per metric.

## Hints
- `re.split(r"^## ", text, flags=re.M)` gets you sections quickly.
- Numbers may be decimals (`3.5 days`). Units are whatever follows the target number.

## Field notes
A charter is a forcing function: if you cannot fill in a measurable baseline, you have found your next discovery
question. Bring the unmeasurable list to the sponsor meeting rather than guessing.
