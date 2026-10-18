"""Container entry point: validate config, wrap the model client, serve on :8080."""
import os
import sys

from .config import ConfigError, load_settings
from .observability import Metrics, json_logger
from .resilience import ResilientLLM
from .service import make_server


def build(env=os.environ, client_factory=None):
    settings = load_settings(env)
    if client_factory is None:
        from fde_kit import AnthropicLLM  # real client only in the container
        client_factory = AnthropicLLM
    metrics = Metrics()
    llm = ResilientLLM(client_factory(), fallback=client_factory(), model=settings.model,
                       fallback_model=settings.fallback_model, metrics=metrics)
    return make_server(settings, llm, metrics, json_logger("pilot", sys.stdout), host="0.0.0.0", port=8080)


def main() -> int:
    try:
        server = build()
    except ConfigError as e:
        print("configuration errors:\n- " + "\n- ".join(e.errors), file=sys.stderr)
        return 2
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
