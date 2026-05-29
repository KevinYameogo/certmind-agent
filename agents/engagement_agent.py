"""Engagement Agent placeholder."""


def recommend_engagement_window(learner_id: str) -> dict:
    """Return a starter engagement recommendation."""
    return {
        "learner_id": learner_id,
        "recommended_window": None,
        "reason": "Work signals not loaded yet.",
    }
