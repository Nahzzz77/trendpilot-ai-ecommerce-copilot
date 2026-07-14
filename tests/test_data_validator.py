import pandas as pd

from src.data_validator import REQUIRED_COLUMNS, validate_required_columns


def test_complete_dataframe_is_valid() -> None:
    dataframe = pd.DataFrame(columns=REQUIRED_COLUMNS)

    result = validate_required_columns(dataframe)

    assert result.is_valid is True
    assert result.missing_columns == ()
    assert result.error_message is None


def test_missing_columns_are_reported_in_required_order() -> None:
    present_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in {"date", "inventory", "rating"}
    ]
    dataframe = pd.DataFrame(columns=present_columns)

    result = validate_required_columns(dataframe)

    assert result.is_valid is False
    assert result.missing_columns == ("date", "inventory", "rating")
    assert result.error_message == (
        "CSV 缺少必填字段：date, inventory, rating。"
        "请补充这些列后重新上传。"
    )


def test_extra_columns_are_allowed() -> None:
    dataframe = pd.DataFrame(columns=[*REQUIRED_COLUMNS, "campaign_name"])

    result = validate_required_columns(dataframe)

    assert result.is_valid is True
