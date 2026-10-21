# ex89 hints · Permission-aware RAG: OIDC token validation, ACL filtering, on-behalf-of

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the two base64url helpers first. Encoding uses `urlsafe_b64encode` and strips the `=` padding; decoding adds
the padding back (`"=" * (-len(s) % 4)`) before decoding. Then `make_token` is header, payload and the HMAC of
`header.payload`, all base64url-encoded and joined with dots. Get the round-trip test passing before the attack
tests.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Verify in a fixed order and raise `AuthError` at the first failure:

1. split into three parts and decode them (malformed tokens fail here);
2. require `alg == "HS256"`;
3. compare signatures with `hmac.compare_digest`;
4. issuer;
5. audience (a string or a list);
6. `exp > now`;
7. `nbf <= now` if it's present.

For ACLs, check the deny groups first and return False straight away. Then allow a listed user, a shared group, or the
group `everyone`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Check the algorithm **before** the signature. `alg: none` with an empty signature is the classic JWT bypass. Never
  let the token choose how it's verified.
- A forged payload with the original signature must fail. Recompute the HMAC over the *received* header and payload.
- Error messages are tested by keyword: include "expired", "issuer", "audience" and "not yet valid".
- Filter documents **before** calling `search_fn`. Ranking first and dropping afterward leaks counts and snippets of
  documents the user can't see.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_token_roundtrip` | Padding left in the token; list audiences not supported |
| `test_token_claim_checks` | Error message lacks the keyword; `exp == now` treated as valid |
| `test_signature_and_alg_none` | `alg: none` accepted; signature compared with `==` or not recomputed over the received parts |
| `test_allowed` | Deny groups checked after the allow rules; `everyone` not handled |
| `test_secure_search_filters_before_ranking` | All documents passed to `search_fn` and filtered afterward; audit counts wrong |
| `test_obo` | Grant type or token type URNs misspelled |
| `test_alg_confusion_rejected` | `alg` compared case-insensitively, or any `HS*`/`RS*` value accepted; the header's `alg` used to pick the verifier |
| `test_expired_wrong_audience_issuer_and_malformed_rejected` | Missing `exp` treated as "never expires"; a header or payload that isn't a JSON object not reported as `malformed` |
| `test_tampered_signature_rejected` | Signature not recomputed over the received parts; an empty signature accepted |
| `test_kid_selects_key_during_rotation` | A dict of keys not supported; an unknown or missing `kid` falls back to some key instead of failing |
| `test_missing_acl_fails_closed` | A chunk without an ACL treated as public; `None` ACL crashes instead of denying |
| `test_nonce_checked_when_expected` | Nonce compared only when the claim is present, so a missing nonce passes; or a nonce required when none was sent |
| `test_azp_checked` | `azp` ignored; a list audience with several values accepted without `azp` |
| `test_id_token_rejected_where_access_token_required` | Header `typ` not checked, so an ID token works as a bearer token; scope compared as a substring instead of a space-separated list |
