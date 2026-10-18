# ex65 · IaC with a least-privilege IAM validator

**Module:** m11 · **Covers:** R06 Cloud platforms, R07 IaC, R17 Security · **Time:** 60 min

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
