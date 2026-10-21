# ex36 · Classical ML baseline vs LLM classifier

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R16 ML fundamentals, R13 Evaluation, R27 Cost

## Learning objectives
- Build a classical baseline before committing a customer to an LLM bill.
- Evaluate classifiers with stratified splits and macro F1.
- Recommend baseline vs LLM with cost and quality numbers.

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
4. `llm_classify(llm, text, labels)` — prompt the model to answer with exactly one label; normalize the reply
   (strip, lower, strip punctuation); unknown replies → `"unknown"`.
5. `recommend(baseline, llm, monthly_volume, llm_cost_per_call)` → `"baseline"` if
   `llm["macro_f1"] - baseline["macro_f1"] < 0.03`, else `"llm"`; also returns the monthly LLM cost:
   `(choice, round(monthly_volume * llm_cost_per_call, 2))`.

**Errors:** calling `predict_proba`/`predict` before `fit` raises `RuntimeError`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch09-llm-application-engineering/ex36-ml-baseline`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch09-llm-application-engineering/ex36-ml-baseline`:
  all 6 pass.
- **Tests:** `test_baseline.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The dataset is small and synthetic, and the comparison uses a single split. Before
  recommending a model in production, evaluate on the customer's labeled tickets with repeated or time-based splits,
  report confidence intervals, and re-check the decision as the ticket mix drifts.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Classical ML baseline vs LLM
classifier". Before I write code, teach me multinomial Naive Bayes, stratified splitting, precision/recall/F1 and
confusion matrices, and how to compare an LLM classifier against a cheap baseline. Use short Python examples that
are not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me
what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch09-llm-application-engineering/ex36-ml-baseline/starter.py so that test_baseline.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `train_test_split`,
`NaiveBayes`, `metrics`, `llm_classify`, `recommend`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch09-llm-application-engineering/ex36-ml-baseline` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Classical ML baseline vs LLM classifier" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Is the split leak-free and deterministic? Is log-space softmax numerically
stable? Is a 0.03 macro-F1 threshold defensible for this customer, and what volume makes the LLM worth it? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
Classify the support ticket into exactly one of these labels: {labels}. Reply with the label only, in lowercase, with no punctuation or explanation.

<ticket>
{ticket_text}
</ticket>
```
