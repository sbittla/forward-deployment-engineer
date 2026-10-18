import json

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _candidates(text: str):
    """Yield substrings that are balanced {...} or [...] spans, scanning left to right."""
    for start, ch in enumerate(text):
        if ch not in "{[":
            continue
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    yield text[start:i + 1]
                    break


def extract_json(text: str):
    for cand in _candidates(text):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            continue
    raise ValueError("no JSON object or array found in model output")


def validate(obj, schema: dict, path: str = "$") -> list[str]:
    errs = []
    t = schema.get("type")
    if t and not TYPES[t](obj):
        return [f"{path}: expected {t}, got {type(obj).__name__}"]
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if "minimum" in schema and obj < schema["minimum"]:
            errs.append(f"{path}: must be >= {schema['minimum']}")
        if "maximum" in schema and obj > schema["maximum"]:
            errs.append(f"{path}: must be <= {schema['maximum']}")
    if isinstance(obj, str) and len(obj) < schema.get("minLength", 0):
        errs.append(f"{path}: shorter than {schema['minLength']} characters")
    if isinstance(obj, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in obj:
                errs.append(f"{path}.{key}: is required")
        for key, val in obj.items():
            if key in props:
                errs += validate(val, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}.{key}: unexpected property '{key}'")
    if isinstance(obj, list) and "items" in schema:
        for i, val in enumerate(obj):
            errs += validate(val, schema["items"], f"{path}[{i}]")
    return errs


def complete_structured(llm, prompt: str, schema: dict, max_repairs: int = 2):
    system = ("Extract the requested data. Reply with a single JSON value that validates against this JSON "
              f"Schema, and nothing else:\n{json.dumps(schema, indent=1)}")
    messages = [{"role": "user", "content": prompt}]
    errors: list[str] = []
    for attempt in range(1, max_repairs + 2):
        reply = llm.complete(messages, system=system).text
        try:
            obj = extract_json(reply)
            errors = validate(obj, schema)
        except ValueError as e:
            errors = [str(e)]
        if not errors:
            return obj, attempt
        messages = messages + [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": "The JSON is invalid:\n- " + "\n- ".join(errors) + "\nReturn corrected JSON only."},
        ]
    raise ValueError("model output failed validation: " + "; ".join(errors))
