# Operational readiness review (handover checklist)

| | |
|---|---|
| **Owner** | FDE with the team taking over |
| **When** | The last two weeks of the engagement |
| **Inputs** | Runbooks, dashboards, access list, recovery procedures |
| **Done when** | Walked through together; every item checked; your access revoked |
| **Book** | Chapter 14, Section 14.7 |

- [ ] Alerts route to the customer's rotation; a game day was run with an injected fault (date).
- [ ] Runbooks pass the linter and cover deploy, rollback (code, prompt, model), scaling, key rotation and kill switches.
- [ ] Dashboards: SLO and budget, cost per day and per tenant, quality signals, drift.
- [ ] The vector index can be rebuilt from source; time to rebuild ______; last tested ______.
- [ ] Budgets and alerts on model spend.
- [ ] Every critical skill has two ready people on the customer's side (enablement report).
- [ ] Known limitations and the decision log are handed over.
- [ ] Support boundaries after hypercare are agreed.
- [ ] Your accounts, keys and tokens are revoked; nothing depends on credentials tied to you.
