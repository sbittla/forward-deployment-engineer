# Data-access checklist

| | |
|---|---|
| **Owner** | FDE, with the data owner |
| **When** | Week 1; before travel for on-site work |
| **Inputs** | The list of systems the solution needs |
| **Done when** | Every source has an owner, an approved access method, a classification and a date |
| **Book** | Chapters 5, 6 and 13 |

| Source | Owner and escalation | What we need (fields, history) | Access method | Classification (public, internal, personal, special category) | Residency | Lead time | Requested | Granted |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

For each source, also confirm:
- [ ] Minimum fields only: the columns the use case needs, no more.
- [ ] Read-only access, through an identity that can be revoked when we leave.
- [ ] Rate limits and maintenance windows, documented and measured.
- [ ] How deletions and corrections reach us (soft deletes, change feed, reconciliation).
- [ ] Retention period for every copy we make (raw, processed, logs, vector chunks).
- [ ] Whether data may leave the network for a model provider, and in what form (redacted, tokenized).
- [ ] A data contract or a draft of one (Chapter 6, Section 6.6).
