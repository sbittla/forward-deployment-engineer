# ex36 hints · Classical ML baseline vs LLM classifier

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `metrics` first. It's pure arithmetic and `test_metrics_exact` gives you every expected number. Build the
confusion matrix as a `Counter` of `(true, pred)` pairs; precision, recall and F1 for each label all come from it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Split:** group rows by label, then for each label in a fixed (sorted) order shuffle the group with one
  `random.Random(seed)` and take the first `round(n * ratio)` rows as the test set.
- **Naive Bayes:** `fit` stores the log prior per label and token counts per label (`Counter`), the vocabulary, and
  the total token count per label. To score, start from the log prior and add
  `log((count + alpha) / (total + alpha * |V|))` for each token. Then normalize: subtract the maximum score,
  exponentiate, and divide by the sum.
- **llm_classify:** list the labels in the prompt, then normalize the reply before checking membership.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Sum logs; don't multiply probabilities. Products of many small numbers underflow to 0.
- Macro-F1 averages the per-class F1 over the labels in **`y_true`**. A label that only appears in predictions
  doesn't count, so `metrics(["a","a"], ["b","b"])` gives a macro-F1 of 0.0. Average the rounded per-class values.
- Undefined precision or recall (dividing by zero) is 0.0, not an exception.
- Normalize replies with `.strip().lower().strip(string.punctuation + " ")`, so `" Billing."` becomes `billing`.
- `predict` before `fit` raises `RuntimeError`. Check that the model has labels.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_split_stratified_deterministic` | Shuffling the whole list (not stratified), or a new unseeded RNG |
| `test_naive_bayes` | Probabilities multiplied (underflow) or not normalized to sum to 1 |
| `test_metrics_exact` | Precision and recall swapped; macro averaged over predicted labels too |
| `test_llm_classify` | Reply not normalized; labels missing from the prompt |
| `test_recommend` | Threshold direction reversed, or cost not rounded to 2 dp |
| `test_predict_before_fit_and_degenerate_metrics` | No guard before fit; a prediction-only label counted in macro-F1 |
