# ex65 hints · IaC with a least-privilege IAM validator

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

IAM fields can be a string or a list. Write a `_list(value)` helper that always returns a list (and `[]` for `None`),
and use it on `Statement`, `Action`, `Resource` and `Principal.AWS`. Most of the linter is then straightforward
membership tests.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Check `NotAction` and the public principal on **every** statement, then skip anything whose `Effect` isn't `Allow`
  for the remaining rules.
- `wildcard-action:<a>` for each action that is `*` or ends with `:*`.
- `wildcard-resource` when the resources include `*` and any action isn't read-only. Read-only means the part after
  `:` starts with Get, List or Describe.
- **generate_policy:** group actions by resource in first-seen order (a dict keeps insertion order), using a set for
  each resource's actions. Then emit sorted actions with `Sid` `S1`, `S2`, ….
- **lint_terraform:** for each bucket, look for resources whose `bucket` equals the exact interpolation string
  `${aws_s3_bucket.NAME.id}`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A `Deny` statement with `*` everywhere is fine. Broad denies are good.
- Remove duplicate issues while keeping their order (`dict.fromkeys`).
- Versioning must be `Enabled`. A versioning resource with `Suspended` still fails.
- The public access block needs all four flags exactly `True`. One `False` fails it.
- In Python, `f"${{aws_s3_bucket.{name}.id}}"` builds the reference string: doubled braces are literal.
- Then write `infra.tf.json` with bucket `docs` and its three companion resources.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_lint_policy` | Rules skipped for single-string fields; Deny statements flagged; duplicates repeated |
| `test_read_only_wildcard_resource_ok` | Any `Resource: *` flagged, without checking for read-only actions |
| `test_generate` | Statements grouped by action instead of resource; actions not sorted or not deduplicated |
| `test_lint_terraform` | Companion resources matched by name instead of by `bucket` reference; flags checked for truthiness only on some keys |
| `test_your_infra` | Your `infra.tf.json` lacks one of the three companion resources or doesn't reference `docs` correctly |
