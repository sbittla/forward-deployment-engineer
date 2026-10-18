# ex08 · Scope negotiation with MoSCoW under a deadline

**Module:** m01 · **Covers:** R20 Bias to action, R18 Requirements, R30 Delivery · **Time:** 45 min

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
