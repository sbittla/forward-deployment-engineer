# ex47 · Conversation memory and summarisation

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R11 Agents, R09 Context engineering

## Learning objectives
- Keep long conversations within budget using rolling summarisation.
- Pin facts that must never be summarised away.
- Assemble context from pinned facts, summary and recent turns.

## Scenario
Field agents keep one copilot conversation open all shift. After two hours the context is huge, slow and expensive,
and the model has "forgotten" the policy number mentioned at the start. You need rolling summarisation plus pinned
facts that never get summarised away.

## Your task
`ConversationMemory(llm, max_tokens=1000, keep_recent=4)` with token count `ceil(len(text)/4)` per message:
- `add(role, content)` — append; then, while the total tokens of un-summarised messages exceed `max_tokens` **and**
  more than `keep_recent` messages are un-summarised, fold the oldest messages (all but the last `keep_recent`) into
  the running summary by calling `llm.complete` once with:
  - system: instructions to update the summary, keeping names, numbers, decisions and open questions
  - user: `"<previous_summary>...</previous_summary>\n<messages>\nrole: content\n...</messages>"`
  The reply text replaces the summary; folded messages are removed.
- `pin(key, value)` — facts that always appear in context; re-pinning a key overwrites.
- `context() -> (system_addendum, messages)`:
  - `system_addendum` contains `"Pinned facts:\n- key: value"` lines (sorted by key) if any, and
    `"Conversation summary:\n<summary>"` if there is a summary, separated by a blank line; `""` if neither.
  - `messages` = the un-summarised messages as `{"role","content"}` dicts.
- `summaries_made` counter.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Conversation memory and
summarisation". Before I write code, teach me conversation memory strategies, rolling summaries, pinned facts, and
how summarisation loses details like policy numbers. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex47-agent-memory/starter.py so that test_memory.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ConversationMemory`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch11-ai-agents/ex47-agent-memory` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Conversation memory and summarisation" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can summarisation run repeatedly in one add() and still terminate? Are pinned
facts kept verbatim? What information is most likely to be lost by the summary prompt? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
Update the running conversation summary. Keep every name, number, identifier, decision and open question exactly as written. Remove small talk. Write at most 150 words in plain sentences.

User turn:
<previous_summary>{summary}</previous_summary>
<messages>
role: content
...
</messages>
```
