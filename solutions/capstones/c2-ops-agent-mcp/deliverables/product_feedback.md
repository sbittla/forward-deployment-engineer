# Product feedback from the retail order-ops deployment

## Summary
We built three pieces of infrastructure by hand that every agentic deployment with side effects will need. Building
them into the platform would cut each new customer's time to production by an estimated 2–3 weeks.

## Requests
1. **First-class approval workflows for tools.** Mark a tool `requires_approval_over` with a threshold and route
   calls to a reviewer UI with a queue, SLAs and audit. We hand-built the `ApprovalQueue` for this.
2. **Per-session tool scoping in the MCP layer.** Bind a server instance to an authenticated principal so tools
   cannot reach other tenants' data. Today every connector reimplements the ownership check.
3. **Tamper-evident audit export.** A hash-chained log of messages, tool calls and decisions that compliance can
   verify independently. Two other retail prospects asked for this in security review.
4. **Built-in injection screening hooks.** A pre-model hook with pluggable detectors and a "block and escalate"
   action, measured in evals.

## Evidence
- Retail customer: 31% of refund requests in the pilot were above the $100 auto-approval limit and needed the
  approval flow.
- Security review raised tenant isolation and audit integrity as blocking items. Both were resolved with custom code.
- The scenario eval suite (10 scenarios, including malicious ones) is reusable and could ship as a template.
