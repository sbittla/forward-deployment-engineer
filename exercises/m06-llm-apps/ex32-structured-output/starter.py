def extract_json(text: str):
    raise NotImplementedError


def validate(obj, schema: dict, path: str = "$") -> list[str]:
    raise NotImplementedError


def complete_structured(llm, prompt: str, schema: dict, max_repairs: int = 2):
    raise NotImplementedError
