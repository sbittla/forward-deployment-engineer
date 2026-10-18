import base64
import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import quote


def rfc3986(s: str) -> str:
    # Java does URLEncoder (form encoding) then patches "+"->"%20", "*"->"%2A", "%7E"->"~".
    # quote() with only the unreserved set marked safe is exactly RFC 3986.
    return quote(s, safe="-_.~")


def encode_path(path: str) -> str:
    return "/".join(rfc3986(seg) for seg in path.split("/"))


def canonical_query(query: dict[str, list[str]]) -> str:
    pairs = [f"{rfc3986(k)}={rfc3986(v)}" for k, values in query.items() for v in values]
    return "&".join(sorted(pairs))   # Java sorts the encoded strings (UTF-16 order == ASCII order here)


def _timestamp(ts: datetime, variant: str) -> str:
    ts = ts.astimezone(timezone.utc)
    return str(int(ts.timestamp())) if variant == "cpp" else ts.strftime("%Y%m%dT%H%M%SZ")


def canonical_request(method: str, path: str, query: dict, body: bytes, ts: datetime, variant: str = "java") -> str:
    if variant not in ("java", "go", "cpp"):
        raise ValueError(f"unknown variant {variant!r}")
    body_hash = hashlib.sha256(body).hexdigest()
    if variant == "cpp":
        body_hash = body_hash.upper()
    return "\n".join([method.upper(), encode_path(path), canonical_query(query), body_hash, _timestamp(ts, variant)])


def sign_headers(method, path, query, body, ts, key_id, secret, variant="java") -> dict:
    canonical = canonical_request(method, path, query, body, ts, variant)
    digest = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).digest()
    sig = digest.hex() if variant == "go" else base64.b64encode(digest).decode()
    headers = {"Authorization": f"NWS1-HMAC-SHA256 Credential={key_id}, Signature={sig}",
               "X-NWS-Date": _timestamp(ts, variant)}
    return {k.lower(): v for k, v in headers.items()} if variant == "go" else headers
