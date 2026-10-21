# ex84 · Workshop, code-with session and knowledge-transfer readiness

**Chapter:** 3 · Technical Communication (`exercises/ch03-technical-communication/`) · **Covers:** R35 Customer enablement & teaching, R24 Enablement material, R19 Communication ·
**Time:** 60 min

## Learning objectives
- Plan a hands-on enablement day with concept, demo, lab and checks.
- Validate lab steps so every step has an observable result.
- Measure knowledge-transfer readiness per person and objective.

## Scenario
Deloitte hires "Technical AI Instructor and Forward Deployed Engineers". Accenture FDEs run "code-with sessions".
AHEAD's FDEs "train operators and stay until the control plane is working". Palantir has a whole Forward Deployed
Enablement track. Every one of those ends in the same test: **can the customer run it without you?** You'll build
the tool that plans a hands-on enablement day and measures whether knowledge transfer actually happened.

## Your task
1. `build_agenda(objectives, start="09:00", total_minutes=360)`: each objective is
   `{"id", "title", "concept_min", "demo_min", "lab_min"}`. For each objective, schedule `concept`, `demo`,
   `lab` and a 5-minute `check` (knowledge check), in that order. Insert a 15-minute `break` whenever 90 or more
   minutes have run since the start or the last break, but only between objectives, and never after the last one.
   Raise `ValueError` if the agenda exceeds `total_minutes` or an objective has no lab
   (`lab_min <= 0`: a workshop without hands-on is a lecture). Return
   `[(start "HH:MM", end "HH:MM", kind, objective_id or None)]`.
2. `lab_steps_valid(steps)`: every lab step is `{"instruction", "verify"}`; return the indices of steps whose
   `verify` is empty or doesn't contain a command or observable result (it must contain a backtick-quoted command
   or one of the words `expect`, `see`, `returns`, `shows`).
3. `readiness(participants, objectives, pass_mark=0.8)`: participants are `{"name", "quiz": {objective_id: score
   0..1}, "labs_done": [objective_id]}`. A participant is *ready* on an objective if quiz ≥ pass_mark **and** the lab
   is done. Return `{"per_person": {name: share of objectives ready (2 dp)}, "uncovered": [objective ids where
   nobody is ready], "can_operate_without_fde": bool}`. The last is True when every objective has at least **two**
   ready people (no single points of failure).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch03-technical-communication/ex84-workshop-builder`.
- **Expected output:** all 4 tests fail against the starter; when you're done, all 4 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch03-technical-communication/ex84-workshop-builder`: all 4 pass.
- **Tests:** `test_workshop.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Readiness rests on a quiz score and a self-reported lab flag. In production, confirm each
  lab from an observable result, keep participants' scores under the customer's HR and privacy rules, and report
  readiness by objective rather than ranking individuals.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Workshop, code-with session and
knowledge-transfer readiness". Before I write code, teach me designing technical workshops and code-with sessions,
lab design, knowledge checks, and readiness criteria for handover. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch03-technical-communication/ex84-workshop-builder/starter.py so that test_workshop.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`build_agenda`, `lab_steps_valid`, `readiness`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch03-technical-communication/ex84-workshop-builder` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Workshop, code-with session and knowledge-transfer readiness" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Are breaks inserted only between objectives? Is a step
with a vague 'verify' caught? Would the readiness report convince you the customer can run the system without you?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
