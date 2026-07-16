import json

import pytest

from src.ai_report_models import AIReport
from src.ai_report_validator import AIReportValidationError, validate_ai_report
from tests.test_ai_report_payload import make_findings


def make_valid_report_data() -> dict[str, object]:
    return {
        "executive_summary": "销售与访客同时承压，建议优先复盘流量和销售漏斗。",
        "finding_explanations": [
            {
                "finding_id": "finding-sales",
                "explanation": "销售下降与访客变化同时出现。",
                "why_priority": "规则引擎已将其识别为高优先级问题。",
            }
        ],
        "cross_issue_insights": [
            {
                "finding_ids": ["finding-sales", "finding-visitors"],
                "insight": "流量下降可能与销售承压相关。",
            }
        ],
        "cause_hypotheses": [
            {
                "finding_id": "finding-sales",
                "cause_id": "C001_TRAFFIC_DECLINE",
                "hypothesis": "有效流量减少可能影响销售表现。",
                "validation_method": "按渠道核对访客变化。",
            }
        ],
        "recommended_actions": [
            {
                "finding_id": "finding-sales",
                "action_id": "A001_REVIEW_SALES_FUNNEL",
                "action_sequence": 1,
                "reason": "先定位销售漏斗中的主要损失环节。",
            },
            {
                "finding_id": "finding-visitors",
                "action_id": "A002_RECOVER_QUALITY_TRAFFIC",
                "action_sequence": 2,
                "reason": "再针对主要渠道恢复有效访客。",
            },
        ],
        "limitations": ["当前数据不能证明确定因果。"],
    }


def test_validator_parses_valid_json_into_ai_report() -> None:
    raw_json = json.dumps(make_valid_report_data(), ensure_ascii=False)

    report = validate_ai_report(raw_json, make_findings())

    assert isinstance(report, AIReport)
    assert report.finding_explanations[0].finding_id == "finding-sales"
    assert report.recommended_actions[1].action_sequence == 2


@pytest.mark.parametrize(
    ("mutation", "error_match"),
    [
        (lambda data: data.pop("limitations"), "缺少字段"),
        (lambda data: data.update({"unexpected": []}), "包含未允许字段"),
        (lambda data: data.update({"executive_summary": 123}), "必须是字符串"),
        (lambda data: data.update({"finding_explanations": "not-a-list"}), "必须是数组"),
    ],
)
def test_validator_rejects_invalid_structure(mutation, error_match: str) -> None:
    data = make_valid_report_data()
    mutation(data)

    with pytest.raises(AIReportValidationError, match=error_match):
        validate_ai_report(data, make_findings())


def test_validator_rejects_invalid_json() -> None:
    with pytest.raises(AIReportValidationError, match="不是有效 JSON"):
        validate_ai_report("```json\n{}\n```", make_findings())


def test_validator_rejects_unknown_finding_reference() -> None:
    data = make_valid_report_data()
    data["finding_explanations"][0]["finding_id"] = "finding-unknown"

    with pytest.raises(AIReportValidationError, match="finding_id 无效"):
        validate_ai_report(data, make_findings())


def test_validator_rejects_cause_not_allowed_for_referenced_finding() -> None:
    data = make_valid_report_data()
    data["cause_hypotheses"][0]["cause_id"] = "C003_CHANNEL_TRAFFIC_WEAKNESS"

    with pytest.raises(AIReportValidationError, match="cause_id 不属于"):
        validate_ai_report(data, make_findings())


def test_validator_rejects_action_not_allowed_for_referenced_finding() -> None:
    data = make_valid_report_data()
    data["recommended_actions"][0]["action_id"] = "A002_RECOVER_QUALITY_TRAFFIC"

    with pytest.raises(AIReportValidationError, match="action_id 不属于"):
        validate_ai_report(data, make_findings())


@pytest.mark.parametrize(
    "finding_ids",
    [
        ["finding-sales", "finding-unknown"],
        ["finding-sales"],
        ["finding-sales", "finding-sales"],
    ],
)
def test_validator_rejects_invalid_cross_issue_references(finding_ids) -> None:
    data = make_valid_report_data()
    data["cross_issue_insights"][0]["finding_ids"] = finding_ids

    with pytest.raises(AIReportValidationError, match="cross_issue_insights"):
        validate_ai_report(data, make_findings())


@pytest.mark.parametrize(
    "sequences",
    [
        [0, 1],
        [1, 1],
        [1, 3],
        [True, 2],
    ],
)
def test_validator_rejects_invalid_action_sequence(sequences) -> None:
    data = make_valid_report_data()
    for action, sequence in zip(data["recommended_actions"], sequences):
        action["action_sequence"] = sequence

    with pytest.raises(AIReportValidationError, match="action_sequence"):
        validate_ai_report(data, make_findings())
