"""Critic / Verifier agent placeholder."""


def verify_response(response: dict) -> dict:
    """Return a starter verification result."""
    return {
        "approved": True,
        "issues": [],
        "response": response,
    }
