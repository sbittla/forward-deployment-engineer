# ex58 · Kubernetes manifests with probes and autoscaling

**Module:** m11 · **Covers:** R07 Containers/Kubernetes, R06 Cloud platforms · **Time:** 60 min

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
