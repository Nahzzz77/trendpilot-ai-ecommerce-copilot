from datetime import date

import pandas as pd
import pytest

from src.metrics import (
    calculate_category_summary,
    calculate_daily_trend,
    calculate_inventory_snapshot,
    calculate_kpis,
    calculate_latest_day_comparison,
    calculate_period_comparison,
    calculate_product_summary,
    get_previous_period_bounds,
    safe_divide,
)


def make_metric_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-02"]),
            "product_id": ["P001", "P001", "P002"],
            "product_name": ["黑色冲锋衣", "黑色冲锋衣", "云白防晒衣"],
            "category": ["冲锋衣", "冲锋衣", "防晒衣"],
            "price": [100.0, 100.0, 150.0],
            "cost": [60.0, 60.0, 100.0],
            "impressions": [1000, 1200, 600],
            "visitors": [100, 120, 60],
            "product_clicks": [50, 60, 30],
            "add_to_cart": [20, 24, 12],
            "orders": [10, 12, 6],
            "units_sold": [10, 12, 6],
            "sales_amount": [1000.0, 1200.0, 900.0],
            "ad_spend": [100.0, 120.0, 90.0],
            "refund_units": [1, 0, 1],
            "inventory": [80, 68, 40],
            "rating": [4.7, 4.7, 4.6],
        }
    )


def test_safe_divide_returns_default_for_zero_denominator() -> None:
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=None) is None


def test_calculate_kpis_uses_aggregated_numerators_and_denominators() -> None:
    dataframe = make_metric_data()
    inventory = pd.DataFrame({"current_inventory": [68, 40]})

    kpis = calculate_kpis(dataframe, inventory)

    assert kpis["sales_amount"] == 3100.0
    assert kpis["impressions"] == 2800
    assert kpis["product_clicks"] == 140
    assert kpis["add_to_cart"] == 56
    assert kpis["orders"] == 28
    assert kpis["units_sold"] == 28
    assert kpis["visitors"] == 280
    assert kpis["click_through_rate"] == pytest.approx(140 / 2800)
    assert kpis["add_to_cart_rate"] == pytest.approx(56 / 140)
    assert kpis["payment_conversion_rate"] == pytest.approx(28 / 280)
    assert kpis["refund_rate"] == pytest.approx(2 / 28)
    assert kpis["average_order_value"] == pytest.approx(3100 / 28)
    assert kpis["roas"] == 10.0
    assert kpis["gross_profit"] == 1180.0
    assert kpis["gross_margin"] == pytest.approx(1180 / 3100)
    assert kpis["ad_spend"] == 310.0
    assert kpis["current_inventory"] == 108


def test_calculate_kpis_handles_all_zero_denominators() -> None:
    dataframe = make_metric_data().iloc[:1].copy()
    for column in [
        "impressions",
        "visitors",
        "product_clicks",
        "add_to_cart",
        "orders",
        "units_sold",
        "sales_amount",
        "ad_spend",
        "refund_units",
    ]:
        dataframe[column] = 0

    kpis = calculate_kpis(dataframe, pd.DataFrame())

    assert kpis["click_through_rate"] == 0.0
    assert kpis["payment_conversion_rate"] == 0.0
    assert kpis["average_order_value"] == 0.0
    assert kpis["roas"] == 0.0
    assert kpis["gross_margin"] == 0.0


def test_daily_product_and_category_summaries_are_sorted_and_aggregated() -> None:
    dataframe = make_metric_data()

    daily = calculate_daily_trend(dataframe)
    products = calculate_product_summary(dataframe)
    categories = calculate_category_summary(dataframe)

    assert daily["date"].tolist() == list(pd.to_datetime(["2026-01-01", "2026-01-02"]))
    assert daily.loc[1, "sales_amount"] == 2100.0
    assert products.iloc[0]["product_id"] == "P001"
    assert products.iloc[0]["sales_amount"] == 2200.0
    assert categories.iloc[0]["category"] == "冲锋衣"


def test_inventory_snapshot_uses_latest_stock_and_period_daily_sales() -> None:
    history = make_metric_data()
    period = history.copy()

    snapshot = calculate_inventory_snapshot(
        history, period, end_date=date(2026, 1, 2)
    )

    p1 = snapshot.set_index("product_id").loc["P001"]
    assert p1["current_inventory"] == 68
    assert p1["period_units_sold"] == 22
    assert p1["average_daily_sales"] == 11
    assert p1["estimated_days_left"] == pytest.approx(68 / 11)


def test_inventory_snapshot_returns_missing_days_left_when_sales_are_zero() -> None:
    history = make_metric_data().query("product_id == 'P002'").copy()
    period = history.copy()
    period["units_sold"] = 0

    snapshot = calculate_inventory_snapshot(
        history, period, end_date=date(2026, 1, 2)
    )

    assert pd.isna(snapshot.loc[0, "estimated_days_left"])


def test_period_comparison_uses_percentage_points_for_rates() -> None:
    current = {"sales_amount": 120.0, "payment_conversion_rate": 0.12}
    previous = {"sales_amount": 100.0, "payment_conversion_rate": 0.10}

    comparison = calculate_period_comparison(current, previous)

    assert comparison["sales_amount"] == pytest.approx(0.2)
    assert comparison["payment_conversion_rate"] == pytest.approx(0.02)


def test_period_comparison_returns_none_when_previous_value_is_zero() -> None:
    comparison = calculate_period_comparison(
        {"sales_amount": 10.0}, {"sales_amount": 0.0}
    )

    assert comparison["sales_amount"] is None


def test_previous_period_bounds_have_the_same_inclusive_length() -> None:
    assert get_previous_period_bounds(date(2026, 1, 8), date(2026, 1, 14)) == (
        date(2026, 1, 1),
        date(2026, 1, 7),
    )


def test_latest_day_comparison_uses_previous_day_and_prior_seven_day_average() -> None:
    dates = pd.date_range("2026-01-01", periods=9, freq="D")
    daily = pd.DataFrame(
        {
            "date": dates,
            "sales_amount": [10, 20, 30, 40, 50, 60, 70, 80, 100],
            "orders": [1, 2, 3, 4, 5, 6, 7, 8, 10],
            "units_sold": [1, 2, 3, 4, 5, 6, 7, 8, 10],
            "visitors": [10, 20, 30, 40, 50, 60, 70, 80, 100],
            "payment_conversion_rate": [0.1] * 9,
            "ad_spend": [1, 2, 3, 4, 5, 6, 7, 8, 10],
            "roas": [10.0] * 9,
        }
    )

    result = calculate_latest_day_comparison(daily, as_of_date=date(2026, 1, 9))
    sales = result.set_index("metric").loc["sales_amount"]

    assert sales["latest"] == 100
    assert sales["previous_day"] == 80
    assert sales["previous_7d_average"] == pytest.approx(50)
