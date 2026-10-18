"""Read the pilot's incident log and turn it into findings, each paired with the fix shipped in this service."""
import re

LINE = re.compile(r"^(\S+)\s+(INFO|WARN|ERROR)\s+(.*)$")


def diagnose(lines: list[str]) -> dict:
    raise NotImplementedError
