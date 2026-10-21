# ex83 hints · Security and procurement questionnaire responder with regulatory triage

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Model `RULES` as a dict from a **tuple of keyword stems** to `(fact_name, answer_template)`. Answering a question is
then: lowercase it, split it into words, score every rule, and keep the best one. Work out the expected confidences
in the tests by hand before you write the code, because they tell you exactly which stems each rule needs.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- A keyword hits when **any** word in the question starts with it (`retain` matches `retained`; `delet` matches
  `deletion`). Confidence = hits / number of keywords in that rule.
- Keep the rule with the highest ratio; a later rule wins only if it scores strictly higher. No hits at all means the
  "needs review" answer.
- Format fact values for humans: booleans as Yes/No, lists joined with commas.
- **answer_all** routes anything without a source fact, or below `min_confidence`, to the review queue.
- **regulatory_triage** has one small boolean expression per obligation. Build the obligations list from those, then
  sort it.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The expected confidences pin down the keyword lists: the retention question must score 0.5 and "Where is data
  hosted?" 0.25, so the retention and residency rules each need **four** stems.
- Reviewing is the safe default. An unconfident auto-answer on a security questionnaire becomes a contractual claim.
- The contradiction checks compare marketing claims with the facts: "zero retention" or "never store" against
  retention days, "never train" against the training flag, "EU only" against residency.
- The EU AI Act tier is checked in order: prohibited, then high-risk domain, then limited (chatbot or generated
  content), then minimal. A healthcare chatbot is *limited*, because healthcare isn't in the high-risk list here.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_answers` | Exact word matching instead of prefix matching; booleans printed as `True`/`False` |
| `test_unknown_goes_to_humans` | A weak match returned instead of the review text |
| `test_answer_all` | Low-confidence answers not routed to the queue, or the queue holds questions instead of indices |
| `test_contradictions` | A claim flagged even though the facts agree with it; result not sorted |
| `test_regulatory_triage` | DPIA without personal data; tier order wrong; obligations not sorted |
