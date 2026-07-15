import pandas as pd

from src.diagnosis_catalog import (
    ACTION_CATALOG,
    CAUSE_CATALOG,
    RULE_ACTION_MAP,
    RULE_IDS,
    get_action_candidate_ids,
    get_cause_candidate_ids,
)
from src.diagnosis_engine import run_diagnosis
from tests.test_diagnosis_rules import make_context


def test_cause_and_action_ids_are_unique() -> None:
    cause_ids = [cause.cause_id for cause in CAUSE_CATALOG]
    action_ids = [action.action_id for action in ACTION_CATALOG]

    assert len(cause_ids) == len(set(cause_ids))
    assert len(action_ids) == len(set(action_ids))


def test_catalog_references_only_known_rules_and_entries() -> None:
    known_rules = set(RULE_IDS)
    cause_ids = {cause.cause_id for cause in CAUSE_CATALOG}
    action_ids = {action.action_id for action in ACTION_CATALOG}

    assert len(RULE_IDS) == len(known_rules)
    assert set(RULE_ACTION_MAP) == known_rules
    assert all(
        cause.applicable_rules and set(cause.applicable_rules) <= known_rules
        for cause in CAUSE_CATALOG
    )
    assert all(set(action_ids_for_rule) <= action_ids for action_ids_for_rule in RULE_ACTION_MAP.values())
    assert all(get_cause_candidate_ids(rule_id) for rule_id in RULE_IDS)
    assert all(get_action_candidate_ids(rule_id) for rule_id in RULE_IDS)
    assert set().union(*(set(get_cause_candidate_ids(rule_id)) for rule_id in RULE_IDS)) <= cause_ids


def test_inventory_and_key_product_rules_have_distinct_mappings() -> None:
    assert get_cause_candidate_ids("R008_INVENTORY_DAYS_LOW") == (
        "C008_SALES_VELOCITY_OUTPACING_STOCK",
        "C009_REPLENISHMENT_LAG",
    )
    assert get_cause_candidate_ids("R009_INVENTORY_DAYS_HIGH") == (
        "C010_DEMAND_BELOW_STOCK_PLAN",
    )
    assert get_action_candidate_ids("R010_KEY_PRODUCT_SALES_DECLINE") == (
        "A013_REVIEW_KEY_PRODUCT",
        "A014_OPTIMIZE_PRODUCT_OFFER",
    )


def test_every_generated_finding_references_valid_catalog_ids() -> None:
    products_previous = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["重点商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [500.0, 500.0],
        }
    )
    products_current = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["重点商品", "其他商品"],
            "category": ["外套", "T恤"],
            "sales_amount": [400.0, 500.0],
        }
    )
    inventory = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "product_name": ["重点商品", "其他商品"],
            "category": ["外套", "T恤"],
            "current_inventory": [200, 700],
            "period_units_sold": [300, 280],
            "average_daily_sales": [10.0, 10.0],
            "estimated_days_left": [20.0, 70.0],
        }
    )
    context = make_context(
        current_kpis={"units_sold": 100},
        comparison={
            "sales_amount": -0.20,
            "visitors": -0.10,
            "payment_conversion_rate": -0.01,
            "roas": -0.20,
            "ad_spend": 0.20,
            "gross_margin": -0.02,
            "refund_rate": 0.01,
        },
        current_products=products_current,
        previous_products=products_previous,
        inventory=inventory,
    )

    findings = run_diagnosis(context)

    assert {finding.rule_id for finding in findings} == set(RULE_IDS)
    for finding in findings:
        assert finding.cause_candidate_ids == get_cause_candidate_ids(finding.rule_id)
        assert finding.action_candidate_ids == get_action_candidate_ids(finding.rule_id)
