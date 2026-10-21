# ex46 · Planner/worker agents with human approval

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R11 Agent orchestration

## Learning objectives
- Separate planning from execution in a multi-agent workflow.
- Validate plans (unknown workers, dangling dependencies, cycles) before running.
- Gate risky steps behind human approval and audit every transition.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch11-ai-agents/ex46-multi-agent-hitl`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch11-ai-agents/ex46-multi-agent-hitl`: all 7 pass.
- **Tests:** `test_orchestrator.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The orchestrator trusts the planner's `requires_approval` flag and keeps its audit trail in
  an in-memory list. Production forces approval for risky workers by policy in code (Section 11.4's
  `ALWAYS_APPROVE`), records who approved what, and writes the audit trail to an append-only, tamper-evident store
  (ex56).

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Planner/worker agents with human
approval". Before I write code, teach me planner/worker orchestration, topological ordering, human-in-the-loop
approval, and audit trails. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex46-multi-agent-hitl/starter.py so that test_orchestrator.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Step`,
`RunReport`, `Orchestrator`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch11-ai-agents/ex46-multi-agent-hitl` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Planner/worker agents with human approval" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Is the topological order stable? Do skipped steps cascade correctly to
dependants? Can a planner output with a worker typo cause a side effect before validation fails? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You plan investigations for an operations team. Available workers: {worker_names}. Return only a JSON array of steps, each {"id", "worker", "task", "depends_on": [ids], "requires_approval": bool}. Use only the listed workers. Set requires_approval to true for any step that moves money, contacts a customer or changes records. Keep plans to the minimum steps needed.

User turn:
Goal: {goal}
```
