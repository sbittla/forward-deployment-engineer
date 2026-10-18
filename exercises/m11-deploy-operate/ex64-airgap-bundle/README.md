# ex64 · Air-gapped deployment bundle

**Module:** m11 · **Covers:** R26 On-site embedding, R22 Production deployment, R17 Security · **Time:** 60 min

## Learning objectives
- Build a signed, checksummed bundle for air-gapped deployment.
- Verify integrity and reject unsafe archive members.
- Extract only after verification succeeds.

## Scenario
A defence customer's network has no internet access. Everything — code, models, dependencies — arrives on approved
media and is scanned at the boundary. Their security officer must be able to verify that the bundle wasn't altered
in transit, and their install script must refuse anything that would write outside the install directory.

## Your task
1. `build_bundle(src_dir, out_path, version, key: bytes) -> dict` — create a `.tar.gz` containing every file under
   `src_dir` (paths relative, POSIX separators, sorted) plus `manifest.json`:
   `{"version", "files": {relpath: {"sha256", "size"}}, "signature"}` where `signature` is
   `HMAC-SHA256(key, canonical_json(manifest without signature))` hex, with `canonical_json` =
   `json.dumps(obj, sort_keys=True, separators=(",", ":"))`. Return the manifest.
2. `verify_bundle(path, key) -> list[str]` — problems found (empty = OK):
   `"bad signature"`, `"missing: <f>"`, `"unexpected: <f>"`, `"checksum mismatch: <f>"`, `"unsafe path: <f>"` (any
   member that is absolute, contains `..`, or is a symlink/hardlink), `"no manifest"`.
3. `safe_extract(path, dest, key)` — verify first; raise `ValueError` listing problems if any; otherwise extract all
   files except the manifest into `dest`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Air-gapped deployment bundle".
Before I write code, teach me air-gapped delivery, manifests and checksums, HMAC signatures, canonical JSON, and tar
path traversal attacks. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex64-airgap-bundle/starter.py so that test_bundle.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `build_bundle`,
`verify_bundle`, `safe_extract`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m11-deploy-operate/ex64-airgap-bundle` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Air-gapped deployment bundle" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Can a symlink or '..' member write outside dest? Is the signature computed over canonical
JSON exactly? Should this use asymmetric signatures instead of HMAC, and why? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
