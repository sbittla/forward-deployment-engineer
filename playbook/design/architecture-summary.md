# Architecture summary with trust boundaries

| | |
|---|---|
| **Owner** | FDE; reviewed by the customer's architect |
| **When** | Before build; updated at each design review |
| **Inputs** | The charter, the data-access checklist, platform and security standards |
| **Done when** | The customer's architect and security reviewer have reviewed it, and every boundary has a control |
| **Book** | Appendix E · Chapters 7, 13 and 14 |

## System context
One paragraph: what the system does, for whom, and what it must never do.

## Components
| Component | Runs where | Owner after handover | Data it holds |
|---|---|---|---|

## Data flows
| # | From → to | Data | Protocol and authentication | Classification |
|---|---|---|---|---|

## Trust boundaries
| Boundary | What crosses it | Control (authentication, validation, redaction, allowlist) | Test that proves it |
|---|---|---|---|

## Alternatives considered
Link the ADRs.

## What's illustrative and what's verified
List any part of this design that hasn't been tested in the customer's environment.
