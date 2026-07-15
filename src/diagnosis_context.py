"""Build a diagnosis context from validated e-commerce operating data."""

from collections.abc import Sequence
from datetime import date

import pandas as pd

from src.data_processor import filter_analysis_data, prepare_analysis_data
from src.diagnosis_models import DiagnosisContext
from src.metrics import (
    calculate_category_summary,
    calculate_daily_trend,
    calculate_inventory_snapshot,
    calculate_kpis,
    calculate_latest_day_comparison,
    calculate_period_comparison,
    calculate_product_summary,
    get_previous_period_bounds,
)


class DiagnosisContextError(ValueError):
    """Raised when the requested diagnosis context cannot be constructed."""


def build_diagnosis_context(
    dataframe: pd.DataFrame,
    start_date: date,
    end_date: date,
    categories: Sequence[str] | None = None,
    product_ids: Sequence[str] | None = None,
    source_name: str = "未知来源",
) -> DiagnosisContext:
    """Return Phase 2 metric outputs prepared as future rule-engine input."""
    if start_date > end_date:
        raise DiagnosisContextError("开始日期不能晚于结束日期。")

    prepared = prepare_analysis_data(dataframe)
    selected_categories = tuple(categories or ())
    selected_product_ids = tuple(product_ids or ())
    entity_history = filter_analysis_data(
        prepared,
        prepared["date"].min().date(),
        prepared["date"].max().date(),
        selected_categories,
        selected_product_ids,
    )
    current_period = filter_analysis_data(
        entity_history, start_date, end_date
    )
    if current_period.empty:
        raise DiagnosisContextError("当前筛选条件下没有可诊断数据。")

    previous_start, previous_end = get_previous_period_bounds(start_date, end_date)
    previous_period = filter_analysis_data(
        entity_history, previous_start, previous_end
    )

    inventory_snapshot = calculate_inventory_snapshot(
        entity_history, current_period, end_date
    )
    previous_inventory = calculate_inventory_snapshot(
        entity_history, previous_period, previous_end
    )
    current_kpis = calculate_kpis(current_period, inventory_snapshot)
    previous_kpis = calculate_kpis(previous_period, previous_inventory)
    history_through_end = entity_history.loc[
        entity_history["date"] <= pd.Timestamp(end_date)
    ]
    history_daily_trend = calculate_daily_trend(history_through_end)

    return DiagnosisContext(
        source_name=source_name,
        start_date=start_date,
        end_date=end_date,
        previous_start_date=previous_start,
        previous_end_date=previous_end,
        categories=selected_categories,
        product_ids=selected_product_ids,
        current_kpis=current_kpis,
        previous_kpis=previous_kpis,
        period_comparison=calculate_period_comparison(current_kpis, previous_kpis),
        daily_trend=calculate_daily_trend(current_period),
        current_product_summary=calculate_product_summary(current_period),
        previous_product_summary=calculate_product_summary(previous_period),
        current_category_summary=calculate_category_summary(current_period),
        previous_category_summary=calculate_category_summary(previous_period),
        inventory_snapshot=inventory_snapshot,
        latest_day_comparison=calculate_latest_day_comparison(
            history_daily_trend, end_date
        ),
    )
