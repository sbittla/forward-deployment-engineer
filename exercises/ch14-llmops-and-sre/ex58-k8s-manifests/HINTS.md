# ex58 hints · Kubernetes manifests with probes and autoscaling

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Build a dict of Deployments by name before linting anything. Services and HPAs are checked *against* the Deployments,
so you need them all first. Then dispatch on `kind`, with one helper for Deployments that returns issues prefixed with
`Deployment/<name>: `.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Deployment:** check replicas, then the pod-level `securityContext.runAsNonRoot`, then loop over the containers:
  resources (cpu *and* memory in *both* requests and limits), the two probes, image tag, secret literals and
  `readOnlyRootFilesystem`.
- **Service:** the selector must be a **subset** of some Deployment's pod-template labels (every selector key/value
  present).
- **HPA:** check `minReplicas`, and that `scaleTargetRef.name` is in your Deployment dict.
- `load` uses `yaml.safe_load_all` and drops empty (`None`) documents.
- Then write `deploy.yaml` so that it passes your own linter.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Use `.get(..., {})` all the way down. The tests delete whole sub-dicts (`securityContext`, `limits`), and a missing
  key must become an issue, not a `KeyError`.
- A secret literal is an env entry that has `value` (not `valueFrom`) **and** a name containing KEY, SECRET, TOKEN or
  PASSWORD. `LOG_LEVEL: INFO` is fine.
- Image tag rules are the same as ex57: take the tag from the last path segment only, and treat a digest as pinned.
- In your own manifest, use `valueFrom.secretKeyRef` for the API key.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_good_is_clean` | Service selector compared for equality instead of as a subset of the pod labels |
| `test_many_violations` | `KeyError` on deleted sub-dicts; issue strings formatted differently from `Kind/name: rule` |
| `test_untagged_image` | Image without a colon treated as tagged |
| `test_selector_subset_ok` | Same as above: the selector must match as a subset |
| `test_your_manifests` | Your `deploy.yaml` is missing a kind, isn't named `answer-svc`, or has no `secretKeyRef` |
