# ex94 · Blameless postmortem and customer incident communications

**Module:** m14 · **Covers:** R44 Incident communication, R19 Stakeholder communication, R15 Reliability ·
**Time:** 50 min

## Learning objectives
- Write fast, jargon-free customer incident updates.
- Compute incident durations and impact from a timeline.
- Write blameless postmortems with owned action items.

## Scenario
Palantir's Forward Deployed Reliability and Enablement engineers go on call for "mission-critical incidents", act
as "the first responder when things go wrong", and turn learnings into documentation and product change. The
technical fix is half the job. The other half is the customer update you send at 2:14 a.m. and the postmortem the
customer's CIO reads on Monday. Both must be fast, accurate, jargon-free and blameless.

## Your task
1. `status_update(stage, impact, next_update_min, eta=None) -> str` for stages `investigating`, `identified`,
   `monitoring`, `resolved`. One plain-language paragraph: it starts with `TEMPLATES[stage]`, then
   `Impact: <impact>.`, then (except when resolved) `Next update in <n> minutes.`, plus `Expected resolution: <eta>.`
   when given. Raise `ValueError` if the impact text contains internal jargon (`JARGON` terms, case-insensitive),
   an IP address or an email address. Customers don't need pod names, and they must never see another
   customer's data.
2. `impact_summary(events)`: events are `{"ts": ISO datetime, "type": "detected"|"mitigated"|"resolved"|...,
   "affected_users": int?}` → `{"duration_min": minutes from first detected to resolved, "time_to_mitigate_min":
   detected → mitigated, "peak_affected_users": max}`.
3. `blame_lint(text) -> list[str]`: flags blameful phrasing: `should have`, `failed to`, `careless`, `human error`,
   `fault`, and `"<Capitalised Name> (broke|caused|forgot|missed)"`. Return the matched phrases in order.
4. `render_postmortem(title, events, root_cause, contributing, went_well, actions)` → markdown with sections
   `Summary` (duration, mitigation time, peak users), `Timeline` (one bullet per event `- HH:MM UTC <type>: <note>`),
   `Root cause`, `Contributing factors`, `What went well`, `Action items` (table `| Action | Owner | Due |
   Priority |`). Every action needs an owner and a due date, otherwise `ValueError`. Raise `ValueError` if
   `blame_lint` flags anything in the root cause or contributing factors.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Blameless postmortem and customer
incident communications". Before I write code, teach me incident communication stages, impact statements, blameless
language, and postmortem structure. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m14-field-leadership/ex94-postmortem-comms/starter.py so that test_postmortem.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`status_update`, `impact_summary`, `blame_lint`, `render_postmortem`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/m14-field-leadership/ex94-postmortem-comms` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Blameless postmortem and customer incident communications" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does jargon detection catch internal hostnames and pod
names? Are durations computed from the right events? Would the customer's CIO understand the summary in one read?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
