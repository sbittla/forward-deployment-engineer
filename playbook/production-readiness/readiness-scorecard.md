# Production-readiness scorecard

| | |
|---|---|
| **Owner** | FDE with the customer's operations lead |
| **When** | Readiness review before go-live |
| **Inputs** | Gate results and the evidence for each dimension |
| **Done when** | All gates pass; weighted score ≥ 3.0; no dimension below 2 |
| **Book** | Chapter 14, Section 14.7 · Appendix D |

## Gates (any failure means not ready)
- [ ] Security release gates
- [ ] No critical-slice regressions
- [ ] Performance targets met at peak, measured
- [ ] Rollback rehearsed by the customer
- [ ] On-call accepted

## Weighted score (0 nothing · 1 ad hoc · 2 documented · 3 tested with evidence · 4 owned by the customer)
| Dimension | Weight | Score | Evidence |
|---|---|---|---|
| Functional correctness | 15% | | |
| AI evaluation | 20% | | |
| Security and privacy | 15% | | |
| Performance | 10% | | |
| Economics | 10% | | |
| Reliability | 10% | | |
| Adoption | 10% | | |
| Handover | 10% | | |
| **Weighted total** | | | |
