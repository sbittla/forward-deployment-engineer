# ex33 · Token budgeting and context packing

**Module:** m06 · **Covers:** R09 Context engineering, R27 Cost & latency · **Time:** 50 min

## Learning objectives
- Treat the context window as a budget and spend it on what improves answers.
- Pack documents by relevance with controlled truncation.
- Keep recent conversation in whole turns and preserve chronology.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Token budgeting and context
packing". Before I write code, teach me context engineering: token budgets, output reservations, document packing,
truncation policies, and history trimming in user/assistant pairs. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m06-llm-apps/ex33-context-packing/starter.py so that test_packing.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Packed`,
`count_tokens`, `pack`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m06-llm-apps/ex33-context-packing` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Token budgeting and context packing" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can packing exceed the budget by a few tokens due to rounding? Is a half pair of
history ever included? Would putting documents in the system prompt break prompt caching for this customer? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
