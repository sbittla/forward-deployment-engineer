# ex94 · Blameless postmortem and customer incident communications

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R44 Incident communication, R19 Stakeholder communication, R15 Reliability ·
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
   `blame_lint` flags anything in the root cause or contributing factors. The record must be complete: raise
   `ValueError` if the root cause is empty or blank, if there are no action items, or if the events don't include
   both a `detected` and a `resolved` event (the summary's duration needs both).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex94-postmortem-comms`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex94-postmortem-comms`: all 9
  pass.
- **Tests:** `test_postmortem.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The jargon and blame checks are word lists and patterns, so they miss paraphrases and can
  flag innocent text. In production, a person reviews every customer update and postmortem before it goes out, and
  timelines come from the incident tool rather than hand-entered events.

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
Implement exercises/ch14-llmops-and-sre/ex94-postmortem-comms/starter.py so that test_postmortem.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`status_update`, `impact_summary`, `blame_lint`, `render_postmortem`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex94-postmortem-comms` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Blameless postmortem and customer incident communications" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does jargon detection catch internal hostnames and pod
names? Are durations computed from the right events? Would the customer's CIO understand the summary in one read?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
