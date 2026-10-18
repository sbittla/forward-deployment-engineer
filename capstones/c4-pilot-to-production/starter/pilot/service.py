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
    raise NotImplementedError
