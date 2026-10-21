# Launch checklist

| | |
|---|---|
| **Owner** | FDE; signed by the sponsor and the customer's operations lead |
| **When** | The week before go-live |
| **Inputs** | Gate results, scorecard, performance report, runbook |
| **Done when** | Every item is checked with evidence, and both signatures are present |
| **Book** | Chapters 12 to 14 |

- [ ] Security release gates pass (link).
- [ ] Held-out evaluation: no critical-slice regressions; launch bar met (link).
- [ ] Performance targets met at expected peak, measured (link to the report).
- [ ] Readiness scorecard: all gates pass; weighted score ≥ 3.0; no dimension below 2 (link).
- [ ] Rollback of code, prompt and model rehearsed by the customer's team (date).
- [ ] Kill switches tested (date).
- [ ] Alerts route to the customer's on-call; rotation has accepted the service.
- [ ] Online monitors and the human review sample are running.
- [ ] Users have been told what it does, what it doesn't, and how to give feedback.
- [ ] Support boundaries and hypercare period communicated.
- [ ] Rollout plan: canary percentage, promotion criteria, rollback criteria.

Signed: ______ (sponsor) ______ (operations lead) on ______
