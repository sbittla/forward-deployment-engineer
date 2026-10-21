# Capstone 5 · Embedded field engagement: healthcare intake from voice calls

**Covers:** R14 Safety · R17 Compliance · R18 Discovery · R19 Exec communication · R20 Ambiguity ·
R21 Rapid POC · R23 Product feedback · R24 Writing · R25 Regulated domain (healthcare) · R26 On-site embedding ·
R30 Value metrics · R32 Voice
**Builds on:** ex01–ex08, ex32,
ex48, ex53, ex68, ex72, ex75
**Take after:** Part V: after all of Part I, ex32, ex48 and ex53 (Part III), and ex72 and ex75 (Part IV).

## The engagement
You are embedded at Lakeside Community Health for six weeks. Their after-hours voice agent records patient calls;
every morning, triage nurses spend about 6 minutes per callback re-asking what the patient already said, and urgent
symptoms sometimes sit in the queue. The CMO wants structured intakes ready before the first callback, with urgent
cases at the top. The Privacy Officer has one rule: **no PHI leaves the clinic network**. The board readout is in
six weeks, and several key questions are unanswered when you arrive.

Data in `data/`: your on-site `discovery_notes.md`, four voice-agent call event logs (`calls.json`) full of PHI, and
nurse-labeled `gold_intakes.json`.

## What you build (`starter/engagement/`)
| Module | Responsibility |
|---|---|
| `discovery.py` | Charter from notes, validation, explicit assumptions for open questions, a 6-milestone plan due on Fridays |
| `voice.py` | Segments, transcript, latency, barge-ins and duration from voice events |
| `deid.py` | Tokenize MRNs, emails, dates, phones and patient names; `phi_scan` to detect leftovers |
| `intake.py` | Structured extraction with schema validation and repair; deterministic red-flag `triage` that only ever escalates |
| `pipeline.py` | transcript → de-identify → **PHI guard on every outbound prompt** → extract → triage |
| `evals.py` | Field accuracy and urgent-case recall (emergencies must be caught *as* emergencies) |
| `value.py` | Nurse-hours ROI and payback |
| `readout.py` | The board readout, generated from measured results, voice metrics, ROI and your assumptions |

The tests' scripted extraction model **under-triages the chest-pain call** on purpose. Your safety layer has to
catch it.

## Deliverables (`starter/deliverables/`)
- `stakeholder_update.md`: a week-3 status update with RAG status, done, next, risks, asks.
- `handoff_runbook.md`: daily operation, red-flag change control, PHI incident response, monitoring, escalation.
- `product_feedback.md`: what the platform should build so the next clinic takes two weeks less.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run
```bash
pytest capstones/c5-field-engagement
pytest --solutions capstones/c5-field-engagement
```

## Reflection prompts (for your portfolio)
1. Which open question would have changed your design most if answered differently?
2. Where did you choose deterministic code over the model, and why?
3. What did you tell the CMO about the limits of a 4-call eval set?

## Assessment
Assessed with the shared [capstone rubric](../RUBRIC.md): gates first (tests, critical correctness, security and
privacy, honest reporting, plus this capstone's own gates), then a weighted score across nine dimensions. The bar is
every gate passing, a weighted score of at least 3.0 and no dimension below 2. Section 4 of the rubric lists C5's
acceptance criteria and gates. Submit your scorecard as `starter/deliverables/scorecard.md`.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest capstones/c5-field-engagement`.
- **Expected output:** all 16 tests fail against the starter; when you're done, all 16 pass.
- **Check the reference solution:** `pytest --solutions capstones/c5-field-engagement`: all 16 pass.
- **Tests:** `tests/test_c5_deliverables.py`, `tests/test_c5_discovery.py`, `tests/test_c5_evals_readout.py`,
  `tests/test_c5_pipeline.py`, `tests/test_c5_voice_deid.py` (16 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** de-identification here is regex patterns plus a known-names list, so a name or identifier
  outside those patterns (a relative's name, an address, a rare format) passes the PHI guard, and the extraction
  model is scripted. A real clinic deployment needs a validated de-identification service measured for recall on
  labeled calls, the Privacy Officer's written sign-off, clinical review of the red-flag rules, and the contracts and
  audit controls that the applicable health-privacy rules require.

