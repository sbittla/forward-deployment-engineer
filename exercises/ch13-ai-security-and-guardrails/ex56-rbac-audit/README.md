# ex56 · RBAC and audit log for a multi-tenant AI service

**Chapter:** 13 · AI Security and Guardrails (`exercises/ch13-ai-security-and-guardrails/`) · **Covers:** R17 Security, auth & compliance

## Learning objectives
- Enforce RBAC with inheritance, wildcards and attribute limits.
- Guarantee tenant isolation even for super-admin permissions.
- Make the audit log tamper-evident with a hash chain.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "RBAC and audit log for a
multi-tenant AI service". Before I write code, teach me role-based access control, permission inheritance,
multi-tenant isolation, attribute-based limits, and hash-chained audit logs. Use short Python examples that are not
the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to
re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch13-ai-security-and-guardrails/ex56-rbac-audit/starter.py so that test_rbac.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `AuditLog`,
`AccessController`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch13-ai-security-and-guardrails/ex56-rbac-audit` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "RBAC and audit log for a multi-tenant AI service" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Can inheritance cycles loop forever? Does '*' ever bypass the tenant
check? Does verify() detect a deleted last entry, and how would you anchor the chain externally? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
