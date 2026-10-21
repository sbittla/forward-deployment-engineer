# ex89 · Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of

**Module:** m14 · **Covers:** R39 Identity & permission-aware access, R10 Retrieval, R17 Security · **Time:** 75 min

## Learning objectives
- Validate OIDC ID tokens correctly, rejecting alg=none and bad claims.
- Filter retrieval candidates by ACL before ranking.
- Build an on-behalf-of token exchange request for downstream APIs.

## Scenario
The copilot indexes the whole SharePoint/Confluence estate. A claims adjuster asks a question, and the top hit is
an HR document about a colleague's disciplinary case. Nothing was "hacked". Retrieval simply ignored permissions.
Anthropic's Staff FDE posting expects "a secure, production-ready design inside a complex enterprise environment of
legacy systems, with identity and access". Enterprise RAG must enforce the **user's** permissions, using the
customer's identity provider (Entra ID, Okta).

## Your task
1. `verify_id_token(token, secret, issuer, audience, now)` for an HS256 JWT (production IdPs use RS256 with their
   JWKS keys; the checks are identical): split `header.payload.signature` (base64url, no padding), require
   `alg == "HS256"` (reject `none` and anything else), verify the HMAC-SHA256 signature with
   `hmac.compare_digest`, then check `iss`, `aud` (string or list), `exp > now` and `nbf <= now` when present.
   Raise `AuthError` with a specific message; return the claims dict.
2. `make_token(claims, secret)` builds such a token (handy for tests and local dev).
3. `Principal.from_claims(claims)`: `user = claims["sub"]`, `email`, `groups` (list, default empty).
4. `allowed(doc_acl, principal)`: ACL is `{"users": [...], "groups": [...], "deny_groups": [...]}`. Deny wins;
   otherwise allow if the user is listed, or shares a group, or the ACL has group `"everyone"`.
5. `secure_search(principal, query, docs, search_fn, k)`: filter to permitted docs **before** ranking (never rank
   and then drop: that leaks result counts and snippets), call `search_fn(query, permitted_docs, k)`, and return
   `(results, audit)` where audit is `{"user", "query", "candidates", "permitted", "denied"}`.
6. `obo_exchange_request(user_token, client_id, client_secret, scope)`: the form body for an OAuth 2.0 token
   exchange (RFC 8693) so downstream APIs see the user's identity rather than a god-mode service account:
   `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, `subject_token`,
   `subject_token_type=urn:ietf:params:oauth:token-type:access_token`, `requested_token_type=...:access_token`,
   `scope`, `client_id`, `client_secret`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

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
Implement exercises/m14-field-leadership/ex89-permission-aware-rag/starter.py so that test_permissions.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`AuthError`, `Principal`, `make_token`, `verify_id_token`, `allowed`, `secure_search`, `obo_exchange_request`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m14-field-leadership/ex89-permission-aware-rag` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Is the signature verified before claims are
trusted? Could ranking before filtering leak counts or snippets? Does the audit record avoid logging document
contents? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
