"""计算 TrendPilot Dashboard 使用的确定性经营指标。"""

from datetime import date, timedelta
from typing import Any

import pandas as pd


RATE_METRICS = {
    "click_through_rate",
    "add_to_cart_rate",
    "payment_conversion_rate",
    "refund_rate",
    "gross_margin",
}


def safe_divide(
    numerator: float | int,
    denominator: float | int,
    default: float | None = 0.0,
) -> float | None:
    """安全执行除法，在分母为零时返回指定默认值。"""

    if denominator == 0:
        return default
    return float(numerator) / float(denominator)


def calculate_kpis(
    period_df: pd.DataFrame, inventory_snapshot: pd.DataFrame
) -> dict[str, float | int]:
    """计算筛选周期的经营 KPI。"""

    sales_amount = float(period_df["sales_amount"].sum())
    orders = int(period_df["orders"].sum())
    units_sold = int(period_df["units_sold"].sum())
    visitors = int(period_df["visitors"].sum())
    impressions = float(period_df["impressions"].sum())
    product_clicks = float(period_df["product_clicks"].sum())
    add_to_cart = float(period_df["add_to_cart"].sum())
    ad_spend = float(period_df["ad_spend"].sum())
    refund_units = float(period_df["refund_units"].sum())
    product_cost = float((period_df["cost"] * period_df["units_sold"]).sum())
    gross_profit = sales_amount - product_cost
    current_inventory = (
        int(inventory_snapshot["current_inventory"].sum())
        if "current_inventory" in inventory_snapshot.columns
        else 0
    )

    return {
        "sales_amount": sales_amount,
        "impressions": int(impressions),
        "product_clicks": int(product_clicks),
        "add_to_cart": int(add_to_cart),
        "orders": orders,
        "units_sold": units_sold,
        "visitors": visitors,
        "click_through_rate": safe_divide(product_clicks, impressions) or 0.0,
        "add_to_cart_rate": safe_divide(add_to_cart, product_clicks) or 0.0,
        "payment_conversion_rate": safe_divide(orders, visitors) or 0.0,
        "refund_rate": safe_divide(refund_units, units_sold) or 0.0,
        "average_order_value": safe_divide(sales_amount, orders) or 0.0,
        "roas": safe_divide(sales_amount, ad_spend) or 0.0,
        "ad_spend": ad_spend,
        "gross_profit": gross_profit,
        "gross_margin": safe_divide(gross_profit, sales_amount) or 0.0,
        "current_inventory": current_inventory,
    }


def _add_derived_metrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    result["click_through_rate"] = result.apply(
        lambda row: safe_divide(row["product_clicks"], row["impressions"]) or 0.0,
        axis=1,
    )
    result["add_to_cart_rate"] = result.apply(
        lambda row: safe_divide(row["add_to_cart"], row["product_clicks"]) or 0.0,
        axis=1,
    )
    result["payment_conversion_rate"] = result.apply(
        lambda row: safe_divide(row["orders"], row["visitors"]) or 0.0,
        axis=1,
    )
    result["refund_rate"] = result.apply(
        lambda row: safe_divide(row["refund_units"], row["units_sold"]) or 0.0,
        axis=1,
    )
    result["roas"] = result.apply(
        lambda row: safe_divide(row["sales_amount"], row["ad_spend"]) or 0.0,
        axis=1,
    )
    result["gross_profit"] = result["sales_amount"] - result["product_cost"]
    result["gross_margin"] = result.apply(
        lambda row: safe_divide(row["gross_profit"], row["sales_amount"]) or 0.0,
        axis=1,
    )
    return result


def calculate_daily_trend(period_df: pd.DataFrame) -> pd.DataFrame:
    """按日期汇总经营趋势，并计算每日确定性比率。"""

    working = period_df.copy()
    working["product_cost"] = working["cost"] * working["units_sold"]
    columns = [
        "sales_amount",
        "orders",
        "units_sold",
        "visitors",
        "impressions",
        "product_clicks",
        "add_to_cart",
        "ad_spend",
        "refund_units",
        "product_cost",
    ]
    daily = working.groupby("date", as_index=False)[columns].sum().sort_values("date")
    return _add_derived_metrics(daily).reset_index(drop=True)


def calculate_product_summary(period_df: pd.DataFrame) -> pd.DataFrame:
    """按商品汇总销售、转化和毛利表现。"""

    working = period_df.copy()
    working["product_cost"] = working["cost"] * working["units_sold"]
    summary = (
        working.groupby(["product_id", "product_name", "category"], as_index=False)
        .agg(
            sales_amount=("sales_amount", "sum"),
            orders=("orders", "sum"),
            units_sold=("units_sold", "sum"),
            visitors=("visitors", "sum"),
            impressions=("impressions", "sum"),
            product_clicks=("product_clicks", "sum"),
            add_to_cart=("add_to_cart", "sum"),
            ad_spend=("ad_spend", "sum"),
            refund_units=("refund_units", "sum"),
            product_cost=("product_cost", "sum"),
            rating=("rating", "mean"),
        )
    )
    return _add_derived_metrics(summary).sort_values(
        "sales_amount", ascending=False
    ).reset_index(drop=True)


