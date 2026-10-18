## Customer
Lakeside Community Health

## Problem
Nurses spend the first 6 minutes of every callback re-asking patients what they already told the after-hours voice line, and urgent symptoms are sometimes buried in long voicemails.

## Stakeholders
- Dr. Amara Okafor — Chief Medical Officer (exec sponsor)
- Jordan Lee — Nurse Manager, Triage
- Sam Patel — IT Security & Privacy Officer
- Riley Chen — Revenue Cycle Director

## Success metrics
- Nurse re-ask time per callback: 6 min -> 2 min
- Urgent calls reviewed within 15 minutes: 70 % -> 98 %
- Intake field accuracy: 80 % -> 95 %
- Patients feel heard

## Constraints
- PHI must be de-identified before any text leaves the clinic network
- Must run inside the clinic's Azure tenant; no internet egress except the approved model endpoint
- Pilot readout before the board meeting in 6 weeks

## Out of scope
- Clinical diagnosis or treatment advice
- Scheduling appointments automatically

## Open questions
- Who owns the triage red-flag list: Nurse Manager or CMO?
- What is the retention period for call recordings?
- Can after-hours calls be processed in batch, or must they be real-time?
