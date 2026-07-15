from datetime import date

import pandas as pd
import pytest

from src.diagnosis_context import DiagnosisContextError, build_diagnosis_context
from src.diagnosis_models import DiagnosisContext


def make_diagnosis_data() -> pd.DataFrame:
    rows = []
    products = [
        ("P001", "黑色冲锋衣", "外套", 100.0, 60.0),
        ("P002", "云白防晒衣", "防晒衣", 200.0, 100.0),
    ]
    for day in range(1, 5):
        for product_id, product_name, category, price, cost in products:
            product_factor = 1 if product_id == "P001" else 2
            units = day * product_factor
            rows.append(
                {
                    "date": f"2026-01-0{day}",
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "price": price,
                    "cost": cost,
                    "impressions": 1000 * product_factor,
                    "visitors": 100 * product_factor,
                    "product_clicks": 50 * product_factor,
                    "add_to_cart": 20 * product_factor,
                    "orders": units,
                    "units_sold": units,
                    "sales_amount": price * units,
                    "ad_spend": 10.0 * day * product_factor,
                    "refund_units": 0,
                    "inventory": 500 - day * units,
                    "rating": 4.6,
                }
            )
    return pd.DataFrame(rows)


def test_build_context_assembles_current_and_previous_period_outputs() -> None:
    raw = make_diagnosis_data()

    context = build_diagnosis_context(
        raw,
        start_date=date(2026, 1, 3),
        end_date=date(2026, 1, 4),
        source_name="单元测试数据",
    )

    assert isinstance(context, DiagnosisContext)
    assert context.source_name == "单元测试数据"
    assert context.start_date == date(2026, 1, 3)
    assert context.end_date == date(2026, 1, 4)
    assert context.previous_start_date == date(2026, 1, 1)
    assert context.previous_end_date == date(2026, 1, 2)
    assert context.categories == ()
    assert context.product_ids == ()
    assert context.current_kpis["sales_amount"] == 3500.0
    assert context.previous_kpis["sales_amount"] == 1500.0
    assert context.period_comparison["sales_amount"] == pytest.approx(4 / 3)
    assert len(context.daily_trend) == 2
    assert len(context.current_product_summary) == 2
    assert len(context.previous_product_summary) == 2
    assert len(context.current_category_summary) == 2
    assert len(context.previous_category_summary) == 2
    assert len(context.inventory_snapshot) == 2
    assert set(context.latest_day_comparison["metric"]) == {
        "sales_amount",
        "orders",
        "units_sold",
        "visitors",
        "payment_conversion_rate",
        "ad_spend",
        "roas",
    }


def test_build_context_filters_entities_before_calculating_outputs() -> None:
    raw = make_diagnosis_data()

    context = build_diagnosis_context(
        raw,
        start_date=date(2026, 1, 3),
        end_date=date(2026, 1, 4),
        categories=["外套"],
        product_ids=["P001"],
    )

    assert context.categories == ("外套",)
    assert context.product_ids == ("P001",)
    assert context.current_kpis["sales_amount"] == 700.0
    assert context.current_product_summary["product_id"].tolist() == ["P001"]
    assert context.inventory_snapshot["product_id"].tolist() == ["P001"]


def test_build_context_does_not_modify_the_input_dataframe() -> None:
    raw = make_diagnosis_data()
    original = raw.copy(deep=True)

    build_diagnosis_context(
        raw,
        start_date=date(2026, 1, 3),
        end_date=date(2026, 1, 4),
    )

    pd.testing.assert_frame_equal(raw, original)


def test_build_context_allows_an_empty_previous_period() -> None:
    raw = make_diagnosis_data()

    context = build_diagnosis_context(
        raw,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
    )

    assert context.previous_kpis["sales_amount"] == 0.0
    assert context.previous_product_summary.empty
    assert context.previous_category_summary.empty


def test_build_context_rejects_invalid_or_empty_current_period() -> None:
    raw = make_diagnosis_data()

    with pytest.raises(DiagnosisContextError, match="开始日期不能晚于结束日期"):
        build_diagnosis_context(
            raw,
            start_date=date(2026, 1, 4),
            end_date=date(2026, 1, 3),
        )

    with pytest.raises(DiagnosisContextError, match="当前筛选条件下没有可诊断数据"):
        build_diagnosis_context(
            raw,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 2),
        )
