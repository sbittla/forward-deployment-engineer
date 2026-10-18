"""Export a learner workspace without reference solutions.

Instructors and book readers who want to avoid spoilers can work from the export instead of the full repo.
usage: python scripts/export_learner.py <target_dir>
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["exercises", "capstones", "fde_kit", "scripts", "conftest.py", "pytest.ini", "requirements.txt",
           "package.json", "README.md", "LICENSE", "LICENSE-CONTENT", "NOTICE.md", "VERSIONS.md", "CHANGELOG.md",
           ".gitattributes"]
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "node_modules")


def export(target: Path) -> int:
    if target.exists() and any(target.iterdir()):
        print(f"refusing to export into non-empty directory: {target}")
        return 1
    target.mkdir(parents=True, exist_ok=True)
    for name in INCLUDE:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, target / name, ignore=SKIP)
        elif src.exists():
            shutil.copy2(src, target / name)
    (target / "scripts" / "export_learner.py").unlink(missing_ok=True)
    note = ("\n> This is a learner export: reference solutions are not included, so `--solutions` runs are "
            "unavailable. Work from each exercise's README and tests.\n")
    readme = target / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + note, encoding="utf-8", newline="\n")
    print(f"exported learner workspace to {target}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(export(Path(sys.argv[1]).resolve()))
