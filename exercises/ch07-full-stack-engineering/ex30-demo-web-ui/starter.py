from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = ""
UNAVAILABLE = "The assistant is unavailable."
MAX_BODY_BYTES = 64 * 1024
MAX_REPLAYS = 256


def sse(event: str, data: dict, event_id: int | None = None) -> bytes:
    raise NotImplementedError


def relay(chunks, wfile, first_id: int = 1) -> str:
    raise NotImplementedError


def make_app(llm, demo_mode: bool = True, api_token: str | None = None) -> ThreadingHTTPServer:
    raise NotImplementedError
