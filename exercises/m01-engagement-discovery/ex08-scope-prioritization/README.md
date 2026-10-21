# ex08 · Scope negotiation with MoSCoW under a deadline

**Module:** m01 · **Covers:** R20 Bias to action, R18 Requirements, R30 Delivery · **Time:** 45 min

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
Implement exercises/m01-engagement-discovery/ex08-scope-prioritization/starter.py so that test_scope.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ScopeError`, `Feature`, `Plan`, `plan`, `tradeoff_message`. Constraints: Python 3.11+, the standard library and the
repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When
you're done, run `pytest exercises/m01-engagement-discovery/ex08-scope-prioritization` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Scope negotiation with MoSCoW under a deadline" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does transitive dependency inclusion double-count effort? Is the
tie-break deterministic? Would the trade-off message survive being forwarded to the customer's VP unchanged? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
