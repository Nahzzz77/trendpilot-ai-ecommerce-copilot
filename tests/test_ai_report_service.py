import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from httpx import Request
from openai import APIConnectionError, APITimeoutError

from src.ai_prompt import JSON_OUTPUT_CONSTRAINTS, SYSTEM_PROMPT
from src.ai_provider import AI_REPORT_SCHEMA
from src.ai_report_payload import SCHEMA_VERSION, build_ai_report_payload
from src.ai_report_service import generate_ai_report
from src.fake_ai_provider import FakeAIProvider
from src.providers.openai_provider import OpenAIProvider
from tests.test_ai_report_payload import make_context, make_findings


class RecordingFakeProvider(FakeAIProvider):
    def __init__(self) -> None:
        self.call_count = 0
        self.payload: Mapping[str, object] | None = None
        self.schema: Mapping[str, object] | None = None

    def generate_report(
        self, payload: Mapping[str, object], schema: Mapping[str, object]
    ) -> str:
        self.call_count += 1
        self.payload = deepcopy(payload)
        self.schema = deepcopy(schema)
        return super().generate_report(payload, schema)


class MutatingReportProvider:
    def __init__(self, mutation: Callable[[dict[str, object]], None]) -> None:
        self._mutation = mutation

    def generate_report(
        self, payload: Mapping[str, object], schema: Mapping[str, object]
    ) -> str:
        report = json.loads(FakeAIProvider().generate_report(payload, schema))
        self._mutation(report)
        return json.dumps(report, ensure_ascii=False)


class InvalidStructureProvider:
    def generate_report(
        self, payload: Mapping[str, object], schema: Mapping[str, object]
    ) -> str:
        return '{"executive_summary": "结构不完整"}'


def test_service_runs_payload_provider_and_validator_chain() -> None:
    context = make_context()
    findings = make_findings()
    provider = RecordingFakeProvider()
    expected_payload = build_ai_report_payload(context, findings)

    result = generate_ai_report(context, findings, provider)

    assert result.status == "success"
    assert result.report is not None
    assert result.report.finding_explanations[0].finding_id == "finding-sales"
    assert provider.call_count == 1
    assert provider.payload == expected_payload
    assert provider.payload["schema_version"] == SCHEMA_VERSION
    assert SCHEMA_VERSION == AI_REPORT_SCHEMA["version"]
    assert provider.schema == AI_REPORT_SCHEMA


def test_service_accepts_valid_json_from_mocked_openai_provider() -> None:
    context = make_context()
    findings = make_findings()
    payload = build_ai_report_payload(context, findings)
    raw_report = FakeAIProvider().generate_report(payload, AI_REPORT_SCHEMA)
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(output_text=raw_report)
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    result = generate_ai_report(context, findings, provider)

    assert result.status == "success"
    assert result.report is not None
    assert result.report.recommended_actions[0].finding_id == "finding-sales"
    assert client.responses.create.call_count == 1
    request = client.responses.create.call_args.kwargs
    assert SYSTEM_PROMPT in request["input"][0]["content"]
    assert JSON_OUTPUT_CONSTRAINTS in request["input"][0]["content"]
    assert request["text"]["format"]["schema"] == AI_REPORT_SCHEMA["schema"]
    user_prompt = request["input"][1]["content"]
    assert f'"schema_version": "{SCHEMA_VERSION}"' in user_prompt
    for field_name in payload:
        assert f'"{field_name}"' in user_prompt


def _set_unknown_finding_id(report: dict[str, object]) -> None:
    report["finding_explanations"][0]["finding_id"] = "finding-unknown"


def _set_disallowed_cause_id(report: dict[str, object]) -> None:
    report["cause_hypotheses"][0][
        "cause_id"
    ] = "C003_CHANNEL_TRAFFIC_WEAKNESS"


def _set_disallowed_action_id(report: dict[str, object]) -> None:
    report["recommended_actions"][0][
        "action_id"
    ] = "A002_RECOVER_QUALITY_TRAFFIC"


@pytest.mark.parametrize(
    "mutation",
    [
        _set_unknown_finding_id,
        _set_disallowed_cause_id,
        _set_disallowed_action_id,
    ],
    ids=["unknown-finding", "disallowed-cause", "disallowed-action"],
)
def test_service_rejects_invalid_report_references(
    mutation: Callable[[dict[str, object]], None],
) -> None:
    provider = MutatingReportProvider(mutation)

    result = generate_ai_report(make_context(), make_findings(), provider)

    assert result.status == "validation_error"
    assert result.report is None
    assert result.message == "AI 报告未通过校验，确定性诊断结果不受影响。"


def _make_failed_openai_provider(failure: str) -> OpenAIProvider:
    client = MagicMock()
    request = Request("POST", "https://api.openai.com/v1/responses")
    if failure == "api_error":
        client.responses.create.side_effect = APIConnectionError(
            message="simulated api failure",
            request=request,
        )
    elif failure == "timeout":
        client.responses.create.side_effect = APITimeoutError(request)
    else:
        client.responses.create.return_value = SimpleNamespace(output_text="  ")
    return OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )


@pytest.mark.parametrize(
    "failure",
    ["api_error", "timeout", "empty_response"],
)
def test_service_converts_provider_failure_to_error_result(
    failure: str,
) -> None:
    provider = _make_failed_openai_provider(failure)

    result = generate_ai_report(make_context(), make_findings(), provider)

    assert result.status == "provider_error"
    assert result.report is None
    assert result.message == "AI 报告生成失败，确定性诊断结果不受影响。"
    assert "simulated" not in result.message


def test_service_does_not_call_provider_without_findings() -> None:
    provider = RecordingFakeProvider()

    result = generate_ai_report(make_context(), (), provider)

    assert result.status == "unavailable"
    assert result.report is None
    assert result.message == "当前没有可生成 AI 报告的诊断问题。"
    assert provider.call_count == 0


def test_service_returns_unavailable_without_provider() -> None:
    result = generate_ai_report(make_context(), make_findings(), None)

    assert result.status == "unavailable"
    assert result.report is None
    assert result.message == "当前未配置 AI 服务，可继续查看确定性诊断结果。"


def test_service_rejects_report_that_fails_validator() -> None:
    result = generate_ai_report(
        make_context(), make_findings(), InvalidStructureProvider()
    )

    assert result.status == "validation_error"
    assert result.report is None
    assert result.message == "AI 报告未通过校验，确定性诊断结果不受影响。"
