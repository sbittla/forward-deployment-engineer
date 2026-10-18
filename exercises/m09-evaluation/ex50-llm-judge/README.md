# ex50 · LLM-as-judge with calibration

**Module:** m09 · **Covers:** R13 Evaluation · **Time:** 60 min

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
