"""为经营指标计算准备并筛选结构化数据。"""

from collections.abc import Sequence
from datetime import date

import pandas as pd

from src.data_validator import validate_required_columns


IDENTIFIER_COLUMNS = ("product_id", "product_name", "category")
NUMERIC_COLUMNS = (
    "price",
    "cost",
    "impressions",
    "visitors",
    "product_clicks",
    "add_to_cart",
    "orders",
    "units_sold",
    "sales_amount",
    "ad_spend",
    "refund_units",
    "inventory",
    "rating",
)
NON_NEGATIVE_COLUMNS = NUMERIC_COLUMNS


class AnalysisDataError(ValueError):
    """表示数据无法安全用于确定性经营分析。"""


def prepare_analysis_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """返回经过类型转换和业务可计算性校验的数据副本。"""

    validation = validate_required_columns(dataframe)
    if not validation.is_valid:
        raise AnalysisDataError(validation.error_message or "数据字段不完整。")

    prepared = dataframe.copy(deep=True)
    issues: list[str] = []

    for column in IDENTIFIER_COLUMNS:
        empty_mask = prepared[column].isna() | prepared[column].astype(str).str.strip().eq("")
        if empty_mask.any():
            issues.append(f"{column} 存在 {int(empty_mask.sum())} 行空值")
        prepared[column] = prepared[column].astype(str).str.strip()

    parsed_dates = pd.to_datetime(prepared["date"], errors="coerce", format="mixed")
    invalid_date_count = int(parsed_dates.isna().sum())
    if invalid_date_count:
        issues.append(f"date 存在 {invalid_date_count} 行无效日期")
    prepared["date"] = parsed_dates.dt.normalize()

    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(prepared[column], errors="coerce")
        invalid_count = int(converted.isna().sum())
        if invalid_count:
            issues.append(f"{column} 存在 {invalid_count} 行非数值")
        prepared[column] = converted

    for column in NON_NEGATIVE_COLUMNS:
        negative_count = int((prepared[column] < 0).sum())
        if negative_count:
            issues.append(f"{column} 存在 {negative_count} 行负数")

    invalid_rating_count = int(((prepared["rating"] < 0) | (prepared["rating"] > 5)).sum())
    if invalid_rating_count:
        issues.append(f"rating 存在 {invalid_rating_count} 行超出 0 至 5")

    if issues:
        raise AnalysisDataError("；".join(issues) + "。请修正后重新上传。")

    return prepared.sort_values(["date", "product_id"]).reset_index(drop=True)


def filter_analysis_data(
    dataframe: pd.DataFrame,
    start_date: date,
    end_date: date,
    categories: Sequence[str] | None = None,
    product_ids: Sequence[str] | None = None,
) -> pd.DataFrame:
    """按闭区间日期、类目和商品筛选分析数据。"""

    if start_date > end_date:
        raise ValueError("开始日期不能晚于结束日期。")

    start_timestamp = pd.Timestamp(start_date)
    end_timestamp = pd.Timestamp(end_date)
    mask = dataframe["date"].between(start_timestamp, end_timestamp, inclusive="both")

    if categories:
        mask &= dataframe["category"].isin(categories)
    if product_ids:
        mask &= dataframe["product_id"].isin(product_ids)

    return dataframe.loc[mask].copy().reset_index(drop=True)
