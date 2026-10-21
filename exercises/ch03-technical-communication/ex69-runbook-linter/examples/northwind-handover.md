# Northwind claims copilot: handover document

*Filled-in example of `playbook/handover/operational-readiness-review.md`, with the ownership and acceptance pages
that travel with it, for the Northwind reference engagement (Appendix E.10). Northwind, its people, dates and numbers
are fictional and illustrative; the measurements are the chapters' worked examples, not a real deployment's.*

| | |
|---|---|
| **Prepared by** | FDE lead, with the claims platform team (the team taking over) |
| **Walked through** | Weeks 13 and 14, in two sessions with the claims platform and policy platform on-call leads |
| **Decision requested** | The sponsor, Dana Ruiz, accepts handover against the SOW's exit criteria |

## 1. What you're taking over

The claims coverage copilot: a streaming answer service for coverage questions, a read-only summary agent for claim
files, nightly ingestion of 600 policy forms into Postgres with pgvector, and the evaluation suite (520 golden cases,
120 development and 400 held-out). Architecture and trust boundaries: Figure E.1 and Table E.4. Decisions and their
revisit triggers: ADR-1 to ADR-5 (Appendix E.4; ADR-3 in full in `adr-003-model-and-retrieval-store.md`).

## 2. Who owns what from today

| Component | Owner | On call |
|---|---|---|
| Answer service and agent | Claims platform team | Claims platform rotation |
| Ingestion, index and data contracts | Policy platform team | Policy platform rotation |
| Golden set and evaluation | Claims quality lead, with Compliance | Not paged; weekly review |
| Policy specification and prompts | Compliance (specification), claims platform team (build) | Not paged |
| Model choice, quotas and cost | Platform engineering | Budget alerts |
| Adoption | Claims operations lead | Not paged; fortnightly review |

## 3. Operational readiness checklist

- [x] Alerts route to the claims platform rotation; a game day with an injected fault (a stalled index refresh) ran
  in week 13.
- [x] The runbook passes ex69's linter and covers deploy, rollback (code, prompt, model), scaling, key rotation and
  the three kill switches. A claims platform engineer ran the rollback from the runbook alone, unaided, in week 13
  (reference runbook: `solutions/exercises/ch03-technical-communication/ex69-runbook-linter/RUNBOOK.md`).
- [x] Dashboards: availability SLO (99.5%, first token within 3 s) and burn-rate alerts, cost per day per team,
  weekly judged pass rate (objective at least 88%), drift.
- [x] The vector index rebuilds from source; time to rebuild about 40 minutes; last tested in week 13.
- [x] Budget alert on model spend at $40,000 a month (ADR-3's revisit trigger).
- [x] Every critical skill has two ready people on Northwind's side (ex84's readiness report, week 12).
- [x] Known limitations and the decision log are handed over (section 5 and the RAID log).
- [x] Support boundaries after hypercare agreed: two weeks of business-hours advice, no on-call.
- [ ] The FDE team's accounts, keys and tokens revoked: scheduled for the last day; confirmed by IT Security.

## 4. Acceptance against the charter

| Criterion | Target | Result | Status |
|---|---|---|---|
| Handle time on coverage questions | 11 to 7 minutes | −2.9 minutes (26%) against control | Missed; business case re-run at 33% ROI, accepted |
| Coverage-error rate, weekly quality sample | 6% to 3% or less | 2.6% (29 of 1,108) | Met |
| Habitual use | At least 50% of invited by week 12 | 38% (150 of 400) | Missed; condition with a plan |
| Held-out pass rate | At least 90% | 90.0% | Met, at the bar |
| Security gates | Pass, or waived in writing | Five pass, one not applicable, one waived | Met, with a waiver |
| Readiness | Score at least 3.0, no dimension below 2 | 3.05 | Met, with conditions |

Full table: Table E.8. Every result is labeled with its status; none is projected.

## 5. Open items and known limitations

| ID | Item | Owner after handover | Due |
|---|---|---|---|
| R-2 | Redaction recall 93% against 95%, under a CISO waiver with a second outbound scan | IT Security | Retest before the waiver ends, week 22 |
| R-4 | Habitual use 38% against 50% | Claims operations lead | Fortnightly review |
| — | A rollout beyond 400 adjusters needs a new quota and load test (knee at about 5.5 requests a second) | Platform engineering | Before any expansion |
| — | Two platform gaps the engagement worked around | FDE lead | Product feedback brief delivered at the close |

## 6. Sign-off

| Role | Name | Accepted |
|---|---|---|
| Sponsor | Dana Ruiz, VP Claims | Date |
| Taking over | Claims platform team lead | Date |
| Security | Priya, IT Security | Date |
| Delivering | FDE lead | Date |
