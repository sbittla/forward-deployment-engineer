# ex86 · One tool-calling interface over Claude, OpenAI and Gemini formats

**Module:** m14 · **Covers:** R36 Vendor AI platforms, R08 LLM apps, R05 Integration · **Hands-on:** multi-provider ·
**Time:** 75 min

## Scenario
Accenture's FDE posting asks for "building abstraction layers to manage multi-provider pipelines"; Deloitte lists
Claude, OpenAI and Gemini side by side. Customers often mandate a provider per region or per data class, and the
same agent has to run on all three. The hard part is the wire format: system prompts, tool schemas, tool calls and
tool results are shaped differently by each API.

## Neutral format (yours)
- `system: str`; `tools: [{"name", "description", "parameters": <JSON Schema>}]`
- messages: `{"role": "user", "content": str}`, `{"role": "assistant", "content": str, "tool_calls": [{"id", "name",
  "arguments": dict}]}` (tool_calls optional), `{"role": "tool", "tool_call_id", "content": str}`

## Your task
1. Request builders (`to_anthropic`, `to_openai`, `to_gemini`) taking `(system, messages, tools)`:
   - **Anthropic Messages API:** top-level `system`; tools `{"name", "description", "input_schema"}`; assistant tool
     calls become content blocks (a `text` block first only if the content is non-empty, then
     `{"type": "tool_use", "id", "name", "input"}`); **consecutive** tool messages merge into **one** `user` message
     of `{"type": "tool_result", "tool_use_id", "content"}` blocks.
   - **OpenAI Chat Completions:** system as the first `{"role": "system"}` message; tools `{"type": "function",
     "function": {"name", "description", "parameters"}}`; assistant `tool_calls: [{"id", "type": "function",
     "function": {"name", "arguments": <JSON string>}}]` with `content` = text or `None`; tool results
     `{"role": "tool", "tool_call_id", "content"}`.
   - **Gemini generateContent:** `systemInstruction: {"parts": [{"text"}]}`; roles `user`/`model`; assistant tool
     calls become `{"functionCall": {"name", "args"}}` parts (after a text part if content is non-empty); tool
     results become a `user` turn of `{"functionResponse": {"name": <the called tool's name>, "response":
     {"content": ...}}}` parts (consecutive results merged); `tools: [{"functionDeclarations": [...]}]`.
2. Response parsers (`from_anthropic`, `from_openai`, `from_gemini`) → `Reply(text, tool_calls, stop)` where `stop`
   is `"end"`, `"tool_use"` or `"max_tokens"`. OpenAI arguments are JSON strings (parse them). Gemini has no call
   ids, so generate `gemini_call_0`, `gemini_call_1`… in order. A Gemini reply containing a function call has stop
   `"tool_use"`.
3. `PROVIDERS = {"anthropic": (to_anthropic, from_anthropic), "openai": (...), "gemini": (...)}`.
