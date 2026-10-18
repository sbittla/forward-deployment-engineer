# ex57 · Production Dockerfile

**Module:** m11 Deploy & Operate · **Covers:** R07 Containers & CI/CD · **Time:** 50 min

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
