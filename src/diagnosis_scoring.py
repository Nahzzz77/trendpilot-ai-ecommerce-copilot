"""Deterministic priority scoring for diagnostic findings."""

from src.diagnosis_models import Priority


def calculate_priority(
    impact: float, magnitude: float, completeness: float
) -> tuple[int, Priority]:
    """Score impact, change magnitude, and data completeness on a 0-100 scale."""
    normalized_impact = min(1.0, max(0.0, impact))
    normalized_magnitude = min(1.0, max(0.0, magnitude))
    normalized_completeness = min(1.0, max(0.0, completeness))
    score = round(
        normalized_impact * 35
        + normalized_magnitude * 45
        + normalized_completeness * 20
    )
    if score >= 80:
        priority: Priority = "high"
    elif score >= 50:
        priority = "medium"
    else:
        priority = "low"
    return score, priority
