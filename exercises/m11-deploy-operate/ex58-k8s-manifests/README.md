# ex58 · Kubernetes manifests with probes and autoscaling

**Module:** m11 · **Covers:** R07 Containers/Kubernetes, R06 Cloud platforms · **Time:** 60 min

## Learning objectives
- Ship Kubernetes manifests that pass admission policies first time.
- Configure probes, resources, security context and autoscaling.
- Reference secrets instead of literal values.

## Scenario
The customer runs EKS/GKE/AKS with an admission controller enforcing their platform standards. Your deployment was
rejected twice last week. Encode the standards as a linter and ship manifests that pass on the first try.

## Your task
1. `lint_manifests(docs: list[dict]) -> list[str]` — `docs` are parsed YAML documents. Return issue strings
   `"<Kind>/<name>: <rule>"` for:
   - Deployment: `replicas` < 2 → `replicas`
   - every container: missing `resources.requests` or `resources.limits` (both cpu & memory) → `resources:<container>`;
     no `livenessProbe` → `liveness:<c>`; no `readinessProbe` → `readiness:<c>`; image tag missing or `latest` →
     `image-tag:<c>`; an `env` entry with a literal `value` whose name contains KEY/SECRET/TOKEN/PASSWORD →
     `secret-literal:<c>`
   - pod `securityContext.runAsNonRoot` not true → `non-root`; container
     `securityContext.readOnlyRootFilesystem` not true → `readonly-fs:<c>`
   - Service: `selector` must match the pod template labels of some Deployment → `selector`
   - HorizontalPodAutoscaler: `minReplicas` < 2 → `hpa-min`; `scaleTargetRef.name` not an existing Deployment →
     `hpa-target`
2. `load(path) -> list[dict]` reads a multi-document YAML file (skip empty documents).
3. Write `deploy.yaml` (Deployment `answer-svc`, Service, HPA) that has **no** issues. Use `secretKeyRef` for the API key.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Kubernetes manifests with probes and
autoscaling". Before I write code, teach me Kubernetes Deployments, Services and HPAs, readiness vs liveness probes,
resource requests and limits, and pod security settings. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex58-k8s-manifests/starter.py so that test_k8s.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `load`,
`lint_manifests`. Also create deploy.yaml in the same folder, exactly as the README specifies. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/m11-deploy-operate/ex58-k8s-manifests` and
show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Kubernetes manifests with probes and autoscaling" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does the Service selector really match the pod labels? Are probes
pointing at the right port and path? What happens during a rolling update with only two replicas? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
