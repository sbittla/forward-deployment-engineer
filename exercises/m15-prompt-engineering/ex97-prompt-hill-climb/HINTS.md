# ex97 hints · Prompt hill-climbing with a held-out test set

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`split`, `run` and `evaluate` are a few lines each. `split` shuffles a **copy** with `random.Random(seed)` and slices
off the test set first. Run the exact test case (seed 7) to confirm your slicing matches. The hill climb builds on
`evaluate`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Keep the current prompt and its train score, plus a dict of unused edits.
- Each round, apply every unused edit to the **current** prompt and score it on train. Pick the best, with ties going
  to the edit listed first in the original dict.
- Accept it only if it beats the current score by more than `min_gain`. Otherwise stop.
- An accepted edit becomes the new prompt, is removed from the unused edits, and is appended to the history.
- After the loop, score the test set once.
- **McNemar:** count `b` (only base passed) and `c` (only the candidate passed), then sum the binomial probabilities
  up to `min(b, c)` with `math.comb`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The test split is the one thing you must not touch during the search. The test checks that the model sees each test
  input exactly once. Scoring test cases every round to pick an edit is how prompts overfit.
- Acceptance is strictly greater than `current + min_gain`. With `min_gain=0.5`, no single edit helps enough, so the
  base prompt comes back unchanged.
- The `verbose_role` edit never helps and must never be applied. That's the point: greedy search only keeps
  measurable gains.
- McNemar with no discordant pairs returns 1.0. Round to 6 places and cap at 1.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_split_is_deterministic_and_disjoint` | Input list shuffled in place; train taken from the front instead of test |
| `test_evaluate` | Empty case list divides by zero |
| `test_hill_climb_greedy_path` | Edits applied to the base prompt every round instead of the current one; ties not broken by listing order |
| `test_round_limit_and_min_gain` | `min_gain` compared with `>=`; an empty edit set crashes |
| `test_test_split_scored_once` | Test cases evaluated during the search |
| `test_overfit_gap` | Gap computed as test minus train, or not rounded |
| `test_mcnemar` | One-sided tail; concordant pairs counted; length mismatch not rejected |
