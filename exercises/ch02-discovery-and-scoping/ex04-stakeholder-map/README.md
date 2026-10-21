# ex04 · Stakeholder map, RACI and comms plan

**Chapter:** 2 · Discovery and Scoping (`exercises/ch02-discovery-and-scoping/`) · **Covers:** R19 Stakeholder communication, R20 Ownership

## Learning objectives
- Classify stakeholders by influence and interest and plan communication cadence.
- Validate a RACI so every workstream has exactly one accountable owner.
- Spot unowned work early and raise it before it becomes a surprise review.

## Scenario
Your pilot has 9 stakeholders across Claims, IT Security, Legal and Procurement. Two weeks in, Legal surprises
you with a review nobody scheduled. You will build the tool that would have prevented it.

## Your task
`Stakeholder(name, role, influence, interest, raci)` — influence/interest are 1–5; `raci` maps
workstream → one of `"R" "A" "C" "I"`.

1. `quadrant(s)` → `"manage closely"` (influence ≥ 4 and interest ≥ 4), `"keep satisfied"` (influence ≥ 4),
   `"keep informed"` (interest ≥ 4), else `"monitor"`.
2. `validate_raci(stakeholders, workstreams)` → list of issues: each workstream needs **exactly one** `A` and
   **at least one** `R`; unknown letters are issues; RACI entries for unknown workstreams are issues.
3. `comms_plan(stakeholders)` → list of `(name, quadrant, cadence, channel)` sorted by influence desc then name.
   Cadence: manage closely → `weekly` / `1:1`; keep satisfied → `biweekly` / `exec summary`;
   keep informed → `weekly` / `status email`; monitor → `monthly` / `newsletter`.

## Field notes
An unowned workstream (no `A`) is a risk you own until someone else does. Raise it in the next steering meeting.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch02-discovery-and-scoping/ex04-stakeholder-map`.
- **Expected output:** all 4 tests fail against the starter; when you're done, all 4 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch02-discovery-and-scoping/ex04-stakeholder-map`:
  all 4 pass.
- **Tests:** `test_stakeholders.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Influence and interest scores are judgements, and the map is only as current as its last
  review. In an engagement, agree the RACI with the sponsor, keep it with the RAID log and re-score stakeholders when
  the project changes phase.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Stakeholder map, RACI and comms
plan". Before I write code, teach me power/interest stakeholder mapping, RACI rules (exactly one A, at least one R),
and how an FDE uses a comms plan to avoid late surprises from Legal, Security or Procurement. Use short Python
examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a time,
and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch02-discovery-and-scoping/ex04-stakeholder-map/starter.py so that test_stakeholders.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Stakeholder`, `quadrant`, `validate_raci`, `comms_plan`. Constraints: Python 3.11+, the standard library and the
repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When
you're done, run `pytest exercises/ch02-discovery-and-scoping/ex04-stakeholder-map` and show me the output. If the
README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Stakeholder map, RACI and comms plan" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does RACI validation catch a workstream with two A's and one with none in the
same run? Is the comms plan ordering deterministic? Which real stakeholder situation does this model miss? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
