# ex47 · Conversation memory and summarisation

**Module:** m08 · **Covers:** R11 Agents, R09 Context engineering · **Time:** 45 min

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
