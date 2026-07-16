from dataclasses import FrozenInstanceError

import pytest

from src.ai_report_models import (
    AIReport,
    AIReportGenerationResult,
    CauseHypothesis,
    CrossIssueInsight,
    FindingExplanation,
    RecommendedAction,
)


def make_report() -> AIReport:
    return AIReport(
        executive_summary="当前经营表现承压，建议优先核查流量变化。",
        finding_explanations=(
            FindingExplanation(
                finding_id="finding-sales",
                explanation="销售下降与访客下降同时出现。",
                why_priority="该问题由规则引擎判定为高优先级。",
            ),
        ),
        cross_issue_insights=(
            CrossIssueInsight(
                finding_ids=("finding-sales", "finding-visitors"),
                insight="流量变化可能与销售承压相关。",
            ),
        ),
        cause_hypotheses=(
            CauseHypothesis(
                finding_id="finding-sales",
                cause_id="C001_TRAFFIC_DECLINE",
                hypothesis="有效流量减少可能影响销售表现。",
                validation_method="按渠道检查访客变化。",
            ),
        ),
        recommended_actions=(
            RecommendedAction(
                finding_id="finding-sales",
                action_id="A001_REVIEW_SALES_FUNNEL",
                action_sequence=1,
                reason="先确认销售漏斗中的主要损失环节。",
            ),
        ),
        limitations=("当前数据不能证明确定因果。",),
    )


def test_ai_report_models_follow_the_frozen_schema() -> None:
    report = make_report()

    assert report.finding_explanations[0].finding_id == "finding-sales"
    assert report.cross_issue_insights[0].finding_ids == (
        "finding-sales",
        "finding-visitors",
    )
    assert report.recommended_actions[0].action_sequence == 1
    assert report.limitations == ("当前数据不能证明确定因果。",)


def test_ai_report_models_are_immutable() -> None:
    report = make_report()

    with pytest.raises(FrozenInstanceError):
        report.executive_summary = "被修改的内容"  # type: ignore[misc]


def test_generation_result_keeps_validated_report_and_status() -> None:
    report = make_report()
    result = AIReportGenerationResult(
        status="success",
        report=report,
        message="报告生成成功。",
    )

    assert result.status == "success"
    assert result.report is report
    assert result.message == "报告生成成功。"