def calculate_category_summary(period_df: pd.DataFrame) -> pd.DataFrame:
    """按类目汇总销售、订单、销量和毛利。"""

    working = period_df.copy()
    working["product_cost"] = working["cost"] * working["units_sold"]
    summary = (
        working.groupby("category", as_index=False)
        .agg(
            sales_amount=("sales_amount", "sum"),
            orders=("orders", "sum"),
            units_sold=("units_sold", "sum"),
            visitors=("visitors", "sum"),
            impressions=("impressions", "sum"),
            product_clicks=("product_clicks", "sum"),
            add_to_cart=("add_to_cart", "sum"),
            ad_spend=("ad_spend", "sum"),
            refund_units=("refund_units", "sum"),
            product_cost=("product_cost", "sum"),
        )
    )
    return _add_derived_metrics(summary).sort_values(
        "sales_amount", ascending=False
    ).reset_index(drop=True)


def calculate_inventory_snapshot(
    history_df: pd.DataFrame,
    period_df: pd.DataFrame,
    end_date: date,
) -> pd.DataFrame:
    """计算截止日最新库存、周期销量和库存可售天数。"""

    history = history_df.loc[history_df["date"] <= pd.Timestamp(end_date)].copy()
    if history.empty:
        return pd.DataFrame(
            columns=[
                "product_id",
                "product_name",
                "category",
                "current_inventory",
                "period_units_sold",
                "average_daily_sales",
                "estimated_days_left",
            ]
        )

    latest = (
        history.sort_values(["product_id", "date"])
        .groupby("product_id", as_index=False)
        .tail(1)[["product_id", "product_name", "category", "inventory"]]
        .rename(columns={"inventory": "current_inventory"})
    )
    sales = (
        period_df.groupby("product_id", as_index=False)["units_sold"]
        .sum()
        .rename(columns={"units_sold": "period_units_sold"})
    )
    snapshot = latest.merge(sales, on="product_id", how="left")
    snapshot["period_units_sold"] = snapshot["period_units_sold"].fillna(0)

    if period_df.empty:
        period_days = 0
    else:
        period_days = (period_df["date"].max() - period_df["date"].min()).days + 1
    snapshot["average_daily_sales"] = snapshot["period_units_sold"].apply(
        lambda value: safe_divide(value, period_days) or 0.0
    )
    snapshot["estimated_days_left"] = snapshot.apply(
        lambda row: safe_divide(
            row["current_inventory"], row["average_daily_sales"], default=None
        ),
        axis=1,
    )
    return snapshot.sort_values(
        "estimated_days_left", ascending=True, na_position="last"
    ).reset_index(drop=True)


def calculate_period_comparison(
    current_kpis: dict[str, Any], previous_kpis: dict[str, Any]
) -> dict[str, float | None]:
    """比较两个等长周期；比率指标返回百分点差，其他指标返回相对变化。"""

    comparison: dict[str, float | None] = {}
    for metric, current_value in current_kpis.items():
        if metric not in previous_kpis:
            continue
        previous_value = previous_kpis[metric]
        if metric in RATE_METRICS:
            comparison[metric] = float(current_value) - float(previous_value)
        else:
            comparison[metric] = safe_divide(
                float(current_value) - float(previous_value),
                float(previous_value),
                default=None,
            )
    return comparison


def get_previous_period_bounds(start_date: date, end_date: date) -> tuple[date, date]:
    """返回紧邻当前周期、且包含相同自然日数的上一周期。"""

    period_days = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_days - 1)
    return previous_start, previous_end


def calculate_latest_day_comparison(
    daily_trend: pd.DataFrame, as_of_date: date
) -> pd.DataFrame:
    """比较最新经营日、前一日和此前七个自然日的日均值。"""

    metrics = [
        "sales_amount",
        "orders",
        "units_sold",
        "visitors",
        "payment_conversion_rate",
        "ad_spend",
        "roas",
    ]
    as_of_timestamp = pd.Timestamp(as_of_date)
    latest_rows = daily_trend.loc[daily_trend["date"] <= as_of_timestamp]
    if latest_rows.empty:
        return pd.DataFrame()
    latest_date = latest_rows["date"].max()
    latest = daily_trend.loc[daily_trend["date"] == latest_date].iloc[0]
    previous_date = latest_date - pd.Timedelta(days=1)
    previous_rows = daily_trend.loc[daily_trend["date"] == previous_date]
    prior_week = daily_trend.loc[
        daily_trend["date"].between(
            latest_date - pd.Timedelta(days=7),
            latest_date - pd.Timedelta(days=1),
            inclusive="both",
        )
    ]

    rows: list[dict[str, Any]] = []
    for metric in metrics:
        latest_value = float(latest[metric])
        previous_value = (
            float(previous_rows.iloc[0][metric]) if not previous_rows.empty else None
        )
        week_average = float(prior_week[metric].mean()) if not prior_week.empty else None
        if metric in RATE_METRICS:
            change_previous = (
                latest_value - previous_value if previous_value is not None else None
            )
            change_week = latest_value - week_average if week_average is not None else None
        else:
            change_previous = (
                safe_divide(latest_value - previous_value, previous_value, default=None)
                if previous_value is not None
                else None
            )
            change_week = (
                safe_divide(latest_value - week_average, week_average, default=None)
                if week_average is not None
                else None
            )
        rows.append(
            {
                "metric": metric,
                "latest": latest_value,
                "previous_day": previous_value,
                "previous_7d_average": week_average,
                "change_vs_previous": change_previous,
                "change_vs_7d_average": change_week,
            }
        )
    return pd.DataFrame(rows)
