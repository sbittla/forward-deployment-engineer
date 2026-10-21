# ex76 hints · One service spec, three clouds (AWS, GCP, Azure)

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write one private function per cloud (`_aws`, `_gcp`, `_azure`), each returning the dict shape from the README table,
and have `render` dispatch to them or raise `ValueError`. Factor out the parts the clouds share: the plain environment
variables as a name-sorted list of `{"name", "value"}`, and a kebab-case helper for Azure secret names.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **AWS** wants CPU units and MiB as strings: `str(int(cpu * 1024))` and `str(int(memory_gb * 1024))`.
- **GCP** puts secrets at the *end* of `env`, as `valueFrom.secretKeyRef` with the name `f"{name}-{secret.lower()}"`.
- **Azure** declares each secret twice: once under `configuration.secrets` (with its Key Vault URL), and once
  referenced from the container's `env` by `secretRef`.
- `model_endpoint` and `egress_allowlist` are dict lookups by cloud. Build the allowlist as a set, then sort it.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Number formatting: GCP CPU `0.5` becomes `"0.5"`, but `memory_gb=1` must render as `"1Gi"`, not `"1.0Gi"`. A helper
  that prints whole floats as ints avoids this.
- Azure keeps `cpu` as a **number** (`0.5`), while GCP wants a string. Copy the README shape exactly for each cloud.
- GCP's secret name only lowercases (`copilot-model_api_key`). Azure's also turns `_` into `-` (`model-api-key`).
- Residency only applies when the jurisdiction is `"eu"`. Any other jurisdiction returns `[]`, whatever the region.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_aws` | CPU not converted to units (`"0.5"` instead of `"512"`); env not sorted by name |
| `test_gcp` | Secrets not at the end of `env`; memory rendered as `1.0Gi` |
| `test_azure` | Secret names not kebab-cased; CPU turned into a string |
| `test_unknown_cloud` | Unknown cloud returns `None` instead of raising |
| `test_endpoints_and_egress` | Allowlist not sorted or not deduplicated; wrong secret-service host per cloud |
| `test_residency` | Azure checked by prefix instead of the region list; non-EU jurisdictions flagged |
