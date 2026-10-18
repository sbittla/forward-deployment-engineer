import math
import random
import string
from collections import Counter, defaultdict

from fde_kit import tokenize


def train_test_split(rows: list[tuple[str, str]], test_ratio: float, seed: int):
    rng = random.Random(seed)
    by_label = defaultdict(list)
    for r in rows:
        by_label[r[1]].append(r)
    train, test = [], []
    for label in sorted(by_label):
        group = list(by_label[label])
        rng.shuffle(group)
        k = round(len(group) * test_ratio)
        test += group[:k]
        train += group[k:]
    return train, test


class NaiveBayes:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, texts: list[str], labels: list[str]) -> "NaiveBayes":
        self.labels = sorted(set(labels))
        n = len(labels)
        self.log_prior = {l: math.log(labels.count(l) / n) for l in self.labels}
        self.counts = {l: Counter() for l in self.labels}
        for text, label in zip(texts, labels):
            self.counts[label].update(tokenize(text))
        self.vocab = set().union(*self.counts.values())
        self.totals = {l: sum(c.values()) for l, c in self.counts.items()}
        return self

    def predict_proba(self, text: str) -> dict[str, float]:
        v = len(self.vocab)
        scores = {}
        for l in self.labels:
            s = self.log_prior[l]
            for tok in tokenize(text):
                s += math.log((self.counts[l][tok] + self.alpha) / (self.totals[l] + self.alpha * v))
            scores[l] = s
        top = max(scores.values())
        exp = {l: math.exp(s - top) for l, s in scores.items()}
        z = sum(exp.values())
        return {l: e / z for l, e in exp.items()}

    def predict(self, text: str) -> str:
        p = self.predict_proba(text)
        return max(p, key=p.get)


def metrics(y_true: list[str], y_pred: list[str]) -> dict:
    labels = sorted(set(y_true) | set(y_pred))
    confusion = Counter(zip(y_true, y_pred))
    per = {}
    for l in labels:
        tp = confusion[(l, l)]
        fp = sum(confusion[(t, l)] for t in labels if t != l)
        fn = sum(confusion[(l, p)] for p in labels if p != l)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[l] = {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3)}
    true_labels = sorted(set(y_true))
    macro = sum(per[l]["f1"] for l in true_labels) / len(true_labels)
    acc = sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)
    return {"accuracy": round(acc, 3), "per_class": per, "macro_f1": round(macro, 3), "confusion": dict(confusion)}


def llm_classify(llm, text: str, labels: list[str]) -> str:
    system = (f"Classify the support ticket into exactly one of: {', '.join(labels)}. "
              "Reply with the label only, no punctuation or explanation.")
    reply = llm.complete([{"role": "user", "content": text}], system=system, max_tokens=5).text
    norm = reply.strip().lower().strip(string.punctuation + " ")
    return norm if norm in labels else "unknown"


def recommend(baseline: dict, llm: dict, monthly_volume: int, llm_cost_per_call: float):
    choice = "llm" if llm["macro_f1"] - baseline["macro_f1"] >= 0.03 else "baseline"
    return choice, round(monthly_volume * llm_cost_per_call, 2)
