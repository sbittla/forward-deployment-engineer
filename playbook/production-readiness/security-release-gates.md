# Security release gates

| | |
|---|---|
| **Owner** | FDE with the customer's security team |
| **When** | Before go-live, against the production configuration |
| **Inputs** | The threat model; red-team suite; access-control tests |
| **Done when** | Every gate passes, or a permitted waiver is signed by the customer's risk owner with an expiry date |
| **Book** | Chapter 13, Section 13.12 |

| Gate | Negative test run | Result | Evidence (link) | Waiver allowed | Waiver (owner, expiry, compensating control) |
|---|---|---|---|---|---|
| Tenant isolation | | | | Never | |
| Tool authorisation | | | | Never | |
| Least privilege | | | | Never (production identities) | |
| Secrets | | | | Never | |
| Prompt injection and egress | | | | Never (egress, side effects) | |
| Human approval | | | | Never | |
| Auditability | | | | Never | |
| Sensitive data | | | | Risk owner | |
| Retention and deletion | | | | Risk owner | |
| Kill switches | | | | Risk owner | |

Run against: configuration version ______ (must be the production configuration, not staging).
