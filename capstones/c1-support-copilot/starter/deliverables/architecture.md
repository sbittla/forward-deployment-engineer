# Architecture: Northwind Insurance support copilot

Template: `playbook/design/architecture-summary.md` (Chapters 9, 10 and 13). Draw the request path and every trust
boundary; name the module that enforces each control.

## Diagram
```text
TODO: a Mermaid or ASCII diagram of the request path, the index, the model and the claim-review tool
```

## Components
TODO: one line per module in `copilot/` and what it owns.

## Trust boundaries
TODO: what crosses each boundary, the control, and the test that proves it.

## Degraded modes
TODO: what the copilot does when the model times out, the index is down, or a refresh is blocked.
