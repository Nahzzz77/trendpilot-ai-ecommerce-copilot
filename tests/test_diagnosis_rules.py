from datetime import date

import pandas as pd
import pytest

from src.diagnosis_models import DiagnosisContext
from src.diagnosis_rules import (
    DEFAULT_THRESHOLDS,
    detect_ad_spend_growth_without_sales_growth,
    detect_conversion_decline,
    detect_gross_margin_decline,
    detect_inventory_days_anomaly,
    detect_key_product_sales_decline,
    detect_refund_rate_increase,
    detect_roas_decline,
    detect_sales_decline,
    detect_visitor_decline,
)


def make_context(
    *,
    current_kpis: dict[str, float | int] | None = None,
    previous_kpis: dict[str, float | int] | None = None,
    comparison: dict[str, float | None] | None = None,
    current_products: pd.DataFrame | None = None,
    previous_products: pd.DataFrame | None = None,
    inventory: pd.DataFrame | None = None,
) -> DiagnosisContext:
    empty = pd.DataFrame()
    return DiagnosisContext(
        source_name="test",
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
        previous_start_date=date(2026, 1, 4),
        previous_end_date=date(2026, 1, 31),
        categories=(),
        product_ids=(),
        current_kpis={"units_sold": 100, **(current_kpis or {})},
        previous_kpis=previous_kpis or {},
        period_comparison=comparison or {},
        daily_trend=empty.copy(),
        current_product_summary=(
            current_products.copy() if current_products is not None else empty.copy()
        ),
        previous_product_summary=(
            previous_products.copy() if previous_products is not None else empty.copy()
        ),
        current_category_summary=empty.copy(),
        previous_category_summary=empty.copy(),
        inventory_snapshot=inventory.copy() if inventory is not None else empty.copy(),
        latest_day_comparison=empty.copy(),
    )


@pytest.mark.parametrize(
    ("detector", "metric", "trigger_value", "safe_value", "rule_id"),
    [
        (detect_sales_decline, "sales_amount", -0.05, -0.049, "R001_SALES_DECLINE"),
        (detect_visitor_decline, "visitors", -0.05, -0.049, "R002_VISITOR_DECLINE"),
        (
            detect_conversion_decline,
            "payment_conversion_rate",
            -0.003,
            -0.0029,
            "R003_CONVERSION_DECLINE",
        ),
        (detect_roas_decline, "roas", -0.10, -0.099, "R004_ROAS_DECLINE"),
        (
            detect_gross_margin_decline,
            "gross_margin",
            -0.01,
            -0.0099,
            "R006_GROSS_MARGIN_DECLINE",
        ),
    ],
)
def test_single_metric_rules_trigger_at_boundary_and_not_before_it(
    detector, metric, trigger_value, safe_value, rule_id
) -> None:
    triggered = detector(make_context(comparison={metric: trigger_value}))
    not_triggered = detector(make_context(comparison={metric: safe_value}))

    assert len(triggered) == 1
    assert triggered[0].rule_id == rule_id
    assert triggered[0].evidence[0].change_value == trigger_value
    assert not not_triggered


def test_ad_spend_growth_without_sales_growth_requires_both_conditions() -> None:
    triggered = detect_ad_spend_growth_without_sales_growth(
        make_context(comparison={"ad_spend": 0.10, "sales_amount": 0.0})
    )
    spend_too_low = detect_ad_spend_growth_without_sales_growth(
        make_context(comparison={"ad_spend": 0.099, "sales_amount": 0.0})
    )
    sales_grew = detect_ad_spend_growth_without_sales_growth(
        make_context(comparison={"ad_spend": 0.10, "sales_amount": 0.001})
    )

    assert len(triggered) == 1
    assert triggered[0].rule_id == "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH"
    assert not spend_too_low
    assert not sales_grew


