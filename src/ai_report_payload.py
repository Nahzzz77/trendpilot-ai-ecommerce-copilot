"""Build the strict, JSON-safe input allowed for future AI report generation."""

import math
from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd

from src.diagnosis_catalog import ACTION_CATALOG, CAUSE_CATALOG
from src.diagnosis_models import DiagnosticFinding, DiagnosisContext, Evidence


SCHEMA_VERSION = "phase3-ai-report-v0.3"

KPI_WHITELIST = (
    "sales_amount",
    "visitors",
    "payment_conversion_rate",
    "ad_spend",
    "roas",
    "gross_margin",
    "refund_rate",
    "current_inventory",
)

_KPI_METADATA = {
    "sales_amount": ("relative", "currency"),
    "visitors": ("relative", "count"),
    "payment_conversion_rate": ("percentage_point", "percentage"),
    "ad_spend": ("relative", "currency"),
    "roas": ("relative", "ratio"),
    "gross_margin": ("percentage_point", "percentage"),
    "refund_rate": ("percentage_point", "percentage"),
    "current_inventory": ("relative", "count"),
}

_CAUSE_BY_ID = {entry.cause_id: entry for entry in CAUSE_CATALOG}
_ACTION_BY_ID = {entry.action_id: entry for entry in ACTION_CATALOG}


class AIReportPayloadError(ValueError):
    """Raised when a finding references a catalog item that cannot be serialized."""


def _json_scalar(value: Any) -> str | int | float | bool | None:
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, np.generic):
        return _json_scalar(value.item())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    raise AIReportPayloadError(f"无法转换为 JSON 标量：{type(value).__name__}")


def _serialize_evidence(evidence: Evidence) -> dict[str, object]:
    return {
        "metric_key": evidence.metric_key,
        "current_value": _json_scalar(evidence.current_value),
        "baseline_value": _json_scalar(evidence.baseline_value),
        "change_value": _json_scalar(evidence.change_value),
        "change_type": evidence.change_type,
        "unit": evidence.unit,
    }


def _serialize_cause_candidates(finding: DiagnosticFinding) -> list[dict[str, str]]:
    candidates = []
    for cause_id in finding.cause_candidate_ids:
        entry = _CAUSE_BY_ID.get(cause_id)
        if entry is None:
            raise AIReportPayloadError(f"Finding 引用了未知 cause_id：{cause_id}")
        candidates.append(
            {
                "cause_id": entry.cause_id,
                "cause_name": entry.cause_name,
                "description": entry.description,
            }
        )
    return candidates


def _serialize_action_candidates(finding: DiagnosticFinding) -> list[dict[str, str]]:
    candidates = []
    for action_id in finding.action_candidate_ids:
        entry = _ACTION_BY_ID.get(action_id)
        if entry is None:
            raise AIReportPayloadError(f"Finding 引用了未知 action_id：{action_id}")
        candidates.append(
            {
                "action_id": entry.action_id,
                "action_name": entry.action_name,
                "owner": entry.owner,
                "suggested_period": entry.suggested_period,
                "observe_metric": entry.observe_metric,
            }
        )
    return candidates


def _serialize_finding(finding: DiagnosticFinding) -> dict[str, object]:
    return {
        "finding_id": finding.finding_id,
        "rule_id": finding.rule_id,
        "dimension": finding.dimension,
        "scope": {
            "scope_type": finding.scope.scope_type,
            "scope_id": finding.scope.scope_id,
            "scope_name": finding.scope.scope_name,
        },
        "title": finding.title,
        "priority": finding.priority,
        "evidence": [_serialize_evidence(item) for item in finding.evidence],
        "cause_candidates": _serialize_cause_candidates(finding),
        "action_candidates": _serialize_action_candidates(finding),
    }


def build_ai_report_payload(
    context: DiagnosisContext,
    findings: Sequence[DiagnosticFinding],
) -> dict[str, object]:
    """Return only the frozen, whitelisted inputs allowed for AI reporting."""
    kpi_summary = []
    for metric_key in KPI_WHITELIST:
        change_type, unit = _KPI_METADATA[metric_key]
        kpi_summary.append(
            {
                "metric_key": metric_key,
                "current_value": _json_scalar(context.current_kpis.get(metric_key)),
                "baseline_value": _json_scalar(context.previous_kpis.get(metric_key)),
                "change_value": _json_scalar(
                    context.period_comparison.get(metric_key)
                ),
                "change_type": change_type,
                "unit": unit,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_scope": {
            "source_name": context.source_name,
            "start_date": context.start_date.isoformat(),
            "end_date": context.end_date.isoformat(),
            "categories": list(context.categories),
            "product_ids": list(context.product_ids),
        },
        "kpi_summary": kpi_summary,
        "findings": [_serialize_finding(finding) for finding in findings],
    }


__all__ = [
    "AIReportPayloadError",
    "KPI_WHITELIST",
    "SCHEMA_VERSION",
    "build_ai_report_payload",
]
