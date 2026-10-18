"""Container entry point: validate config, wrap the model client, serve on :8080."""
import os
import sys

from .config import ConfigError, load_settings
from .observability import Metrics, json_logger
from .resilience import ResilientLLM
from .service import make_server


def build(env=os.environ, client_factory=None):
    raise NotImplementedError


def main() -> int:
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
