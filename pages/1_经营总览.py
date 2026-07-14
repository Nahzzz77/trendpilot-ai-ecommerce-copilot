"""TrendPilot deterministic e-commerce operating dashboard."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.charts import (
    build_category_share_chart,
    build_conversion_funnel_chart,
    build_orders_units_chart,
    build_product_ranking_chart,
    build_sales_trend_chart,
)
from src.data_processor import AnalysisDataError, filter_analysis_data, prepare_analysis_data
from src.metrics import (
    RATE_METRICS,
    calculate_category_summary,
    calculate_daily_trend,
    calculate_inventory_snapshot,
    calculate_kpis,
    calculate_latest_day_comparison,
    calculate_period_comparison,
    calculate_product_summary,
    get_previous_period_bounds,
)


DATA_SESSION_KEY = "sales_data"
SOURCE_SESSION_KEY = "sales_data_source"


def format_currency(value: float | int) -> str:
    return f"¥{value:,.2f}"


def format_number(value: float | int) -> str:
    return f"{value:,.0f}"


def format_percent(value: float | int) -> str:
    return f"{value:.2%}"


def format_decimal(value: float | int) -> str:
    return f"{value:,.2f}"


def format_delta(value: float | None, *, percentage_points: bool = False) -> str | None:
    if value is None or pd.isna(value):
        return None
    if percentage_points:
        return f"{value * 100:+.2f} 个百分点"
    return f"{value:+.1%}"


def metric_card(
    column,
    label: str,
    value: float | int,
    formatter,
    comparison: dict[str, float | None],
    key: str,
) -> None:
    column.metric(
        label,
        formatter(value),
        format_delta(comparison.get(key), percentage_points=key in RATE_METRICS),
        border=True,
    )


st.set_page_config(page_title="经营总览 | TrendPilot", page_icon="📊", layout="wide")
st.title("经营总览")
st.caption("以确定性指标呈现流量、销售、毛利与库存表现")

if DATA_SESSION_KEY not in st.session_state:
    st.warning("请先返回首页加载数据，再进入经营总览。")
    st.markdown("[🏠 返回首页](../)")
    st.stop()

try:
    prepared = prepare_analysis_data(st.session_state[DATA_SESSION_KEY])
except AnalysisDataError as exc:
    st.error(f"当前数据暂时无法分析：{exc}")
    st.markdown("[🏠 返回首页重新加载数据](../)")
    st.stop()

minimum_date = prepared["date"].min().date()
maximum_date = prepared["date"].max().date()
default_start = max(minimum_date, maximum_date - timedelta(days=29))

with st.sidebar:
    st.header("分析筛选")
    selected_dates = st.date_input(
        "分析周期",
        value=(default_start, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
    )
    selected_categories = st.multiselect(
        "商品类目",
        options=sorted(prepared["category"].unique()),
        placeholder="全部类目",
    )
    product_pool = prepared
    if selected_categories:
        product_pool = product_pool.loc[product_pool["category"].isin(selected_categories)]
    product_options = (
        product_pool[["product_id", "product_name"]]
        .drop_duplicates()
        .sort_values("product_id")
    )
    product_labels = {
        row.product_id: f"{row.product_name}（{row.product_id}）"
        for row in product_options.itertuples(index=False)
    }
    selected_products = st.multiselect(
        "商品",
        options=list(product_labels),
        format_func=lambda product_id: product_labels[product_id],
        placeholder="全部商品",
    )

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("请选择完整的开始日期和结束日期。")
    st.stop()

start_date, end_date = selected_dates
entity_history = filter_analysis_data(
    prepared,
    minimum_date,
    maximum_date,
    selected_categories,
    selected_products,
)
current_period = filter_analysis_data(
    entity_history, start_date, end_date, [], []
)
if current_period.empty:
    st.info("当前筛选条件下没有数据，请调整日期、类目或商品范围。")
    st.stop()

previous_start, previous_end = get_previous_period_bounds(start_date, end_date)
previous_period = filter_analysis_data(
    entity_history, previous_start, previous_end, [], []
)
current_inventory = calculate_inventory_snapshot(entity_history, current_period, end_date)
previous_inventory = calculate_inventory_snapshot(
    entity_history, previous_period, previous_end
)
current_kpis = calculate_kpis(current_period, current_inventory)
previous_kpis = calculate_kpis(previous_period, previous_inventory)
comparison = calculate_period_comparison(current_kpis, previous_kpis)
daily_trend = calculate_daily_trend(current_period)
product_summary = calculate_product_summary(current_period)
category_summary = calculate_category_summary(current_period)

source = st.session_state.get(SOURCE_SESSION_KEY, "未知来源")
st.caption(
    f"数据来源：{source} ｜ 分析周期：{start_date.isoformat()} 至 {end_date.isoformat()} "
    f"｜ {len(current_period):,} 条记录"
)

st.subheader("核心经营指标")
core_columns = st.columns(6)
core_specs = [
    ("销售额", "sales_amount", format_currency),
    ("订单量", "orders", format_number),
    ("访客数", "visitors", format_number),
    ("支付转化率", "payment_conversion_rate", format_percent),
    ("客单价", "average_order_value", format_currency),
    ("ROAS", "roas", format_decimal),
]
for column, (label, key, formatter) in zip(core_columns, core_specs):
    metric_card(column, label, current_kpis[key], formatter, comparison, key)

with st.expander("更多经营指标", expanded=False):
    detail_columns = st.columns(6)
    detail_specs = [
        ("商品销量", "units_sold", format_number),
        ("广告投入", "ad_spend", format_currency),
        ("退款率", "refund_rate", format_percent),
        ("毛利额", "gross_profit", format_currency),
        ("毛利率", "gross_margin", format_percent),
        ("当前库存", "current_inventory", format_number),
    ]
    for column, (label, key, formatter) in zip(detail_columns, detail_specs):
        metric_card(column, label, current_kpis[key], formatter, comparison, key)

st.subheader("经营趋势")
sales_column, orders_column = st.columns(2)
with sales_column:
    st.markdown("**每日销售额**")
    st.plotly_chart(build_sales_trend_chart(daily_trend), width="stretch")
with orders_column:
    st.markdown("**每日订单量与销量**")
    st.plotly_chart(build_orders_units_chart(daily_trend), width="stretch")

st.subheader("经营结构")
funnel_column, ranking_column = st.columns(2)
with funnel_column:
    st.markdown("**流量转化漏斗**")
    st.plotly_chart(build_conversion_funnel_chart(current_kpis), width="stretch")
with ranking_column:
    st.markdown("**商品销售额 Top 10**")
    st.plotly_chart(build_product_ranking_chart(product_summary), width="stretch")

category_column, margin_column = st.columns(2)
with category_column:
    st.markdown("**类目销售额占比**")
    st.plotly_chart(build_category_share_chart(category_summary), width="stretch")
with margin_column:
    st.markdown("**商品毛利表现**")
    margin_view = product_summary[
        ["product_name", "sales_amount", "gross_profit", "gross_margin"]
    ].rename(
        columns={
            "product_name": "商品",
            "sales_amount": "销售额",
            "gross_profit": "毛利额",
            "gross_margin": "毛利率",
        }
    )
    st.dataframe(
        margin_view,
        hide_index=True,
        width="stretch",
        column_config={
            "销售额": st.column_config.NumberColumn(format="¥ %.2f"),
            "毛利额": st.column_config.NumberColumn(format="¥ %.2f"),
            "毛利率": st.column_config.NumberColumn(format="percent"),
        },
    )

st.subheader("库存明细")
inventory_view = current_inventory.rename(
    columns={
        "product_id": "商品ID",
        "product_name": "商品",
        "category": "类目",
        "current_inventory": "截止日库存",
        "period_units_sold": "周期销量",
        "average_daily_sales": "日均销量",
        "estimated_days_left": "库存可售天数",
    }
)
st.dataframe(
    inventory_view,
    hide_index=True,
    width="stretch",
    column_config={
        "日均销量": st.column_config.NumberColumn(format="%.2f"),
        "库存可售天数": st.column_config.NumberColumn(format="%.1f"),
    },
)

st.subheader("最新经营日对比")
history_daily = calculate_daily_trend(
    entity_history.loc[entity_history["date"] <= pd.Timestamp(end_date)]
)
latest_comparison = calculate_latest_day_comparison(history_daily, end_date)
metric_names = {
    "sales_amount": "销售额",
    "orders": "订单量",
    "units_sold": "商品销量",
    "visitors": "访客数",
    "payment_conversion_rate": "支付转化率",
    "ad_spend": "广告投入",
    "roas": "ROAS",
}
latest_view = latest_comparison.copy()
latest_view["metric"] = latest_view["metric"].map(metric_names)
latest_view = latest_view.rename(
    columns={
        "metric": "指标",
        "latest": "最新一天",
        "previous_day": "前一天",
        "previous_7d_average": "此前7日均值",
        "change_vs_previous": "较前一天",
        "change_vs_7d_average": "较此前7日均值",
    }
)
st.dataframe(latest_view, hide_index=True, width="stretch")
st.caption("对比仅展示确定性计算结果；比率变化为百分点，其他指标为相对变化率。")
