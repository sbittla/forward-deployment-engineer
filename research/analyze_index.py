"""Recompute every posting figure the book publishes from postings-index.csv alone (no posting text needed).

    python research/analyze_index.py                 # uses research/postings-index.csv
    python research/analyze_index.py my-index.csv    # an index you built with classify.py

A role counts once: only rows with representative == "y" (the first posting of each duplicate group among
included postings) enter the denominators. Percentages are rounded half away from zero to one decimal place.
"""
import csv
import sys
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from classify import EXTRA, TAXONOMY

HERE = Path(__file__).parent


def pct(k, n):
    return float(Decimal(100 * k / n).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if n else 0.0


def nums(cell):
    return [int(x) for x in cell.split(";") if x]


def analyze(rows):
    roles = [r for r in rows if r["representative"] == "y"]
    n = len(roles)
    out = dict(
        collected=len(rows),
        included=sum(r["included"] == "y" for r in rows),
        roles=n,
        companies=len({r["company"] for r in roles}),
        by_company=Counter(r["company"] for r in roles).most_common(),
        excluded=Counter(r["exclusion_reason"] for r in rows if r["included"] == "n").most_common(),
        requirements=sorted(
            ({"id": rid, "name": name, "count": sum(int(r[rid]) for r in roles),
              "pct": pct(sum(int(r[rid]) for r in roles), n)} for rid, name, _ in TAXONOMY),
            key=lambda d: (-d["pct"], d["id"])),
        extra={k: {"count": sum(int(r[k]) for r in roles), "pct": pct(sum(int(r[k]) for r in roles), n)}
               for k, _ in EXTRA},
    )
    clear = [r for r in roles if r["clearance"] == "1"]
    out["clearance_by_company"] = Counter(r["company"] for r in clear).most_common()
    years = Counter(y for r in roles for y in nums(r["years_stated"]))
    out["years_roles_per_figure"] = dict(sorted(years.items()))
    out["years_any_stated"] = sum(bool(nums(r["years_stated"])) for r in roles)
    out["years_8_plus"] = sum(any(y >= 8 for y in nums(r["years_stated"])) for r in roles)
    out["years_8_plus_titles"] = [r["title"] for r in roles if any(y >= 8 for y in nums(r["years_stated"]))]
    travel = [max(nums(r["travel_pct_stated"])) for r in roles if nums(r["travel_pct_stated"])]
    out["travel_figure_stated"] = len(travel)
    out["travel_max_figures"] = sorted(travel)
    return out


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "postings-index.csv"
    with open(path, encoding="utf-8", newline="") as f:
        a = analyze(list(csv.DictReader(f)))
    n = a["roles"]
    print(f"collected postings:     {a['collected']}")
    print(f"included postings:      {a['included']}")
    print(f"unique roles (n):       {n}")
    print(f"companies with a role:  {a['companies']}")
    print("excluded:", ", ".join(f"{k} {v}" for k, v in a["excluded"]))
    print("roles by company:", ", ".join(f"{k} {v}" for k, v in a["by_company"]))
    print()
    print("| id | requirement | roles | % of roles |")
    print("|---|---|---|---|")
    for r in a["requirements"]:
        print(f"| {r['id']} | {r['name']} | {r['count']} | {r['pct']:.1f} |")
    print()
    for k, v in a["extra"].items():
        print(f"{k:10s} {v['count']:4d} roles  {v['pct']:5.1f}%")
    print("clearance by company:", ", ".join(f"{k} {v}" for k, v in a["clearance_by_company"]))
    print(f"years: roles stating a figure {a['years_any_stated']}; roles per figure {a['years_roles_per_figure']}; "
          f"roles asking for 8+ years {a['years_8_plus']}")
    tf = a["travel_max_figures"]
    if tf:
        mid = [t for t in tf if 20 <= t <= 50]
        print(f"travel: roles stating a percentage {len(tf)}; highest stated figure per role {tf}; "
              f"within 20-50%: {len(mid)} ({pct(len(mid), len(tf))}%)")


if __name__ == "__main__":
    main()
