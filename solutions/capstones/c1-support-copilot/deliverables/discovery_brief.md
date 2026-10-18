# Discovery brief: Northwind Insurance support copilot

## Problem
Claims adjusters spend about 11 minutes per coverage question searching 80-page policy PDFs. Answers vary by
adjuster, and roughly 1 in 8 coverage answers is later corrected by a supervisor.

## Users
- Primary: 400 internal claims adjusters on the phone and email queues.
- Secondary: claims supervisors who review escalations.
- Not in scope for the pilot: policyholders directly.

## Success metrics
| Metric | Baseline | Pilot target |
|---|---|---|
| Average handle time for coverage questions | 11 min | 8 min |
| Supervisor corrections of coverage answers | 12.5% | below 5% |
| Golden-set pass rate | n/a | at least 90% |
| Answers to questions the policy does not cover | n/a | 0% (must abstain) |

## Data sources
- Policy forms HO-3 and PAP-1 (markdown export from the document management system), refreshed nightly.
- The claims process guide maintained by Claims Operations.
- Intent examples labelled from 3 months of resolved tickets (PII removed).

## Constraints
- Policyholder PII must not leave the customer's VPC unredacted. Emails, phone numbers and policy numbers are
  tokenised before any model call.
- Per-question model cost must stay under $0.02.
- Go-live before the Q3 renewal season. The runbook must be owned by the Claims Platform team at handoff.

## Out of scope
- Approving, denying or paying claims.
- Legal interpretation of coverage disputes (these go to a licensed agent).
- Direct chat with policyholders.

## Stakeholders
| Name | Role | Interest |
|---|---|---|
| Dana Ruiz | VP Claims (executive sponsor) | Handle time and quality |
| Lee Park | Claims Ops Manager | Day-to-day adoption |
| Priya Shah | IT Security Lead | PII handling and network egress |
| Ana Gomez | Compliance | Citations and abstention behaviour |
