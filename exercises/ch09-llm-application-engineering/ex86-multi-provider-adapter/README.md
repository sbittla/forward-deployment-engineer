# ex86 · One tool-calling interface over Claude, OpenAI and Gemini formats

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R36 Vendor AI platforms, R08 LLM apps, R05 Integration · **Hands-on:** multi-provider ·
**Time:** 75 min

## Learning objectives
- Translate one neutral tool-calling format to Anthropic, OpenAI and Gemini APIs.
- Map tool calls and tool results correctly in each wire format.
- Parse each provider's response back into one neutral shape.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch09-llm-application-engineering/ex86-multi-provider-adapter`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex86-multi-provider-adapter`: all 5 pass.
- **Tests:** `test_providers.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The adapters are tested against hand-written payloads for one snapshot of each API format
  (as of October 2026). Production adapters need tests against recorded real responses, handling of streaming,
  errors, refusals and usage fields, and a check on every SDK or API version upgrade.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "One tool-calling interface over
Claude, OpenAI and Gemini formats". Before I write code, teach me the differences between the Anthropic Messages
API, OpenAI Chat Completions and Gemini generateContent: system prompts, tool schemas, tool calls, tool results, and
role names. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch09-llm-application-engineering/ex86-multi-provider-adapter/starter.py so that test_providers.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`Reply`, `to_anthropic`, `to_openai`, `to_gemini`, `from_anthropic`, `from_openai`, `from_gemini`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch09-llm-application-engineering/ex86-multi-provider-adapter` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "One tool-calling interface over Claude, OpenAI and Gemini formats" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Are consecutive tool results merged into one
user message for Anthropic? Are OpenAI arguments a JSON string? Does Gemini receive function responses with the
right role and names? Rank findings by customer impact, quote the line for each, and say which ones a test should
catch.
```
