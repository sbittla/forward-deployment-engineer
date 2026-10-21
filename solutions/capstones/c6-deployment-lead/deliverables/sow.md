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

## Support boundaries
- Hypercare: the FDE team and Atlas SI fix defects in delivered scope for 10 working days after go-live, during bank
  business hours, through the Bank IT service desk queue.
- Bank IT runs first-line support and on-call from go-live; the FDE team is second line during hypercare only.
- Not covered: changes to source systems, new data sources or features (these go through change control), and
  issues in the bank's SSO, network or warehouse platforms.
- After hypercare, the bank's support contract with the platform vendor applies; this SOW ends.

## Exit criteria
The engagement closes when each criterion is met, with the evidence named:
- Go-live milestone accepted (acceptance record signed by the bank sponsor).
- Both Atlas SI deliverables accepted through the review gate (review memos).
- Knowledge-transfer exit criteria in the enablement plan met (two Bank IT engineers per skill, signed runbook
  walkthrough).
- Hypercare ended with no open severity-1 or severity-2 defects (service desk report).
- Access for FDE and Atlas SI staff revoked (Bank IT access review).

## Change control
Scope, milestone or acceptance changes need a written change request signed by both sponsors; estimates are
re-baselined on approval.

## Estimate
| Confidence | Working days | Fees (at $2,400/day) |
|---|---|---|
| P50 | 23.3 | $55,920 |
| P90 | 26.3 | $63,120 |
