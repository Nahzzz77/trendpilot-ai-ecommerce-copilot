"""校验 TrendPilot 经营数据的必填字段。"""

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS: tuple[str, ...] = (
    "date",
    "product_id",
    "product_name",
    "category",
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


@dataclass(frozen=True)
class ValidationResult:
    """字段校验的结构化结果。"""

    missing_columns: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.missing_columns

    @property
    def error_message(self) -> str | None:
        if self.is_valid:
            return None
        missing = ", ".join(self.missing_columns)
        return f"CSV 缺少必填字段：{missing}。请补充这些列后重新上传。"


def validate_required_columns(dataframe: pd.DataFrame) -> ValidationResult:
    """按规定顺序返回数据中缺失的必填字段。"""

    present_columns = set(dataframe.columns)
    missing_columns = tuple(
        column for column in REQUIRED_COLUMNS if column not in present_columns
    )
    return ValidationResult(missing_columns=missing_columns)
