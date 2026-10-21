"""Steering-committee update generated from the plan, gates and measurements."""


def render_steering(eng: dict, rag: dict, forecast: dict, reviews: list[dict], security: dict, funnel: dict,
                    impact: dict, decision: dict) -> str:
    """Markdown for the Friday update: title, then `## Decisions needed` (one bullet per blocker, then condition, or
    `- none`), `## Overall`, `## Changed since last week` (with `### Workstreams` and `### Partner deliverables`),
    `## Adoption and impact`, `## Risks and asks`, `## Next milestone`. See the README for each section's lines."""
    raise NotImplementedError
