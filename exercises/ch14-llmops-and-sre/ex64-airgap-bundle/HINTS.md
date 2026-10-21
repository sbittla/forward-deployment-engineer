# ex64 hints · Air-gapped deployment bundle

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `_canonical(obj)` and `_sign(key, manifest)` first. Signing removes the `signature` key, serialises with
`sort_keys=True, separators=(",", ":")`, and HMACs the bytes. Build and verify both use this pair, so any mismatch
between them shows up as "bad signature".
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **build_bundle:** walk `src_dir` with `rglob("*")`, keep the files, and sort them. For each, compute the relative
  POSIX path, SHA-256 and size, and add it to the tar with `arcname=rel`. Sign the manifest last, and add it as an
  in-memory member (`TarInfo` plus `BytesIO`).
- **verify_bundle**, in order:
  1. flag unsafe members;
  2. require the manifest;
  3. check the signature, and stop there if it's bad;
  4. compare the manifest's files with the archive's files: missing, checksum mismatch, unexpected.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Use `PurePosixPath(name)` to detect unsafe members: absolute paths, any `..` part, symlinks and hard links
  (`issym()`, `islnk()`). Report an unsafe member only as unsafe, not also as unexpected.
- Use `hmac.compare_digest` for the signature comparison.
- Never call `tarfile.extractall` on an untrusted archive. In `safe_extract`, verify first, then write each regular
  file yourself under `dest`, creating parent directories as you go.
- Sort the file list so the bundle is reproducible.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_build_and_verify` | Windows `\` separators in member names; signature computed with the `signature` key still present |
| `test_tamper_detected` | Unsafe member also reported as unexpected; no early return after a missing manifest |
| `test_safe_extract` | `extractall` used; manifest extracted; extraction happens before verification |
| `test_downgrade_refused` | Versions compared as strings (`"1.10.0" < "1.9.2"`); the same version refused; `installed_version` not passed on by `safe_extract` |
| `test_boundary_shared_key_can_resign` | Pins a limitation, not a bug: with a shared HMAC key, a re-signed bundle verifies. If it fails, the manifest isn't rebuilt from the current files, or `verify_bundle` checks more than the spec says |
