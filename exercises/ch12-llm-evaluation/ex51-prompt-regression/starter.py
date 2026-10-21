import argparse
import json
from dataclasses import dataclass, field


@dataclass
class Gate:
    base_rate: float
    cand_rate: float
    delta: float
    regressions: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    critical_regressions: list[str] = field(default_factory=list)
    passed: bool = True


def compare(base: dict, cand: dict, max_drop: float = 0.02, critical_tags=("safety",)) -> Gate:
    raise NotImplementedError


def render(gate: Gate) -> str:
    raise NotImplementedError


def main(argv=None) -> int:
    raise NotImplementedError
