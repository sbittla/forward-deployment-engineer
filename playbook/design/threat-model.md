# Threat model

| | |
|---|---|
| **Owner** | FDE with the customer's security team |
| **When** | Design review; before the security gates |
| **Inputs** | The architecture summary and its trust boundaries |
| **Done when** | Every threat has a control and a test, and the security team has reviewed it |
| **Book** | Chapter 13 |

| # | Threat | Boundary | Likelihood (1–5) | Impact (1–5) | Control | Negative test | Gate (Section 13.6) | Residual risk | Accepted by, review date |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Prompt injection in retrieved or inbound content | | | | | | | | | |
| T2 | Data shown to a user without permission | | | | | | | | | |
| T3 | Data from one tenant reaching another | | | | | | | | | |
| T4 | Personal data leaving the network unredacted | | | | | | | | | |
| T5 | A tool used beyond its intended permission | | | | | | | | | |
| T6 | Secrets in code, images, logs or prompts | | | | | | | | | |
| T7 | Over-reliance: a confident wrong answer acted on | | | | | | | | | |
| T8 | Tool poisoning: a tool description or result that carries instructions | | | | | | | | | |
| T9 | Token passthrough: a user's token forwarded to a downstream service | | | | | | | | | |
| T10 | A forged, expired or misdirected identity token accepted | | | | | | | | | |

A critical threat can't be accepted; it blocks release until its negative test passes. Any other residual risk
needs a named customer owner, a compensating control and a review date (ex93's `RiskAcceptance`).

Use the OWASP Top 10 for LLM applications as a prompt for anything missing.
