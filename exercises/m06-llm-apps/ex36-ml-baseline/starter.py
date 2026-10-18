from fde_kit import tokenize


def train_test_split(rows: list[tuple[str, str]], test_ratio: float, seed: int):
    raise NotImplementedError


class NaiveBayes:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, texts: list[str], labels: list[str]) -> "NaiveBayes":
        raise NotImplementedError

    def predict_proba(self, text: str) -> dict[str, float]:
        raise NotImplementedError

    def predict(self, text: str) -> str:
        raise NotImplementedError


def metrics(y_true: list[str], y_pred: list[str]) -> dict:
    raise NotImplementedError


def llm_classify(llm, text: str, labels: list[str]) -> str:
    raise NotImplementedError


def recommend(baseline: dict, llm: dict, monthly_volume: int, llm_cost_per_call: float):
    raise NotImplementedError
