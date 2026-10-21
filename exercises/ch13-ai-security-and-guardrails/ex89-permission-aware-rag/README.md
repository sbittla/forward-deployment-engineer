# ex89 · Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of

**Chapter:** 13 · AI Security and Guardrails (`exercises/ch13-ai-security-and-guardrails/`) · **Covers:** R39 Identity & permission-aware access, R10 Retrieval, R17 Security

## Learning objectives
- Validate OIDC ID tokens correctly, rejecting alg=none and bad claims.
- Tell ID tokens (who signed in, checked by the client) from access tokens (what an API call may do, checked by
  the API).
- Filter retrieval candidates by ACL before ranking.
- Build an on-behalf-of token exchange request for downstream APIs.

## Scenario
The copilot indexes the whole SharePoint/Confluence estate. A claims adjuster asks a question, and the top hit is
an HR document about a colleague's disciplinary case. Nothing was "hacked". Retrieval simply ignored permissions.
Anthropic's Staff FDE posting expects "a secure, production-ready design inside a complex enterprise environment of
legacy systems, with identity and access". Enterprise RAG must enforce the **user's** permissions, using the
customer's identity provider (Entra ID, Okta).

## Your task
This is a **teaching implementation**, not complete production OIDC: HS256 with a shared secret keeps the tests
self-contained. Production uses the identity provider's supported validation and a maintained library configured with
the right issuer, audience, algorithm and token type.

Three tokens, three validators. **Authentication:** the user signs in at the identity provider and the copilot (the
OIDC client) receives an **ID token** with `aud` = its client id; the copilot validates it and starts a session.
**API authorization:** the client obtains an **access token** whose audience is the API (the resource server); the
API validates it on every request. **Downstream calls:** the API exchanges the incoming access token for one with the
downstream API's audience (RFC 8693) instead of passing it through. An ID token is never accepted as an API bearer
token.

