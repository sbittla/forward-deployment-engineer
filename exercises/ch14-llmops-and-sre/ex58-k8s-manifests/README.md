# ex58 · Kubernetes manifests with probes and autoscaling

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R07 Containers/Kubernetes, R06 Cloud platforms

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
     `securityContext.readOnlyRootFilesystem` not true → `readonly-fs:<c>`; container `securityContext.privileged`
     or `securityContext.allowPrivilegeEscalation` true → `privileged:<c>`
   - Service: `selector` must match the pod template labels of some Deployment → `selector`
   - HorizontalPodAutoscaler: `minReplicas` < 2 → `hpa-min`; `scaleTargetRef.name` not an existing Deployment →
     `hpa-target`
2. `load(path) -> list[dict]` reads a multi-document YAML file (skip empty documents).
3. Write `deploy.yaml` (Deployment `answer-svc`, Service, HPA) that has **no** issues. Use `secretKeyRef` for the API key.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex58-k8s-manifests`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex58-k8s-manifests`: all 6
  pass.
- **Tests:** `test_k8s.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linter checks a fixed subset of an admission policy on parsed YAML; it doesn't apply
  the manifests, prove the probes work, or cover network policies, disruption budgets and RBAC. In production, run a
  server-side dry run against the customer's real admission controller and policy set.

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
Implement exercises/ch14-llmops-and-sre/ex58-k8s-manifests/starter.py so that test_k8s.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `load`,
`lint_manifests`. Also create deploy.yaml in the same folder, exactly as the README specifies. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex58-k8s-manifests` and
show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Kubernetes manifests with probes and autoscaling" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does the Service selector really match the pod labels? Are probes
pointing at the right port and path? What happens during a rolling update with only two replicas? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
