"""Check SECURITY-MATRIX.md: every test it names must exist in that row's exercise or capstone.

The matrix lists each security-sensitive exercise's assets, trust boundary, identities and permissions, likely failure
modes and the negative tests that pin them. A renamed or deleted test would leave the matrix claiming protection
that nothing checks, so this runs with the other linters.
usage: python scripts/security_matrix.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "SECURITY-MATRIX.md"


def folder(ident: str) -> list[Path]:
    if ident.lower().startswith("c"):
        return [*ROOT.glob(f"capstones/{ident.lower()}-*")]
    return [*ROOT.glob(f"exercises/*/{ident}-*")]


def main() -> int:
    problems, rows = [], 0
    for n, line in enumerate(MATRIX.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"\| (ex\d+|C\d+|c\d+)\b[^|]*\|", line)
        if not m:
            continue
        rows += 1
        dirs = folder(m.group(1))
        if not dirs:
            problems.append(f"SECURITY-MATRIX.md:{n}: no folder for {m.group(1)}")
            continue
        tests = "\n".join(p.read_text(encoding="utf-8", errors="replace") for d in dirs
                          for p in d.rglob("*") if p.is_file() and re.match(r"(test_.*\.py|.*\.test\.ts)$", p.name))
        last = line.rstrip(" |").rsplit("|", 1)[-1]
        for name in sorted(set(re.findall(r"`(test_\w+|[a-z]\w*)`", last))):
            if name.startswith("test_") and not re.search(rf"def {name}\b|test\(\s*[\"'`]{name}\b", tests):
                problems.append(f"SECURITY-MATRIX.md:{n}: {m.group(1)} names {name}, which isn't in its tests")
    for p in problems:
        print(p)
    print(f"security-matrix: {rows} rows, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
