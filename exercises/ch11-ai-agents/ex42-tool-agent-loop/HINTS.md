# ex42 hints · Tool-calling agent loop

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Build the tool specs once, before the loop: `[{"name": n, "description": t.description, "input_schema":
t.input_schema} for n, t in tools.items()]`. Then write a separate `_execute(tools, call)` helper that turns one tool
call into one `tool_result` block, success or failure. The loop itself is short once that helper exists.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Loop `for step in range(1, max_steps + 1)`:

1. Call the model with the messages, system prompt and tool specs.
2. No tool calls? Return the result, with `step` as the step count.
3. Otherwise, append one **assistant** turn whose content is a list of blocks: a `text` block (only if there's
   text), then one `tool_use` block per call (`id`, `name`, `input`).
4. Append one **user** turn whose content is the list of `tool_result` blocks, one per call, in the same order.

If the loop ends without returning, raise `AgentLoopError`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- All results for one model turn go in a **single** user turn. One turn per result breaks the alternation that the
  API expects.
- Each `tool_result` echoes `tool_use_id`, and always sets `is_error` (to `False` on success too).
- A raising tool becomes `"<ExceptionType>: <message>"` with `is_error: True`. Catch it inside `_execute`, so the other
  calls in the same turn still run.
- Encode non-string results with `json.dumps`. Pass a **copy** of the messages list to `llm.complete` if you keep
  appending to it afterward.
- Charge the budget straight after `llm.complete` returns, before the "no tool calls?" check and before any tool
  runs. Otherwise the over-budget turn's side effects have already happened when you stop.
- Repeats: keep one `{fingerprint: count}` dict for the whole run, not per turn. Check every call in the turn before
  executing any of them.
- Catch `TimeoutError` before the generic `except Exception`, or it becomes an ordinary error result.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_multi_step` | Tools or system prompt not passed; text block missing from the assistant turn; result not JSON-encoded |
| `test_parallel_results_single_turn_and_errors` | One user turn per result; an exception aborts the turn; empty text block added |
| `test_max_steps` | Loop runs forever, or returns instead of raising after `max_steps` |
| `test_budget_tokens_stops_before_tools_run` | Budget charged after the tools ran; input and output tokens not both counted |
| `test_budget_usd` | Prices applied per token instead of per million tokens; input and output prices swapped |
| `test_budget_seconds_uses_clock` | `time.monotonic` called directly instead of the `clock` argument; start time re-read each step |
| `test_budget_within_limits` | The final (no tool calls) response not charged |
| `test_repeated_identical_call_detected` | Counts reset each turn; `sort_keys` missing so key order changes the fingerprint |
| `test_per_tool_cap` | Cap check after executing; refused calls counted toward the cap; wrong message text |
| `test_timeout_is_outcome_unknown` | `TimeoutError` caught by the generic handler and reported with `is_error: True` |
