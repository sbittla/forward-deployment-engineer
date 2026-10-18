# ex79 · LangGraph-style state graph with checkpoints and interrupts

**Module:** m13 · **Covers:** R11 Agent orchestration, R22 Production · **Hands-on:** LangGraph/LangChain concepts ·
**Time:** 75 min

## Scenario
Half the agent codebases you'll inherit on site use LangGraph (or something shaped like it): a typed state, nodes
that return partial updates, conditional edges, checkpoints per thread, and interrupts for human approval. Build the
core so you can debug any of them, and know exactly what the framework does for you.

| This exercise | LangGraph equivalent |
|---|---|
| `StateGraph(reducers)` | `StateGraph(State)` with `Annotated[list, add]` reducers |
| `add_node`, `add_edge`, `add_conditional_edges`, `set_entry_point`, `END` | same names |
| `compile(checkpointer, interrupt_before)` | `graph.compile(checkpointer=MemorySaver(), interrupt_before=[...])` |
| `invoke(state, thread_id)` / `resume(thread_id, updates)` | `graph.invoke(input, config={"configurable": {"thread_id": ...}})`, `update_state` + `invoke(None, ...)` |

## Your task
- `StateGraph(reducers: dict[str, callable] = {})` — keys without a reducer are overwritten by updates; keys with
  a reducer are merged with `reducer(old, new)`.
- `add_node(name, fn)` where `fn(state) -> dict` (partial update); `add_edge(src, dst)`;
  `add_conditional_edges(src, router)` where `router(state) -> node name or END`; `set_entry_point(name)`.
- `compile(checkpointer=None, interrupt_before=(), max_steps=25) -> App`. Validate and raise `ValueError` for: no
  entry point, an edge or entry referencing an unknown node, a node with no outgoing edge, a node with both a plain
  and a conditional edge, or nodes unreachable from the entry (conditional edges count as reaching every node; they
  can go anywhere).
- `App.invoke(state, thread_id=None) -> Result(state, status, steps)`: run from the entry point. Before executing a
  node listed in `interrupt_before`, stop and return `status="interrupted"` with `next=<node>` (when resuming, that
  node runs without interrupting again). Reaching `END` → `status="done"`. More than `max_steps` node executions →
  `RuntimeError`.
- Checkpointer (`MemoryCheckpointer`): after every node and at every interrupt, store
  `{"state", "next"}` under `thread_id`. `history(thread_id)` returns all checkpoints.
- `App.resume(thread_id, updates=None)` loads the latest checkpoint, applies `updates` **through the reducers**, and
  continues from `next`.
