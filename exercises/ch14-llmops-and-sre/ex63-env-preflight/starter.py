import os
import shutil
import socket
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Check:
    name: str
    fn: Callable[[], tuple[bool, str]]
    severity: str = "fail"
    hint: str = ""


@dataclass
class Report:
    results: list[tuple[Check, bool, str]] = field(default_factory=list)

    @property
    def status(self) -> str:
        raise NotImplementedError

    @property
    def exit_code(self) -> int:
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError


def python_version(min_version, current=sys.version_info[:3], severity="fail", hint="") -> Check:
    raise NotImplementedError


def env_vars(names, env, severity="fail", hint="") -> Check:
    raise NotImplementedError


def disk_free(path, min_gb, usage=shutil.disk_usage, severity="fail", hint="") -> Check:
    raise NotImplementedError


def dns(host, resolve=socket.gethostbyname, severity="fail", hint="") -> Check:
    raise NotImplementedError


def tcp(host, port, connect, severity="fail", hint="") -> Check:
    raise NotImplementedError


def clock_skew(reference_epoch, max_skew_s=60, now=time.time, severity="warn", hint="") -> Check:
    raise NotImplementedError


def writable(path, severity="fail", hint="") -> Check:
    raise NotImplementedError


def run_preflight(checks: list[Check]) -> Report:
    raise NotImplementedError
