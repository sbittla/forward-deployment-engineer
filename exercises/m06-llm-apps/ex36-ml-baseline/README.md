# ex36 · Classical ML baseline vs LLM classifier

**Module:** m06 · **Covers:** R16 ML fundamentals, R13 Evaluation, R27 Cost · **Time:** 60 min

## Scenario
The customer wants an LLM to route 500k tickets/month into `billing | login | outage`. Before you commit them to
that bill, a good FDE builds a 20-line baseline. Sometimes the baseline is good enough; sometimes it proves the
LLM is worth it. Either way, you now have numbers.

## Your task
1. `train_test_split(rows, test_ratio, seed)` — **stratified** by label, deterministic for a seed
   (use `random.Random(seed)`); each class contributes `round(n_class * test_ratio)` test rows.
2. `NaiveBayes` — multinomial Naive Bayes over `fde_kit.tokenize` tokens with Laplace smoothing (`alpha=1.0`):
   `fit(texts, labels)`, `predict_proba(text) -> {label: p}` (sums to 1; compute in log space, then softmax),
   `predict(text)`.
3. `metrics(y_true, y_pred) -> dict` with `accuracy`, `per_class` (`{label: {"precision","recall","f1"}}`, 0.0 when
   undefined), `macro_f1`, `confusion` (`{(true, pred): count}`). Round floats to 3 dp.
4. `llm_classify(llm, text, labels)` — prompt the model to answer with exactly one label; normalise the reply
   (strip, lower, strip punctuation); unknown replies → `"unknown"`.
5. `recommend(baseline, llm, monthly_volume, llm_cost_per_call)` → `"baseline"` if
   `llm["macro_f1"] - baseline["macro_f1"] < 0.03`, else `"llm"`; also returns the monthly LLM cost:
   `(choice, round(monthly_volume * llm_cost_per_call, 2))`.
