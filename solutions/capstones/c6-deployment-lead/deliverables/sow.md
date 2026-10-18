# Statement of work: Meridian Bank relationship-manager briefing assistant

## Objectives
- Cut the time relationship managers spend preparing a client briefing from about 41 minutes to under 25.
- Reach 60% weekly activation across the commercial and private-banking pilot teams.

## In scope
- Briefing assistant over CRM notes, transaction summaries and research (agent workstream, FDE).
- Data ingestion into the bank's warehouse (data workstream, Atlas SI).
- Agent-desktop UI (frontend workstream, Atlas SI).
- Enablement: workshops, champions and runbooks (FDE).

## Out of scope
- Credit decisions or product recommendations to clients.
- Changes to core banking systems.

## Deliverables and acceptance criteria
| Milestone | Due | Acceptance criteria |
|---|---|---|
| Charter signed | 2026-11-05 | Sponsor signs charter with quantified success metrics |
| Eval bar met | 2026-12-01 | Golden-set pass rate of 90% or more; zero answers outside permitted data |
| Go-live | 2026-12-03 | Partner deliverables accepted, security questionnaire closed, runbook accepted by Bank IT |

## Timeline
Critical path: discovery -> landing-zone -> ingest -> agent-evals -> go-live (P50 finish 23.3 working days).

## Assumptions
- The warehouse landing zone is available by day 10.
- Atlas SI staffs the data and frontend workstreams full time from week 2.

## Customer responsibilities
- Provide SSO (Entra ID) app registration and test users by 2026-11-09.
- Name a model-risk reviewer for the MRM validation.

## Partner responsibilities
- Atlas SI delivers designs and evidence (tests, evals, threat model) for review two days before each milestone.
- Partner deliverables are accepted only through the Deployment Lead's review gate.

## Change control
Scope, milestone or acceptance changes need a written change request signed by both sponsors; estimates are
re-baselined on approval.

## Estimate
| Confidence | Working days | Fees (at $2,400/day) |
|---|---|---|
| P50 | 23.3 | $55,920 |
| P90 | 26.3 | $63,120 |
