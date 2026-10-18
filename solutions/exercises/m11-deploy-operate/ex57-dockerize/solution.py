import re

SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASSWORD", re.I)


def _instructions(text: str) -> list[tuple[str, str]]:
    joined = re.sub(r"\\\s*\n", " ", text)
    out = []
    for line in joined.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        op, _, rest = line.partition(" ")
        out.append((op.upper(), rest.strip()))
    return out


def _sets_secret(rest: str) -> bool:
    for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*[= ]\s*(\S*)", rest):
        if SECRET_NAME.search(m.group(1)) and m.group(2):
            return True
    return False


def lint_dockerfile(text: str) -> list[str]:
    ins = _instructions(text)
    issues = set()
    for op, rest in ins:
        if op == "FROM":
            image = rest.split()[0]
            if "@sha256:" not in image:
                tag = image.rsplit(":", 1)[1] if ":" in image.split("/")[-1] else ""
                if not tag or tag == "latest":
                    issues.add("pinned-base")
        if op in ("ENV", "ARG") and _sets_secret(rest):
            issues.add("no-secrets")
        if op in ("CMD", "ENTRYPOINT") and not rest.startswith("["):
            issues.add("exec-form")
        if op == "RUN" and "pip install" in rest and "--no-cache-dir" not in rest:
            issues.add("no-cache-dir")

    ops = [op for op, _ in ins]
    user_idx = [i for i, (op, _) in enumerate(ins) if op == "USER"]
    cmd_idx = [i for i, op in enumerate(ops) if op in ("CMD", "ENTRYPOINT")]
    if not user_idx or ins[user_idx[-1]][1] in ("root", "0") or (cmd_idx and user_idx[-1] > cmd_idx[-1]):
        issues.add("non-root")
    if "HEALTHCHECK" not in ops:
        issues.add("healthcheck")
    def copies_context(rest: str) -> bool:
        sources = [t for t in rest.split()[:-1] if not t.startswith("--")]
        return any(s in (".", "./") for s in sources)

    copy_all = [i for i, (op, rest) in enumerate(ins) if op == "COPY" and copies_context(rest)]
    pip_req = [i for i, (op, rest) in enumerate(ins) if op == "RUN" and re.search(r"pip install.*-r\s", rest)]
    if copy_all and pip_req and min(pip_req) > min(copy_all):
        issues.add("layer-cache")
    return sorted(issues)
