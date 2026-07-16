import json
from copy import deepcopy
from datetime import date

import numpy as np
import pandas as pd

from src.ai_report_payload import KPI_WHITELIST, SCHEMA_VERSION, build_ai_report_payload
from src.diagnosis_models import (
    DiagnosisContext,
    DiagnosticFinding,
    Evidence,
    FindingScope,
)


def make_context() -> DiagnosisContext:
    hidden_dataframe = pd.DataFrame(
        {"raw_csv_row": ["不得进入 payload"], "inventory": [999]}
    )
    return DiagnosisContext(
        source_name="示例数据",
        start_date=date(2026, 1, 2),
        end_date=date(2026, 1, 31),
        previous_start_date=date(2025, 12, 3),
        previous_end_date=date(2026, 1, 1),
        categories=("外套",),
        product_ids=("P001",),
        current_kpis={
            "sales_amount": np.float64(900.0),
            "visitors": np.int64(80),
            "payment_conversion_rate": np.float64(0.1),
            "ad_spend": np.float64(120.0),
            "roas": np.float64(7.5),
            "gross_margin": np.float64(0.4),
            "refund_rate": np.float64(0.02),
            "current_inventory": np.int64(30),
            "orders": np.int64(8),
        },
        previous_kpis={
            "sales_amount": np.float64(1000.0),
            "visitors": np.int64(100),
            "payment_conversion_rate": np.float64(0.12),
            "ad_spend": np.float64(100.0),
            "roas": np.float64(10.0),
            "gross_margin": np.float64(0.45),
            "refund_rate": np.float64(0.01),
            "current_inventory": np.int64(40),
            "orders": np.int64(12),
        },
        period_comparison={
            "sales_amount": np.float64(-0.1),
            "visitors": np.float64(-0.2),
            "payment_conversion_rate": np.float64(-0.02),
            "ad_spend": np.float64(0.2),
            "roas": np.float64(-0.25),
            "gross_margin": np.float64(-0.05),
            "refund_rate": np.float64(0.01),
            "current_inventory": np.float64(-0.25),
        },
        daily_trend=hidden_dataframe.copy(),
        current_product_summary=hidden_dataframe.copy(),
        previous_product_summary=hidden_dataframe.copy(),
        current_category_summary=hidden_dataframe.copy(),
        previous_category_summary=hidden_dataframe.copy(),
        inventory_snapshot=hidden_dataframe.copy(),
        latest_day_comparison=hidden_dataframe.copy(),
    )


def make_findings() -> tuple[DiagnosticFinding, ...]:
    return (
        DiagnosticFinding(
            finding_id="finding-sales",
            rule_id="R001_SALES_DECLINE",
            dimension="sales",
            scope=FindingScope("overall", None, "全店"),
            title="销售额下降",
            evidence=(
                Evidence(
                    metric_key="sales_amount",
                    current_value=np.float64(900.0),
                    baseline_value=np.float64(1000.0),
                    change_value=np.float64(-0.1),
                    change_type="relative",
                    unit="currency",
                ),
            ),
            priority_score=88,
            priority="high",
            cause_candidate_ids=("C001_TRAFFIC_DECLINE",),
            action_candidate_ids=("A001_REVIEW_SALES_FUNNEL",),
        ),
        DiagnosticFinding(
            finding_id="finding-visitors",
            rule_id="R002_VISITOR_DECLINE",
            dimension="traffic",
            scope=FindingScope("overall", None, "全店"),
            title="访客下降",
            evidence=(
                Evidence(
                    metric_key="visitors",
                    current_value=np.int64(80),
                    baseline_value=np.int64(100),
                    change_value=np.float64(-0.2),
                    change_type="relative",
                    unit="count",
                ),
            ),
            priority_score=70,
            priority="medium",
            cause_candidate_ids=("C003_CHANNEL_TRAFFIC_WEAKNESS",),
            action_candidate_ids=("A002_RECOVER_QUALITY_TRAFFIC",),
        ),
    )


def test_payload_contains_only_whitelisted_analysis_inputs() -> None:
    payload = build_ai_report_payload(make_context(), make_findings())

    assert set(payload) == {
        "schema_version",
        "analysis_scope",
        "kpi_summary",
        "findings",
    }
    assert SCHEMA_VERSION == "phase3-ai-report-v0.3"
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["analysis_scope"] == {
        "source_name": "示例数据",
        "start_date": "2026-01-02",
        "end_date": "2026-01-31",
        "categories": ["外套"],
        "product_ids": ["P001"],
    }
    assert [item["metric_key"] for item in payload["kpi_summary"]] == list(
        KPI_WHITELIST
    )
    assert set(payload["findings"][0]) == {
        "finding_id",
        "rule_id",
        "dimension",
        "scope",
        "title",
        "priority",
        "evidence",
        "cause_candidates",
        "action_candidates",
    }


def test_payload_uses_only_candidates_allowed_by_each_finding() -> None:
    payload = build_ai_report_payload(make_context(), make_findings())
    sales_finding = payload["findings"][0]

    assert [item["cause_id"] for item in sales_finding["cause_candidates"]] == [
        "C001_TRAFFIC_DECLINE"
    ]
    assert [item["action_id"] for item in sales_finding["action_candidates"]] == [
        "A001_REVIEW_SALES_FUNNEL"
    ]
    assert sales_finding["action_candidates"][0]["observe_metric"] == "sales_amount"


def test_payload_is_strictly_json_serializable_and_normalizes_numpy_values() -> None:
    payload = build_ai_report_payload(make_context(), make_findings())

    serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False)

    assert "示例数据" in serialized
    assert type(payload["kpi_summary"][0]["current_value"]) in {int, float}
    assert type(payload["findings"][1]["evidence"][0]["current_value"]) is int


def test_payload_normalizes_pandas_missing_values_to_json_null() -> None:
    context = make_context()
    context.period_comparison["sales_amount"] = pd.NA

    payload = build_ai_report_payload(context, make_findings())

    assert payload["kpi_summary"][0]["change_value"] is None
    json.dumps(payload, ensure_ascii=False, allow_nan=False)


def test_payload_does_not_serialize_context_dataframes_or_forbidden_fields() -> None:
    payload = build_ai_report_payload(make_context(), make_findings())
    serialized = json.dumps(payload, ensure_ascii=False)

    for forbidden in (
        "raw_csv_row",
        "daily_trend",
        "current_product_summary",
        "inventory_snapshot",
        "latest_day_comparison",
        "priority_score",
        "session_state",
    ):
        assert forbidden not in serialized.lower()


def test_payload_builder_does_not_modify_findings() -> None:
    findings = make_findings()
    original = deepcopy(findings)

    build_ai_report_payload(make_context(), findings)

    assert findings == original
