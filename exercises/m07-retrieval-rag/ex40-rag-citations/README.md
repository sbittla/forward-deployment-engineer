# ex40 · RAG answers with citations and abstention

**Module:** m07 · **Covers:** R10 RAG, R08 LLM apps, R14 Guardrails (groundedness) · **Time:** 60 min

## Scenario
The insurer's compliance team has one non-negotiable: every answer about coverage must cite the policy text it
came from, and when the documents don't contain the answer, the assistant must say so rather than improvise.

## Your task
`answer(question, retrieve, llm, k=4, min_score=0.2) -> Answer`

- `retrieve(question, k) -> list[Source]` where `Source(doc_id, text, score)` sorted by score desc.
- If there are no sources or the top score is below `min_score`, **do not call the LLM**; return
  `Answer(text=ABSTAIN_TEXT, citations=[], abstained=True, grounded=True, invalid_citations=[])`.
- Otherwise build the prompt with `build_prompt(question, sources) -> (system, user)`:
  - system: answer only from the sources; cite with `[n]` after each claim; if the sources don't contain the
    answer reply exactly `ABSTAIN_TEXT`
  - user: sources numbered from 1 as `[1] (doc_id) text` lines, then `Question: ...`
- Parse `[n]` markers (also `[1][2]` and `[1, 3]`). Map valid numbers to `doc_id`s (deduplicated, in first-seen
  order). Numbers outside `1..len(sources)` go to `invalid_citations` and are removed from the returned text.
- If the model replied with `ABSTAIN_TEXT`, return `abstained=True`.
- `grounded` is True only when the answer has ≥ 1 valid citation and no invalid ones (or abstained).
