"""Execution-accuracy evals: compare the analyst's result set with the gold query's result set."""
import json
from pathlib import Path

from fde_kit import FakeLLM

from .analyst import Analyst


def _normalise(rows, ordered: bool):
    raise NotImplementedError


def run_questions(conn, questions_path) -> dict:
    raise NotImplementedError
