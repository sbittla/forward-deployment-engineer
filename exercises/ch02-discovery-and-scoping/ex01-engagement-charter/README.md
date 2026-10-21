# ex01 · Engagement charter from discovery notes

**Chapter:** 2 · Discovery and Scoping (`exercises/ch02-discovery-and-scoping/`) · **Covers:** R18 Customer discovery, R30 Value metrics, R19 Stakeholder communication

## Learning objectives
- Turn messy discovery notes into a charter an executive sponsor can sign.
- Make success measurable: every metric needs a numeric baseline and target.
- Use validation gaps (no sponsor, no out-of-scope list) as your next discovery questions.

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
- `pytest exercises/ch02-discovery-and-scoping/ex01-engagement-charter` passes.
- A charter with zero issues renders a table row per metric.

## Hints
- `re.split(r"^## ", text, flags=re.M)` gets you sections quickly.
- Numbers may be decimals (`3.5 days`). Units are whatever follows the target number.

## Field notes
A charter is a forcing function: if you cannot fill in a measurable baseline, you have found your next discovery
question. Bring the unmeasurable list to the sponsor meeting rather than guessing.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch02-discovery-and-scoping/ex01-engagement-charter`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch02-discovery-and-scoping/ex01-engagement-charter`: all 5 pass.
- **Tests:** `test_charter.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The validator checks that a charter's fields are present and numeric, not that the
  baselines were measured or the sponsor agreed. A real charter also needs data access, acceptance criteria, owners
  and a stop/go decision, and only counts once the named sponsor has signed it.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Engagement charter from discovery
notes". Before I write code, teach me what an engagement charter is for, why pilots without a named sponsor,
measurable baselines and an explicit out-of-scope list stall, and how to turn a vague goal like "make claims faster"
into a metric with a baseline, target and unit. Use short Python examples that are not the exercise solution. Then
ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch02-discovery-and-scoping/ex01-engagement-charter/starter.py so that test_charter.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Metric`, `Charter`, `parse_notes`, `validate`, `render`. Constraints: Python 3.11+, the standard library and the
repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When
you're done, run `pytest exercises/ch02-discovery-and-scoping/ex01-engagement-charter` and show me the output. If the
README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Engagement charter from discovery notes" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Does the parser survive real notes (en dash vs em dash, decimals like 3.5
days, extra blank lines)? Are validation messages specific enough to read aloud in a sponsor meeting? What would a
sponsor misread in the rendered charter? Rank findings by customer impact, quote the line for each, and say which
ones a test should catch.
```
