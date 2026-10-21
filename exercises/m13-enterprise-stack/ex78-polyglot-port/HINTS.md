# ex78 hints · Port a customer's Java/Go/C++ request signer to Python

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Get `rfc3986` exactly right first; every other piece depends on it. `urllib.parse.quote(s, safe="-_.~")` encodes UTF-8
and leaves only the RFC 3986 unreserved characters alone. Notice that `/` must be encoded inside a value, which is why
`safe` doesn't include it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **encode_path:** split on `/`, encode each segment, and join with `/` again.
- **canonical_query:** expand every `(key, value)` pair, encode both sides, then sort the encoded `k=v` strings
  themselves (not the raw keys).
- **canonical_request:** five lines joined by `\n`: upper-cased method, encoded path, canonical query, SHA-256 of the
  body, timestamp. The variant changes only the body-hash case and the timestamp format.
- **sign_headers:** HMAC-SHA256 of the canonical request with the secret, then base64 or hex depending on the variant.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The Java reference uses `URLEncoder`, which does *form* encoding (space becomes `+`), and then patches the result.
  The test vectors come from the patched output, so match RFC 3986, not form encoding.
- Sort **after** encoding: `customer%20name=…` must sort before `q=…`, and two `q` values sort by their encoded
  values.
- The `cpp` timestamp is epoch seconds in UTC; the others are `YYYYMMDDTHHMMSSZ`. The `X-NWS-Date` header uses the
  same string as the canonical request.
- An unknown variant raises `ValueError` in both functions. Validate it in `canonical_request` and the signer inherits
  the check.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_rfc3986` | `quote` default `safe="/"` left on; space encoded as `+` |
| `test_java_vectors` | Pairs sorted before encoding; method not upper-cased; body hash of `str` instead of bytes |
| `test_go_variant` | Signature still base64; header names not lower-cased |
| `test_cpp_variant` | Body hash not upper-cased; timestamp not epoch seconds |
| `test_unknown_variant_and_unicode` | Unknown variant silently treated as `java`; empty query not `""` |
