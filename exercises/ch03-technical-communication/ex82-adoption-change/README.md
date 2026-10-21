# ex82 · Adoption funnel, change management and pre/post KPI impact

**Chapter:** 3 · Technical Communication (`exercises/ch03-technical-communication/`) · **Covers:** R34 Adoption & change management, R30 Value, R13 Measurement

## Learning objectives
- Instrument an adoption funnel and cohort retention.
- Find lagging teams and plan targeted change actions.
- Measure impact with difference-in-differences instead of before/after.

## Scenario
"Deployments that deliver measurable value against customer goals, drive adoption, and become critical to their
workflows" is how OpenAI measures its Deployment Leads. A copilot nobody opens is a failed deployment, however good
the evals. You'll instrument adoption, find the teams that are stuck, and prove impact with a control group instead
of a before/after anecdote.

## Your task
Usage events: `{"user", "team", "event": "invited"|"login"|"query", "week": int}`.

1. `funnel(events) -> dict` with counts of distinct users: `invited`, `activated` (≥ 1 login), `engaged` (≥ 1 query),
   `habitual` (queries in ≥ 3 distinct weeks), plus `activation_rate` and `habit_rate` (relative to invited, 3 dp).
2. `weekly_retention(events, cohort_week) -> list[float]`: for users whose **first login** was in `cohort_week`, the
   share active (any login/query) in weeks `cohort_week, cohort_week+1, ...` up to the last week seen (3 dp).
3. `lagging_teams(events, threshold=0.5) -> list[(team, activation_rate)]`: teams whose activation rate is below
   the threshold, sorted by rate then team.
4. `change_plan(lagging) -> list[str]`: for each lagging team, actions by severity: rate < 0.25 →
   `"<team>: executive sponsor message + hands-on workshop + named champion"`; otherwise
   `"<team>: champion office hours + in-app tips"`.
5. `diff_in_diff(pre_treat, post_treat, pre_ctrl, post_ctrl) -> dict` on per-agent metric lists (e.g. handle time):
   `treatment_change`, `control_change`, `effect = treatment_change - control_change`, and `effect_pct` relative to
   the treatment pre-mean (2 dp). Means are arithmetic.

**Errors:** `diff_in_diff` raises `ValueError` if any of the four lists is empty.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Adoption funnel, change management
and pre/post KPI impact". Before I write code, teach me adoption metrics (activation, engagement, habit), cohort
retention, change management playbooks, and difference-in-differences. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch03-technical-communication/ex82-adoption-change/starter.py so that test_adoption.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `funnel`,
`weekly_retention`, `lagging_teams`, `change_plan`, `diff_in_diff`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/ch03-technical-communication/ex82-adoption-change` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Adoption funnel, change management and pre/post KPI impact" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Is 'first login' cohort assignment correct? Are rates
relative to invited users? What assumption does difference-in-differences make, and how would you check it? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
