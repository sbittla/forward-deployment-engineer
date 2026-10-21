# Runbook

| | |
|---|---|
| **Owner** | FDE; executed by the customer's operations team before handover |
| **When** | Before handover |
| **Inputs** | Deployment, monitoring and escalation details |
| **Done when** | Passes ex69's linter, and someone other than the author has run the rollback from it |
| **Book** | Chapter 3 · ex69 |

# Overview
What the service does, who uses it, and the SLO.

# Prerequisites
Access, tools and credentials the operator needs, and how to get them.

# Deploy
Numbered steps, each with the exact command and what success looks like.

# Rollback
```bash
kubectl rollout undo deployment/<SERVICE> -n <NAMESPACE>
```
`<SERVICE>` is the deployment name and `<NAMESPACE>` its namespace; write both out here. After rollback you should
see the previous revision serving traffic. Also document how to roll back a prompt and a model (configuration only).

# Monitoring
Dashboards, alerts, what each alert means and the first thing to check.

# Escalation
On-call rotation, then the named escalation contact: name, email address and phone number.
