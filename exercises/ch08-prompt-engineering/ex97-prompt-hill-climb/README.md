# ex97 · Prompt hill-climbing with a held-out test set

**Chapter:** 8 · Prompt Engineering (`exercises/ch08-prompt-engineering/`) · **Covers:** R09 Prompt & context engineering, R13 Evaluation

## Learning objectives
- Improve a prompt systematically: one candidate edit at a time, measured against an eval, not judged by eye.
- Keep a train/test split so prompt tuning doesn't overfit the cases you stare at.
- Decide whether a gain is real with a paired significance test, not a headline accuracy number.

## Scenario
The customer's triage prompt has been "tuned" for weeks in a chat window. Every change fixed the example someone
was looking at and broke two others nobody re-ran. You'll turn tuning into a loop: candidate edits, a train split
to choose among them, a held-out test split scored once at the end, and a paired test to tell the customer whether
the new prompt is actually better than the old one.

## Your task
A **model** is `(prompt, input) -> output`; a **grader** is `(output, expected) -> bool`; cases are
`{"input", "expected"}`. Scores are rounded to 4 decimal places.

- `split(cases, test_frac=0.3, seed=0) -> (train, test)`: shuffle a copy with `random.Random(seed)`; the first
  `max(1, round(n * test_frac))` cases are test, the rest train. `ValueError` unless `0 < test_frac < 1`.
- `run(prompt, cases, model, grader) -> list[bool]` and `evaluate(...) -> float` (pass rate; `0.0` for no cases).
- `hill_climb(base_prompt, edits: dict[name, fn(prompt) -> prompt], train, test, model, grader, max_rounds=5,
  min_gain=0.0) -> ClimbResult`:
  - History starts with `{"round": 0, "edit": None, "train": base_score}`.
  - Each round, apply every **unused** edit to the current prompt and score it on train. Take the best (ties: the
    edit listed first). Accept it only if its score is greater than `current + min_gain`; otherwise stop. An accepted
    edit is used up and appended to history as `{"round", "edit", "train"}`.
  - Score `test` exactly once, on the final prompt.
- `ClimbResult(prompt, train, test, history)` with property `overfit_gap = round(train - test, 4)`.
- `mcnemar_p(base: list[bool], cand: list[bool]) -> float`: exact two-sided McNemar. With `b` = cases only base
  passed and `c` = cases only the candidate passed, return `min(1, 2 × P(X ≤ min(b, c)))` for `X ~ Binomial(b + c, 0.5)`,
  rounded to 6 places; `1.0` when there are no discordant pairs; `ValueError` on length mismatch.

## Field notes
Greedy search over hand-written edits is crude, but it makes the team write their hypotheses down as edits. That
habit matters more than the optimiser. With a live model, run each prompt several times: sampling noise can be larger
than the edit's effect.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch08-prompt-engineering/ex97-prompt-hill-climb`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch08-prompt-engineering/ex97-prompt-hill-climb`:
  all 7 pass.
- **Tests:** `test_hill_climb.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The model is a deterministic stub, so one run per case is enough and `min_gain=0.0` is
  safe. With a live model, pin the model id, repeat runs per case, set `min_gain` above the run-to-run noise, freeze
  the evaluation set by content hash, and keep an experiment record (Section 8.4) for every change that ships; a
  p-value of 0.05 or more means no gain is claimed.

## Prompt kit
**Learn (tutor prompt)**
```text
Teach me how to tune prompts like an ML engineer. Explain train/test splits for prompt work, why looking at
failures in the test set leaks information, and what a paired test (McNemar) tells me that two accuracy numbers
don't. Use a 20-case classification example with numbers. Then list the 5 prompt edits you would try first on a
classification prompt that sometimes answers in full sentences.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch08-prompt-engineering/ex97-prompt-hill-climb/starter.py so test_hill_climb.py passes. Follow the
README rules for shuffling, tie-breaks, rounding and when the test split is evaluated (exactly once). Standard library
only (random, math). Don't change the tests. Show the pytest output when done. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Audit this prompt-optimisation loop for leakage and false confidence: Does anything read the test split before the
end? Is greedy acceptance with min_gain=0 likely to chase noise with a sampled model? What sample size would I need
to detect a 5-point improvement with McNemar at p<0.05? Suggest the smallest change that makes the loop robust to
sampling noise.
```
**Generate candidate edits (use with a live model)**
```text
You are helping tune a classification prompt. Below are the current prompt and 8 training failures (input, expected,
actual). Propose 5 independent, single-purpose edits to the prompt, each as a short instruction to append or a
replacement for one sentence. For each, say which failures it should fix and what it might break. Do not propose
edits that mention specific test inputs.

<prompt>{current_prompt}</prompt>
<failures>{failures}</failures>
```
