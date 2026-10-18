# ex42 · Tool-calling agent loop

**Module:** m08 Agents, Tools & MCP · **Covers:** R11 Agents & tool use, R08 LLM apps · **Time:** 60 min

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
