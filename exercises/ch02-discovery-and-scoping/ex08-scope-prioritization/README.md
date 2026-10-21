# ex08 · Scope negotiation with MoSCoW under a deadline

**Chapter:** 2 · Discovery and Scoping (`exercises/ch02-discovery-and-scoping/`) · **Covers:** R20 Bias to action, R18 Requirements, R30 Delivery

## Learning objectives
- Plan scope under a fixed capacity using MoSCoW and value per effort.
- Respect dependencies so nothing is included without what it needs.
- Communicate trade-offs and a phase-2 list instead of cutting quality silently.

## Scenario
The customer wants 11 features in a 6-week pilot; you have 25 engineer-days. Saying "no" well — with a plan,
the trade-offs and what lands later — is a core FDE skill.

## Your task
`Feature(name, priority, value, effort, depends_on=())` — priority is `must|should|could|wont`.

`plan(features, capacity) -> Plan(included, deferred, slack)`:
1. All `must` features (plus their dependencies, transitively) are included first. If they exceed capacity raise
   `ScopeError` whose message lists the overflow in days (e.g. `"musts need 30 days, capacity 25"`).
2. Then `should`, then `could`, each tier ordered by `value/effort` desc (ties: name). A feature is included only
   if it fits remaining capacity **and** all its dependencies are already included (or can be included together
   within capacity — include deps first).
3. `wont` features are always deferred.
4. `included` keeps inclusion order; `deferred` is sorted by name; `slack` = unused days.

`tradeoff_message(plan)` → `"Included: a, b. Deferred to phase 2: c, d. Slack: 2 days."`
(`"Deferred to phase 2: none."` when empty).

## Field notes
Never cut quality silently to fit scope. Cut scope loudly, with a written phase-2 list.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch02-discovery-and-scoping/ex08-scope-prioritization`.
- **Expected output:** all 4 tests fail against the starter; when you're done, all 4 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch02-discovery-and-scoping/ex08-scope-prioritization`: all 4 pass.
- **Tests:** `test_scope.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Value and effort are single-point guesses and the planner trusts them. Real scope plans use
  ranged estimates, keep contingency for customer dependencies and route every change through change control with the
  sponsor's approval.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Scope negotiation with MoSCoW under
a deadline". Before I write code, teach me MoSCoW prioritisation, greedy value/effort planning with dependencies,
and how to tell a customer what is deferred and why. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch02-discovery-and-scoping/ex08-scope-prioritization/starter.py so that test_scope.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ScopeError`, `Feature`, `Plan`, `plan`, `tradeoff_message`. Constraints: Python 3.11+, the standard library and the
repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When
you're done, run `pytest exercises/ch02-discovery-and-scoping/ex08-scope-prioritization` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Scope negotiation with MoSCoW under a deadline" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does transitive dependency inclusion double-count effort? Is the
tie-break deterministic? Would the trade-off message survive being forwarded to the customer's VP unchanged? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
