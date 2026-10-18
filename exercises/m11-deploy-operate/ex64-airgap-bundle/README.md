# ex64 · Air-gapped deployment bundle

**Module:** m11 · **Covers:** R26 On-site embedding, R22 Production deployment, R17 Security · **Time:** 60 min

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
