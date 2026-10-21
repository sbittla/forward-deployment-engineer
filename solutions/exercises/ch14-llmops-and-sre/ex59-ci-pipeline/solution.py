import re

import yaml

CLOUD_KEY = re.compile(r"secrets\.(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AZURE_CLIENT_SECRET|AZURE_CREDENTIALS"
                       r"|GCP_SA_KEY|GOOGLE_CREDENTIALS)\b")


def _triggers(doc: dict) -> set[str]:
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    return set(on or {})


def _permissions_ok(perms) -> bool:
    if not perms or perms == "write-all":
        return False
    if isinstance(perms, str):
        return perms == "read-all"
    return all(v != "write" or k == "id-token" for k, v in perms.items())


def _pinned(uses: str) -> bool:
    if uses.startswith("./") or uses.startswith("docker://"):
        return True
    if "@" not in uses:
        return False
    return uses.rsplit("@", 1)[1] not in ("main", "master", "")


def lint_workflow(doc: dict) -> list[str]:
    issues = []
    if not {"pull_request", "push"} <= _triggers(doc):
        issues.append("triggers")
    if not _permissions_ok(doc.get("permissions")):
        issues.append("permissions")
    jobs = doc.get("jobs", {})
    has_matrix = False
    for name, job in jobs.items():
        if "timeout-minutes" not in job:
            issues.append(f"timeout:{name}")
        steps = job.get("steps", [])
        if any("uses" in s and not _pinned(s["uses"]) for s in steps):
            issues.append(f"pin:{name}")
        if any(re.search(r"echo.*\$\{\{\s*secrets\.", line)
               for s in steps for line in str(s.get("run", "")).splitlines()):
            issues.append(f"secret-echo:{name}")
        if CLOUD_KEY.search(str(job)):
            issues.append(f"static-cloud-key:{name}")
        versions = job.get("strategy", {}).get("matrix", {}).get("python-version", [])
        if isinstance(versions, list) and len(versions) >= 2:
            has_matrix = True
    if not has_matrix:
        issues.append("matrix")
    deploy = jobs.get("deploy")
    if deploy is not None:
        needs = deploy.get("needs", [])
        needs = [needs] if isinstance(needs, str) else needs
        if "test" not in needs or "refs/heads/main" not in str(deploy.get("if", "")):
            issues.append("deploy-gate")
    return issues
