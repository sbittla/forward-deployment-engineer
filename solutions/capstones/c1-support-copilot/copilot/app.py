"""Minimal HTTP API for the copilot (stdlib only, so it runs in the customer's hardened base image)."""
import hmac
import json
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_server(copilot, tokens, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    tokens = set(tokens)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, status, payload):
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Request-ID", self.rid)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self.rid = self.headers.get("X-Request-ID") or uuid.uuid4().hex
            if self.path == "/healthz":
                return self._send(200, {"status": "ok"})
            self._send(404, {"error": "not found"})

        def do_POST(self):
            self.rid = self.headers.get("X-Request-ID") or uuid.uuid4().hex
            if self.path != "/v1/ask":
                return self._send(404, {"error": "not found"})
            auth = self.headers.get("Authorization", "")
            if not (auth.startswith("Bearer ") and any(hmac.compare_digest(auth[7:], t) for t in tokens)):
                self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 1 << 20))  # drain so the client reads the 401 instead of a TCP reset
                return self._send(401, {"error": "unauthorized"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)))
                question = body["question"]
                assert isinstance(question, str) and 0 < len(question.strip()) <= 2000
            except Exception:
                return self._send(400, {"error": "body must be JSON with a non-empty 'question' (max 2000 chars)"})
            try:
                resp = copilot.ask(question)
            except Exception:
                return self._send(500, {"error": "internal error", "request_id": self.rid})
            return self._send(200, {**asdict(resp), "request_id": self.rid})

    return ThreadingHTTPServer((host, port), Handler)
