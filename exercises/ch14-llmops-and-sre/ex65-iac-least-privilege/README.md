# ex65 · IaC with a least-privilege IAM validator

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R06 Cloud platforms, R07 IaC, R17 Security

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex65-iac-least-privilege`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex65-iac-least-privilege`: all
  5 pass.
- **Tests:** `test_iac.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linters check a few IAM and S3 rules on JSON; they don't evaluate conditions,
  permission boundaries, organization policies or resource policies. In production, generate the policy from observed
  calls, confirm it with the cloud's access-analysis tools, and run the customer's policy-as-code checks in CI.

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
Implement exercises/ch14-llmops-and-sre/ex65-iac-least-privilege/starter.py so that test_iac.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_policy`,
`generate_policy`, `lint_terraform`. Also create infra.tf.json in the same folder, exactly as the README specifies.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch14-llmops-and-sre/ex65-iac-least-privilege` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "IaC with a least-privilege IAM validator" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Are string-or-list fields handled everywhere? Does the read-only heuristic
misclassify actions like GetObjectAcl? What would a cloud security reviewer still reject? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
