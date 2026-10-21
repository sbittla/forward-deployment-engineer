import base64
import hashlib
import hmac
import json
from dataclasses import dataclass, field

TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"


class AuthError(Exception):
    pass


@dataclass
class Principal:
    user: str
    email: str = ""
    groups: list[str] = field(default_factory=list)

    @classmethod
    def from_claims(cls, claims: dict) -> "Principal":
        return cls(claims["sub"], claims.get("email", ""), list(claims.get("groups", [])))


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(signing_input: str, secret: str) -> str:
    return _b64e(hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest())


def make_token(claims: dict, secret: str) -> str:
    head = _b64e(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64e(json.dumps(claims).encode())
    return f"{head}.{body}.{_sign(f'{head}.{body}', secret)}"


def verify_id_token(token: str, secret: str, issuer: str, audience: str, now: int) -> dict:
    try:
        head_s, body_s, sig = token.split(".")
        header, claims = json.loads(_b64d(head_s)), json.loads(_b64d(body_s))
    except (ValueError, json.JSONDecodeError):
        raise AuthError("malformed token") from None
    if header.get("alg") != "HS256":
        raise AuthError(f"unsupported alg {header.get('alg')!r}")
    if not hmac.compare_digest(sig, _sign(f"{head_s}.{body_s}", secret)):
        raise AuthError("bad signature")
    if claims.get("iss") != issuer:
        raise AuthError("wrong issuer")
    aud = claims.get("aud")
    if audience not in (aud if isinstance(aud, list) else [aud]):
        raise AuthError("wrong audience")
    if claims.get("exp", 0) <= now:
        raise AuthError("token expired")
    if "nbf" in claims and claims["nbf"] > now:
        raise AuthError("token not yet valid")
    return claims


def allowed(doc_acl: dict, principal: Principal) -> bool:
    groups = set(principal.groups)
    if groups & set(doc_acl.get("deny_groups", [])):
        return False
    if principal.user in doc_acl.get("users", []):
        return True
    acl_groups = set(doc_acl.get("groups", []))
    return "everyone" in acl_groups or bool(groups & acl_groups)


def secure_search(principal: Principal, query: str, docs: list[dict], search_fn, k: int):
    permitted = [d for d in docs if allowed(d.get("acl", {}), principal)]   # filter BEFORE ranking
    results = search_fn(query, permitted, k)
    audit = {"user": principal.user, "query": query, "candidates": len(docs), "permitted": len(permitted),
             "denied": len(docs) - len(permitted)}
    return results, audit


def obo_exchange_request(user_token: str, client_id: str, client_secret: str, scope: str) -> dict:
    return {"grant_type": TOKEN_EXCHANGE, "subject_token": user_token, "subject_token_type": ACCESS_TOKEN,
            "requested_token_type": ACCESS_TOKEN, "scope": scope, "client_id": client_id, "client_secret": client_secret}
