# ex79 hints · LangGraph-style state graph with checkpoints and interrupts

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Separate building from running. `StateGraph` only records things: a dict of nodes, a dict of plain edges (`src ->
dst`), a dict of routers for conditional edges, and the entry point. `compile` validates the graph and returns an
`App` that does the running. Get the simple FAQ path working before you add checkpoints or interrupts.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Applying an update:** copy the state; for each key, use `reducer(old, new)` if that key has a reducer and already
  exists, otherwise overwrite.
- **The run loop:** `while node != END`:
  - stop at an interrupt (unless resuming);
  - count the step, and raise past `max_steps`;
  - run the node and apply its update;
  - pick the next node (the router's answer or the plain edge);
  - save a checkpoint of `{state, next}`.
- **resume:** load the latest checkpoint, apply the human's updates *through the reducers*, and continue from `next`
  with the interrupt skipped once.
- **Reachability:** a graph walk from the entry, where a conditional edge counts as reaching every node.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Save the checkpoint at the interrupt as well as after each node. The expected history for the refund thread is
  `draft_refund, issue_refund, issue_refund, END`: two node checkpoints, the interrupt, and the final node.
- Resuming must not immediately interrupt again at the same node. Pass a "skip the interrupt once" flag into the
  loop.
- Human updates go through the reducers, which is why `"human-approved"` is *appended* to the log rather than
  replacing it.
- Deep-copy checkpoints when storing and loading, or later changes to the state silently rewrite history.
- Validation covers: no entry point, an unknown target, no outgoing edge, both edge kinds on one node, and
  unreachable nodes.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_simple_path_and_reducer` | Reducer keys overwritten instead of merged; steps counted wrongly |
| `test_interrupt_and_resume_with_checkpoints` | No checkpoint at the interrupt; resume interrupts again; updates bypass the reducers |
| `test_validation` | One of the five validation rules missing (often reachability, or both edge kinds on one node) |
| `test_max_steps` | Loop never stops, or the limit is checked after running the extra node |
