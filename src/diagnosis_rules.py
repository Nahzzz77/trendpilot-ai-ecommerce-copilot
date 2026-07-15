"""MVP deterministic operating diagnosis rules."""

from dataclasses import dataclass

import pandas as pd

from src.diagnosis_catalog import get_action_candidate_ids, get_cause_candidate_ids
from src.diagnosis_models import DiagnosticFinding, DiagnosisContext, Evidence, FindingScope
from src.diagnosis_scoring import calculate_priority


EPSILON = 1e-12


@dataclass(frozen=True, slots=True)
class DiagnosisThresholds:
    sales_decline_relative: float = 0.05
    visitor_decline_relative: float = 0.05
    conversion_decline_points: float = 0.003
    roas_decline_relative: float = 0.10
    ad_spend_increase_relative: float = 0.10
    gross_margin_decline_points: float = 0.01
    refund_rate_increase_points: float = 0.005
    refund_min_units_sold: int = 50
    inventory_low_days: float = 21.0
    inventory_high_days: float = 60.0
    key_product_previous_sales_share: float = 0.05
    key_product_sales_decline_relative: float = 0.10


DEFAULT_THRESHOLDS = DiagnosisThresholds()


def _declined_at_least(change: float | None, threshold: float) -> bool:
    return change is not None and change < 0 and -change + EPSILON >= threshold


def _increased_at_least(change: float | None, threshold: float) -> bool:
    return change is not None and change > 0 and change + EPSILON >= threshold


def _magnitude(change: float, threshold: float) -> float:
    return min(1.0, abs(change) / (threshold * 3))


def _overall_finding(
    context: DiagnosisContext,
    *,
    metric_key: str,
    change: float,
    threshold: float,
    rule_id: str,
    dimension: str,
    title: str,
    change_type: str,
    unit: str,
) -> DiagnosticFinding:
    score, priority = calculate_priority(
        impact=1.0,
        magnitude=_magnitude(change, threshold),
        completeness=1.0,
    )
    return DiagnosticFinding(
        finding_id=f"{rule_id.lower()}-overall",
        rule_id=rule_id,
        dimension=dimension,
        scope=FindingScope("overall", None, "全店"),
        title=title,
        evidence=(
            Evidence(
                metric_key=metric_key,
                current_value=context.current_kpis.get(metric_key),
                baseline_value=context.previous_kpis.get(metric_key),
                change_value=change,
                change_type=change_type,
                unit=unit,
            ),
        ),
        priority_score=score,
        priority=priority,
        cause_candidate_ids=get_cause_candidate_ids(rule_id),
        action_candidate_ids=get_action_candidate_ids(rule_id),
    )


def detect_sales_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("sales_amount")
    if not _declined_at_least(change, thresholds.sales_decline_relative):
        return []
    return [
        _overall_finding(
            context,
            metric_key="sales_amount",
            change=change,
            threshold=thresholds.sales_decline_relative,
            rule_id="R001_SALES_DECLINE",
            dimension="sales",
            title="销售额下降",
            change_type="relative",
            unit="currency",
        )
    ]


def detect_visitor_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("visitors")
    if not _declined_at_least(change, thresholds.visitor_decline_relative):
        return []
    return [
        _overall_finding(
            context,
            metric_key="visitors",
            change=change,
            threshold=thresholds.visitor_decline_relative,
            rule_id="R002_VISITOR_DECLINE",
            dimension="traffic",
            title="访客数下降",
            change_type="relative",
            unit="count",
        )
    ]


def detect_conversion_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("payment_conversion_rate")
    if not _declined_at_least(change, thresholds.conversion_decline_points):
        return []
    return [
        _overall_finding(
            context,
            metric_key="payment_conversion_rate",
            change=change,
            threshold=thresholds.conversion_decline_points,
            rule_id="R003_CONVERSION_DECLINE",
            dimension="conversion",
            title="支付转化率下降",
            change_type="percentage_point",
            unit="rate",
        )
    ]


def detect_roas_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("roas")
    if not _declined_at_least(change, thresholds.roas_decline_relative):
        return []
    return [
        _overall_finding(
            context,
            metric_key="roas",
            change=change,
            threshold=thresholds.roas_decline_relative,
            rule_id="R004_ROAS_DECLINE",
            dimension="advertising",
            title="ROAS 下降",
            change_type="relative",
            unit="ratio",
        )
    ]


