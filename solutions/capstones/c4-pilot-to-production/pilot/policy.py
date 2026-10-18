"""The customer platform team's admission policy, as code (subset of ex57-ex59)."""
import re

SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASSWORD", re.I)


def _tag_ok(image: str) -> bool:
    if "@sha256:" in image:
        return True
    last = image.rsplit("/", 1)[-1]
    return ":" in last and last.rsplit(":", 1)[1] not in ("", "latest")


def lint_dockerfile(text: str) -> list[str]:
    text = re.sub(r"\\\s*\n", " ", text)
    ins = [(l.split(None, 1)[0].upper(), (l.split(None, 1) + [""])[1].strip())
           for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    issues = set()
    ops = [op for op, _ in ins]
    for op, rest in ins:
        if op == "FROM" and not _tag_ok(rest.split()[0]):
            issues.add("pinned-base")
        if op in ("CMD", "ENTRYPOINT") and not rest.startswith("["):
            issues.add("exec-form")
        if op in ("ENV", "ARG") and any(SECRET_NAME.search(n) and v for n, v in
                                        re.findall(r"([A-Za-z_]\w*)\s*=\s*(\S*)", rest)):
            issues.add("no-secrets")
    users = [rest for op, rest in ins if op == "USER"]
    if not users or users[-1] in ("root", "0"):
        issues.add("non-root")
    if "HEALTHCHECK" not in ops:
        issues.add("healthcheck")
    return sorted(issues)


def lint_k8s(docs: list[dict]) -> list[str]:
    issues = []
    for d in docs:
        if d.get("kind") != "Deployment":
            continue
        name, spec = d["metadata"]["name"], d.get("spec", {})
        pod = spec.get("template", {}).get("spec", {})
        if spec.get("replicas", 1) < 2:
            issues.append(f"{name}: replicas")
        if not pod.get("securityContext", {}).get("runAsNonRoot"):
            issues.append(f"{name}: non-root")
        for c in pod.get("containers", []):
            res = c.get("resources", {})
            if not all(k in res.get(p, {}) for p in ("requests", "limits") for k in ("cpu", "memory")):
                issues.append(f"{name}: resources")
            for probe, path in (("livenessProbe", "/healthz"), ("readinessProbe", "/readyz")):
                if c.get(probe, {}).get("httpGet", {}).get("path") != path:
                    issues.append(f"{name}: {probe}")
            if not _tag_ok(c.get("image", "")):
                issues.append(f"{name}: image-tag")
            if any("value" in e and SECRET_NAME.search(e.get("name", "")) for e in c.get("env", [])):
                issues.append(f"{name}: secret-literal")
    if not any(d.get("kind") == "Deployment" for d in docs):
        issues.append("no Deployment found")
    return issues


def lint_ci(doc: dict) -> list[str]:
    issues = []
    perms = doc.get("permissions")
    if not perms or perms == "write-all" or (isinstance(perms, dict) and
                                             any(v == "write" and k != "id-token" for k, v in perms.items())):
        issues.append("permissions")
    for name, job in doc.get("jobs", {}).items():
        if "timeout-minutes" not in job:
            issues.append(f"timeout:{name}")
        for s in job.get("steps", []):
            uses = s.get("uses")
            if uses and ("@" not in uses or uses.rsplit("@", 1)[1] in ("main", "master")):
                issues.append(f"pin:{name}")
    runs = " ".join(s.get("run", "") for j in doc.get("jobs", {}).values() for s in j.get("steps", []))
    if "pytest" not in runs:
        issues.append("tests")
    return issues
