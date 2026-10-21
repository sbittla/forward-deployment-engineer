import hashlib
import hmac
import io
import json
import tarfile
from pathlib import Path, PurePosixPath

MANIFEST = "manifest.json"


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _sign(key: bytes, manifest: dict) -> str:
    body = {k: v for k, v in manifest.items() if k != "signature"}
    return hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()


def build_bundle(src_dir, out_path, version: str, key: bytes) -> dict:
    src = Path(src_dir)
    files = sorted(p for p in src.rglob("*") if p.is_file())
    manifest = {"version": version, "files": {}}
    with tarfile.open(out_path, "w:gz") as tf:
        for p in files:
            rel = p.relative_to(src).as_posix()
            data = p.read_bytes()
            manifest["files"][rel] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
            tf.add(p, arcname=rel)
        manifest["signature"] = _sign(key, manifest)
        blob = json.dumps(manifest, indent=1, sort_keys=True).encode()
        info = tarfile.TarInfo(MANIFEST)
        info.size = len(blob)
        tf.addfile(info, io.BytesIO(blob))
    return manifest


def _unsafe(m: tarfile.TarInfo) -> bool:
    p = PurePosixPath(m.name)
    return p.is_absolute() or ".." in p.parts or m.issym() or m.islnk() or m.name.startswith("\\")


def _version(v: str) -> tuple[int, ...] | None:
    try:
        return tuple(int(p) for p in str(v).split("."))
    except ValueError:
        return None


def verify_bundle(path, key: bytes, installed_version: str | None = None) -> list[str]:
    problems = []
    with tarfile.open(path) as tf:
        members = tf.getmembers()
        names = {m.name: m for m in members if m.isfile()}
        problems += [f"unsafe path: {m.name}" for m in members if _unsafe(m)]
        if MANIFEST not in names:
            return problems + ["no manifest"]
        manifest = json.loads(tf.extractfile(names[MANIFEST]).read())
        if not hmac.compare_digest(manifest.get("signature", ""), _sign(key, manifest)):
            return problems + ["bad signature"]
        if installed_version is not None:
            have, new = _version(installed_version), _version(manifest.get("version", ""))
            if have is None or new is None:
                problems.append(f"unparseable version: {manifest.get('version')}")
            elif new < have:
                problems.append(f"downgrade: {manifest['version']} < {installed_version}")
        expected = manifest["files"]
        for rel in sorted(expected):
            if rel not in names:
                problems.append(f"missing: {rel}")
            elif hashlib.sha256(tf.extractfile(names[rel]).read()).hexdigest() != expected[rel]["sha256"]:
                problems.append(f"checksum mismatch: {rel}")
        unsafe_names = {m.name for m in members if _unsafe(m)}
        problems += [f"unexpected: {n}" for n in sorted(names) if n not in expected and n != MANIFEST
                     and n not in unsafe_names]
    return problems


def safe_extract(path, dest, key: bytes, installed_version: str | None = None) -> None:
    problems = verify_bundle(path, key, installed_version)
    if problems:
        raise ValueError("refusing to extract: " + "; ".join(problems))
    dest = Path(dest)
    with tarfile.open(path) as tf:
        for m in tf.getmembers():
            if m.isfile() and m.name != MANIFEST:
                target = dest / m.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tf.extractfile(m).read())
