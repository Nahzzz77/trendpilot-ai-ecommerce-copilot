from datetime import date

import pandas as pd
import pytest

from src.data_processor import (
    AnalysisDataError,
    filter_analysis_data,
    prepare_analysis_data,
)
from src.data_validator import REQUIRED_COLUMNS


def make_dataframe() -> pd.DataFrame:
    rows = [
        [
            "2026-01-01",
            "P001",
            "黑色冲锋衣",
            "冲锋衣",
            "699",
            "360",
            "1000",
            "100",
            "50",
            "20",
            "10",
            "10",
            "6990",
            "500",
            "1",
            "80",
            "4.7",
        ],
        [
            "2026-01-02",
            "P002",
            "云白防晒衣",
            "防晒衣",
            "329",
            "150",
            "800",
            "80",
            "40",
            "16",
            "8",
            "8",
            "2632",
            "300",
            "0",
            "120",
            "4.6",
        ],
    ]
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def test_prepare_analysis_data_converts_types_without_mutating_input() -> None:
    original = make_dataframe()

    prepared = prepare_analysis_data(original)

    assert original.loc[0, "date"] == "2026-01-01"
    assert pd.api.types.is_datetime64_any_dtype(prepared["date"])
    assert pd.api.types.is_numeric_dtype(prepared["sales_amount"])
    assert prepared.loc[0, "inventory"] == 80


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("date", "not-a-date", "date 存在 1 行无效日期"),
        ("price", "not-a-number", "price 存在 1 行非数值"),
        ("inventory", "-1", "inventory 存在 1 行负数"),
        ("rating", "5.5", "rating 存在 1 行超出 0 至 5"),
        ("product_id", " ", "product_id 存在 1 行空值"),
    ],
)
def test_prepare_analysis_data_reports_invalid_values(
    column: str, value: str, message: str
) -> None:
    dataframe = make_dataframe()
    dataframe.loc[0, column] = value

    with pytest.raises(AnalysisDataError, match=message):
        prepare_analysis_data(dataframe)


def test_filter_analysis_data_uses_inclusive_dates_and_entity_filters() -> None:
    prepared = prepare_analysis_data(make_dataframe())

    result = filter_analysis_data(
        prepared,
        start_date=date(2026, 1, 2),
        end_date=date(2026, 1, 2),
        categories=["防晒衣"],
        product_ids=["P002"],
    )

    assert result["product_id"].tolist() == ["P002"]


def test_filter_analysis_data_empty_filters_mean_all_entities() -> None:
    prepared = prepare_analysis_data(make_dataframe())

    result = filter_analysis_data(
        prepared,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
        categories=[],
        product_ids=[],
    )

    assert len(result) == 2
