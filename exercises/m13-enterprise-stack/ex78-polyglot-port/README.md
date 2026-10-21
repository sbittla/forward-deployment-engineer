# ex78 · Port a customer's Java/Go/C++ request signer to Python

**Module:** m13 · **Covers:** R29 Debugging in customer code, R05 Integration, R17 Security ·
**Hands-on:** Java, Go, C++ · **Time:** 60 min

## Learning objectives
- Port a request signer from customer code with no documentation.
- Match byte-for-byte canonicalisation across Java, Go and C++ variants.
- Avoid the classic URL-encoding bug (form vs RFC 3986).

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

**Errors:** an unknown `variant` raises `ValueError` (silently signing with the wrong layout produces 401s that are very hard to debug).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Port a customer's Java/Go/C++
request signer to Python". Before I write code, teach me request signing (canonical requests, HMAC), RFC 3986
percent-encoding versus form encoding, and reading unfamiliar code as the spec. Use short Python examples that are
not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to
re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m13-enterprise-stack/ex78-polyglot-port/starter.py so that test_polyglot.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `rfc3986`,
`encode_path`, `canonical_query`, `canonical_request`, `sign_headers`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/m13-enterprise-stack/ex78-polyglot-port` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Port a customer's Java/Go/C++ request signer to Python" as a senior forward deployed engineer
would before it ships to a customer. Specifically: Is '~' left unencoded and space encoded as %20? Are pairs sorted
after encoding? Which test vector would catch a Java URLEncoder-style bug? Rank findings by customer impact, quote
the line for each, and say which ones a test should catch.
```
