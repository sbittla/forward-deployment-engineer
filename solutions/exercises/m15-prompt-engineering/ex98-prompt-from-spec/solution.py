"""Compile a customer's policy spec into a system prompt, trace every policy, and test conformance."""
import re
from dataclasses import dataclass
from html import escape

POLICY_ID = re.compile(r"^[A-Z]+-\d+$")
KINDS = ("must", "must_not", "escalate")
KIND_PREFIX = {"must": "Always", "must_not": "Never", "escalate": "Hand off to a human when"}


@dataclass(frozen=True)
class Policy:
    id: str
    kind: str
    rule: str
    why: str = ""
    tests: tuple = ()          # ({"input": str, "expect_contains": [...], "expect_absent": [...]}, ...)


def load_policies(rows: list[dict]) -> list[Policy]:
    out, seen = [], set()
    for row in rows:
        pid, kind = row.get("id", ""), row.get("kind")
        if not POLICY_ID.match(pid):
            raise ValueError(f"bad policy id {pid!r}")
        if pid in seen:
            raise ValueError(f"duplicate policy id {pid}")
        if kind not in KINDS:
            raise ValueError(f"{pid}: kind must be one of {KINDS}")
        if not row.get("rule", "").strip():
            raise ValueError(f"{pid}: empty rule")
        seen.add(pid)
        out.append(Policy(pid, kind, row["rule"].strip(), row.get("why", "").strip(), tuple(row.get("tests", ()))))
    return out


def build_system_prompt(role: str, policies: list[Policy], output_format: str) -> str:
    lines = [f"<role>\n{role.strip()}\n</role>", "", "<policies>"]
    for kind in KINDS:
        for p in (p for p in policies if p.kind == kind):
            why = f" Why: {escape(p.why.rstrip('.'), quote=False)}." if p.why else ""
            lines.append(f'<policy id="{p.id}">{KIND_PREFIX[kind]} {escape(p.rule, quote=False)}.{why}</policy>')
    lines += ["</policies>", "",
              "When policies conflict, escalation wins over never, and never wins over always. Cite the ids of the "
              "policies you applied in a final line: Policies: <ids>.", "",
              f"<output_format>\n{output_format.strip()}\n</output_format>"]
    return "\n".join(lines)


def trace(prompt: str, policies: list[Policy]) -> dict[str, bool]:
    return {p.id: f'<policy id="{p.id}">' in prompt for p in policies}


def coverage(policies: list[Policy]) -> float:
    return round(sum(bool(p.tests) for p in policies) / len(policies), 4) if policies else 0.0


def generate_cases(policies: list[Policy]) -> list[dict]:
    return [{"policy_id": p.id, "case": f"{p.id}#{i + 1}", **t} for p in policies for i, t in enumerate(p.tests)]


def run_conformance(llm, prompt: str, policies: list[Policy]) -> dict:
    results = []
    for case in generate_cases(policies):
        reply = llm.complete([{"role": "user", "content": case["input"]}], system=prompt).text
        low = reply.lower()
        missing = [s for s in case.get("expect_contains", []) if s.lower() not in low]
        leaked = [s for s in case.get("expect_absent", []) if s.lower() in low]
        results.append({"case": case["case"], "policy_id": case["policy_id"], "passed": not missing and not leaked,
                        "missing": missing, "leaked": leaked})
    by_policy: dict[str, bool] = {}
    for r in results:
        by_policy[r["policy_id"]] = by_policy.get(r["policy_id"], True) and r["passed"]
    untested = [p.id for p in policies if not p.tests]
    return {"results": results, "by_policy": by_policy, "untested": untested,
            "pass_rate": round(sum(r["passed"] for r in results) / len(results), 4) if results else 0.0,
            "traced": all(trace(prompt, policies).values())}


def diff_policies(old: list[Policy], new: list[Policy]) -> dict[str, list[str]]:
    o, n = {p.id: p for p in old}, {p.id: p for p in new}
    return {"added": sorted(n.keys() - o.keys()), "removed": sorted(o.keys() - n.keys()),
            "changed": sorted(k for k in o.keys() & n.keys() if (o[k].kind, o[k].rule) != (n[k].kind, n[k].rule))}
