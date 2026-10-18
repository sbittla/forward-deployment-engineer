# ex03 · ROI and payback model for an AI deployment

**Module:** m01 · **Covers:** R30 Value metrics, R27 Cost optimization · **Time:** 45 min

## Scenario
The CFO of your customer asks: *"What does this pay back, and when?"* An FDE who can answer with a defensible
model — including the model's token bill and a sensitivity analysis — earns the right to go to production.

## Your task
Implement in `starter.py` (all money in the same currency, monthly volumes):

| Function | Formula / behaviour |
|---|---|
| `annual_labor_savings(tasks_per_month, minutes_saved, hourly_cost, adoption=1.0)` | `tasks*12*adoption*minutes/60*hourly_cost` |
| `annual_llm_cost(tasks_per_month, in_tokens, out_tokens, price_in_mtok, price_out_mtok, calls_per_task=1)` | token cost per call × calls × tasks × 12 |
| `payback_months(one_time_cost, monthly_net_benefit)` | `inf` if net benefit ≤ 0, else cost / benefit |
| `roi_summary(**inputs)` | dict with `annual_savings`, `annual_llm_cost`, `annual_run_cost` (llm + `annual_platform_cost`), `annual_net`, `roi_pct` (first year, includes one-time cost), `payback_months` — rounded to 2 dp |
| `sensitivity(inputs, param, multipliers)` | list of `(multiplier, annual_net)` re-running the summary with `inputs[param] * m` |

`roi_summary` takes keyword args: `tasks_per_month, minutes_saved, hourly_cost, adoption, in_tokens, out_tokens,
price_in_mtok, price_out_mtok, calls_per_task, annual_platform_cost, one_time_cost`.

## Field notes
Lead with adoption sensitivity: the token bill is rarely what kills ROI — low adoption is.
