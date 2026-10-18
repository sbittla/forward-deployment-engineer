import hmac
import json
import logging
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 65536
MAX_QUESTION = 2000
ROUTES = {"/healthz": {"GET"}, "/v1/answer": {"POST"}}
log = logging.getLogger("answer-service")


def make_server(answer_fn, tokens, host="127.0.0.1", port=0) -> ThreadingHTTPServer:
    tokens = set(tokens)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # route access logs through logging, not stderr
            log.info(fmt, *args)

        def _send(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Request-ID", self.rid)
            self.end_headers()
            self.wfile.write(data)

        def _authorized(self):
            auth = self.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return False
            given = auth[7:]
            return any(hmac.compare_digest(given, t) for t in tokens)

        def _dispatch(self, method):
            self.rid = self.headers.get("X-Request-ID") or uuid.uuid4().hex
            path = self.path.split("?", 1)[0]
            if path not in ROUTES:
                return self._send(404, {"error": "not found"})
            if method not in ROUTES[path]:
                return self._send(405, {"error": "method not allowed"})
            if path == "/healthz":
                return self._send(200, {"status": "ok"})
            if not self._authorized():
                self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 1 << 20))  # drain so the client reads the 401 instead of a TCP reset
                return self._send(401, {"error": "unauthorized"})
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                remaining = min(length, 1 << 20)  # drain so the client sees our 413, then hang up
                while remaining > 0:
                    chunk = self.rfile.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                self.close_connection = True
                return self._send(413, {"error": "payload too large"})
            try:
                body = json.loads(self.rfile.read(length) or b"")
            except (json.JSONDecodeError, UnicodeDecodeError):
                return self._send(400, {"error": "body must be JSON"})
            q = body.get("question") if isinstance(body, dict) else None
            if not isinstance(q, str) or not q.strip():
                return self._send(400, {"error": "question must be a non-empty string"})
            if len(q) > MAX_QUESTION:
                return self._send(400, {"error": f"question longer than {MAX_QUESTION} characters"})
            try:
                answer = answer_fn(q)
            except Exception:
                log.exception("answer_fn failed request_id=%s", self.rid)
                return self._send(500, {"error": "internal error", "request_id": self.rid})
            return self._send(200, {"answer": answer, "request_id": self.rid})

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

    return ThreadingHTTPServer((host, port), Handler)
