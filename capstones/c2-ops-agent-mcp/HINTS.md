# Capstone 2 hints · Agentic order operations with MCP connectors (retail)

This is a multi-day engagement, so these hints point to the order of work and the exercises you've already solved.
Open a hint only after you've been stuck for a while. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Build from the bottom up. The safety of this system lives in the lower layers, not in the prompt:

| Order | Module | Reuse |
|---|---|---|
| 1 | `store.py` | plain SQLite queries |
| 2 | `policy.py` | small pure function |
| 3 | `audit.py` | ex56 hash chain |
| 4 | `tools.py` | ex43 validation, ex10 idempotency ideas |
| 5 | `mcp.py` | ex44 server, ex45 client |
| 6 | `agent.py` | ex42 loop, ex54 injection defenses |
| 7 | `evals.py` | ex49 harness |

`test_c2_store_policy.py` and `test_c2_mcp_tools.py` don't involve a model at all. Get them green first.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Policy:** delivered? Within 30 days? Amount ≤ remaining balance (order total minus refunds so far)? Allowed
  above $100 but needs approval. Always return a reason.
- **Tools are customer-scoped when they're built:** `build_tools(store, policy, customer, …)` closes over the
  authenticated customer, and an order belonging to anyone else simply reports "not found". The model can't talk its
  way past code that never looks at other customers' rows.
- **issue_refund:** validate the arguments, evaluate the policy, then refund, queue for approval, or return an
  actionable error. Audit every outcome.
- **The agent:**
  1. Count the injection signals and block before any model call if there are two or more.
  2. Wrap the message as untrusted.
  3. Run the tool loop through the MCP client.
  4. Escalate at `max_steps`.
  5. Map what happened to the outcome status.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Neutralize any `</untrusted>` inside the customer text, so it can't close your wrapper early (the test checks there
  is exactly one).
- Approval over the limit: with no approver available, the status is `pending_approval` and nothing is refunded. When
  a supervisor resolves an approval, the refund happens then, and is audited.
- The remaining balance is inclusive: refunding exactly the remaining $100 is allowed, $100.01 is not.
- The eval runner re-checks **every refund in the store** against the policy independently. Don't trust the agent's
  own report of what it did.
- The MCP server is ex44 again: `_meta` version on each request, `-32022` with the supported and requested versions,
  `resultType` and `ttlMs` in the modern era, and legacy `initialize` still answered.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_store` | Refund ids not sequential with the seeded data; `today` not read from the snapshot |
| `test_policy` | Balance check uses the order total instead of the remaining balance; boundary off by a cent |
| `test_audit_chain` | `verify` doesn't recompute the hash over each entry's data |
| `test_discovery_and_listing` | `connect` not using `server/discover`; required fields missing from the schema |
| `test_tools_are_customer_scoped` | Another customer's order returned, or a different error leaks that it exists |
| `test_refund_paths` | Policy reason not passed through; validation error format differs from ex43 |
| `test_approval_queue` | Refund recorded before approval; approval resolution not audited |
| `test_protocol_errors` | Missing `_meta` accepted; `-32022` data incomplete; reply sent for a notification |
| `test_legacy_handshake_still_served` | Legacy replies include `resultType`, or `initialize` not supported |
| `test_injection_blocked_before_model` | Injection check runs after the model call, or isn't audited |
| `test_message_is_wrapped_and_tools_passed` | Wrapper not neutralized; system prompt doesn't tell the model the content is untrusted |
| `test_pending_when_no_approver` | Over-limit refund executed, or the status not set to `pending_approval` |
| `test_runaway_loop_escalates` | No step limit, or the actions not recorded |
| `test_scenario_suite` | Read `m["failures"]`: each names the scenario and the expected outcome |
| `test_deliverable` | A required heading missing, a placeholder left in, or fewer than three bolded feature requests |
