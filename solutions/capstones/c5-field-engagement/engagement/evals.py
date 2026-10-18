"""Field-level accuracy against nurse-labelled gold intakes, with urgent-case recall as the safety metric."""

FIELDS = ("urgency", "symptoms", "callback_window")


def evaluate(results, gold: dict) -> dict:
    correct = {f: 0 for f in FIELDS}
    urgent_total = urgent_caught = 0
    for r in results:
        g = gold[r.call_id]
        correct["urgency"] += r.intake["urgency"] == g["urgency"]
        correct["symptoms"] += sorted(r.intake["symptoms"]) == sorted(g["symptoms"])
        correct["callback_window"] += r.intake["callback_window"] == g["callback_window"]
        if g["urgency"] in ("emergency", "urgent"):
            urgent_total += 1
            urgent_caught += r.intake["urgency"] in ("emergency", "urgent") and (
                g["urgency"] != "emergency" or r.intake["urgency"] == "emergency")
    n = len(results)
    out = {f: round(c / n, 4) for f, c in correct.items()}
    out["field_accuracy"] = round(sum(correct.values()) / (n * len(FIELDS)), 4)
    out["urgent_recall"] = round(urgent_caught / urgent_total, 4) if urgent_total else 1.0
    out["calls"] = n
    return out
