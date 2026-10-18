# ex57 · Production Dockerfile

**Module:** m11 Deploy & Operate · **Covers:** R07 Containers & CI/CD · **Time:** 50 min

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
Implement exercises/m11-deploy-operate/ex57-dockerize/starter.py so that test_dockerfile.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`lint_dockerfile`. Also create Dockerfile in the same folder, exactly as the README specifies. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/m11-deploy-operate/ex57-dockerize` and show
me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Production Dockerfile" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Are line continuations handled when linting? Would the image still build reproducibly in a
year? Does anything in the build context leak into the image? Rank findings by customer impact, quote the line for
each, and say which ones a test should catch.
```
