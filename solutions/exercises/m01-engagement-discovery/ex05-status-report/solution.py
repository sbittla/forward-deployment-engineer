from datetime import date, timedelta


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _overdue(t, today):
    return t["status"] != "done" and _d(t["due"]) < today


def overall_status(tasks: list[dict], today: date) -> str:
    overdue = [t for t in tasks if _overdue(t, today)]
    blocked = [t for t in tasks if t["status"] == "blocked"]
    if any(_d(t["due"]) <= today + timedelta(days=7) for t in blocked) or len(overdue) >= 3:
        return "red"
    if overdue or blocked:
        return "amber"
    return "green"


def _section(title, items):
    return [f"## {title}"] + (items or ["- none"]) + [""]


def render(tasks: list[dict], today: date, project: str) -> str:
    week_ago = today - timedelta(days=7)
    done = [f"- {t['title']} ({t['owner']})" for t in tasks
            if t["status"] == "done" and t.get("completed") and week_ago <= _d(t["completed"]) <= today]
    upcoming = sorted((t for t in tasks if t["status"] != "done" and today <= _d(t["due"]) <= today + timedelta(days=14)),
                      key=lambda t: t["due"])
    nxt = [f"- {t['due']} {t['title']} ({t['owner']})" for t in upcoming]
    risks = [f"- {t['title']} — {'blocked' if t['status'] == 'blocked' else 'overdue'} (owner: {t['owner']}, due {t['due']})"
             for t in tasks if t["status"] == "blocked" or _overdue(t, today)]
    asks = [f"- {t['ask']}" for t in tasks if t.get("ask")]
    lines = [f"# {project} — status {today.isoformat()}", "", f"**Overall: {overall_status(tasks, today).upper()}**", ""]
    lines += _section("Done this week", done) + _section("Next up", nxt)
    lines += _section("Risks & blockers", risks) + _section("Asks", asks)
    return "\n".join(lines)
