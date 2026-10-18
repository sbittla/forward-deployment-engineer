# ex46 · Planner/worker agents with human approval

**Module:** m08 · **Covers:** R11 Agent orchestration · **Time:** 60 min

## Scenario
The customer wants an "AI operations analyst" that investigates a billing dispute: pull the invoice, check payment
logs, draft a customer email, and — only with a human's OK — issue a refund. A planner model writes the plan;
specialised workers execute steps; risky steps pause for approval. Everything is audited.

## Your task
`Orchestrator(planner_llm, workers: dict[str, Callable[[str, dict], str]], approve: Callable[[Step], bool])`

1. `plan(goal) -> list[Step]` — ask the planner (system prompt must list the available worker names) for a JSON
   array of `{"id", "worker", "task", "depends_on": [...], "requires_approval": bool}` and validate:
   unknown worker → `ValueError`; dependency on an unknown id → `ValueError`; cycles → `ValueError`.
   Return steps in a **topological order** (stable: original order among ready steps).
2. `run(goal) -> RunReport` — plan, then execute each step:
   - if any dependency is not `done` → status `skipped`
   - if `requires_approval` and `approve(step)` is False → `rejected`
   - else call `workers[step.worker](step.task, context)` where `context = {dep_id: output}` for its dependencies;
     success → `done` with output; exception → `failed` (output = `"<ExceptionType>: <msg>"`)
3. `RunReport(steps, statuses: {id: status}, outputs: {id: str}, audit: list[str])` — audit lines like
   `"plan: 4 steps"`, `"s1: done"`, `"s4: approval requested"`, `"s4: rejected"`, in the order they happen.
