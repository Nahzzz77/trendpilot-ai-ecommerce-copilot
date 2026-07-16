import json

from src.ai_provider import AI_REPORT_SCHEMA, AIProvider
from src.ai_report_payload import build_ai_report_payload
from src.ai_report_validator import validate_ai_report
from src.fake_ai_provider import FakeAIProvider
from tests.test_ai_report_payload import make_context, make_findings


def test_fake_provider_implements_provider_contract() -> None:
    provider = FakeAIProvider()

    assert isinstance(provider, AIProvider)


def test_fake_provider_returns_deterministic_valid_report_without_credentials() -> None:
    provider = FakeAIProvider()
    findings = make_findings()
    payload = build_ai_report_payload(make_context(), findings)

    first_response = provider.generate_report(payload, AI_REPORT_SCHEMA)
    second_response = provider.generate_report(payload, AI_REPORT_SCHEMA)
    report = validate_ai_report(first_response, findings)

    assert first_response == second_response
    assert report.finding_explanations
    assert report.cross_issue_insights[0].finding_ids == (
        "finding-sales",
        "finding-visitors",
    )
    assert report.recommended_actions[0].action_sequence == 1


def test_provider_schema_matches_the_frozen_output_contract() -> None:
    properties = AI_REPORT_SCHEMA["schema"]["properties"]
    action_schema = properties["recommended_actions"]["items"]

    assert AI_REPORT_SCHEMA["name"] == "trendpilot_ai_report_v0_3"
    assert set(AI_REPORT_SCHEMA["schema"]["required"]) == {
        "executive_summary",
        "finding_explanations",
        "cross_issue_insights",
        "cause_hypotheses",
        "recommended_actions",
        "limitations",
    }
    assert action_schema["required"] == [
        "finding_id",
        "action_id",
        "action_sequence",
        "reason",
    ]
    json.dumps(AI_REPORT_SCHEMA, ensure_ascii=False, allow_nan=False)
