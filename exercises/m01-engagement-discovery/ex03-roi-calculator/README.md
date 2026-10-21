# ex03 · ROI and payback model for an AI deployment

**Module:** m01 · **Covers:** R30 Value metrics, R27 Cost optimization · **Time:** 45 min

## Learning objectives
- Build a defensible ROI and payback model that includes the model's token bill.
- Show which assumption dominates the outcome with a sensitivity analysis.
- Explain ROI to a CFO in terms of adoption risk, not only token cost.

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
| `sensitivity(inputs, param, multipliers)` | list of `(multiplier, annual_net)` re-running the summary with `inputs[param] * m`; `param` may also be a tuple of names scaled together, e.g. `("price_in_mtok", "price_out_mtok")` for the token price |

`roi_summary` takes keyword args: `tasks_per_month, minutes_saved, hourly_cost, adoption, in_tokens, out_tokens,
price_in_mtok, price_out_mtok, calls_per_task, annual_platform_cost, one_time_cost`.

## Field notes
Lead with adoption sensitivity: the token bill is rarely what kills ROI — low adoption is.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "ROI and payback model for an AI
deployment". Before I write code, teach me how to model labor savings, LLM token cost and platform cost for an AI
deployment, how first-year ROI and payback months are computed, and why adoption sensitivity usually matters more
than price per token. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m01-engagement-discovery/ex03-roi-calculator/starter.py so that test_roi.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`annual_labor_savings`, `annual_llm_cost`, `payback_months`, `roi_summary`, `sensitivity`. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest
exercises/m01-engagement-discovery/ex03-roi-calculator` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "ROI and payback model for an AI deployment" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Are monthly and annual figures mixed anywhere? Does payback handle zero
or negative benefit? Which input would a skeptical CFO challenge first, and does the sensitivity output answer that
challenge? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
