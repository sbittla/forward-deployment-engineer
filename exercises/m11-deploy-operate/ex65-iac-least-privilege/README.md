# ex65 · IaC with a least-privilege IAM validator

**Module:** m11 · **Covers:** R06 Cloud platforms, R07 IaC, R17 Security · **Time:** 60 min

## Learning objectives
- Lint IAM policies for wildcards, NotAction and public principals.
- Generate least-privilege policies from actual needs.
- Validate Terraform for encrypted, versioned, private buckets.

## Scenario
Your RAG service needs to read documents from one S3 bucket, write embeddings to one DynamoDB table and invoke one
model endpoint. The draft IAM policy from a tutorial grants `"Action": "*"`. The customer's cloud security team runs
a policy linter in CI; you'll write it, generate a least-privilege policy instead, and ship Terraform (JSON syntax)
for the bucket that passes their storage rules.

## Your task
1. `lint_policy(policy: dict) -> list[str]` (AWS IAM policy JSON). Statement fields may be a string or a list.
   - `wildcard-action:<action>` — any `Allow` action that is `*` or ends with `:*`
   - `wildcard-resource` — an `Allow` statement whose resources include `*` together with any action that is not
     read-only (read-only = action name after `:` starts with `Get`, `List` or `Describe`)
   - `not-action` — any statement uses `NotAction`
   - `public-principal` — `Principal` is `*` or `{"AWS": "*"}`
2. `generate_policy(needs: list[tuple[action, resource_arn]]) -> dict` — one `Allow` statement per distinct resource
   (in first-seen order), actions sorted and de-duplicated, `Sid` = `"S1"`, `"S2"`… ; `Version` = `"2012-10-17"`.
3. `lint_terraform(doc: dict) -> list[str]` over Terraform JSON (`{"resource": {type: {name: {...}}}}`):
   for every `aws_s3_bucket` named `N` require resources referencing it: an
   `aws_s3_bucket_server_side_encryption_configuration` (`sse:N`), an `aws_s3_bucket_versioning` with
   `versioning_configuration.status == "Enabled"` (`versioning:N`), and an `aws_s3_bucket_public_access_block`
   with all four `block_*`/`ignore_public_acls`/`restrict_public_buckets` flags true (`public-access:N`).
   "Referencing" means the resource's `bucket` attribute equals `"${aws_s3_bucket.N.id}"`.
4. Write `infra.tf.json` in this directory: bucket `docs` that passes `lint_terraform`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "IaC with a least-privilege IAM
validator". Before I write code, teach me least-privilege IAM, policy statement structure, and S3 storage controls
in Terraform. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex65-iac-least-privilege/starter.py so that test_iac.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_policy`,
`generate_policy`, `lint_terraform`. Also create infra.tf.json in the same folder, exactly as the README specifies.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m11-deploy-operate/ex65-iac-least-privilege` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "IaC with a least-privilege IAM validator" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Are string-or-list fields handled everywhere? Does the read-only heuristic
misclassify actions like GetObjectAcl? What would a cloud security reviewer still reject? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
