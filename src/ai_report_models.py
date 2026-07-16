"""Immutable data structures for validated AI operating reports."""

from dataclasses import dataclass
from typing import Literal


AIReportGenerationStatus = Literal[
    "success",
    "unavailable",
    "provider_error",
    "invalid_json",
    "validation_error",
]


@dataclass(frozen=True, slots=True)
class FindingExplanation:
    finding_id: str
    explanation: str
    why_priority: str


@dataclass(frozen=True, slots=True)
class CrossIssueInsight:
    finding_ids: tuple[str, ...]
    insight: str


@dataclass(frozen=True, slots=True)
class CauseHypothesis:
    finding_id: str
    cause_id: str
    hypothesis: str
    validation_method: str


@dataclass(frozen=True, slots=True)
class RecommendedAction:
    finding_id: str
    action_id: str
    action_sequence: int
    reason: str


@dataclass(frozen=True, slots=True)
class AIReport:
    executive_summary: str
    finding_explanations: tuple[FindingExplanation, ...]
    cross_issue_insights: tuple[CrossIssueInsight, ...]
    cause_hypotheses: tuple[CauseHypothesis, ...]
    recommended_actions: tuple[RecommendedAction, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AIReportGenerationResult:
    status: AIReportGenerationStatus
    report: AIReport | None = None
    message: str = ""


__all__ = [
    "AIReport",
    "AIReportGenerationResult",
    "AIReportGenerationStatus",
    "CauseHypothesis",
    "CrossIssueInsight",
    "FindingExplanation",
    "RecommendedAction",
]
