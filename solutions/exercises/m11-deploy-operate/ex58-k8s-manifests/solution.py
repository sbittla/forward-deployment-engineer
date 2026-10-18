import re

import yaml

SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASSWORD", re.I)


def load(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [d for d in yaml.safe_load_all(f) if d]


def _tag_ok(image: str) -> bool:
    if "@sha256:" in image:
        return True
    last = image.rsplit("/", 1)[-1]
    return ":" in last and last.rsplit(":", 1)[1] != "latest"


def _lint_deployment(d: dict) -> list[str]:
    name = d["metadata"]["name"]
    spec = d.get("spec", {})
    pod = spec.get("template", {}).get("spec", {})
    issues = []
    if spec.get("replicas", 1) < 2:
        issues.append("replicas")
    if not pod.get("securityContext", {}).get("runAsNonRoot"):
        issues.append("non-root")
    for c in pod.get("containers", []):
        cn = c["name"]
        res = c.get("resources", {})
        if not all(k in res.get(part, {}) for part in ("requests", "limits") for k in ("cpu", "memory")):
            issues.append(f"resources:{cn}")
        if "livenessProbe" not in c:
            issues.append(f"liveness:{cn}")
        if "readinessProbe" not in c:
            issues.append(f"readiness:{cn}")
        if not _tag_ok(c.get("image", "")):
            issues.append(f"image-tag:{cn}")
        if any("value" in e and SECRET_NAME.search(e.get("name", "")) for e in c.get("env", [])):
            issues.append(f"secret-literal:{cn}")
        if not c.get("securityContext", {}).get("readOnlyRootFilesystem"):
            issues.append(f"readonly-fs:{cn}")
    return [f"Deployment/{name}: {i}" for i in issues]


def lint_manifests(docs: list[dict]) -> list[str]:
    deployments = {d["metadata"]["name"]: d for d in docs if d.get("kind") == "Deployment"}
    pod_labels = [d.get("spec", {}).get("template", {}).get("metadata", {}).get("labels", {}) for d in deployments.values()]
    issues = []
    for d in docs:
        kind, name = d.get("kind"), d.get("metadata", {}).get("name")
        if kind == "Deployment":
            issues += _lint_deployment(d)
        elif kind == "Service":
            sel = d.get("spec", {}).get("selector", {})
            if not sel or not any(all(labels.get(k) == v for k, v in sel.items()) for labels in pod_labels):
                issues.append(f"Service/{name}: selector")
        elif kind == "HorizontalPodAutoscaler":
            spec = d.get("spec", {})
            if spec.get("minReplicas", 1) < 2:
                issues.append(f"HorizontalPodAutoscaler/{name}: hpa-min")
            if spec.get("scaleTargetRef", {}).get("name") not in deployments:
                issues.append(f"HorizontalPodAutoscaler/{name}: hpa-target")
    return issues
