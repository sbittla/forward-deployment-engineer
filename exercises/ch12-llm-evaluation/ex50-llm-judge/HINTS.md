# ex50 hints · LLM-as-judge with calibration

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `agreement` first. It's pure arithmetic, and the comment in `test_agreement` works the kappa example through
step by step. Turn both score lists into pass/fail booleans (`score >= threshold`) before computing kappa.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Cohen's kappa:**
  - `po` is the share of items where the two pass/fail lists agree.
  - `pe` is the agreement you'd expect by chance: `pj * ph + (1 - pj) * (1 - ph)`, where `pj` and `ph` are each
    rater's pass rates.
  - kappa is `(po - pe) / (1 - pe)`.
- **judge:** the system prompt holds the rubric and the JSON format, with `reasoning` before `score`. The user message
  holds the question, the reference and the candidate answer. Pull the first `{...}` out of the reply and parse it.
- **pairwise:** ask twice, `(a, b)` then `(b, a)`, and translate each "1" or "2" back to "A" or "B" for that order.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Validate the score strictly: `"4"` (a string), `3.5` and `True` are all invalid. Check `isinstance(score, int)` and
  exclude `bool`.
- When `pe == 1` (both raters gave the same verdict on every item), the formula divides by zero. The spec says kappa
  is 1.0 then.
- In the second pairwise call, "1" means **B**. If the two translated answers differ, the judge is following
  position, not quality: return `"tie"`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_judge_parses` | Rubric not in the system prompt; reference missing from the user message |
| `test_judge_rejects` | String, float or out-of-range scores accepted |
| `test_agreement` | Kappa computed on raw scores instead of pass/fail; `pe` formula wrong |
| `test_agreement_perfect` | Division by zero when `pe == 1` |
| `test_pairwise` | Second-order answer not translated; answers shown in the same order both times |
