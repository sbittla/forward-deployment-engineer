# ex56 hints · RBAC and audit log for a multi-tenant AI service

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Build `AuditLog` first, because it's independent. `append(record)`: take the previous entry's hash (or 64 zeros), build
the body as the record plus `prev_hash`, hash `prev_hash + json.dumps(body, sort_keys=True)`, and store the body with
`hash` added. `verify()` walks the entries and recomputes exactly the same thing.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **permissions(role):** recursive, carrying a `seen` set. Return an empty set if the role has already been seen
  (which breaks cycles) or doesn't exist; otherwise union its own permissions with each parent's.
- **Matching one permission:**
  - `*` matches everything;
  - `type:*` matches when the action's prefix before `:` equals `type`;
  - `name<=N` matches when `name == action` and `resource["amount"] <= N`;
  - anything else must equal the action exactly.
- **check:** check the tenant first, then look for any matching permission, then append to the audit log in every
  case.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Check the tenant **before** permissions. Even `*` can't cross tenants.
- In `verify`, check both that each entry's `prev_hash` equals the previous entry's hash *and* that its own hash
  recomputes. Deleting an entry breaks the first check; editing one breaks the second.
- `granted by <permission>` names the permission that matched. Iterate in a deterministic order (sorted) so the reason
  is stable.
- A limited permission with no `amount` on the resource should not match. Defaulting the amount to infinity does that.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_inheritance` | Cycle loops forever (no `seen` set), or inherited permissions not merged |
| `test_basic` | `ticket:*` not matched as a prefix wildcard; `*` not handled |
| `test_limits` | `<=` limit compared as a string, or the boundary excluded |
| `test_tenant_isolation` | Wildcard checked before the tenant |
| `test_audit_entries_and_chain` | First `prev_hash` isn't 64 zeros; `tenant` field missing from the entry |
| `test_tamper_detection` | `verify` trusts stored hashes without recomputing them |
| `test_delete_detection` | `verify` checks each hash on its own but not the `prev_hash` link |
