"""An embedded FDE engagement end to end: discovery -> POC pipeline -> evals -> value -> readout."""
from .deid import PHILeak, deidentify, phi_scan
from .discovery import Charter, assumptions_for, engagement_plan, parse_notes, validate_charter
from .evals import evaluate
from .intake import RED_FLAGS, extract_intake, triage
from .pipeline import IntakeResult, run_pipeline
from .readout import render_readout
from .value import roi
from .voice import call_metrics, caller_transcript, segments

__all__ = ["PHILeak", "deidentify", "phi_scan", "Charter", "assumptions_for", "engagement_plan", "parse_notes",
           "validate_charter", "evaluate", "RED_FLAGS", "extract_intake", "triage", "IntakeResult", "run_pipeline",
           "render_readout", "roi", "call_metrics", "caller_transcript", "segments"]
