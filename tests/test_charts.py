from copy import deepcopy

import pandas as pd

from src.charts import (
    build_category_share_chart,
    build_conversion_funnel_chart,
    build_orders_units_chart,
    build_product_ranking_chart,
    build_sales_trend_chart,
)


def test_sales_trend_chart_uses_daily_sales_without_mutating_input():
    data = pd.DataFrame(
        {"date": pd.to_datetime(["2026-06-01", "2026-06-02"]), "sales_amount": [1200, 1600]}
    )
    original = data.copy(deep=True)

    figure = build_sales_trend_chart(data)

    assert len(figure.data) == 1
    assert figure.data[0].type == "scatter"
    assert list(figure.data[0].y) == [1200, 1600]
    pd.testing.assert_frame_equal(data, original)


def test_orders_units_chart_contains_two_series():
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-06-01", "2026-06-02"]),
            "orders": [10, 12],
            "units_sold": [11, 15],
        }
    )

    figure = build_orders_units_chart(data)

    assert [trace.name for trace in figure.data] == ["订单量", "商品销量"]


def test_conversion_funnel_uses_precalculated_kpis():
    kpis = {"impressions": 1000, "product_clicks": 160, "add_to_cart": 48, "orders": 20}

    figure = build_conversion_funnel_chart(deepcopy(kpis))

    assert len(figure.data) == 1
    assert figure.data[0].type == "funnel"
    assert list(figure.data[0].y) == ["曝光量", "商品点击量", "加购量", "订单量"]
    assert list(figure.data[0].x) == [1000, 160, 48, 20]


def test_product_ranking_is_limited_to_top_ten():
    data = pd.DataFrame(
        {"product_name": [f"商品{i}" for i in range(12)], "sales_amount": list(range(12))}
    )

    figure = build_product_ranking_chart(data)

    assert len(figure.data) == 1
    assert len(figure.data[0].x) == 10
    assert max(figure.data[0].x) == 11
    assert min(figure.data[0].x) == 2


def test_category_share_chart_builds_pie_and_empty_inputs_are_safe():
    data = pd.DataFrame({"category": ["卫衣", "T恤"], "sales_amount": [800, 1200]})

    figure = build_category_share_chart(data)
    empty_figure = build_category_share_chart(data.iloc[0:0])

    assert figure.data[0].type == "pie"
    assert list(figure.data[0].labels) == ["卫衣", "T恤"]
    assert len(empty_figure.data) == 0