def test_refund_rate_rule_enforces_change_and_minimum_sample_boundaries() -> None:
    triggered = detect_refund_rate_increase(
        make_context(
            current_kpis={"units_sold": DEFAULT_THRESHOLDS.refund_min_units_sold},
            comparison={"refund_rate": 0.005},
        )
    )
    insufficient_sample = detect_refund_rate_increase(
        make_context(
            current_kpis={"units_sold": DEFAULT_THRESHOLDS.refund_min_units_sold - 1},
            comparison={"refund_rate": 0.005},
        )
    )
    increase_too_small = detect_refund_rate_increase(
        make_context(current_kpis={"units_sold": 100}, comparison={"refund_rate": 0.0049})
    )

    assert len(triggered) == 1
    assert triggered[0].rule_id == "R007_REFUND_RATE_INCREASE"
    assert not insufficient_sample
    assert not increase_too_small


def test_comparison_rules_ignore_missing_previous_values_and_zero_denominators() -> None:
    context = make_context(
        previous_kpis={"sales_amount": 0, "visitors": 0, "roas": 0},
        comparison={
            "sales_amount": None,
            "visitors": None,
            "payment_conversion_rate": None,
            "roas": None,
            "ad_spend": None,
            "gross_margin": None,
            "refund_rate": None,
        },
    )

    detectors = [
        detect_sales_decline,
        detect_visitor_decline,
        detect_conversion_decline,
        detect_roas_decline,
        detect_ad_spend_growth_without_sales_growth,
        detect_gross_margin_decline,
        detect_refund_rate_increase,
    ]

    assert all(not detector(context) for detector in detectors)


def test_inventory_rule_detects_low_and_high_days_at_boundaries() -> None:
    inventory = pd.DataFrame(
        {
            "product_id": ["P001", "P002", "P003", "P004"],
            "product_name": ["低库存商品", "高库存商品", "正常商品", "无销量商品"],
            "category": ["外套", "外套", "T恤", "T恤"],
            "current_inventory": [210, 600, 400, 100],
            "period_units_sold": [280, 280, 280, 0],
            "average_daily_sales": [10.0, 10.0, 10.0, 0.0],
            "estimated_days_left": [21.0, 60.0, 40.0, None],
        }
    )

    findings = detect_inventory_days_anomaly(make_context(inventory=inventory))

    assert {finding.scope.scope_id for finding in findings} == {"P001", "P002"}
    assert {finding.rule_id for finding in findings} == {
        "R008_INVENTORY_DAYS_LOW",
        "R009_INVENTORY_DAYS_HIGH",
    }


def test_inventory_rule_ignores_values_inside_thresholds() -> None:
    inventory = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["商品一", "商品二"],
            "category": ["外套", "T恤"],
            "current_inventory": [220, 590],
            "period_units_sold": [280, 280],
            "average_daily_sales": [10.0, 10.0],
            "estimated_days_left": [21.1, 59.9],
        }
    )

    assert not detect_inventory_days_anomaly(make_context(inventory=inventory))


def test_key_product_rule_uses_previous_sales_share_and_product_decline_boundaries() -> None:
    previous = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["重点商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [50.0, 950.0],
        }
    )
    current = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["重点商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [45.0, 960.0],
        }
    )

    findings = detect_key_product_sales_decline(
        make_context(current_products=current, previous_products=previous)
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "R010_KEY_PRODUCT_SALES_DECLINE"
    assert findings[0].scope.scope_id == "P001"
    assert findings[0].evidence[0].change_value == pytest.approx(-0.10)


@pytest.mark.parametrize(
    ("previous_sales", "current_sales"),
    [(49.0, 0.0), (50.0, 45.01)],
)
def test_key_product_rule_requires_both_share_and_decline_thresholds(
    previous_sales, current_sales
) -> None:
    previous = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["目标商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [previous_sales, 1000.0 - previous_sales],
        }
    )
    current = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["目标商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [current_sales, 1000.0 - previous_sales],
        }
    )

    assert not detect_key_product_sales_decline(
        make_context(current_products=current, previous_products=previous)
    )


def test_key_product_rule_ignores_an_empty_previous_period() -> None:
    current = pd.DataFrame(
        {
            "product_id": ["P001"],
            "product_name": ["商品"],
            "category": ["外套"],
            "sales_amount": [100.0],
        }
    )

    assert not detect_key_product_sales_decline(
        make_context(current_products=current, previous_products=pd.DataFrame())
    )
