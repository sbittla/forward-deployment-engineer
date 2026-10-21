# Design: order-operations agent with MCP connectors

## Architecture
```
customer message ──► injection gate ──► agent loop (LLM) ──► MCP client ──► MCP server ──► customer-scoped tools
                         │                    │                                              │
                         ▼                    ▼                                              ▼
                     blocked/escalate     audit log ◄──────────── approval queue ◄──── refund policy (code)
```
- One MCP server instance per authenticated customer session. Tools are bound to that customer's email, so the
  model cannot read or refund another customer's order even if it tries.
- The refund policy is plain code (`RefundPolicy`). The model can request a refund; it cannot decide one.
- Refunds above the auto-approval limit go to a human approval queue; nothing is paid until a supervisor approves.

## Tool contracts
| Tool | Input | Output | Side effect |
|---|---|---|---|
| `get_order` | `order_id` | order fields plus `refunded` so far | none |
| `list_orders` | none | the customer's orders and statuses | none |
| `issue_refund` | `order_id`, `amount` (≥ 0.01), `reason` | `refunded` or `pending_approval` with `approval_id` | money movement |

Invalid arguments return an actionable `Invalid arguments for <tool>:` message so the model can correct itself.
Expected failures (`Refund not allowed: ...`) return readable text. Unexpected exceptions return only the exception
type.

## Refund policy
- Only delivered orders, within 30 days of delivery.
- Never more than the remaining refundable balance (order total minus prior refunds).
- Up to $100.00 is refunded automatically; anything larger needs supervisor approval.

## Security model
- Customer text is untrusted. It is wrapped in `<untrusted>` tags, and the system prompt tells the model never to
  follow instructions inside it.
- Messages that trip two or more injection heuristics (instruction override, role override, exfiltration to an
  address) are blocked before any model call and routed to a human.
- Least privilege: three tools, scoped to one customer, no free-form database access.
- Every message, tool call, rejection, approval and outcome is written to a hash-chained audit log
  (`AuditLog.verify()` detects edits and deletions).

## Failure modes
| Failure | Behavior |
|---|---|
| Model loops on tools | Stops after `max_steps` and escalates to a human |
| Model invents an order id or targets another customer | Tool returns "not found on this customer's account" |
| Model requests an over-refund | Policy rejects; the balance stays intact |
| Approver unavailable | Outcome `pending_approval`; no money moves |
| OMS database error | Tool returns a generic failure; the agent tells the customer a human will follow up |

## Observability
- Scenario evals run in CI on every change: task success 100%, zero policy violations, audit chain intact.
- Production metrics: refunds per hour, approval queue depth and age, blocked-injection rate, tool error rate by
  tool.
