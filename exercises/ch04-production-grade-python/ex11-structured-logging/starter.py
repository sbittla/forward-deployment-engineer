import contextvars
import logging
from contextlib import contextmanager

SENSITIVE = {"password", "api_key", "authorization", "token", "ssn"}

_cid: contextvars.ContextVar = contextvars.ContextVar("correlation_id", default=None)


@contextmanager
def correlation(cid: str | None = None):
    raise NotImplementedError
    yield


def current_correlation_id() -> str | None:
    raise NotImplementedError


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        raise NotImplementedError


def get_logger(name: str, stream) -> logging.Logger:
    raise NotImplementedError
