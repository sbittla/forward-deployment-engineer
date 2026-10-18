# ex40 · RAG answers with citations and abstention

**Module:** m07 · **Covers:** R10 RAG, R08 LLM apps, R14 Guardrails (groundedness) · **Time:** 60 min

## Learning objectives
- Generate answers that cite sources and abstain when evidence is weak.
- Skip the model call entirely when retrieval is below threshold.
- Detect and strip invalid citations before the user sees them.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "RAG answers with citations and
abstention". Before I write code, teach me grounded generation, citation formats, abstention thresholds, and
citation validation. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m07-retrieval-rag/ex40-rag-citations/starter.py so that test_rag.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Source`, `Answer`,
`build_prompt`, `answer`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m07-retrieval-rag/ex40-rag-citations` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "RAG answers with citations and abstention" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Are formats like [1][2] and [1, 3] parsed? Is the abstain text matched
exactly? What would you log to measure how often abstention is wrong? Rank findings by customer impact, quote the
line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You answer questions about insurance policies using only the numbered sources provided. After each claim, cite the supporting source like [1] or [2]. If the sources do not contain the answer, reply exactly: {ABSTAIN_TEXT}

User turn:
[1] (doc_id) source text
[2] (doc_id) source text

Question: {question}
```
