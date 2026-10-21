import hashlib
import io
import json
import tarfile

import pytest

KEY = b"customer-shared-secret"


@pytest.fixture
def src(tmp_path):
    d = tmp_path / "src"
    (d / "app").mkdir(parents=True)
    (d / "app" / "main.py").write_text("print('hi')\n")
    (d / "models").mkdir()
    (d / "models" / "classifier.bin").write_bytes(b"\x00\x01" * 100)
    (d / "README.md").write_text("install me")
    return d


def rewrite(path, mutate):
    """Copy a bundle, letting `mutate(name, data)` return new data, None to drop, or add extras via list."""
    with tarfile.open(path) as tf:
        members = [(m.name, tf.extractfile(m).read()) for m in tf.getmembers() if m.isfile()]
    out = path.with_name("tampered.tar.gz")
    with tarfile.open(out, "w:gz") as tf:
        for name, data in mutate(members):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return out


def test_build_and_verify(impl, src, tmp_path):
    out = tmp_path / "bundle.tar.gz"
    m = impl.build_bundle(src, out, "1.4.0", KEY)
    assert sorted(m["files"]) == ["README.md", "app/main.py", "models/classifier.bin"]
    assert m["files"]["README.md"] == {"sha256": hashlib.sha256(b"install me").hexdigest(), "size": 10}
    assert m["version"] == "1.4.0" and len(m["signature"]) == 64
    assert impl.verify_bundle(out, KEY) == []
    assert impl.verify_bundle(out, b"wrong-key") == ["bad signature"]


def test_tamper_detected(impl, src, tmp_path):
    out = tmp_path / "bundle.tar.gz"
    impl.build_bundle(src, out, "1", KEY)
    bad = rewrite(out, lambda ms: [(n, b"print('pwned')\n" if n == "app/main.py" else d) for n, d in ms])
    assert impl.verify_bundle(bad, KEY) == ["checksum mismatch: app/main.py"]
    bad = rewrite(out, lambda ms: [(n, d) for n, d in ms if n != "README.md"] + [("extra.sh", b"rm -rf /")])
    assert sorted(impl.verify_bundle(bad, KEY)) == ["missing: README.md", "unexpected: extra.sh"]
    bad = rewrite(out, lambda ms: ms + [("../../etc/cron.d/x", b"evil")])
    assert "unsafe path: ../../etc/cron.d/x" in impl.verify_bundle(bad, KEY)
    bad = rewrite(out, lambda ms: [(n, d) for n, d in ms if n != "manifest.json"])
    assert impl.verify_bundle(bad, KEY) == ["no manifest"]


def test_safe_extract(impl, src, tmp_path):
    out = tmp_path / "bundle.tar.gz"
    impl.build_bundle(src, out, "1", KEY)
    dest = tmp_path / "install"
    impl.safe_extract(out, dest, KEY)
    assert (dest / "app" / "main.py").read_text() == "print('hi')\n"
    assert not (dest / "manifest.json").exists()
    bad = rewrite(out, lambda ms: ms + [("../escape.txt", b"x")])
    with pytest.raises(ValueError):
        impl.safe_extract(bad, tmp_path / "install2", KEY)
    assert not (tmp_path / "escape.txt").exists()


def test_boundary_shared_key_can_resign(impl, src, tmp_path):
    # HMAC is symmetric: anyone holding the key can sign altered content, and it verifies.
    original = impl.build_bundle(src, tmp_path / "bundle.tar.gz", "1", KEY)
    (src / "app" / "main.py").write_text("print('altered')\n")
    out = tmp_path / "resigned.tar.gz"
    resigned = impl.build_bundle(src, out, "1", KEY)
    assert resigned["files"]["app/main.py"] != original["files"]["app/main.py"]
    assert impl.verify_bundle(out, KEY) == []
