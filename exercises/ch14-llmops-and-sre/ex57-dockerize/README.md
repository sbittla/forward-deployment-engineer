# ex57 · Production Dockerfile

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R07 Containers & CI/CD

## Learning objectives
- Write a production Dockerfile that passes a registry policy check.
- Lint Dockerfiles for root users, unpinned bases, secrets and cache misuse.
- Order layers for fast, reproducible builds.

## Scenario
The customer's container platform team rejects images that run as root, use `:latest`, bake secrets into layers, or
lack health checks. They run an automated policy check in their registry. You'll write the check *and* a Dockerfile
that passes it, for the answer service from ex20.

## Your task
1. `lint_dockerfile(text) -> list[str]` returns rule ids that fail (order irrelevant, no duplicates):
   | rule | fails when |
   |---|---|
   | `pinned-base` | any `FROM` image has no tag, or tag `latest` (a `@sha256:` digest also counts as pinned) |
   | `non-root` | no `USER` instruction, or the last `USER` is `root`/`0`, or it comes after `CMD`/`ENTRYPOINT` |
   | `healthcheck` | no `HEALTHCHECK` instruction |
   | `no-secrets` | an `ENV` or `ARG` sets a name containing `KEY`, `SECRET`, `TOKEN` or `PASSWORD` to a non-empty value |
   | `layer-cache` | a `pip install -r <file>` runs after a `COPY . ` (whole-context copy) |
   | `no-cache-dir` | a `pip install` without `--no-cache-dir` |
   | `exec-form` | `CMD`/`ENTRYPOINT` is not JSON exec form (`["..."]`) |
   Instructions are case-insensitive; handle `\` line continuations.
2. Write `Dockerfile` in this directory that yields **no** issues and would run `python -m app` on port 8080.

The starter `Dockerfile` violates most rules — fix it.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex57-dockerize`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex57-dockerize`: all 9 pass.
- **Tests:** `test_dockerfile.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linter checks one Dockerfile's text with simple rules; it doesn't build the image, scan
  it for vulnerabilities or verify digests and signatures. In production, run the customer's own image scanners and
  registry policies (with an SBOM and signing where required) in CI, and keep this linter as a fast pre-check.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Production Dockerfile". Before I
write code, teach me container hardening: pinned base images, non-root users, healthchecks, secret handling, layer
caching and exec-form entrypoints. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch14-llmops-and-sre/ex57-dockerize/starter.py so that test_dockerfile.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`lint_dockerfile`. Also create Dockerfile in the same folder, exactly as the README specifies. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex57-dockerize` and show
me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Production Dockerfile" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Are line continuations handled when linting? Would the image still build reproducibly in a
year? Does anything in the build context leak into the image? Rank findings by customer impact, quote the line for
each, and say which ones a test should catch.
```
