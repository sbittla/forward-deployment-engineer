"""The hardened summarisation service: auth, limits, probes, metrics, structured logs, graceful degradation."""
import hmac
import json
import logging
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .config import Settings
from .observability import Metrics, json_logger
from .resilience import CircuitOpen

SYSTEM = "Summarise the shipment exception report for an operations manager in at most 5 bullet points."


def make_server(settings: Settings, llm, metrics: Metrics | None = None, logger: logging.Logger | None = None,
                host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    metrics = metrics or Metrics()
    log = logger or json_logger("pilot", sys.stdout)
    requests = metrics.counter("pilot_requests_total", "HTTP requests by route and status")
    latency = metrics.histogram("pilot_request_seconds", "Request latency in seconds")
    tokens = [t.reveal() for t in settings.api_tokens]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, status, payload, ctype="application/json", extra=None):
            # Record before writing so a client that reads /metrics right after this response sees it.
            route = self.path.split("?")[0]
            elapsed = time.perf_counter() - self.t0
            requests.inc({"route": route, "status": str(status)})
            latency.observe(elapsed, {"route": route})
            log.info("request", extra={"fields": {"request_id": self.rid, "route": route, "status": status,
                                                  "duration_ms": round(elapsed * 1000, 1)}})
            body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Request-ID", self.rid)
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _start(self):
            self.t0 = time.perf_counter()
            self.rid = self.headers.get("X-Request-ID") or uuid.uuid4().hex

        def do_GET(self):
            self._start()
            if self.path == "/healthz":
                return self._send(200, {"status": "ok"})
            if self.path == "/readyz":
                state = getattr(llm, "breaker_state", "closed")
                if state == "open":
                    return self._send(503, {"status": "degraded", "llm_circuit": state})
                return self._send(200, {"status": "ready", "llm_circuit": state})
            if self.path == "/metrics":
                return self._send(200, metrics.render().encode(), "text/plain; version=0.0.4")
            self._send(404, {"error": "not found"})

        def do_POST(self):
            self._start()
            if self.path != "/v1/summarize":
                return self._send(404, {"error": "not found"})
            auth = self.headers.get("Authorization", "")
            if not (auth.startswith("Bearer ") and any(hmac.compare_digest(auth[7:], t) for t in tokens)):
                self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 1 << 20))  # drain so the client reads the 401 instead of a TCP reset
                return self._send(401, {"error": "unauthorized"})
            length = int(self.headers.get("Content-Length") or 0)
            if length > settings.max_input_chars * 4 + 1024:
                self.rfile.read(min(length, 1 << 20))
                self.close_connection = True
                return self._send(413, {"error": "payload too large"})
            try:
                text = json.loads(self.rfile.read(length))["text"]
                if not isinstance(text, str) or not text.strip():
                    raise ValueError
            except Exception:
                return self._send(400, {"error": "body must be JSON with non-empty string 'text'"})
            if len(text) > settings.max_input_chars:
                return self._send(413, {"error": f"text longer than {settings.max_input_chars} characters"})
            try:
                resp = llm.complete([{"role": "user", "content": text}], system=SYSTEM, max_tokens=1024)
            except CircuitOpen:
                return self._send(503, {"error": "summaries temporarily unavailable", "request_id": self.rid},
                                  extra={"Retry-After": "30"})
            except Exception as exc:
                log.error("llm failure", extra={"fields": {"request_id": self.rid, "error": type(exc).__name__}})
                return self._send(502, {"error": "upstream model error", "request_id": self.rid})
            return self._send(200, {"summary": resp.text, "model": resp.model, "request_id": self.rid})

    return ThreadingHTTPServer((host, port), Handler)
