"""Plotly chart builders for the TrendPilot operating dashboard."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd
import plotly.graph_objects as go


PRIMARY = "#2563EB"
SECONDARY = "#14B8A6"
ACCENT = "#8B5CF6"
PALETTE = [PRIMARY, SECONDARY, ACCENT, "#F59E0B", "#64748B", "#06B6D4"]


def _style(figure: go.Figure, *, height: int = 360) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=35, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(148,163,184,0.18)")
    return figure


def build_sales_trend_chart(daily_trend: pd.DataFrame) -> go.Figure:
    """Build the daily sales line chart from a pre-aggregated daily trend."""
    figure = go.Figure()
    if not daily_trend.empty:
        figure.add_trace(
            go.Scatter(
                x=daily_trend["date"],
                y=daily_trend["sales_amount"],
                mode="lines+markers",
                name="销售额",
                line=dict(color=PRIMARY, width=3),
                hovertemplate="%{x|%Y-%m-%d}<br>销售额：¥%{y:,.2f}<extra></extra>",
            )
        )
    figure.update_yaxes(title="销售额（元）", tickprefix="¥")
    return _style(figure)


def build_orders_units_chart(daily_trend: pd.DataFrame) -> go.Figure:
    """Build daily orders and units-sold lines from pre-aggregated data."""
    figure = go.Figure()
    if not daily_trend.empty:
        for column, label, color in (
            ("orders", "订单量", PRIMARY),
            ("units_sold", "商品销量", SECONDARY),
        ):
            figure.add_trace(
                go.Scatter(
                    x=daily_trend["date"],
                    y=daily_trend[column],
                    mode="lines+markers",
                    name=label,
                    line=dict(color=color, width=2),
                    hovertemplate=f"%{{x|%Y-%m-%d}}<br>{label}：%{{y:,.0f}}<extra></extra>",
                )
            )
    figure.update_yaxes(title="数量")
    return _style(figure)


def build_conversion_funnel_chart(kpis: Mapping[str, float | int]) -> go.Figure:
    """Build a conversion funnel from already calculated KPI totals."""
    labels = ["曝光量", "商品点击量", "加购量", "订单量"]
    keys = ["impressions", "product_clicks", "add_to_cart", "orders"]
    values = [kpis.get(key, 0) for key in keys]
    figure = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=[PRIMARY, "#3B82F6", SECONDARY, ACCENT]),
            hovertemplate="%{y}：%{x:,.0f}<extra></extra>",
        )
    )
    return _style(figure)


def build_product_ranking_chart(product_summary: pd.DataFrame) -> go.Figure:
    """Build a horizontal sales ranking for the ten highest-selling products."""
    figure = go.Figure()
    if not product_summary.empty:
        ranking = product_summary.nlargest(10, "sales_amount").sort_values("sales_amount")
        figure.add_trace(
            go.Bar(
                x=ranking["sales_amount"],
                y=ranking["product_name"],
                orientation="h",
                marker_color=PRIMARY,
                name="商品销售额",
                hovertemplate="%{y}<br>销售额：¥%{x:,.2f}<extra></extra>",
            )
        )
    figure.update_xaxes(title="销售额（元）", tickprefix="¥")
    return _style(figure, height=420)


def build_category_share_chart(category_summary: pd.DataFrame) -> go.Figure:
    """Build the category sales share pie chart from category summaries."""
    figure = go.Figure()
    if not category_summary.empty:
        figure.add_trace(
            go.Pie(
                labels=category_summary["category"],
                values=category_summary["sales_amount"],
                hole=0.52,
                marker=dict(colors=PALETTE),
                textinfo="label+percent",
                hovertemplate="%{label}<br>销售额：¥%{value:,.2f}<br>占比：%{percent}<extra></extra>",
            )
        )
    return _style(figure, height=420)
