"""Field-level accuracy against nurse-labelled gold intakes, with urgent-case recall as the safety metric."""

FIELDS = ("urgency", "symptoms", "callback_window")


def evaluate(results, gold: dict) -> dict:
    raise NotImplementedError
