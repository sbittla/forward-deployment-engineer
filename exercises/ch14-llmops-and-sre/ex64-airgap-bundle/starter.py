import hashlib
import hmac
import io
import json
import tarfile
from pathlib import Path


def build_bundle(src_dir, out_path, version: str, key: bytes) -> dict:
    raise NotImplementedError


def verify_bundle(path, key: bytes, installed_version: str | None = None) -> list[str]:
    raise NotImplementedError


def safe_extract(path, dest, key: bytes, installed_version: str | None = None) -> None:
    raise NotImplementedError
