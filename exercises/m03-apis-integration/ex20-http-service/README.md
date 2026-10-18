# ex20 · Minimal HTTP service with auth and health

**Module:** m03 · **Covers:** R05 APIs, R28 Backend architecture, R22 Production · **Time:** 60 min

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
