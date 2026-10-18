"""Production-hardened summarisation service: config, resilience, observability, ops tooling and deploy policy."""
from .config import ConfigError, Secret, Settings, load_settings
from .incident import diagnose
from .loadtest import LoadReport, required_replicas, run_load
from .observability import Metrics, json_logger
from .policy import lint_ci, lint_dockerfile, lint_k8s
from .preflight import run_preflight
from .resilience import CircuitOpen, ResilientLLM
from .service import make_server
from .slo import SLO

__all__ = ["ConfigError", "Secret", "Settings", "load_settings", "diagnose", "LoadReport", "required_replicas",
           "run_load", "Metrics", "json_logger", "lint_ci", "lint_dockerfile", "lint_k8s", "run_preflight",
           "CircuitOpen", "ResilientLLM", "make_server", "SLO"]
