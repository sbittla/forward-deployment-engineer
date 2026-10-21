"""Release gate for dated facts: VERSIONS.md must be recently checked and must list every model id the code uses.

Fails if any section of VERSIONS.md has no "Last checked: YYYY-MM-DD" line or one older than --max-age days, or if a
model id appears in the code but not in VERSIONS.md. Run by `verify_release.py`, not by CI: it depends on the date.
usage: python scripts/currency_check.py [--max-age 120] [--today YYYY-MM-DD]
"""
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = re.compile(r"\bclaude-(?:opus|sonnet|haiku|fable)-\d+(?:-\d+)*\b")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age", type=int, default=120)
    ap.add_argument("--today", default=datetime.date.today().isoformat())
    args = ap.parse_args(argv)
    today = datetime.date.fromisoformat(args.today)
    text = (ROOT / "VERSIONS.md").read_text(encoding="utf-8")
    problems = []
    for section in re.split(r"^(?=## )", text, flags=re.M)[1:]:
        title = section.splitlines()[0][3:]
        m = re.search(r"Last checked: (\d{4}-\d{2}-\d{2})", section)
        if not m:
            problems.append(f"VERSIONS.md '{title}': no 'Last checked' date")
        elif (age := (today - datetime.date.fromisoformat(m.group(1))).days) > args.max_age:
            problems.append(f"VERSIONS.md '{title}': last checked {age} days ago (limit {args.max_age})")
    listed = set(MODEL_ID.findall(text))
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    used: dict[str, str] = {}
    for f in files:
        if f.endswith((".py", ".ts", ".json", ".yaml", ".yml", ".md")) and f != "VERSIONS.md":
            for mid in MODEL_ID.findall((ROOT / f).read_text(encoding="utf-8", errors="replace")):
                used.setdefault(mid, f)
    for mid, f in sorted(used.items()):
        if mid not in listed:
            problems.append(f"model id {mid} (first used in {f}) isn't listed in VERSIONS.md")
    for p in problems:
        print(p)
    print(f"currency-check: {len(used)} model ids in use, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
