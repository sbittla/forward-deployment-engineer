import base64
import hashlib
import hmac
import json
from dataclasses import dataclass, field

TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
ACCESS_TOKEN_TYP = "at+jwt"            # RFC 9068 header typ for JWT access tokens


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


def make_token(claims: dict, secret: str, kid: str | None = None, typ: str = "JWT") -> str:
    header = {"alg": "HS256", "typ": typ} | ({"kid": kid} if kid is not None else {})
    head = _b64e(json.dumps(header).encode())
    body = _b64e(json.dumps(claims).encode())
    return f"{head}.{body}.{_sign(f'{head}.{body}', secret)}"


def _verify_jwt(token: str, secret: str | dict[str, str], issuer: str, audience: str, now: int) -> tuple[dict, dict]:
    """The checks every JWT gets: structure, alg allowlist, key by kid, signature, iss, aud, exp, nbf."""
    try:
        head_s, body_s, sig = token.split(".")
        header, claims = json.loads(_b64d(head_s)), json.loads(_b64d(body_s))
    except (ValueError, json.JSONDecodeError):
        raise AuthError("malformed token") from None
    if not (isinstance(header, dict) and isinstance(claims, dict)):
        raise AuthError("malformed token")
    if header.get("alg") != "HS256":
        raise AuthError(f"unsupported alg {header.get('alg')!r}")
    if isinstance(secret, dict):                      # a key set during rotation: the kid picks the key
        if header.get("kid") not in secret:
            raise AuthError(f"unknown kid {header.get('kid')!r}")
        secret = secret[header["kid"]]
    if not hmac.compare_digest(sig.encode(), _sign(f"{head_s}.{body_s}", secret).encode()):
        raise AuthError("bad signature")
    if claims.get("iss") != issuer:
        raise AuthError("wrong issuer")
    aud = claims.get("aud")
    if audience not in (aud if isinstance(aud, list) else [aud]):
        raise AuthError("wrong audience")
    exp = claims.get("exp")
    if not isinstance(exp, (int, float)) or exp <= now:     # a missing exp fails closed
        raise AuthError("token expired or missing exp")
    nbf = claims.get("nbf")
    if nbf is not None and (not isinstance(nbf, (int, float)) or nbf > now):
        raise AuthError("token not yet valid")
    return header, claims


def _typ(header: dict) -> str:
    return str(header.get("typ", "")).lower().removeprefix("application/")


def verify_id_token(token: str, secret: str | dict[str, str], issuer: str, audience: str, now: int,
                    expected_nonce: str | None = None) -> dict:
    """OIDC ID-token validation by the client (audience = its client_id). A teaching implementation, not full OIDC."""
    header, claims = _verify_jwt(token, secret, issuer, audience, now)
    if _typ(header) == ACCESS_TOKEN_TYP:              # an access token never establishes a session
        raise AuthError("wrong token type: access token presented as an ID token")
    aud = claims["aud"]
    if ("azp" in claims or (isinstance(aud, list) and len(aud) > 1)) and claims.get("azp") != audience:
        raise AuthError("wrong or missing azp")
    if expected_nonce is not None and claims.get("nonce") != expected_nonce:
        raise AuthError("nonce missing or mismatched")
    return claims


def verify_access_token(token: str, secret: str | dict[str, str], issuer: str, audience: str, now: int,
                        required_scope: str | None = None) -> dict:
    """Access-token validation by the API (audience = the API), for a JWT access token per RFC 9068."""
    header, claims = _verify_jwt(token, secret, issuer, audience, now)
    if _typ(header) != ACCESS_TOKEN_TYP:              # an ID token is never an API bearer token
        raise AuthError(f"wrong token type {header.get('typ')!r}: an access token needs typ at+jwt")
    if required_scope is not None and required_scope not in str(claims.get("scope", "")).split():
        raise AuthError(f"insufficient scope: {required_scope} required")
    return claims


def allowed(doc_acl: dict, principal: Principal) -> bool:
    if not isinstance(doc_acl, dict):                 # a missing ACL denies: fail closed
        return False
    groups = set(principal.groups)
    if groups & set(doc_acl.get("deny_groups", [])):
        return False
    if principal.user in doc_acl.get("users", []):
        return True
    acl_groups = set(doc_acl.get("groups", []))
    return "everyone" in acl_groups or bool(groups & acl_groups)


def secure_search(principal: Principal, query: str, docs: list[dict], search_fn, k: int):
    permitted = [d for d in docs if allowed(d.get("acl"), principal)]   # filter BEFORE ranking
    results = search_fn(query, permitted, k)
    audit = {"user": principal.user, "query": query, "candidates": len(docs), "permitted": len(permitted),
             "denied": len(docs) - len(permitted)}
    return results, audit


def obo_exchange_request(user_token: str, client_id: str, client_secret: str, scope: str) -> dict:
    return {"grant_type": TOKEN_EXCHANGE, "subject_token": user_token, "subject_token_type": ACCESS_TOKEN,
            "requested_token_type": ACCESS_TOKEN, "scope": scope, "client_id": client_id, "client_secret": client_secret}
