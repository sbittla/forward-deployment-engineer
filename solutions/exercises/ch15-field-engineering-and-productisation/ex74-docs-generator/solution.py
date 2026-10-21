import inspect
import re


def _defined_here(module, obj) -> bool:
    return (inspect.isfunction(obj) or inspect.isclass(obj)) and getattr(obj, "__module__", None) == module.__name__


def public_api(module) -> list[str]:
    if hasattr(module, "__all__"):
        return sorted(module.__all__)
    return sorted(n for n, o in vars(module).items() if not n.startswith("_") and _defined_here(module, o))


def parse_google_docstring(doc: str | None) -> dict:
    out = {"summary": "", "args": {}, "returns": ""}
    if not doc:
        return out
    text = inspect.cleandoc(doc)
    blocks = re.split(r"\n\s*\n", text)
    out["summary"] = " ".join(blocks[0].split())
    section, last_arg = None, None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in ("Args:", "Arguments:", "Parameters:"):
            section, last_arg = "args", None
            continue
        if stripped in ("Returns:", "Return:"):
            section = "returns"
            continue
        if not stripped:
            continue
        if section == "args":
            m = re.match(r"^\s{1,8}(\w+)(?:\s*\([^)]*\))?:\s*(.*)$", line)
            indent = len(line) - len(line.lstrip())
            if m and indent <= 4:
                last_arg = m.group(1)
                out["args"][last_arg] = m.group(2).strip()
            elif last_arg:
                out["args"][last_arg] += " " + stripped
        elif section == "returns":
            out["returns"] = f"{out['returns']} {stripped}".strip()
    return out


def _signature(obj) -> str:
    if inspect.isclass(obj):
        sig = inspect.signature(obj.__init__)
        params = [p for name, p in sig.parameters.items() if name != "self"]
        return str(sig.replace(parameters=params, return_annotation=inspect.Signature.empty))
    return str(inspect.signature(obj))


def render_reference(module) -> str:
    lines = [f"# {module.__name__}", "", parse_google_docstring(module.__doc__)["summary"], ""]
    for name in public_api(module):
        obj = getattr(module, name)
        prefix = "class " if inspect.isclass(obj) else ""
        lines.append(f"## {prefix}`{name}{_signature(obj)}`")
        doc = parse_google_docstring(inspect.getdoc(obj))
        if doc["summary"]:
            lines += ["", doc["summary"]]
        if doc["args"]:
            lines += ["", "| Argument | Description |", "|---|---|"]
            lines += [f"| {a} | {d} |" for a, d in doc["args"].items()]
        if doc["returns"]:
            lines += ["", f"**Returns:** {doc['returns']}"]
        lines.append("")
    return "\n".join(lines)


def missing_docs(module) -> list[str]:
    missing = []
    for name in public_api(module):
        obj = getattr(module, name)
        if not obj.__doc__:
            missing.append(name)
        if inspect.isclass(obj):
            for mname, m in vars(obj).items():
                if inspect.isfunction(m) and not mname.startswith("_") and not m.__doc__:
                    missing.append(f"{name}.{mname}")
    return sorted(missing)
