# ex89 · Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of

**Module:** m14 · **Covers:** R39 Identity & permission-aware access, R10 Retrieval, R17 Security · **Time:** 75 min

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
