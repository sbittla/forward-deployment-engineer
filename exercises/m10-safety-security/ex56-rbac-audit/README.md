# ex56 · RBAC and audit log for a multi-tenant AI service

**Module:** m10 · **Covers:** R17 Security, auth & compliance · **Time:** 60 min

## Scenario
Your copilot is being rolled out to three business units (tenants) of a bank. Their security architecture review
requires: role-based permissions with inheritance, strict tenant isolation, attribute limits (supervisors can
approve refunds only up to $500), and a tamper-evident audit log of every authorization decision.

## Your task
`AccessController(roles)` where `roles = {role: {"inherits": [...], "permissions": [...]}}`.
Permissions look like `"ticket:read"`, `"ticket:*"`, `"*"`, or with a numeric limit `"refund:approve<=500"`.

- `permissions(role) -> set[str]` — own plus inherited (transitively; cycles must not loop forever).
- `check(user, action, resource) -> bool` where `user = {"id", "tenant", "roles"}` and
  `resource = {"tenant", ...attrs}`:
  1. tenant mismatch → deny (`reason="tenant mismatch"`), even for `*`
  2. allowed if any permission matches: exact, `resource_type:*`, or `*`; a limited permission
     `action<=N` matches only if `resource["amount"] <= N`
  3. every decision is appended to the audit log with `(user_id, action, tenant, allowed, reason)`;
     reasons: `"tenant mismatch"`, `"granted by <permission>"`, `"no matching permission"`
- `AuditLog` — append-only, hash-chained: each entry stores `prev_hash` and `hash = sha256(prev_hash + json(entry
  without hash, sort_keys))`. The first `prev_hash` is `"0" * 64`. `verify() -> bool` recomputes the chain;
  editing or deleting any entry makes it False.
