# Capstone 5 hints · Embedded field engagement: healthcare intake from voice calls

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Read `data/discovery_notes.md` before writing code, the way you would on day one at the clinic. Then build in this
order:

| Order | Module | Reuse |
|---|---|---|
| 1 | `discovery.py` | ex01 charter, ex06 assumptions |
| 2 | `voice.py` | ex48 transcripts |
| 3 | `deid.py` | ex53 PII, ex72 de-identification |
| 4 | `intake.py` | ex32 structured output and repair |
| 5 | `pipeline.py` | the PHI guard |
| 6 | `evals.py` | field accuracy and urgent recall |
| 7 | `value.py` | ex03 ROI |
| 8 | `readout.py` | ex05 status report, ex75 risk doc |

The tests' scripted model is designed to **under-triage** the chest-pain call. Plan for that from the start rather
than discovering it in the eval.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Pipeline per call:** build the transcript, de-identify it with the patient's name, wrap the model in a guard that
  scans **every** outbound prompt for PHI and raises `PHILeak`, extract the intake, then run deterministic triage over
  the *original* caller text.
- **Triage** is a red-flag keyword list that can only **raise** urgency (to `emergency`, callback `asap`), never lower
  it. Clinical safety lives in code you can audit, not in the model's judgement.
- **Extraction** validates the schema (urgency and callback window from fixed sets), normalises the symptoms (lower
  case, deduplicated), and feeds validation errors back for one repair attempt.
- **Urgent recall:** of the gold emergencies, the share you also labelled emergency. Being labelled "urgent" doesn't
  count.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- De-identify more than the caller says. The agent says names too, and a first name alone ("Grace") is still PHI.
  Redact each part of the patient's name.
- Phone numbers come in several shapes, including `(773) 555-0123`. The leak test looks for the bare area code too.
- `phi_scan` returns the PHI types found, in a fixed order (MRN, date, phone, name). Run it on the safe text as a
  check in your own pipeline as well.
- The engagement plan's milestones fall on **Fridays**. A start on a Monday makes the first due date that Friday; a
  start on a Friday is due the same day.
- Each open question becomes an explicit assumption starting "Until confirmed, we assume…", and all three appear in
  the readout.
- The readout recommends GO only from measured results, and names the call the safety layer caught (`calls C2`).
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_charter` | Metric parsing or the unmeasurable-metric check (see ex01); open questions not captured |
| `test_assumptions` | Assumption templates don't match the question type (owner, retention, fallback) |
| `test_engagement_plan` | Milestones not on Fridays; wrong milestone titles |
| `test_voice_metrics` | Overlapping speech not counted as a barge-in; latency or duration computed wrongly (see ex48) |
| `test_deidentify_removes_all_phi` | A PHI type missed; `phi_scan` order differs; tokens not numbered per type |
| `test_names_mentioned_by_agent_and_emails` | Only the full name redacted; parenthesised phone format missed |
| `test_pipeline_end_to_end` | Triage run on the model output instead of the caller text; PHI reaches the model |
| `test_guard_blocks_phi` | Guard checks only the patient name, not dates and other PHI |
| `test_extraction_repair_and_failure` | Symptoms not normalised; validation error not fed back; no error after the last attempt |
| `test_triage_never_downgrades` | Triage replaces urgency with a lower level; callback window not set to `asap` |
| `test_evaluate` | Urgent recall counts "urgent" as catching an emergency |
| `test_roi` | Payback uses gross instead of net monthly savings |
| `test_readout` | Headings out of order; numbers typed in instead of computed; assumptions missing |
| `test_deliverable` | A required heading missing, a placeholder left in, or no RAG status in the update |
