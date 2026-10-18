# ex02 · Discovery interview to user stories

**Module:** m01 · **Covers:** R18 Customer discovery, R08 LLM application development · **Time:** 60 min

## Scenario
You recorded a 40-minute interview with the claims operations team. Transcribing is easy; turning it into a
backlog the customer agrees with is not. You will use an LLM to draft **user stories with acceptance criteria**
and make the pipeline robust to the model returning bad JSON.

## Your task
Implement in `starter.py`:

1. `build_prompt(transcript) -> (system, user)` — the system prompt must instruct the model to return **only**
   a JSON array of objects with keys `as_a`, `i_want`, `so_that`, `acceptance_criteria` (list of strings). The
   user message must contain the transcript wrapped in `<transcript>...</transcript>` tags.
2. `parse_stories(text) -> list[Story]` — parse JSON (tolerate a ```json fenced block), validate every story has
   the four keys, non-empty strings, and ≥1 acceptance criterion. Raise `ValueError` with a message naming the
   problem otherwise. Drop duplicate stories (same `as_a` + `i_want`, case-insensitive).
3. `extract(transcript, llm, max_attempts=2) -> list[Story]` — call `llm.complete(...)`; if parsing fails, append
   the bad reply and a user message containing the error and retry. Raise `ValueError` after `max_attempts`.

`llm` follows `fde_kit.llm.FakeLLM`'s interface: `complete(messages, system=..., ...) -> LLMResponse`.

## Acceptance criteria
- All tests pass; the retry message tells the model *what* was wrong.

## Field notes
Always read the LLM's backlog back to the customer in their words. The model drafts; the customer owns it.
