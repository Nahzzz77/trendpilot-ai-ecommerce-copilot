from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    DataLoadError,
    load_csv,
    load_sample_data,
    summarize_dataset,
)
from src.data_validator import REQUIRED_COLUMNS


def test_load_csv_reads_uploaded_bytes_and_trims_column_names() -> None:
    upload = BytesIO(b" date ,product_id\n2026-01-01,P001\n")

    dataframe = load_csv(upload)

    assert list(dataframe.columns) == ["date", "product_id"]
    assert dataframe.loc[0, "product_id"] == "P001"


def test_load_csv_rejects_an_empty_file() -> None:
    with pytest.raises(DataLoadError, match="CSV 文件为空"):
        load_csv(BytesIO(b""))


def test_summarize_dataset_returns_display_values() -> None:
    dataframe = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-03", "2026-01-03"],
            "product_id": ["P001", "P001", "P002"],
        }
    )

    summary = summarize_dataset(dataframe)

    assert summary == {
        "row_count": 3,
        "product_count": 2,
        "start_date": "2026-01-01",
        "end_date": "2026-01-03",
    }


def test_sample_data_covers_ninety_days_and_ten_products() -> None:
    sample_path = Path("data/sample_sales_data.csv")

    dataframe = load_sample_data(sample_path)

    assert set(REQUIRED_COLUMNS).issubset(dataframe.columns)
    assert dataframe["date"].nunique() >= 90
    assert dataframe["product_id"].nunique() == 10
    assert len(dataframe) >= 900
