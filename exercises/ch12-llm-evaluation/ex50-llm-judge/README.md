# ex50 · LLM-as-judge with calibration

**Chapter:** 12 · LLM Evaluation (`exercises/ch12-llm-evaluation/`) · **Covers:** R13 Evaluation

## Learning objectives
- Use an LLM judge for criteria regex can't check.
- Measure judge-human agreement with exact match, within-1 and Cohen's kappa.
- Detect and neutralise position bias in pairwise judging.

## Scenario
Many copilot answers can't be graded by regex ("Is this explanation of the exclusion accurate and polite?"). An
LLM judge scales grading, but only if you check it agrees with humans and isn't fooled by answer order.

## Your task
1. `judge(llm, question, answer, reference, rubric) -> Verdict(score, reasoning)` — the system prompt contains the
   rubric and asks for JSON `{"reasoning": str, "score": 1-5}` (reasoning first, so the model thinks before
   scoring). Parse the first JSON object in the reply; invalid JSON or a score outside 1–5 (or not an int) →
   `ValueError`.
2. `agreement(judge_scores, human_scores) -> dict` with `exact` (share equal), `within_1` (share |diff| ≤ 1), and
   `kappa`: Cohen's kappa on pass/fail where pass = score ≥ `threshold` (default 4). Round to 3 dp. If expected
   agreement is 1, kappa is 1.0.
3. `pairwise(llm, question, a, b) -> "A" | "B" | "tie"` — ask the judge twice with the answers in both orders; the
   model replies `"1"` or `"2"` (first/second shown). Return the winner only if both orders agree; otherwise `"tie"`
   (position bias).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch12-llm-evaluation/ex50-llm-judge`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch12-llm-evaluation/ex50-llm-judge`: all 9 pass.
- **Tests:** `test_judge.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Order-swapping removes only position bias; verbosity and self-preference bias pass straight
  through, and the kappa is only as good as the expert-labelled sample behind it. In production, pin the judge's
  model version and rubric, store them with every score, re-run calibration (including length-matched pairs) whenever
  either changes, and send critical cases graded only by the judge to expert review.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "LLM-as-judge with calibration".
Before I write code, teach me LLM-as-judge design (rubrics, reasoning before score), calibration against human
labels, Cohen's kappa, and position bias. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch12-llm-evaluation/ex50-llm-judge/starter.py so that test_judge.py passes. README.md in that folder
is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Verdict`, `judge`,
`agreement`, `pairwise`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch12-llm-evaluation/ex50-llm-judge` and show me the output. If the README and the tests disagree, stop and tell
me instead of guessing.
```
**Review**
```text
Review my solution to "LLM-as-judge with calibration" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Is the score validated as an integer in range, rejecting 4.5 and True? Is kappa correct
when expected agreement is 1? Does pairwise judging swap the answers, not just the labels? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You grade a support copilot's answer against a reference answer using this rubric:
{rubric}

Think through the rubric first, then score. Return only JSON: {"reasoning": "<2-4 sentences>", "score": <integer 1-5>}.

User turn:
<question>{question}</question>
<reference>{reference}</reference>
<answer>{answer}</answer>
```
