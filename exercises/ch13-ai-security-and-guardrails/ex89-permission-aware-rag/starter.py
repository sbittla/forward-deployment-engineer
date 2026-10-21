import base64
import hashlib
import hmac
import json
from dataclasses import dataclass, field


class AuthError(Exception):
    pass


@dataclass
class Principal:
    user: str
    email: str = ""
    groups: list[str] = field(default_factory=list)

    @classmethod
    def from_claims(cls, claims: dict) -> "Principal":
        raise NotImplementedError


def make_token(claims: dict, secret: str, kid: str | None = None, typ: str = "JWT") -> str:
    raise NotImplementedError


def verify_id_token(token: str, secret: str | dict[str, str], issuer: str, audience: str, now: int,
                    expected_nonce: str | None = None) -> dict:
    raise NotImplementedError


def verify_access_token(token: str, secret: str | dict[str, str], issuer: str, audience: str, now: int,
                        required_scope: str | None = None) -> dict:
    raise NotImplementedError


def allowed(doc_acl: dict, principal: Principal) -> bool:
    raise NotImplementedError


def secure_search(principal: Principal, query: str, docs: list[dict], search_fn, k: int):
    raise NotImplementedError


def obo_exchange_request(user_token: str, client_id: str, client_secret: str, scope: str) -> dict:
    raise NotImplementedError
