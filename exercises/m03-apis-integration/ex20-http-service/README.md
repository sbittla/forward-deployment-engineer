# ex20 · Minimal HTTP service with auth and health

**Module:** m03 · **Covers:** R05 APIs, R28 Backend architecture, R22 Production · **Time:** 60 min

## Learning objectives
- Build a standard-library HTTP service that meets a platform team's checklist.
- Authenticate, validate input, cap payload size and return JSON errors.
- Propagate request ids and never leak exception text.

## Scenario
The customer's platform team will only deploy services that expose a health endpoint, authenticate every
business endpoint, return JSON errors and propagate a request id. You will build the smallest service that passes
their checklist using only the standard library, so it runs in their locked-down base image.

## Your task
`make_server(answer_fn, tokens, host="127.0.0.1", port=0) -> ThreadingHTTPServer`

| Request | Response |
|---|---|
| `GET /healthz` | `200 {"status": "ok"}` — no auth |
| `POST /v1/answer` with `Authorization: Bearer <t>` (t in `tokens`) and JSON `{"question": str}` | `200 {"answer": answer_fn(question), "request_id": ...}` |
| missing/invalid token on `/v1/answer` | `401 {"error": "unauthorized"}` |
| body not JSON / `question` missing, not a string, empty, or > 2000 chars | `400 {"error": ...}` |
| `Content-Length` > 65536 | `413 {"error": "payload too large"}` (do not parse it; drain at most 1 MiB so the client can read the response, then close) |
| wrong method on a known path | `405` |
| unknown path | `404` |
| `answer_fn` raises | `500 {"error": "internal error", "request_id": ...}` — never leak the exception text |

Every response is JSON and carries an `X-Request-ID` header: echo the client's `X-Request-ID` if sent, otherwise
generate one. Use `uuid4().hex`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Minimal HTTP service with auth and
health". Before I write code, teach me what platform teams require from a deployable service (health checks, auth,
JSON errors, request ids, payload limits) and how to implement them with http.server. Use short Python examples that
are not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me
what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m03-apis-integration/ex20-http-service/starter.py so that test_service.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `make_server`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m03-apis-integration/ex20-http-service` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Minimal HTTP service with auth and health" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Is the token comparison constant-time? Can an oversized body or a slow client
tie up a thread? Does any 500 response contain exception details? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
