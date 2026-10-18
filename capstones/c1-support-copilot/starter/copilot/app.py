"""Minimal HTTP API for the copilot (stdlib only, so it runs in the customer's hardened base image)."""
import hmac
import json
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_server(copilot, tokens, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    raise NotImplementedError
