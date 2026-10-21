import base64
import json

import pytest

SECRET = "idp-shared-secret"
ISS, AUD, NOW = "https://login.northwind.example", "copilot-api", 1_800_000_000
CLAIMS = {"sub": "u-123", "email": "lee@northwind.example", "groups": ["claims", "staff"], "iss": ISS, "aud": AUD,
          "exp": NOW + 600, "nbf": NOW - 10}


def b64(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def test_token_roundtrip(impl):
    tok = impl.make_token(CLAIMS, SECRET)
    assert tok.count(".") == 2 and "=" not in tok
    assert impl.verify_id_token(tok, SECRET, ISS, AUD, NOW)["sub"] == "u-123"
    assert impl.verify_id_token(impl.make_token({**CLAIMS, "aud": ["x", AUD]}, SECRET), SECRET, ISS, AUD, NOW)


@pytest.mark.parametrize("mutate,msg", [
    (lambda c: {**c, "exp": NOW - 1}, "expired"),
    (lambda c: {**c, "iss": "https://evil.example"}, "issuer"),
    (lambda c: {**c, "aud": "other-app"}, "audience"),
    (lambda c: {**c, "nbf": NOW + 100}, "not yet valid"),
])
def test_token_claim_checks(impl, mutate, msg):
    with pytest.raises(impl.AuthError) as e:
        impl.verify_id_token(impl.make_token(mutate(CLAIMS), SECRET), SECRET, ISS, AUD, NOW)
    assert msg in str(e.value).lower()


def test_signature_and_alg_none(impl):
    tok = impl.make_token(CLAIMS, SECRET)
    with pytest.raises(impl.AuthError):
        impl.verify_id_token(tok, "wrong-secret", ISS, AUD, NOW)
    h, p, s = tok.split(".")
    forged = b64({**CLAIMS, "groups": ["hr-admins"]})
    with pytest.raises(impl.AuthError):
        impl.verify_id_token(f"{h}.{forged}.{s}", SECRET, ISS, AUD, NOW)
    none_tok = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{p}."
    with pytest.raises(impl.AuthError):
        impl.verify_id_token(none_tok, SECRET, ISS, AUD, NOW)


DOCS = [
    {"id": "policy-ho3", "text": "flood excluded", "acl": {"groups": ["everyone"]}},
    {"id": "claims-playbook", "text": "flood claims playbook", "acl": {"groups": ["claims"]}},
    {"id": "hr-case-17", "text": "flood of complaints disciplinary", "acl": {"groups": ["hr"], "users": ["u-999"]}},
    {"id": "exec-memo", "text": "flood reserve memo", "acl": {"users": ["u-123"], "deny_groups": ["contractors"]}},
]


def test_allowed(impl):
    lee = impl.Principal.from_claims(CLAIMS)
    assert lee.groups == ["claims", "staff"]
    assert [d["id"] for d in DOCS if impl.allowed(d["acl"], lee)] == ["policy-ho3", "claims-playbook", "exec-memo"]
    contractor = impl.Principal("u-123", groups=["contractors"])
    assert not impl.allowed(DOCS[3]["acl"], contractor)


def test_secure_search_filters_before_ranking(impl):
    seen = []

    def search_fn(query, docs, k):
        seen.append([d["id"] for d in docs])
        return [d["id"] for d in docs if query in d["text"]][:k]

    lee = impl.Principal.from_claims(CLAIMS)
    results, audit = impl.secure_search(lee, "flood", DOCS, search_fn, k=10)
    assert "hr-case-17" not in results and "hr-case-17" not in seen[0]
    assert audit == {"user": "u-123", "query": "flood", "candidates": 4, "permitted": 3, "denied": 1}


def test_obo(impl):
    body = impl.obo_exchange_request("user-at", "copilot", "s3cr3t", "https://graph.example/.default")
    assert body == {"grant_type": "urn:ietf:params:oauth:grant-type:token-exchange", "subject_token": "user-at",
                    "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                    "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
                    "scope": "https://graph.example/.default", "client_id": "copilot", "client_secret": "s3cr3t"}
