---
name: claims-triage
description: Routes new insurance claims to the correct adjuster queue by line of business and severity. Use when a new claim, FNOL report or claim email needs a queue, priority or escalation decision.
---
# Claims triage

1. Identify the line of business (home, auto, health) from the claim text.
2. Assign severity using `reference/routing-rules.md`. Read it before deciding; do not guess thresholds.
3. Any injury, fatality, fire or suspected fraud is severity 1 and goes to the major-loss queue immediately.
4. Output JSON: `{"queue": ..., "severity": 1-4, "reason": ..., "needs_human": true|false}`.
5. If the claim lacks a policy number or date of loss, set `needs_human` to true and list what is missing.
