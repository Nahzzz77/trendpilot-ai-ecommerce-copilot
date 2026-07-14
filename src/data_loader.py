"""读取 CSV 数据并生成首页所需的数据摘要。"""

from pathlib import Path
from typing import IO

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


DEFAULT_SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_sales_data.csv"


class DataLoadError(ValueError):
    """表示无法向普通用户展示的 CSV 读取错误。"""


def load_csv(source: str | Path | IO[str] | IO[bytes]) -> pd.DataFrame:
    """读取 CSV，并清理字段名前后的空白字符。"""

    try:
        dataframe = pd.read_csv(source)
    except EmptyDataError as exc:
        raise DataLoadError("CSV 文件为空，请选择包含经营数据的文件。") from exc
    except (ParserError, UnicodeDecodeError, OSError) as exc:
        raise DataLoadError(
            "无法读取 CSV，请确认文件采用 UTF-8 编码且内容格式正确。"
        ) from exc

    dataframe.columns = dataframe.columns.astype(str).str.strip()
    return dataframe


def load_sample_data(path: str | Path = DEFAULT_SAMPLE_PATH) -> pd.DataFrame:
    """读取项目自带的模拟经营数据。"""

    return load_csv(path)


def summarize_dataset(dataframe: pd.DataFrame) -> dict[str, int | str]:
    """返回首页展示所需的行数、商品数与日期范围。"""

    dates = pd.to_datetime(dataframe["date"], errors="coerce").dropna()
    start_date = dates.min().date().isoformat() if not dates.empty else "无有效日期"
    end_date = dates.max().date().isoformat() if not dates.empty else "无有效日期"

    return {
        "row_count": len(dataframe),
        "product_count": dataframe["product_id"].nunique(),
        "start_date": start_date,
        "end_date": end_date,
    }
