READ_PREFIXES = ("Get", "List", "Describe")
PAB_FLAGS = ("block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets")


def _list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _read_only(action: str) -> bool:
    return ":" in action and action.split(":", 1)[1].startswith(READ_PREFIXES)


def lint_policy(policy: dict) -> list[str]:
    issues = []
    for st in _list(policy.get("Statement")):
        if "NotAction" in st:
            issues.append("not-action")
        principal = st.get("Principal")
        if principal == "*" or (isinstance(principal, dict) and "*" in _list(principal.get("AWS"))):
            issues.append("public-principal")
        if st.get("Effect") != "Allow":
            continue
        actions = _list(st.get("Action"))
        issues += [f"wildcard-action:{a}" for a in actions if a == "*" or a.endswith(":*")]
        if "*" in _list(st.get("Resource")) and any(not _read_only(a) for a in actions):
            issues.append("wildcard-resource")
    return list(dict.fromkeys(issues))


def generate_policy(needs: list[tuple[str, str]]) -> dict:
    by_resource: dict[str, set[str]] = {}
    for action, resource in needs:
        by_resource.setdefault(resource, set()).add(action)
    statements = [{"Sid": f"S{i}", "Effect": "Allow", "Action": sorted(actions), "Resource": resource}
                  for i, (resource, actions) in enumerate(by_resource.items(), 1)]
    return {"Version": "2012-10-17", "Statement": statements}


def lint_terraform(doc: dict) -> list[str]:
    res = doc.get("resource", {})

    def refs(rtype, bucket):
        ref = f"${{aws_s3_bucket.{bucket}.id}}"
        return [r for r in res.get(rtype, {}).values() if r.get("bucket") == ref]

    issues = []
    for name in res.get("aws_s3_bucket", {}):
        if not refs("aws_s3_bucket_server_side_encryption_configuration", name):
            issues.append(f"sse:{name}")
        if not any(r.get("versioning_configuration", {}).get("status") == "Enabled"
                   for r in refs("aws_s3_bucket_versioning", name)):
            issues.append(f"versioning:{name}")
        if not any(all(r.get(f) is True for f in PAB_FLAGS) for r in refs("aws_s3_bucket_public_access_block", name)):
            issues.append(f"public-access:{name}")
    return issues
