# ex33 · Token budgeting and context packing

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R09 Context engineering, R27 Cost & latency

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch09-llm-application-engineering/ex33-context-packing`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex33-context-packing`: all 5 pass.
- **Tests:** `test_packing.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Tokens are estimated as `ceil(len(text) / 4)`, which can be off by a factor of two for
  code, JSON or non-Latin scripts. Production packing uses the provider's token-counting endpoint or tokeniser and
  logs what was included, truncated and dropped for every request.

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
Implement exercises/ch09-llm-application-engineering/ex33-context-packing/starter.py so that test_packing.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Packed`,
`count_tokens`, `pack`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch09-llm-application-engineering/ex33-context-packing` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Token budgeting and context packing" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can packing exceed the budget by a few tokens due to rounding? Is a half pair of
history ever included? Would putting documents in the system prompt break prompt caching for this customer? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
