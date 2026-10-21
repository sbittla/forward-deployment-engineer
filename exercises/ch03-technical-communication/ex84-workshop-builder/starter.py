def build_agenda(objectives: list[dict], start: str = "09:00", total_minutes: int = 360) -> list[tuple]:
    raise NotImplementedError


def lab_steps_valid(steps: list[dict]) -> list[int]:
    raise NotImplementedError


def readiness(participants: list[dict], objectives: list[str], pass_mark: float = 0.8) -> dict:
    raise NotImplementedError
