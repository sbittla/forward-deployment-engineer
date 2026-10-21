# ex03 hints · ROI and payback model for an AI deployment

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

The first three functions are one-line formulas from the README table. Write those, check them against the comment in
`test_llm_cost`, then build `roi_summary` by calling them rather than repeating the arithmetic.
</details>

<details>
<summary>Hint 2 · The approach</summary>

In `roi_summary`, work in this order: annual savings, then annual LLM cost, then run cost (LLM plus
`annual_platform_cost`), then net (savings minus run cost). Payback uses the **monthly** net benefit, `net / 12`.
First-year ROI subtracts the one-time cost from the gain and adds it to the cost:
`(net - one_time) / (one_time + run) * 100`. Round each output to 2 dp only at the end.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Token prices are per **million** tokens. Divide by `1e6`, not `1e3`.
- `sensitivity` must not change the caller's dict. Build a new one for each multiplier (`{**inputs, param: ...}`)
  and re-run `roi_summary` on it. When `param` is a tuple, scale every name in it by the same multiplier; a
  plain string is a one-name tuple.
- `payback_months` returns `math.inf` when the benefit is zero *or negative*. Keep the infinity when you round in
  the summary.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_labor_savings` | Forgot `* 12` (monthly to annual) or `/ 60` (minutes to hours) |
| `test_llm_cost` | Prices treated as per-thousand tokens, or `calls_per_task` ignored |
| `test_payback` | Only `== 0` handled; a negative benefit must also give infinity |
| `test_summary` | Run cost missing the platform cost; ROI computed without the one-time cost on both sides |
| `test_sensitivity` | The input dict changed in place (the test checks `adoption` is still 0.6 afterwards) |
| `test_sensitivity_scales_several_params_together` | A tuple `param` used as one dict key, or only the first name scaled |
| `test_edge_cases` | Division by zero when volume or adoption is zero |
