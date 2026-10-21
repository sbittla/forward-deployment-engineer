# ex99 hints · Agent trajectory evals and pass^k reliability

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `tool_calls` and `final_text` first: two list comprehensions over the steps. Then build `score_trajectory`'s
`checks` dict one key at a time. Start with `has_final`, and add each other check only `if key in spec`. `passed` is
`all(checks.values())`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Order is a subsequence test**, not adjacency: the listed names must appear in that order, with anything allowed in
  between. A neat trick is one shared iterator over the call names, and `any(x == y for y in it)` for each needed name.
- **Arg checks:** for each tool in `arg_checks`, pass if *any* call to that tool has every expected key/value pair.
- **Tool-call F1 as multisets:** turn each call into `(name, tuple(sorted(arguments.items())))`, then match each made
  call against a copy of the expected list, removing each match as you use it.
- **pass@k and pass^k:** `math.comb` does the binomial coefficients.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Efficiency is `required / steps`, capped at 1, where "required" means the number of *required tools* (1 if none).
  With zero calls, it's 1.0 unless tools were required, in which case it's 0.0.
- `pass_at_k` returns 1.0 when `n - c < k`: there aren't enough failures to fill k draws.
- Validate `0 ≤ c ≤ n` and `1 ≤ k ≤ n` in **both** pass functions.
- In `run_suite`, count every failed check across all trials for `top_failures`, and sort by
  `(-count, name)`. `mean_steps` averages over every trial of every case.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_good_trajectory` | Checks added for keys not in the spec, or the `args:<tool>` key named differently |
| `test_right_answer_wrong_path` | Order checked as a set, so refund-before-lookup passes |
| `test_forbidden_wrong_args_and_no_final` | Arg check requires every call to match instead of any one |
| `test_efficiency_and_step_budget` | Efficiency uses total steps including the final; zero-call edge cases |
| `test_helpers` | `final_text` returns the first final instead of the last |
| `test_tool_call_f1` | Duplicates matched twice (sets instead of multisets); argument order breaks equality |
| `test_pass_at_k_and_pass_hat_k` | Missing the `n - c < k` shortcut; validation missing in one of the two functions |
| `test_run_suite` | Failure counts sorted by name first; steps averaged per case instead of per trial |
