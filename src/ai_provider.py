"""Provider-neutral interface for future AI report generation."""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable


AI_REPORT_SCHEMA: dict[str, object] = {
    "name": "trendpilot_ai_report_v0_3",
    "version": "phase3-ai-report-v0.3",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "executive_summary",
            "finding_explanations",
            "cross_issue_insights",
            "cause_hypotheses",
            "recommended_actions",
            "limitations",
        ],
        "properties": {
            "executive_summary": {"type": "string", "minLength": 1},
            "finding_explanations": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["finding_id", "explanation", "why_priority"],
                    "properties": {
                        "finding_id": {"type": "string", "minLength": 1},
                        "explanation": {"type": "string", "minLength": 1},
                        "why_priority": {"type": "string", "minLength": 1},
                    },
                },
            },
            "cross_issue_insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["finding_ids", "insight"],
                    "properties": {
                        "finding_ids": {
                            "type": "array",
                            "minItems": 2,
                            "uniqueItems": True,
                            "items": {"type": "string", "minLength": 1},
                        },
                        "insight": {"type": "string", "minLength": 1},
                    },
                },
            },
            "cause_hypotheses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "finding_id",
                        "cause_id",
                        "hypothesis",
                        "validation_method",
                    ],
                    "properties": {
                        "finding_id": {"type": "string", "minLength": 1},
                        "cause_id": {"type": "string", "minLength": 1},
                        "hypothesis": {"type": "string", "minLength": 1},
                        "validation_method": {"type": "string", "minLength": 1},
                    },
                },
            },
            "recommended_actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "finding_id",
                        "action_id",
                        "action_sequence",
                        "reason",
                    ],
                    "properties": {
                        "finding_id": {"type": "string", "minLength": 1},
                        "action_id": {"type": "string", "minLength": 1},
                        "action_sequence": {"type": "integer", "minimum": 1},
                        "reason": {"type": "string", "minLength": 1},
                    },
                },
            },
            "limitations": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
        },
    },
}


@runtime_checkable
class AIProvider(Protocol):
    """Return an untrusted JSON string for the supplied report contract."""

    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str: ...


__all__ = ["AIProvider", "AI_REPORT_SCHEMA"]
