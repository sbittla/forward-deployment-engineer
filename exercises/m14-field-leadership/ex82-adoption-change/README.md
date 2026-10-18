# ex82 · Adoption funnel, change management and pre/post KPI impact

**Module:** m14 · **Covers:** R34 Adoption & change management, R30 Value, R13 Measurement · **Time:** 60 min

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
