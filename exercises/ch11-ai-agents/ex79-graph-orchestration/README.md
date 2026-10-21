# ex79 · LangGraph-style state graph with checkpoints and interrupts

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R11 Agent orchestration, R22 Production · **Hands-on:** LangGraph/LangChain concepts ·
**Time:** 75 min

## Learning objectives
- Build the core of a LangGraph-style state graph.
- Validate graphs at compile time and checkpoint state per thread.
- Pause for human approval with interrupts and resume safely.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch11-ai-agents/ex79-graph-orchestration`.
- **Expected output:** all 4 tests fail against the starter; when you're done, all 4 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch11-ai-agents/ex79-graph-orchestration`: all 4
  pass.
- **Tests:** `test_graph.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Checkpoints live in memory, and the step limit is the only guard against cycles. Production
  uses a durable checkpointer, authorises who may resume an interrupted thread and with what updates, and records
  each resume in the audit trail.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "LangGraph-style state graph with
checkpoints and interrupts". Before I write code, teach me state graphs, reducers, conditional edges, checkpointing,
interrupts, and how LangGraph maps to these ideas. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex79-graph-orchestration/starter.py so that test_graph.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Result`,
`MemoryCheckpointer`, `StateGraph`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package
only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/ch11-ai-agents/ex79-graph-orchestration` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "LangGraph-style state graph with checkpoints and interrupts" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Are unreachable nodes detected when conditional edges
exist? Does resume apply updates through reducers? Is max_steps enforced to stop infinite loops? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
