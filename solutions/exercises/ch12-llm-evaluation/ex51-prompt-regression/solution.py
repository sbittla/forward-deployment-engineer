import argparse
import json
import sys
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
    b, c = base["results"], cand["results"]
    common = sorted(set(b) & set(c))
    br = round(sum(b[k]["passed"] for k in common) / len(common), 4) if common else 0.0
    cr = round(sum(c[k]["passed"] for k in common) / len(common), 4) if common else 0.0
    regressions = [k for k in common if b[k]["passed"] and not c[k]["passed"]]
    fixes = [k for k in common if not b[k]["passed"] and c[k]["passed"]]
    missing = sorted(set(b) - set(c))
    critical = [k for k in regressions if set(c[k].get("tags", [])) & set(critical_tags)]
    delta = round(cr - br, 4)
    passed = delta >= -max_drop and not critical and not missing
    return Gate(br, cr, delta, regressions, fixes, missing, critical, passed)


def _section(title, ids, critical=()):
    items = [f"- {i}{' (critical)' if i in critical else ''}" for i in ids] or ["- none"]
    return [f"### {title}"] + items + [""]


def render(gate: Gate) -> str:
    lines = [f"## Eval gate: {'PASS' if gate.passed else 'FAIL'}", "",
             f"Pass rate: {gate.base_rate:.4f} -> {gate.cand_rate:.4f} ({gate.delta:+.4f})", ""]
    lines += _section("Regressions", gate.regressions, gate.critical_regressions)
    lines += _section("Fixes", gate.fixes) + _section("Missing", gate.missing)
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compare two eval runs and fail on regressions.")
    ap.add_argument("base")
    ap.add_argument("candidate")
    ap.add_argument("--max-drop", type=float, default=0.02)
    ap.add_argument("--critical-tag", action="append", default=None)
    args = ap.parse_args(argv)
    with open(args.base, encoding="utf-8") as f:
        base = json.load(f)
    with open(args.candidate, encoding="utf-8") as f:
        cand = json.load(f)
    gate = compare(base, cand, args.max_drop, tuple(args.critical_tag or ("safety",)))
    print(render(gate))
    return 0 if gate.passed else 1


if __name__ == "__main__":
    sys.exit(main())
