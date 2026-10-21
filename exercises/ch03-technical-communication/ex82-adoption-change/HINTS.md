# ex82 hints · Adoption funnel, change management and pre/post KPI impact

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Everything here is set arithmetic over users. Build the sets first (invited, logged in, queried) and the funnel counts
are their sizes. For "habitual", map each user to the *set of weeks* in which they queried, and count users with at
least three distinct weeks.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Retention:** find each user's first login week (walk events sorted by week and keep the first). The cohort is
  everyone whose first login is the given week. For each week from the cohort week to the last week seen, divide the
  number of cohort members active that week (any login or query) by the cohort size.
- **lagging_teams:** per team, activation rate = logged-in users who were invited to that team / invited users.
- **diff_in_diff:** the treatment group's change minus the control group's change, which removes whatever moved both
  groups (seasonality, a new policy).
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Retention runs to the **last week in the data**, so trailing weeks with nobody active still appear as `0.0`.
- Activation is computed against *invited* users. With no invitations, return 0.0 rather than dividing by zero.
- Rates use 3 dp. Diff-in-diff values use 2 dp, and `effect_pct` is relative to the treatment group's **pre** mean.
- Diff-in-diff assumes the two groups would have moved in parallel without the change. Say so in your readout.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_funnel` | Counting events instead of distinct users; habitual counts query events, not distinct weeks |
| `test_retention` | Cohort defined by any activity instead of the first login; trailing weeks omitted |
| `test_lagging_and_plan` | Not sorted by rate then team; threshold uses `<=`; plan threshold not `< 0.25` |
| `test_diff_in_diff` | Effect sign reversed; percentage relative to the post mean |
| `test_empty_inputs` | Empty lists raise `ZeroDivisionError` instead of `ValueError`; empty funnel divides by zero |
