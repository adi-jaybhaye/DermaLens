"""
Service for retrieving curated skin concern knowledge.
"""

from typing import Optional

from app.data.skin_concerns_knowledge import (
    SKIN_CONCERNS_KNOWLEDGE,
    SAFETY_DISCLAIMER,
)


def get_all_concerns() -> list[dict]:
    """Return all curated concern entries."""
    return list(SKIN_CONCERNS_KNOWLEDGE.values())


def get_concern(concept: str) -> Optional[dict]:
    """Look up a single concern by its model class name."""
    return SKIN_CONCERNS_KNOWLEDGE.get(concept)


def get_concern_names() -> list[str]:
    """Return all supported concern class names."""
    return list(SKIN_CONCERNS_KNOWLEDGE.keys())


def get_safety_disclaimer() -> dict:
    """Return the standard safety disclaimer."""
    return SAFETY_DISCLAIMER


def build_why_identified(
    region_name: str,
    predicted_concern: str,
    confidence: float,
) -> str:
    """Generate a human-readable explanation of why the AI flagged a
    concern for a specific facial region.

    This is NOT a medical explanation — it describes the model's
    behaviour.
    """
    confidence_pct = round(confidence * 100, 1)

    if confidence >= 0.75:
        qualifier = "patterns consistent with"
    elif confidence >= 0.50:
        qualifier = "patterns that may be associated with"
    else:
        qualifier = "weak patterns that could possibly relate to"

    knowledge = get_concern(predicted_concern)
    display_name = (
        knowledge["display_name"]
        if knowledge
        else predicted_concern
    )

    return (
        f"The model detected {qualifier} {display_name} in the "
        f"{region_name.replace('_', ' ')} region "
        f"(confidence: {confidence_pct}%). "
        f"This is based on visual pattern recognition and does not "
        f"constitute a medical diagnosis."
    )
