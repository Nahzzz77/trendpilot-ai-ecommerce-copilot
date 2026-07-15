"""Data structures passed into the deterministic diagnosis engine."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

import pandas as pd


Priority = Literal["high", "medium", "low"]
ChangeType = Literal["relative", "percentage_point", "absolute"]


@dataclass(frozen=True, slots=True)
class FindingScope:
    """The business entity affected by a diagnostic finding."""

    scope_type: Literal["overall", "product"]
    scope_id: str | None
    scope_name: str


@dataclass(frozen=True, slots=True)
class Evidence:
    """A deterministic metric comparison supporting a finding."""

    metric_key: str
    current_value: float | int | None
    baseline_value: float | int | None
    change_value: float | None
    change_type: ChangeType
    unit: str


@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    """A rule-triggered and evidence-backed operating finding."""

    finding_id: str
    rule_id: str
    dimension: str
    scope: FindingScope
    title: str
    evidence: tuple[Evidence, ...]
    priority_score: int
    priority: Priority
    cause_candidate_ids: tuple[str, ...]
    action_candidate_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DiagnosisContext:
    """Prepared Phase 2 outputs required by future diagnosis rules."""

    source_name: str
    start_date: date
    end_date: date
    previous_start_date: date
    previous_end_date: date
    categories: tuple[str, ...]
    product_ids: tuple[str, ...]
    current_kpis: dict[str, float | int]
    previous_kpis: dict[str, float | int]
    period_comparison: dict[str, float | None]
    daily_trend: pd.DataFrame
    current_product_summary: pd.DataFrame
    previous_product_summary: pd.DataFrame
    current_category_summary: pd.DataFrame
    previous_category_summary: pd.DataFrame
    inventory_snapshot: pd.DataFrame
    latest_day_comparison: pd.DataFrame
