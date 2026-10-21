# ex86 hints · One tool-calling interface over Claude, OpenAI and Gemini formats

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write a small generator that walks the neutral messages and yields `(role, [messages])`, grouping **consecutive** tool
messages together. Anthropic and Gemini both need parallel tool results merged into one turn, and OpenAI simply
doesn't group. With that helper, each builder is a short loop.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Anthropic:** an assistant turn with tool calls becomes a list of content blocks (optional text, then `tool_use`
  blocks). A tool group becomes one `user` message of `tool_result` blocks.
- **OpenAI:** tool calls stay on the assistant message, with `arguments` as a **JSON string** and `content` as `None`
  when there's no text. Each tool result is its own `role: tool` message.
- **Gemini:** roles are `user` and `model`. Tool results need the *function name*, not the call id, so build an
  id → name map from the earlier tool calls first.
- **Parsers:** normalise each provider's stop reason to `end`, `tool_use` or `max_tokens`, and its tool calls to
  `{id, name, arguments}`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- OpenAI arguments come back as a JSON string. `json.loads` them (treat an empty string as `{}`).
- Gemini returns `finishReason: "STOP"` even when it calls a function, so derive `tool_use` from the presence of
  function calls, not from the finish reason.
- Gemini has no call ids. Number them `gemini_call_0`, `gemini_call_1`… in order.
- Only add a text block or part when the content is non-empty. Empty text blocks are rejected by some providers.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_anthropic_request` | Tool results sent as two user messages instead of one; empty text block added |
| `test_openai_request` | Arguments left as a dict; `content` is `""` instead of `None` for tool-only turns |
| `test_gemini_request` | `functionResponse` uses the call id instead of the tool name; roles not mapped to `model` |
| `test_parsers` | OpenAI arguments not parsed; Gemini stop taken from `finishReason`; missing generated ids |
| `test_registry_roundtrip` | `PROVIDERS` missing a provider, or holding names instead of functions |
