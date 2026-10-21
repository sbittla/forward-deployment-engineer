# ex57 hints · Production Dockerfile

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Before checking any rule, normalise the file into a list of `(INSTRUCTION, rest)` pairs. Join `\` continuations into
one line (a regex replacing a backslash, optional spaces and a newline with a space does it), skip blank lines and
comments, and uppercase the instruction word. Every rule then becomes a short loop over that list.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Per-instruction rules** (`pinned-base`, `no-secrets`, `exec-form`, `no-cache-dir`) can be checked in one pass.
- **Order rules** need positions:
  - `non-root` compares the index of the last `USER` with the index of the last `CMD` or `ENTRYPOINT`;
  - `layer-cache` compares the first `pip install -r` with the first `COPY` whose source is `.` or `./`.
- Collect issues in a set, so each rule appears once.
- Then write your own `Dockerfile`: dependencies first, `--no-cache-dir`, a non-root numeric user, a `HEALTHCHECK`
  in exec form, and `CMD ["python", "-m", "app"]`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Image tags: `python@sha256:…` counts as pinned. A registry with a port (`reg:5000/app`) has a colon that *isn't* a
  tag, so look for the tag only in the last path segment.
- `ARG GITHUB_TOKEN` (no value) and `ARG BUILD_TOKEN=` (empty value) are fine. Only a non-empty value is a secret.
- `USER` placed *after* `CMD` doesn't help the running container, which is why it fails `non-root`.
- Slim images have no `curl`, so write the health check with `python -c "import urllib.request; …"`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_bad_has_all_issues` | A rule missing, or instructions matched case-sensitively |
| `test_good_clean` | Continuation lines not joined, so `--no-cache-dir` on the next line is missed; `AS base` breaks tag parsing |
| `test_rules` | Digest-pinned image flagged; `ARG` with no value flagged as a secret; `USER` after `CMD` accepted |
| `test_your_dockerfile_passes` | Your `Dockerfile` still breaks a rule, or doesn't mention `8080` and `app` |
