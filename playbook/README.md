# FDE engagement playbook

Copyable templates for the artefacts the book teaches, in five packs that follow an engagement from the first
meeting to handover. Each template states its owner, when to use it, its inputs and when it's done. Appendix F of
*The Forward Deployed Engineer* describes how the packs fit together; Appendix E shows them filled in for a
reference engagement.

Copy a template into the engagement's own repository or document store; don't edit these in place.

## Discovery pack

| Template | Owner | When |
|---|---|---|
| [Stakeholder interview guide](discovery/stakeholder-interview-guide.md) | FDE | Week 1, one per stakeholder |
| [Current-state workflow map](discovery/current-state-workflow-map.md) | FDE, with a user | Week 1, after sitting with users |
| [Data-access checklist](discovery/data-access-checklist.md) | FDE, with the data owner | Week 1; before travel for on-site work |
| [Engagement charter](discovery/charter.md) | FDE; approved by the sponsor | End of week 1 |
| [Stakeholder map and RACI](discovery/stakeholder-map-raci.md) | FDE | Week 1; reviewed at every steering meeting |
| [Business case](discovery/business-case.md) | FDE with the customer's finance partner | Before the pilot; re-run at the readout |

## Solution design pack

| Template | Owner | When |
|---|---|---|
| [Architecture summary with trust boundaries](design/architecture-summary.md) | FDE; reviewed by the customer's architect | Before build; updated at each design review |
| [Architecture decision record](design/adr.md) | The person proposing the decision; a named decider | Whenever a decision is expensive to reverse |
| [Threat model](design/threat-model.md) | FDE with the customer's security team | Design review; before the security gates |
| [Evaluation plan](design/evaluation-plan.md) | FDE with the customer's domain experts | Before the first demo |
| [Performance test plan](design/performance-test-plan.md) | FDE with the SRE team | Before the pilot ends; re-run on model, prompt or load changes |

## Delivery pack

| Template | Owner | When |
|---|---|---|
| [Weekly status note](delivery/status-note.md) | FDE | Every week, the day before the sponsor reads it |
| [RAID log (risk register)](delivery/raid-log.md) | FDE; reviewed at every steering meeting | From week 1 to the close |
| [Change request](delivery/change-request.md) | FDE; approved by the sponsor | Within a week of any informal request that changes scope |
| [Steering committee update](delivery/steering-update.md) | Deployment lead | A day before each steering meeting |

## Production readiness pack

| Template | Owner | When |
|---|---|---|
| [Security release gates](production-readiness/security-release-gates.md) | FDE with the customer's security team | Before go-live, against the production configuration |
| [Launch checklist](production-readiness/launch-checklist.md) | FDE; signed by the sponsor and the customer's operations lead | The week before go-live |
| [Production-readiness scorecard](production-readiness/readiness-scorecard.md) | FDE with the customer's operations lead | Readiness review before go-live |
| [Performance test report](production-readiness/performance-test-report.md) | FDE | After the performance test plan has run |
| [Runbook](production-readiness/runbook.md) | FDE; executed by the customer's operations team before handover | Before handover |

## Handover pack

| Template | Owner | When |
|---|---|---|
| [Integration register](handover/integration-register.md) | FDE; handed to the team taking over | From the first integration; first page of the handover pack |
| [Operational readiness review (handover checklist)](handover/operational-readiness-review.md) | FDE with the team taking over | The last two weeks of the engagement |
| [Adoption plan](handover/adoption-plan.md) | Adoption workstream owner | From discovery; reviewed weekly after launch |
| [Enablement plan](handover/enablement-plan.md) | FDE | Before handover |
| [Final executive readout](handover/final-readout.md) | FDE or deployment lead | End of the pilot or engagement |
| [Product feedback brief](handover/product-feedback-brief.md) | FDE | Monthly, and at the close of every engagement |
