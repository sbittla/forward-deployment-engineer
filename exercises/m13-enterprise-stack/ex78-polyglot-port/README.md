# ex78 · Port a customer's Java/Go/C++ request signer to Python

**Module:** m13 · **Covers:** R29 Debugging in customer code, R05 Integration, R17 Security ·
**Hands-on:** Java, Go, C++ · **Time:** 60 min

## Scenario
The customer's internal APIs require signed requests. They have signers in three languages: the Java SDK (the
reference), a Go dispatch service and a C++ edge agent on warehouse scanners. You need a Python signer that
interoperates with **all three** backends. No docs exist; the code is the spec. Read `reference/` carefully: the
classic bug in ports like this is URL encoding (Java's `URLEncoder` is *form* encoding).

The Java file compiles and prints test vectors (`javac CustomerSigner.java && java CustomerSigner`). The vectors in
the tests came from exactly that run.

## Your task
- `rfc3986(s)` → percent-encode UTF-8 per RFC 3986 (unreserved `A-Z a-z 0-9 - _ . ~` stay literal; space → `%20`).
- `encode_path(path)` → encode each `/`-separated segment, keep the slashes.
- `canonical_query(query: dict[str, list[str]])` → encode every key and value, join `k=v`, **sort the encoded
  pairs**, join with `&`.
- `canonical_request(method, path, query, body: bytes, ts: datetime, variant="java")` — Java layout:
  `METHOD\nPATH\nQUERY\nsha256hex(body)\nYYYYMMDDTHHMMSSZ`. The `cpp` variant uses an upper-case body hash and
  epoch seconds; `go` is identical to `java`.
- `sign_headers(method, path, query, body, ts, key_id, secret, variant="java") -> dict` — signature is
  base64(HMAC-SHA256) for `java` and `cpp`, lowercase hex for `go`. Headers: `Authorization:
  NWS1-HMAC-SHA256 Credential=<key_id>, Signature=<sig>` and `X-NWS-Date: <timestamp string used in the canonical
  request>`. For `go`, header names are lower case.
