# ex64 · Air-gapped deployment bundle

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R26 On-site embedding, R22 Production deployment, R17 Security

## Learning objectives
- Build a signed, checksummed bundle for air-gapped deployment.
- Verify integrity and reject unsafe archive members.
- Extract only after verification succeeds.

## Scenario
A defense customer's network has no internet access. Everything — code, models, dependencies — arrives on approved
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
   `verify_bundle(path, key, installed_version=None)`: when `installed_version` is given and the signature is valid,
   compare versions numerically, part by part (`1.10.0` is newer than `1.9.2`). A bundle older than the installed
   version adds `"downgrade: <bundle version> < <installed version>"` (a replayed old bundle); the same version is
   allowed. If either version isn't dot-separated integers, add `"unparseable version: <bundle version>"`.
   A deliberate rollback is also a downgrade: the operator either re-signs the previous release with a higher version
   number or runs the install without `installed_version`, recording who approved it in the change record.
3. `safe_extract(path, dest, key, installed_version=None)` — verify first (passing `installed_version` on); raise
   `ValueError` listing problems if any; otherwise extract all files except the manifest into `dest`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex64-airgap-bundle`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex64-airgap-bundle`: all 5
  pass.
- **Tests:** `test_bundle.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Signs with a shared HMAC key, so anyone who can verify can also sign, and nothing refuses
  an older bundle. In production, sign with an asymmetric key held in a KMS or HSM, pin the public key on the
  customer's side, refuse downgrades, ship an SBOM and keep the customer's boundary scan.

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
Implement exercises/ch14-llmops-and-sre/ex64-airgap-bundle/starter.py so that test_bundle.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `build_bundle`,
`verify_bundle`, `safe_extract`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch14-llmops-and-sre/ex64-airgap-bundle` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Air-gapped deployment bundle" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Can a symlink or '..' member write outside dest? Is the signature computed over canonical
JSON exactly? Should this use asymmetric signatures instead of HMAC, and why? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
