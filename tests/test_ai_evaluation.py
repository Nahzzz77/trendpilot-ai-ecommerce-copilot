import json
from dataclasses import replace

import pytest

from src.ai_provider import AI_REPORT_SCHEMA
from src.ai_report_models import AIReport
from src.ai_report_payload import build_ai_report_payload
from src.ai_report_validator import validate_ai_report
from src.diagnosis_models import DiagnosticFinding, Evidence, FindingScope
from src.fake_ai_provider import FakeAIProvider
from tests.test_ai_prompt import GOLDEN_SCENARIOS
from tests.test_ai_report_payload import make_context


HYPOTHESIS_MARKERS = ("可能", "假设", "待验证", "需验证", "进一步验证")


def _make_scenario_findings(
    finding_specs: tuple[tuple[str, ...], ...],
) -> tuple[DiagnosticFinding, ...]:
    return tuple(
        DiagnosticFinding(
            finding_id=finding_id,
            rule_id=rule_id,
            dimension="evaluation",
            scope=FindingScope("overall", None, "评估范围"),
            title=title,
            evidence=(
                Evidence(
                    metric_key="evaluation_metric",
                    current_value=1.0,
                    baseline_value=2.0,
                    change_value=-0.5,
                    change_type="relative",
                    unit="ratio",
                ),
            ),
            priority_score=80,
            priority="high",
            cause_candidate_ids=(cause_id,),
            action_candidate_ids=(action_id,),
        )
        for finding_id, rule_id, title, cause_id, action_id in finding_specs
    )


def _natural_language_fields(report: AIReport) -> tuple[str, ...]:
    fields = [report.executive_summary, *report.limitations]
    for explanation in report.finding_explanations:
        fields.extend((explanation.explanation, explanation.why_priority))
    for insight in report.cross_issue_insights:
        fields.append(insight.insight)
    for hypothesis in report.cause_hypotheses:
        fields.extend((hypothesis.hypothesis, hypothesis.validation_method))
    for action in report.recommended_actions:
        fields.append(action.reason)
    return tuple(fields)


@pytest.mark.parametrize(
    ("scenario_name", "finding_specs"),
    GOLDEN_SCENARIOS,
    ids=[scenario[0] for scenario in GOLDEN_SCENARIOS],
)
def test_golden_scenario_report_passes_automatic_quality_gates(
    scenario_name: str,
    finding_specs: tuple[tuple[str, ...], ...],
) -> None:
    findings = _make_scenario_findings(finding_specs)
    context = replace(make_context(), source_name=scenario_name)
    payload = build_ai_report_payload(context, findings)
    raw_report = FakeAIProvider().generate_report(payload, AI_REPORT_SCHEMA)

    parsed_report = json.loads(raw_report)
    report = validate_ai_report(raw_report, findings)

    assert set(parsed_report) == set(AI_REPORT_SCHEMA["schema"]["required"])
    assert payload["analysis_scope"]["source_name"] == scenario_name

    findings_by_id = {finding.finding_id: finding for finding in findings}
    referenced_finding_ids = {
        explanation.finding_id for explanation in report.finding_explanations
    }
    referenced_finding_ids.update(
        finding_id
        for insight in report.cross_issue_insights
        for finding_id in insight.finding_ids
    )
    referenced_finding_ids.update(
        hypothesis.finding_id for hypothesis in report.cause_hypotheses
    )
    referenced_finding_ids.update(
        action.finding_id for action in report.recommended_actions
    )
    assert referenced_finding_ids <= set(findings_by_id)

    assert all(
        hypothesis.cause_id
        in findings_by_id[hypothesis.finding_id].cause_candidate_ids
        for hypothesis in report.cause_hypotheses
    )
    assert all(
        action.action_id in findings_by_id[action.finding_id].action_candidate_ids
        for action in report.recommended_actions
    )
    assert all(
        not any(character.isdigit() for character in text)
        for text in _natural_language_fields(report)
    )
    assert all(
        any(marker in hypothesis.hypothesis for marker in HYPOTHESIS_MARKERS)
        for hypothesis in report.cause_hypotheses
    )
