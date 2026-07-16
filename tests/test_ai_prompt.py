import json
from copy import deepcopy

import pytest

from src.ai_prompt import (
    JSON_OUTPUT_CONSTRAINTS,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    build_ai_report_prompt,
)


GOLDEN_SCENARIOS = (
    (
        "流量下降导致销售下降",
        (
            (
                "finding-sales",
                "R001_SALES_DECLINE",
                "销售额下降",
                "C001_TRAFFIC_DECLINE",
                "A001_REVIEW_SALES_FUNNEL",
            ),
            (
                "finding-visitors",
                "R002_VISITOR_DECLINE",
                "访客下降",
                "C003_CHANNEL_TRAFFIC_WEAKNESS",
                "A002_RECOVER_QUALITY_TRAFFIC",
            ),
        ),
    ),
    (
        "流量稳定但转化下降",
        (
            (
                "finding-conversion",
                "R003_CONVERSION_DECLINE",
                "支付转化率下降",
                "C004_PRODUCT_PAGE_FRICTION",
                "A003_AUDIT_CONVERSION_FUNNEL",
            ),
        ),
    ),
    (
        "广告投入增加但销售未增长",
        (
            (
                "finding-ad-spend",
                "R005_AD_SPEND_UP_WITHOUT_SALES_GROWTH",
                "广告投入增加但销售未增长",
                "C005_AD_TRAFFIC_EFFICIENCY",
                "A004_REVIEW_CAMPAIGN_EFFICIENCY",
            ),
            (
                "finding-roas",
                "R004_ROAS_DECLINE",
                "ROAS下降",
                "C005_AD_TRAFFIC_EFFICIENCY",
                "A005_REALLOCATE_AD_BUDGET",
            ),
        ),
    ),
    (
        "销售增长但毛利下降",
        (
            (
                "finding-margin",
                "R006_GROSS_MARGIN_DECLINE",
                "毛利率下降",
                "C006_COST_OR_DISCOUNT_PRESSURE",
                "A006_REVIEW_MARGIN_DRIVERS",
            ),
        ),
    ),
    (
        "重点商品下降并伴随库存风险",
        (
            (
                "finding-key-product",
                "R010_KEY_PRODUCT_SALES_DECLINE",
                "重点商品销售下降",
                "C011_PRODUCT_DEMAND_WEAKNESS",
                "A013_REVIEW_KEY_PRODUCT",
            ),
            (
                "finding-high-inventory",
                "R009_INVENTORY_DAYS_HIGH",
                "库存可售天数偏高",
                "C010_DEMAND_BELOW_STOCK_PLAN",
                "A012_PLAN_INVENTORY_CLEARANCE",
            ),
        ),
    ),
)


def make_golden_payload(name: str, finding_specs: tuple[tuple[str, ...], ...]):
    return {
        "schema_version": "phase3-ai-report-v0.3",
        "analysis_scope": {
            "source_name": name,
            "start_date": "2026-01-01",
            "end_date": "2026-01-30",
            "categories": [],
            "product_ids": [],
        },
        "kpi_summary": [],
        "findings": [
            {
                "finding_id": finding_id,
                "rule_id": rule_id,
                "title": title,
                "priority": "high",
                "evidence": [],
                "cause_candidates": [
                    {
                        "cause_id": cause_id,
                        "cause_name": "固定场景候选原因",
                        "description": "仅用于 Prompt 边界测试。",
                    }
                ],
                "action_candidates": [
                    {
                        "action_id": action_id,
                        "action_name": "固定场景候选行动",
                        "owner": "运营",
                        "suggested_period": "3天内",
                        "observe_metric": "sales_amount",
                    }
                ],
            }
            for finding_id, rule_id, title, cause_id, action_id in finding_specs
        ],
    }


def test_system_prompt_defines_role_allowed_tasks_and_forbidden_actions() -> None:
    for required_text in (
        "电商经营分析助手",
        "综合已有 Finding",
        "解释问题关联",
        "候选 Cause",
        "候选 Action",
        "验证方法",
        "数据限制",
        "原始 CSV",
        "创建新的 Finding",
        "创建新的 Cause ID",
        "创建新的 Action ID",
        "修改或重新计算 Finding Priority",
        "重新计算指标",
        "编造数字",
        "确定因果",
    ):
        assert required_text in SYSTEM_PROMPT


def test_json_constraints_define_frozen_shape_and_reference_rules() -> None:
    for field_name in (
        "executive_summary",
        "finding_explanations",
        "cross_issue_insights",
        "cause_hypotheses",
        "recommended_actions",
        "limitations",
        "finding_id",
        "cause_id",
        "action_id",
        "action_sequence",
    ):
        assert field_name in JSON_OUTPUT_CONSTRAINTS

    assert "cause_candidate_ids" in JSON_OUTPUT_CONSTRAINTS
    assert "action_candidate_ids" in JSON_OUTPUT_CONSTRAINTS
    assert "只返回一个 JSON 对象" in JSON_OUTPUT_CONSTRAINTS
    assert "Markdown" in JSON_OUTPUT_CONSTRAINTS


@pytest.mark.parametrize(("scenario_name", "finding_specs"), GOLDEN_SCENARIOS)
def test_user_prompt_contains_each_fixed_golden_scenario(
    scenario_name: str, finding_specs: tuple[tuple[str, ...], ...]
) -> None:
    payload = make_golden_payload(scenario_name, finding_specs)

    system_prompt, user_prompt = build_ai_report_prompt(payload)

    assert SYSTEM_PROMPT in system_prompt
    assert JSON_OUTPUT_CONSTRAINTS in system_prompt
    assert scenario_name in user_prompt
    for finding_id, rule_id, _title, cause_id, action_id in finding_specs:
        assert finding_id in user_prompt
        assert rule_id in user_prompt
        assert cause_id in user_prompt
        assert action_id in user_prompt


def test_prompt_builder_is_deterministic_and_does_not_modify_payload() -> None:
    scenario_name, finding_specs = GOLDEN_SCENARIOS[0]
    payload = make_golden_payload(scenario_name, finding_specs)
    original = deepcopy(payload)

    first = build_ai_report_prompt(payload)
    second = build_ai_report_prompt(payload)

    assert first == second
    assert payload == original
    assert "{payload_json}" in USER_PROMPT_TEMPLATE
    serialized_payload = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
    )
    assert serialized_payload in first[1]
