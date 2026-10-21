# ex59 · CI pipeline as code

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R07 CI/CD

## Learning objectives
- Write CI workflows that pass a security audit.
- Apply least-privilege tokens, pinned actions, timeouts and deploy gates.
- Lint workflows as code.

## Scenario
The customer's security team audits every GitHub Actions workflow that touches their repos: least-privilege token
permissions, pinned actions, timeouts, no secrets echoed to logs, deploys only from `main` and only after tests pass.

## Your task
1. `lint_workflow(doc: dict) -> list[str]` (parsed YAML; note PyYAML parses the key `on` as `True` — handle both):
   | rule | fails when |
   |---|---|
   | `triggers` | the workflow doesn't run on both `pull_request` and `push` |
   | `permissions` | no top-level `permissions`, or it is `write-all`, or grants any `write` scope other than `id-token` |
   | `timeout:<job>` | a job has no `timeout-minutes` |
   | `pin:<job>` | a step `uses:` an action at a branch ref (`@main`, `@master`) or with no ref |
   | `secret-echo:<job>` | a `run:` contains `echo` and `${{ secrets.` on the same line |
   | `static-cloud-key:<job>` | anything in the job (step or job `env`, `with`) references a long-lived cloud key secret: `secrets.AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_SECRET`, `AZURE_CREDENTIALS`, `GCP_SA_KEY` or `GOOGLE_CREDENTIALS` (federate with OIDC instead) |
   | `matrix` | no job uses `strategy.matrix` with ≥ 2 python versions under key `python-version` |
   | `deploy-gate` | a job named `deploy` lacks `needs` including `test`, or lacks an `if` mentioning `refs/heads/main` |
2. Write `ci.yml` in this directory (jobs `test` and `deploy`) that has **no** issues; the test job must run `pytest`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex59-ci-pipeline`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex59-ci-pipeline`: all 5 pass.
- **Tests:** `test_ci.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linter accepts version tags, which can be moved, and looks for secrets only in `echo`
  lines. Production workflows pin actions to full commit SHAs, federate to the cloud with OIDC, and pass the
  customer's own workflow audit.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "CI pipeline as code". Before I write
code, teach me GitHub Actions security: permissions, action pinning, secret handling, matrix builds and gated
deploys. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch14-llmops-and-sre/ex59-ci-pipeline/starter.py so that test_ci.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_workflow`.
Also create ci.yml in the same folder, exactly as the README specifies. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex59-ci-pipeline` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "CI pipeline as code" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Is the 'on' key handled when YAML parses it as True? Would pinning to a tag satisfy a strict
auditor, or only a commit SHA? Can a pull request from a fork reach the deploy job? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
