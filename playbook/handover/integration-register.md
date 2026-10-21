# Integration register

| | |
|---|---|
| **Owner** | FDE; handed to the team taking over |
| **When** | From the first integration; one entry added the week each one is built |
| **Inputs** | Endpoints, credentials process, owners, measured limits and recorded fixtures for each connected system |
| **Done when** | Every integration has an entry with no blank cells; the team taking over has debugged one integration from it |
| **Book** | Chapter 5, Section 5.6 · first page of the handover pack (Appendix F) |

| Integration | Endpoint and environment | Authentication; who issues credentials | Owner; escalation contact | Rate limits (documented / measured) | Error behavior worth knowing | Data classification | Test fixtures |
|---|---|---|---|---|---|---|---|
| <system> | <base URL>, <prod / test> | <OAuth client credentials, API key, mTLS>; <team> | <team>; <contact> | <n> req/min / <n> req/min | <"returns 200 with an error body on timeout"> | <public, internal, confidential, personal> | <repo path> |

Record the measured limit next to the documented one; they often differ. An integration without fixtures can't be
tested after you've left: add it to the RAID log until they exist.
