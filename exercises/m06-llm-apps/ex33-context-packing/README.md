# ex33 · Token budgeting and context packing

**Module:** m06 · **Covers:** R09 Context engineering, R27 Cost & latency · **Time:** 50 min

## Scenario
Long conversations plus 20 retrieved policy chunks blew through the customer's per-request cost budget and
latency SLO. Context is a budget: spend it on what most improves the answer.

## Your task
`count_tokens(text) = ceil(len(text) / 4)` (a deliberate approximation; in production use the provider's
token-counting endpoint).

`pack(system, question, docs, history, budget, reserve_output) -> Packed`
- `docs`: list of `(doc_id, text, score)`; `history`: chronological list of `{"role","content"}` messages.
- Available input tokens = `budget - reserve_output`. `system` and `question` are mandatory; if they alone don't fit,
  raise `ValueError`.
- Add docs by **score desc**. If a doc doesn't fit and at least `MIN_PARTIAL = 50` tokens remain, include a
  truncated prefix (`text[: remaining * 4]`) and record it in `truncated`; then stop adding docs.
- Then add **history from most recent backwards**, in whole user/assistant pairs (the last two messages form the
  most recent pair), while they fit. Keep chronological order in the output.
- Output `Packed(system, messages, included_docs, truncated, dropped_docs, tokens)`:
  - `system` = original system + `"\n\n<documents>\n"` + each included doc as
    `<doc id="ID">TEXT</doc>` joined by `"\n"` + `"\n</documents>"` (omit the block if no docs)
  - `messages` = packed history + `{"role": "user", "content": question}`
  - `tokens` = sum of `count_tokens` over the final system text and every message content.
