# Engagement charter: Northwind Insurance support copilot

Status labels: *exercise data* (the capstone's scenario, consistent with Appendix E), *measured* (by the capstone's
tests), *illustrative* (invented for the example). Template: `playbook/discovery/charter.md`.

## Sponsor
Dana Ruiz, VP Claims. She owns the claims budget and signs the go/no-go decision with the Head of Compliance and the
CISO.

## Problem and baseline
"My adjusters spend more time finding the clause than deciding the claim." A coverage question takes a median of
11 minutes (exercise data: observed over two afternoons, Appendix E.2). The weekly quality sample finds a wrong
coverage answer in 6% of sampled answers (exercise data).

## Acceptance criteria
Every criterion carries through to the evaluation report, the test report and the final readout unchanged.

| Criterion | Baseline | Target | Measured how | Gate or condition |
|---|---|---|---|---|
| Handle time on coverage questions | 11 min | 7 min | Pilot teams against control teams, three weeks | Value: decides go or go with conditions |
| Golden-set pass rate | n/a | ≥ 90% | `run_golden` | Gate `pass_rate` |
| Citation precision | n/a | ≥ 95% | `run_golden` | Gate `citation_precision` |
| Answers to unanswerable questions | n/a | 0% | `run_golden`, unanswerable slice | Gate `false_answer_rate` |
| Answerable questions refused | n/a | ≤ 10% | `run_golden` | Gate `over_refusal_rate` |
| Retrieval recall (expected document in the top 4) | n/a | ≥ 90% | `run_golden` | Gate `retrieval_recall` |
| Documents shown to someone without permission | n/a | 0 | `run_security`, 5 probes | Gate `permission_leaks` |
| Latency, p95 | n/a | ≤ 4 s | `run_load` (simulated) | Gate `p95_ms` |
| Model cost per successful answer | n/a | ≤ $0.025 | `run_load` (computed) | Gate `cost_per_success_usd` |
| Claim reviews opened without a supervisor's approval | n/a | 0 | `test_c1_agent_tools.py` | Capstone security gate |

## Scope
In scope: coverage questions from licensed adjusters over the published HO-3, PAP-1 and claims-process documents;
claim-status routing; opening a claim review with a supervisor's approval (added in week 5, see the change log).
Out of scope, acknowledged by the sponsor: policyholder use, Spanish-language questions, drafting emails, CRM
write-back, approving or paying claims, and special investigations documents for anyone outside the unit.

## Stakeholders
| Name | Role | RACI |
|---|---|---|
| Dana Ruiz | VP Claims, sponsor | Accountable |
| Ana Gomez | Compliance | Consulted on the golden set; signs the go/no-go |
| Priya Shah | IT Security | Consulted on the threat model; signs the go/no-go |
| Lee Park | Claims operations manager | Responsible for adoption |
| Claims platform team | Future owner of the service | Responsible after handover |
| FDE team | Build, evaluation, handover | Responsible until handover |

## Budget
- **Model spend:** Finance caps the worst-case cost of one question at $0.02 (enforced before the call by
  `Copilot._fit_budget`, which drops the lowest-ranked sources and abstains if even one doesn't fit). The go-live
  gate is cost per *successful* answer, at most $0.025 (Table E.8's target).
- **Tool execution:** at most 3 tool calls per request (`ExecutionBudget`); every attempt counts, including refused
  ones.
- **Team:** two FDEs for 14 weeks (illustrative).

## Change log
| Week | Change | Requested by | Impact on acceptance criteria | Approved by |
|---|---|---|---|---|
| 1 | Handle-time target raised from 8 minutes (discovery brief) to 7 minutes | Dana Ruiz | Value target 7 min | Dana Ruiz |
| 5 | Adjusters may open a claim review (pausing payment) from the copilot | Lee Park | New consequential action: authorization, supervisor approval, idempotency and a tool budget; new security gate | Dana Ruiz, Priya Shah |
| 6 | Security finding SF-1: special investigations and other-tenant documents retrievable in v0 | FDE team (security probes) | New gate `permission_leaks` = 0; go-live blocked until fixed | Priya Shah |
