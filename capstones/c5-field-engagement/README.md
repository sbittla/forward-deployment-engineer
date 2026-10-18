# Capstone 5 · Embedded field engagement: healthcare intake from voice calls

**Covers:** R14 Safety · R17 Compliance · R18 Discovery · R19 Exec communication · R20 Ambiguity ·
R21 Rapid POC · R23 Product feedback · R24 Writing · R25 Regulated domain (healthcare) · R26 On-site embedding ·
R30 Value metrics · R32 Voice
**Suggested time:** 3 days (the whole arc of a 6-week engagement, compressed) · **Builds on:** ex01–ex08, ex32,
ex48, ex53, ex68, ex72, ex75
**Take after:** Part V: after all of Part I, ex32 and ex48 (Part III), and ex72 and ex75 (Part IV).

## The engagement
You are embedded at Lakeside Community Health for six weeks. Their after-hours voice agent records patient calls;
every morning, triage nurses spend about 6 minutes per callback re-asking what the patient already said, and urgent
symptoms sometimes sit in the queue. The CMO wants structured intakes ready before the first callback, with urgent
cases at the top. The Privacy Officer has one rule: **no PHI leaves the clinic network**. The board readout is in
six weeks, and several key questions are unanswered when you arrive.

Data in `data/`: your on-site `discovery_notes.md`, four voice-agent call event logs (`calls.json`) full of PHI, and
nurse-labelled `gold_intakes.json`.

## What you build (`starter/engagement/`)
| Module | Responsibility |
|---|---|
| `discovery.py` | Charter from notes, validation, explicit assumptions for open questions, a 6-milestone plan due on Fridays |
| `voice.py` | Segments, transcript, latency, barge-ins and duration from voice events |
| `deid.py` | Tokenise MRNs, emails, dates, phones and patient names; `phi_scan` to detect leftovers |
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

## Run
```bash
pytest capstones/c5-field-engagement
pytest --solutions capstones/c5-field-engagement
```

## Reflection prompts (for your portfolio)
1. Which open question would have changed your design most if answered differently?
2. Where did you choose deterministic code over the model, and why?
3. What did you tell the CMO about the limits of a 4-call eval set?
