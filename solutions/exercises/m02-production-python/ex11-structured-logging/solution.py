import contextvars
import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

SENSITIVE = {"password", "api_key", "authorization", "token", "ssn"}

_cid: contextvars.ContextVar = contextvars.ContextVar("correlation_id", default=None)


@contextmanager
def correlation(cid: str | None = None):
    cid = cid or uuid.uuid4().hex
    token = _cid.set(cid)
    try:
        yield cid
    finally:
        _cid.reset(token)


def current_correlation_id() -> str | None:
    return _cid.get()


def _redact(obj):
    if isinstance(obj, dict):
        return {k: "[REDACTED]" if str(k).lower() in SENSITIVE else _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "correlation_id": current_correlation_id(),
        }
        out.update(_redact(getattr(record, "fields", {}) or {}))
        if record.exc_info:
            out["exc_type"] = record.exc_info[0].__name__
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str)


def get_logger(name: str, stream) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.propagate = False
    if not any(getattr(h, "_fde_json", False) for h in log.handlers):
        h = logging.StreamHandler(stream)
        h.setFormatter(JsonFormatter())
        h._fde_json = True
        log.addHandler(h)
    return log