def detect_ad_spend_growth_without_sales_growth(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    spend_change = context.period_comparison.get("ad_spend")
    sales_change = context.period_comparison.get("sales_amount")
    if not _increased_at_least(spend_change, thresholds.ad_spend_increase_relative):
        return []
    if sales_change is None or sales_change > 0:
        return []
    score, priority = calculate_priority(
        impact=1.0,
        magnitude=_magnitude(spend_change, thresholds.ad_spend_increase_relative),
        completeness=1.0,
    )
    return [
        DiagnosticFinding(
            finding_id="r005_ad_spend_up_without_sales_growth-overall",
            rule_id="R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH",
            dimension="advertising",
            scope=FindingScope("overall", None, "全店"),
            title="广告投入增加但销售未增长",
            evidence=(
                Evidence(
                    "ad_spend",
                    context.current_kpis.get("ad_spend"),
                    context.previous_kpis.get("ad_spend"),
                    spend_change,
                    "relative",
                    "currency",
                ),
                Evidence(
                    "sales_amount",
                    context.current_kpis.get("sales_amount"),
                    context.previous_kpis.get("sales_amount"),
                    sales_change,
                    "relative",
                    "currency",
                ),
            ),
            priority_score=score,
            priority=priority,
            cause_candidate_ids=get_cause_candidate_ids(
                "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH"
            ),
            action_candidate_ids=get_action_candidate_ids(
                "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH"
            ),
        )
    ]


def detect_gross_margin_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("gross_margin")
    if not _declined_at_least(change, thresholds.gross_margin_decline_points):
        return []
    return [
        _overall_finding(
            context,
            metric_key="gross_margin",
            change=change,
            threshold=thresholds.gross_margin_decline_points,
            rule_id="R006_GROSS_MARGIN_DECLINE",
            dimension="profitability",
            title="毛利率下降",
            change_type="percentage_point",
            unit="rate",
        )
    ]


def detect_refund_rate_increase(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    change = context.period_comparison.get("refund_rate")
    units_sold = int(context.current_kpis.get("units_sold", 0))
    if units_sold < thresholds.refund_min_units_sold:
        return []
    if not _increased_at_least(change, thresholds.refund_rate_increase_points):
        return []
    return [
        _overall_finding(
            context,
            metric_key="refund_rate",
            change=change,
            threshold=thresholds.refund_rate_increase_points,
            rule_id="R007_REFUND_RATE_INCREASE",
            dimension="after_sales",
            title="退款率上升",
            change_type="percentage_point",
            unit="rate",
        )
    ]


def _product_sales_share(context: DiagnosisContext, product_id: str) -> float:
    summary = context.current_product_summary
    if summary.empty or "sales_amount" not in summary.columns:
        return 0.0
    total = float(summary["sales_amount"].sum())
    if total == 0:
        return 0.0
    product_sales = float(
        summary.loc[summary["product_id"] == product_id, "sales_amount"].sum()
    )
    return product_sales / total


def detect_inventory_days_anomaly(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    inventory = context.inventory_snapshot
    if inventory.empty or "estimated_days_left" not in inventory.columns:
        return []

    findings: list[DiagnosticFinding] = []
    for row in inventory.itertuples(index=False):
        days_left = row.estimated_days_left
        if pd.isna(days_left):
            continue
        if days_left <= thresholds.inventory_low_days:
            rule_id = "R008_INVENTORY_DAYS_LOW"
            title = f"{row.product_name}库存可售天数偏低"
            threshold = thresholds.inventory_low_days
            distance = max((threshold - float(days_left)) / threshold, 1 / 3)
        elif days_left >= thresholds.inventory_high_days:
            rule_id = "R009_INVENTORY_DAYS_HIGH"
            title = f"{row.product_name}库存可售天数偏高"
            threshold = thresholds.inventory_high_days
            distance = max((float(days_left) - threshold) / threshold, 1 / 3)
        else:
            continue
        score, priority = calculate_priority(
            impact=_product_sales_share(context, row.product_id),
            magnitude=min(1.0, distance),
            completeness=1.0,
        )
        findings.append(
            DiagnosticFinding(
                finding_id=f"{rule_id.lower()}-{row.product_id}",
                rule_id=rule_id,
                dimension="inventory",
                scope=FindingScope("product", row.product_id, row.product_name),
                title=title,
                evidence=(
                    Evidence(
                        "estimated_days_left",
                        float(days_left),
                        threshold,
                        float(days_left) - threshold,
                        "absolute",
                        "days",
                    ),
                ),
                priority_score=score,
                priority=priority,
                cause_candidate_ids=get_cause_candidate_ids(rule_id),
                action_candidate_ids=get_action_candidate_ids(rule_id),
            )
        )
    return findings


def detect_key_product_sales_decline(
    context: DiagnosisContext, thresholds: DiagnosisThresholds = DEFAULT_THRESHOLDS
) -> list[DiagnosticFinding]:
    previous = context.previous_product_summary
    if previous.empty or "sales_amount" not in previous.columns:
        return []
    previous_total = float(previous["sales_amount"].sum())
    if previous_total == 0:
        return []

    current = context.current_product_summary
    current_sales = (
        current.set_index("product_id")["sales_amount"].to_dict()
        if not current.empty and "sales_amount" in current.columns
        else {}
    )
    findings: list[DiagnosticFinding] = []
    for row in previous.itertuples(index=False):
        previous_sales = float(row.sales_amount)
        if previous_sales == 0:
            continue
        previous_share = previous_sales / previous_total
        if previous_share + EPSILON < thresholds.key_product_previous_sales_share:
            continue
        product_current_sales = float(current_sales.get(row.product_id, 0.0))
        sales_change = (product_current_sales - previous_sales) / previous_sales
        if not _declined_at_least(
            sales_change, thresholds.key_product_sales_decline_relative
        ):
            continue
        score, priority = calculate_priority(
            impact=min(1.0, previous_share),
            magnitude=_magnitude(
                sales_change, thresholds.key_product_sales_decline_relative
            ),
            completeness=1.0,
        )
        findings.append(
            DiagnosticFinding(
                finding_id=f"r010_key_product_sales_decline-{row.product_id}",
                rule_id="R010_KEY_PRODUCT_SALES_DECLINE",
                dimension="product",
                scope=FindingScope("product", row.product_id, row.product_name),
                title=f"重点商品{row.product_name}销售下降",
                evidence=(
                    Evidence(
                        "product_sales_amount",
                        product_current_sales,
                        previous_sales,
                        sales_change,
                        "relative",
                        "currency",
                    ),
                    Evidence(
                        "previous_sales_share",
                        previous_share,
                        thresholds.key_product_previous_sales_share,
                        previous_share
                        - thresholds.key_product_previous_sales_share,
                        "absolute",
                        "rate",
                    ),
                ),
                priority_score=score,
                priority=priority,
                cause_candidate_ids=get_cause_candidate_ids(
                    "R010_KEY_PRODUCT_SALES_DECLINE"
                ),
                action_candidate_ids=get_action_candidate_ids(
                    "R010_KEY_PRODUCT_SALES_DECLINE"
                ),
            )
        )
    return findings
