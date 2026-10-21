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
    # Several audiences: OIDC then requires azp, the authorized party, to be this client.
    assert impl.verify_id_token(impl.make_token({**CLAIMS, "aud": ["x", AUD], "azp": AUD}, SECRET), SECRET, ISS, AUD, NOW)


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


def _signed(header, claims, secret=SECRET):
    import hashlib
    import hmac
    head, body = b64(header), b64(claims)
    sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest())
    return f"{head}.{body}.{sig.rstrip(b'=').decode()}"


@pytest.mark.parametrize("alg", ["none", "None", "NONE", "RS256", "ES256", "HS512", "", None])
def test_alg_confusion_rejected(impl, alg):
    # Correctly HMAC-signed with the right secret, but the header names another algorithm: the allowlist decides,
    # never the token. (Algorithm confusion: an RS256 verifier tricked into HMAC with its public key.)
    header = {"typ": "JWT"} if alg is None else {"alg": alg, "typ": "JWT"}
    with pytest.raises(impl.AuthError) as e:
        impl.verify_id_token(_signed(header, CLAIMS), SECRET, ISS, AUD, NOW)
    assert "alg" in str(e.value).lower()


def test_expired_wrong_audience_issuer_and_malformed_rejected(impl):
    no_exp = {k: v for k, v in CLAIMS.items() if k != "exp"}
    for claims, word in [(no_exp, "exp"), ({**CLAIMS, "exp": NOW}, "expired"),
                         ({**CLAIMS, "aud": ["other-app"]}, "audience"), ({**CLAIMS, "aud": []}, "audience"),
                         ({**CLAIMS, "iss": ISS + "/"}, "issuer")]:
        with pytest.raises(impl.AuthError) as e:
            impl.verify_id_token(impl.make_token(claims, SECRET), SECRET, ISS, AUD, NOW)
        assert word in str(e.value).lower()
    for bad in ["", "abc", "a.b", "a.b.c.d", "!!.@@.##", f"{b64([1])}.{b64(CLAIMS)}.x"]:
        with pytest.raises(impl.AuthError) as e:
            impl.verify_id_token(bad, SECRET, ISS, AUD, NOW)
        assert "malformed" in str(e.value).lower()


def test_tampered_signature_rejected(impl):
    h, p, s = impl.make_token(CLAIMS, SECRET).split(".")
    flipped = ("A" if s[0] != "A" else "B") + s[1:]
    for tok in [f"{h}.{p}.{flipped}", f"{h}.{p}.", f"{h}.{p}.{s}x"]:
        with pytest.raises(impl.AuthError) as e:
            impl.verify_id_token(tok, SECRET, ISS, AUD, NOW)
        assert "signature" in str(e.value).lower()


def test_kid_selects_key_during_rotation(impl):
    keys = {"2026-09": "old-key", "2026-10": "new-key"}   # both published while tokens signed with the old key expire
    for kid, key in keys.items():
        assert impl.verify_id_token(impl.make_token(CLAIMS, key, kid=kid), keys, ISS, AUD, NOW)["sub"] == "u-123"
    with pytest.raises(impl.AuthError, match="kid"):
        impl.verify_id_token(impl.make_token(CLAIMS, "old-key", kid="2026-08"), keys, ISS, AUD, NOW)
    with pytest.raises(impl.AuthError, match="kid"):
        impl.verify_id_token(impl.make_token(CLAIMS, "old-key"), keys, ISS, AUD, NOW)    # no kid header
    with pytest.raises(impl.AuthError, match="signature"):
        impl.verify_id_token(impl.make_token(CLAIMS, "old-key", kid="2026-10"), keys, ISS, AUD, NOW)


def test_missing_acl_fails_closed(impl):
    lee = impl.Principal.from_claims(CLAIMS)
    assert not impl.allowed({}, lee) and not impl.allowed(None, lee)
    docs = DOCS + [{"id": "no-acl", "text": "flood notes"}, {"id": "null-acl", "text": "flood", "acl": None}]
    results, audit = impl.secure_search(lee, "flood", docs, lambda q, ds, k: [d["id"] for d in ds][:k], k=10)
    assert "no-acl" not in results and "null-acl" not in results
    assert audit["denied"] == 3


def test_nonce_checked_when_expected(impl):
    # The client sent nonce n-1 in the authorization request; the ID token must echo it (replay protection).
    ok = impl.make_token({**CLAIMS, "nonce": "n-1"}, SECRET)
    assert impl.verify_id_token(ok, SECRET, ISS, AUD, NOW, expected_nonce="n-1")["nonce"] == "n-1"
    assert impl.verify_id_token(ok, SECRET, ISS, AUD, NOW)          # no nonce sent, none required
    for claims in [{**CLAIMS, "nonce": "n-2"}, CLAIMS]:              # mismatched, then missing
        with pytest.raises(impl.AuthError, match="nonce"):
            impl.verify_id_token(impl.make_token(claims, SECRET), SECRET, ISS, AUD, NOW, expected_nonce="n-1")


def test_azp_checked(impl):
    for claims in [{**CLAIMS, "aud": [AUD, "other-app"]},                    # several audiences, no azp
                   {**CLAIMS, "aud": [AUD, "other-app"], "azp": "other-app"},
                   {**CLAIMS, "azp": "other-app"}]:                          # azp present must be this client
        with pytest.raises(impl.AuthError, match="azp"):
            impl.verify_id_token(impl.make_token(claims, SECRET), SECRET, ISS, AUD, NOW)
    assert impl.verify_id_token(impl.make_token({**CLAIMS, "azp": AUD}, SECRET), SECRET, ISS, AUD, NOW)


API = "https://claims-api.northwind.example"


def test_id_token_rejected_where_access_token_required(impl):
    # The API validates access tokens issued for its own audience; an ID token is never an API bearer token.
    at_claims = {**CLAIMS, "aud": API, "scope": "claims.read profile", "client_id": AUD}
    at = impl.make_token(at_claims, SECRET, typ="at+jwt")
    assert impl.verify_access_token(at, SECRET, ISS, API, NOW, required_scope="claims.read")["sub"] == "u-123"
    with pytest.raises(impl.AuthError, match="scope"):
        impl.verify_access_token(at, SECRET, ISS, API, NOW, required_scope="claims.write")
    id_token_for_api = impl.make_token({**CLAIMS, "aud": API}, SECRET)     # typ JWT, even with the API's audience
    with pytest.raises(impl.AuthError, match="type"):
        impl.verify_access_token(id_token_for_api, SECRET, ISS, API, NOW)
    with pytest.raises(impl.AuthError, match="audience"):               # the client's ID token: wrong audience too
        impl.verify_access_token(impl.make_token(CLAIMS, SECRET, typ="at+jwt"), SECRET, ISS, API, NOW)
    with pytest.raises(impl.AuthError, match="type"):                   # and an access token doesn't sign anyone in
        impl.verify_id_token(impl.make_token(CLAIMS, SECRET, typ="at+jwt"), SECRET, ISS, AUD, NOW)
