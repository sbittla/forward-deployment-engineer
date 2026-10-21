# Final readout: Northwind Insurance support copilot

For Dana Ruiz (VP Claims), the Head of Compliance and the CISO. Status labels: *measured* (capstone test run),
*exercise data* (the pilot of Appendix E), *illustrative*.

## Decision
**Go with conditions** (computed by `golive.go_no_go`): every gate passes, and the pilot cut handle time by 2.9
minutes against the control group, short of the 7-minute target. We recommend rolling out to all 400 adjusters
through a canary, and ask for a decision at the steering committee on 2027-01-15 (illustrative date).

## Value against the baseline
| | Minutes per coverage question | Status |
|---|---|---|
| Baseline (both groups, before the pilot) | 11.0 | Exercise data |
| Target (charter) | 7.0 | Agreed in week 1 |
| Pilot teams, three weeks | 7.5 | Exercise data |
| Control teams, same weeks | 10.4 | Exercise data |
| Effect against control | 2.9 (26%) | Computed |

The business case re-run with the measured 2.9-minute effect, not the 4-minute target, still returns 33% ROI after
review and operations costs (Appendix E.8; exercise data).

## Gates
| Gate | Threshold | Measured | Result |
|---|---|---|---|
| Pass rate | ≥ 90% | 100% of 12 | Pass |
| Citation precision | ≥ 95% | 100% | Pass |
| Retrieval recall | ≥ 90% | 100% | Pass |
| Answers to unanswerable questions | 0% | 0% | Pass |
| Answerable questions refused | ≤ 10% | 0% | Pass |
| Permission leaks (cross-tenant, SIU, drafts) | 0 | 0 of 5 | Pass |
| Latency p95 | ≤ 4 s | 1.5 s (simulated) | Pass |
| Cost per successful answer | ≤ $0.025 | $0.0006 (computed, fake model) | Pass |

The first build (v0) failed three of these gates and was stopped (evaluation report, "v0 against v1").

## Risks
| Risk | Owner | Mitigation |
|---|---|---|
| Real-model latency and cost exceed the simulated numbers | Platform engineering | Performance test at peak before the canary passes 10% |
| A new document source arrives without ACLs | Policy platform team | Missing ACL means invisible (fail closed); ingestion alerts on blocked documents |
| Adoption stalls below the habitual-use target | Claims operations lead | Champions per team; usage reviewed every two weeks |

## Conditions
1. Re-run the business case with the measured 2.9-minute effect and present it with the rollout plan.
2. Canary at 10%, then 50%, then 100%, with automatic rollback on any leak, any answer to an unanswerable question,
   or a pass-rate drop of more than 3 points (`slo.run_rollout`).
3. Retest redaction recall before the CISO's waiver expires (Table E.6).

## Ownership transfer
The claims platform team owns the service and the on-call rotation from the end of week 14; Compliance owns the
golden set with the claims quality lead; the policy platform team owns ingestion and ACL metadata; the claims
operations lead owns adoption. The runbook's "Ownership transfer" section is the checklist, and the FDE team's
access is revoked at sign-off.
