"""Validate AI report structure and deterministic ID references."""

import json
from collections.abc import Mapping, Sequence
from typing import Any

from src.ai_report_models import (
    AIReport,
    CauseHypothesis,
    CrossIssueInsight,
    FindingExplanation,
    RecommendedAction,
)
from src.diagnosis_models import DiagnosticFinding


_TOP_LEVEL_FIELDS = {
    "executive_summary",
    "finding_explanations",
    "cross_issue_insights",
    "cause_hypotheses",
    "recommended_actions",
    "limitations",
}


class AIReportValidationError(ValueError):
    """Raised when an AI report violates the frozen report contract."""


def _require_object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AIReportValidationError(f"{path} 必须是对象。")
    return value


def _require_exact_fields(
    value: Mapping[str, Any], expected: set[str], path: str
) -> None:
    actual = set(value)
    missing = expected - actual
    if missing:
        raise AIReportValidationError(
            f"{path} 缺少字段：{', '.join(sorted(missing))}。"
        )
    extra = actual - expected
    if extra:
        raise AIReportValidationError(
            f"{path} 包含未允许字段：{', '.join(sorted(extra))}。"
        )


def _require_array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise AIReportValidationError(f"{path} 必须是数组。")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise AIReportValidationError(f"{path} 必须是字符串。")
    if not value.strip():
        raise AIReportValidationError(f"{path} 不能为空字符串。")
    return value


def _require_valid_finding_id(
    value: Any,
    path: str,
    findings_by_id: Mapping[str, DiagnosticFinding],
) -> str:
    finding_id = _require_string(value, path)
    if finding_id not in findings_by_id:
        raise AIReportValidationError(f"{path} finding_id 无效：{finding_id}。")
    return finding_id


def _load_report_data(report_data: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(report_data, str):
        try:
            parsed = json.loads(report_data)
        except json.JSONDecodeError as exc:
            raise AIReportValidationError("AI 报告不是有效 JSON。") from exc
    else:
        parsed = report_data
    return _require_object(parsed, "AIReport")


def validate_ai_report(
    report_data: str | Mapping[str, Any],
    findings: Sequence[DiagnosticFinding],
) -> AIReport:
    """Return a validated report or reject the complete untrusted response."""
    data = _load_report_data(report_data)
    _require_exact_fields(data, _TOP_LEVEL_FIELDS, "AIReport")
    findings_by_id = {finding.finding_id: finding for finding in findings}

    executive_summary = _require_string(
        data["executive_summary"], "executive_summary"
    )

    explanation_rows = _require_array(
        data["finding_explanations"], "finding_explanations"
    )
    if not explanation_rows:
        raise AIReportValidationError("finding_explanations 不能为空数组。")
    explanations = []
    for index, raw_item in enumerate(explanation_rows):
        path = f"finding_explanations[{index}]"
        item = _require_object(raw_item, path)
        _require_exact_fields(
            item, {"finding_id", "explanation", "why_priority"}, path
        )
        explanations.append(
            FindingExplanation(
                finding_id=_require_valid_finding_id(
                    item["finding_id"], f"{path}.finding_id", findings_by_id
                ),
                explanation=_require_string(
                    item["explanation"], f"{path}.explanation"
                ),
                why_priority=_require_string(
                    item["why_priority"], f"{path}.why_priority"
                ),
            )
        )

    insight_rows = _require_array(
        data["cross_issue_insights"], "cross_issue_insights"
    )
    insights = []
    for index, raw_item in enumerate(insight_rows):
        path = f"cross_issue_insights[{index}]"
        item = _require_object(raw_item, path)
        _require_exact_fields(item, {"finding_ids", "insight"}, path)
        raw_finding_ids = _require_array(
            item["finding_ids"], f"{path}.finding_ids"
        )
        finding_ids = tuple(
            _require_valid_finding_id(
                finding_id, f"{path}.finding_ids[{item_index}]", findings_by_id
            )
            for item_index, finding_id in enumerate(raw_finding_ids)
        )
        if len(finding_ids) < 2 or len(set(finding_ids)) != len(finding_ids):
            raise AIReportValidationError(
                f"{path}.finding_ids 必须引用至少两个不同的有效 Finding。"
            )
        insights.append(
            CrossIssueInsight(
                finding_ids=finding_ids,
                insight=_require_string(item["insight"], f"{path}.insight"),
            )
        )

    hypothesis_rows = _require_array(
        data["cause_hypotheses"], "cause_hypotheses"
    )
    hypotheses = []
    for index, raw_item in enumerate(hypothesis_rows):
        path = f"cause_hypotheses[{index}]"
        item = _require_object(raw_item, path)
        _require_exact_fields(
            item,
            {"finding_id", "cause_id", "hypothesis", "validation_method"},
            path,
        )
        finding_id = _require_valid_finding_id(
            item["finding_id"], f"{path}.finding_id", findings_by_id
        )
        cause_id = _require_string(item["cause_id"], f"{path}.cause_id")
        if cause_id not in findings_by_id[finding_id].cause_candidate_ids:
            raise AIReportValidationError(
                f"{path}.cause_id 不属于对应 Finding 的候选原因：{cause_id}。"
            )
        hypotheses.append(
            CauseHypothesis(
                finding_id=finding_id,
                cause_id=cause_id,
                hypothesis=_require_string(
                    item["hypothesis"], f"{path}.hypothesis"
                ),
                validation_method=_require_string(
                    item["validation_method"], f"{path}.validation_method"
                ),
            )
        )

    action_rows = _require_array(
        data["recommended_actions"], "recommended_actions"
    )
    actions = []
    action_sequences = []
    for index, raw_item in enumerate(action_rows):
        path = f"recommended_actions[{index}]"
        item = _require_object(raw_item, path)
        _require_exact_fields(
            item, {"finding_id", "action_id", "action_sequence", "reason"}, path
        )
        finding_id = _require_valid_finding_id(
            item["finding_id"], f"{path}.finding_id", findings_by_id
        )
        action_id = _require_string(item["action_id"], f"{path}.action_id")
        if action_id not in findings_by_id[finding_id].action_candidate_ids:
            raise AIReportValidationError(
                f"{path}.action_id 不属于对应 Finding 的候选行动：{action_id}。"
            )
        action_sequence = item["action_sequence"]
        if (
            isinstance(action_sequence, bool)
            or not isinstance(action_sequence, int)
            or action_sequence < 1
        ):
            raise AIReportValidationError(
                f"{path}.action_sequence 必须是从1开始的正整数。"
            )
        action_sequences.append(action_sequence)
        actions.append(
            RecommendedAction(
                finding_id=finding_id,
                action_id=action_id,
                action_sequence=action_sequence,
                reason=_require_string(item["reason"], f"{path}.reason"),
            )
        )
    if sorted(action_sequences) != list(range(1, len(action_sequences) + 1)):
        raise AIReportValidationError(
            "recommended_actions.action_sequence 必须从1开始连续编号且不得重复。"
        )

    limitation_rows = _require_array(data["limitations"], "limitations")
    limitations = tuple(
        _require_string(item, f"limitations[{index}]")
        for index, item in enumerate(limitation_rows)
    )

    return AIReport(
        executive_summary=executive_summary,
        finding_explanations=tuple(explanations),
        cross_issue_insights=tuple(insights),
        cause_hypotheses=tuple(hypotheses),
        recommended_actions=tuple(actions),
        limitations=limitations,
    )


__all__ = ["AIReportValidationError", "validate_ai_report"]