1. `verify_id_token(token, secret, issuer, audience, now, expected_nonce=None)` for an HS256 JWT, where `audience` is
   the client id. Check, in this order, and raise
   `AuthError` at the first failure, with a message containing the keyword in brackets:
   - **structure**: three base64url segments (no padding), whose header and payload decode to JSON objects
     (`malformed`);
   - **algorithm**: `alg` must be exactly `"HS256"`, an allowlist of one. `none` in any capitalization, `RS256`,
     `ES256`, `HS512`, an empty or a missing `alg` are all rejected (`alg`). The token never chooses how it's verified;
   - **key**: `secret` is either one key (a string) or a key set during rotation, a dict of `kid -> key`. With a dict,
     the header's `kid` selects the key; a missing or unknown `kid` is rejected (`kid`);
   - **signature**: the HMAC-SHA256 of the received `header.payload`, compared with `hmac.compare_digest`
     (`signature`);
   - **issuer** `iss` equals `issuer` (`issuer`);
   - **audience** `aud` (a string or a list) includes `audience` (`audience`);
   - **expiry**: `exp` must be a number greater than `now`; a missing `exp` fails closed (`expired`, plus `exp`
     when it's missing: for example `token expired or missing exp`);
   - **not-before**: when `nbf` is present it must be `<= now` (`not yet valid`);
   - **token type**: a header `typ` of `at+jwt` (or `application/at+jwt`, any case) is an access token and is rejected
     (`type`);
   - **authorized party**: when `azp` is present, or `aud` is a list of more than one value, `azp` must equal
     `audience` (`azp`);
   - **nonce**: when `expected_nonce` is given (the client sent a nonce in the authorization request), the `nonce`
     claim must equal it; a missing or different nonce is rejected (`nonce`).

   Return the claims dict.
2. `make_token(claims, secret, kid=None, typ="JWT")` builds such a token (handy for tests and local dev), adding a
   `kid` header when one is given; `typ="at+jwt"` makes a JWT access token.
3. `verify_access_token(token, secret, issuer, audience, now, required_scope=None)`: what the **API** runs, where
   `audience` is the API's own identifier. The same checks as `verify_id_token` from structure to not-before, then
   **token type**: the header `typ` must be `at+jwt` (RFC 9068; `application/at+jwt` and any case accepted), so an
   ID token is rejected (`type`); and **scope**: when `required_scope` is given it must be one of the
   space-separated values in the `scope` claim (`scope`). Return the claims dict. (Opaque access tokens are checked by
   token introspection instead; that's out of scope here.)
4. `Principal.from_claims(claims)`: `user = claims["sub"]`, `email`, `groups` (list, default empty).
5. `allowed(doc_acl, principal)`: ACL is `{"users": [...], "groups": [...], "deny_groups": [...]}`. Deny wins;
   otherwise allow if the user is listed, or shares a group, or the ACL has group `"everyone"`. A missing, `None` or
   empty ACL denies: retrieval authorization **fails closed** (Chapter 10, Section 10.6, makes the same rule for
   tenant metadata).
6. `secure_search(principal, query, docs, search_fn, k)`: filter to permitted docs (by each doc's `acl`, which may
   be absent) **before** ranking (never rank
   and then drop: that leaks result counts and snippets), call `search_fn(query, permitted_docs, k)`, and return
   `(results, audit)` where audit is `{"user", "query", "candidates", "permitted", "denied"}`.
7. `obo_exchange_request(user_token, client_id, client_secret, scope)`: the form body for an OAuth 2.0 token
   exchange (RFC 8693) so downstream APIs see the user's identity rather than a god-mode service account:
   `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, `subject_token`,
   `subject_token_type=urn:ietf:params:oauth:token-type:access_token`, `requested_token_type=...:access_token`,
   `scope`, `client_id`, `client_secret`.

### Algorithms and key management

The exercise signs with **HS256**, a shared secret, so the tests need no key server. Production identity providers
(Entra ID, Okta, Ping) sign with an asymmetric algorithm, **RS256** or **ES256**: they keep the private key and
publish the public keys at a **JWKS** endpoint (found through the provider's OpenID configuration document). Your
service then:

- pins the allowlist to the provider's algorithm (`["RS256"]`), never to whatever the header says. Letting the
  header choose enables **algorithm confusion**: a token that says `HS256` is checked with the RSA *public* key as
  the HMAC secret, and anyone can forge it. `test_alg_confusion_rejected` is the negative test;
- selects the key by the header's `kid`, caches the key set, and refetches it at most once (rate-limited) on an
  unknown `kid`. During **rotation** the provider publishes the new key before signing with it and keeps the old one
  until tokens signed with it expire, so the cached set holds both. `test_kid_selects_key_during_rotation` models this
  with a dict of keys;
- validates the same boundary as here: issuer, audience, token type, `nonce` and `azp` for ID tokens, scope for
  access tokens, expiry and not-before (allow a small clock skew, at most a
  minute or two, in production), and rejects `alg: none`;
- keeps any shared secret it does have (client secrets for token exchange) in the secret manager, never in code.

Use a maintained JWT library and configure these explicitly; don't hand-roll verification in production.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch13-ai-security-and-guardrails/ex89-permission-aware-rag`.
- **Expected output:** all 24 tests fail against the starter; when you're done, all 24 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch13-ai-security-and-guardrails/ex89-permission-aware-rag`: all 24 pass.
- **Tests:** `test_permissions.py` (24 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** HS256 with a shared secret keeps the tests self-contained. Production uses a maintained JWT
  library with an explicit RS256 or ES256 allowlist and JWKS keys selected by `kid` and cached, synchronizes ACLs
  from the source systems quickly enough that revoked access takes effect, and uses the identity provider's own
  token-exchange grant.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Permission-aware RAG: OIDC token
validation, ACL filtering, on-behalf-of". Before I write code, teach me OIDC/JWT validation (alg, signature, iss,
aud, exp, nbf), document ACLs with deny rules, permission-aware RAG, and OAuth 2.0 token exchange (RFC 8693). Use
short Python examples that are not the exercise solution. Then ask me three questions to check my understanding, one
at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch13-ai-security-and-guardrails/ex89-permission-aware-rag/starter.py so that test_permissions.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`AuthError`, `Principal`, `make_token`, `verify_id_token`, `verify_access_token`, `allowed`, `secure_search`,
`obo_exchange_request`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch13-ai-security-and-guardrails/ex89-permission-aware-rag` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Is the signature verified before claims are
trusted? Could ranking before filtering leak counts or snippets? Does the audit record avoid logging document
contents? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
