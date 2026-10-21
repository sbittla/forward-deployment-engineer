import re

BREAK_AFTER = 90
BREAK_MIN = 15
CHECK_MIN = 5


def _hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def build_agenda(objectives: list[dict], start: str = "09:00", total_minutes: int = 360) -> list[tuple]:
    h, m = map(int, start.split(":"))
    t0 = h * 60 + m
    t, since_break, out = t0, 0, []
    for i, o in enumerate(objectives):
        if o["lab_min"] <= 0:
            raise ValueError(f"objective {o['id']} has no hands-on lab")
        for kind, dur in (("concept", o["concept_min"]), ("demo", o["demo_min"]), ("lab", o["lab_min"]),
                          ("check", CHECK_MIN)):
            if dur > 0:
                out.append((_hhmm(t), _hhmm(t + dur), kind, o["id"]))
                t += dur
                since_break += dur
        if since_break >= BREAK_AFTER and i < len(objectives) - 1:
            out.append((_hhmm(t), _hhmm(t + BREAK_MIN), "break", None))
            t += BREAK_MIN
            since_break = 0
    if t - t0 > total_minutes:
        raise ValueError(f"agenda needs {t - t0} minutes, only {total_minutes} available")
    return out


OBSERVABLE = re.compile(r"`[^`]+`|\b(expect|see|returns|shows)\b", re.I)


def lab_steps_valid(steps: list[dict]) -> list[int]:
    return [i for i, s in enumerate(steps) if not s.get("verify") or not OBSERVABLE.search(s["verify"])]


def readiness(participants: list[dict], objectives: list[str], pass_mark: float = 0.8) -> dict:
    ready = {o: [] for o in objectives}
    per_person = {}
    for p in participants:
        mine = [o for o in objectives if p["quiz"].get(o, 0) >= pass_mark and o in p["labs_done"]]
        for o in mine:
            ready[o].append(p["name"])
        per_person[p["name"]] = round(len(mine) / len(objectives), 2)
    return {"per_person": per_person,
            "uncovered": [o for o in objectives if not ready[o]],
            "can_operate_without_fde": all(len(v) >= 2 for v in ready.values())}
