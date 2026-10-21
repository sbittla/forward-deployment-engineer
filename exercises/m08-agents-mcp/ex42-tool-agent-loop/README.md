# ex42 · Tool-calling agent loop

**Module:** m08 Agents, Tools & MCP · **Covers:** R11 Agents & tool use, R08 LLM apps · **Time:** 60 min

## Learning objectives
- Write the tool-calling agent loop that every framework wraps.
- Return tool results and tool errors in the provider's message format.
- Stop runaway agents with a run budget across steps, tokens, time and dollars.
- Catch loops early: repeated identical calls, per-tool caps, and timeouts reported as "outcome unknown".

## Scenario
The customer wants an assistant that can look up an order and issue a store credit. Before reaching for a
framework, write the loop yourself once — every framework (and every production incident) is a variation of it.

## Message format (Anthropic Messages API shape)
- assistant turn: `{"role": "assistant", "content": [{"type": "text", "text": ...},
  {"type": "tool_use", "id": ..., "name": ..., "input": {...}}]}`
- tool results go back in **one** user turn: `{"role": "user", "content": [{"type": "tool_result",
  "tool_use_id": ..., "content": "<string>", "is_error": bool}, ...]}`

## Your task
`run_agent(llm, tools, user_msg, system=None, max_steps=8) -> AgentResult`
- `tools`: `{name: Tool(description, input_schema, fn)}`; pass them to `llm.complete(..., tools=[{"name",
  "description", "input_schema"}])`.
- Loop: call the model; if the response has no tool calls, return `AgentResult(final_text, steps, messages)`.
  Otherwise append the assistant turn (text block only if text is non-empty, then tool_use blocks), execute **every**
  tool call, and append all results in a single user turn.
- Tool results: `json.dumps(result)` unless already a string. A raising tool → `is_error: True` with
  `"<ExceptionType>: <message>"`. Unknown tool → `is_error: True`, `"unknown tool <name>"`.
- `steps` counts model calls. If the model still wants tools after `max_steps` calls, raise `AgentLoopError`.

### Budgets and loop detection (keyword-only arguments; the defaults keep the behaviour above)
`run_agent(..., *, budget=None, usd_per_mtok=(0.0, 0.0), tool_caps=None, max_repeats=3, clock=time.monotonic)`
- `RunBudget(max_steps=8, max_tokens=200_000, max_seconds=120.0, max_usd=2.0)` also tracks `steps`, `tokens` and
  `usd` (all start at 0). `charge(tokens, usd, elapsed_s)` adds one step, the tokens and the dollars, then checks
  steps, tokens, seconds and usd in that order and raises `BudgetExceeded(f"{name}: {used} > {limit}")` for the first
  that is strictly over its limit (`name` is `steps`, `tokens`, `seconds` or `usd`).
- With a `budget`, charge it after **every** model call, before running that turn's tools:
  `tokens = input_tokens + output_tokens`, `usd = (input_tokens * usd_per_mtok[0] + output_tokens * usd_per_mtok[1])
  / 1_000_000`, and `elapsed_s = clock() - <clock() read once at the start of the run>`. A turn that exceeds the
  budget runs none of its tools.
- `call_fingerprint(name, arguments) -> str` — SHA-256 hex of `json.dumps([name, arguments], sort_keys=True)`, so
  argument order doesn't matter. Count fingerprints over the whole run, checking every call of a turn before running
  any of them; when one reaches `max_repeats`, raise `RepeatedCallError` without executing that turn.
- `tool_caps`: `{tool_name: max_calls_per_run}`. A call beyond its cap is not executed; it gets `is_error: True` and
  `"cap reached: <name> allows <n> call(s) per run"`. Calls refused by the cap don't count towards it.
- A tool that raises `TimeoutError` may have succeeded, so it is not reported as a failure: `is_error: False` and
  `"outcome unknown: <name> timed out; check the current state before retrying"`.
- `BudgetExceeded` and `RepeatedCallError` subclass `AgentLoopError`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Tool-calling agent loop". Before I
write code, teach me the Anthropic Messages API tool-use flow (tool_use blocks, tool_result blocks in one user turn,
is_error), and how agent frameworks build on this loop. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m08-agents-mcp/ex42-tool-agent-loop/starter.py so that test_agent.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Tool`,
`AgentResult`, `AgentLoopError`, `BudgetExceeded`, `RepeatedCallError`, `RunBudget`, `call_fingerprint`,
`run_agent`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed
where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/m08-agents-mcp/ex42-tool-agent-loop` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Tool-calling agent loop" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Are all tool results for one assistant turn returned in a single user message? Can a tool
exception crash the loop? Is the budget charged per model call, before that turn's tools run? Can a timed-out refund
be retried blindly? Rank findings by customer impact, quote the line for each, and say which ones a test should
catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You are an order-support assistant with tools to look up orders and issue store credit. Look up the order before taking any action on it. Issue store credit only when the order exists and the customer's request matches the policy. If a tool returns an error, explain the problem to the customer or ask for the missing information instead of retrying the same call.
```
