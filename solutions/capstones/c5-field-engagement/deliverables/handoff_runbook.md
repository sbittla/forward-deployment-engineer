# After-hours intake pipeline: handoff runbook

## Overview
Every after-hours voice call is turned into a structured intake (reason, urgency, symptoms, callback window) for
the morning triage nurses. The pipeline runs inside Lakeside's Azure tenant. Transcripts are de-identified before
the model sees them, and any prompt that still contains PHI is blocked. Owner after handoff: Clinical Informatics.

## Daily operation
- Intakes appear in the triage queue within 5 minutes of hang-up, sorted emergency → urgent → routine.
- Emergency intakes page the on-call nurse immediately. The red-flag rules decide this, not the model.
- Nurses correct fields in the queue. Corrections feed the weekly eval review.

## Red-flag list changes
The CMO owns the list (`RED_FLAGS`). Changes go through change control: the Nurse Manager proposes, the CMO
approves, Clinical Informatics deploys after the eval suite passes with 100% urgent recall.

## PHI incident response
1. If a `PHILeak` error appears in the logs, the prompt was blocked and nothing left the network. File a ticket
   with the call ID only.
2. If PHI is suspected to have reached the model endpoint, stop the pipeline (`intake-pipeline` scale to 0),
   notify the Privacy Officer within 1 hour, and preserve logs for the breach assessment.

## Monitoring
- Urgent-case recall on the weekly nurse-labelled sample must stay at 100%. Any miss is a sev-1.
- Field accuracy target is 95% or higher; review misses weekly.
- Voice agent p95 response latency stays under 3 s, and barge-ins are tracked per week.

## Escalation
1. Clinical Informatics on-call: informatics-oncall@lakeside.example, +1 608 555 0175.
2. Privacy Officer (any PHI concern): privacy@lakeside.example.
3. Nurse Manager, Triage (clinical questions about intake content).
