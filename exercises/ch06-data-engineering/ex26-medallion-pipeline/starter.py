COUNTRY_ALIASES = {"usa": "US", "united states": "US", "u.s.": "US", "uk": "GB", "united kingdom": "GB",
                   "deutschland": "DE", "germany": "DE", "india": "IN"}


def bronze(lines: list[str], source: str, ingested_at: str) -> list[dict]:
    raise NotImplementedError


def silver(bronze_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    raise NotImplementedError


def gold(events: list[dict]) -> dict:
    raise NotImplementedError
