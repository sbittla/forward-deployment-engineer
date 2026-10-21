from fde_kit import tokenize

SEVERITY_WEIGHT = {"blocker": 5, "major": 2, "minor": 1}


def cluster(items: list[dict], threshold: float = 0.3) -> list[list[int]]:
    raise NotImplementedError


def score(cluster_items: list[dict]) -> float:
    raise NotImplementedError


def brief(items: list[dict], top: int = 3, threshold: float = 0.3) -> str:
    raise NotImplementedError
