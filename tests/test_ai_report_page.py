import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src import ai_provider_factory as ai_provider_factory_module
from src.ai_provider import AI_REPORT_SCHEMA
from src.ai_report_payload import build_ai_report_payload
from src.data_loader import load_sample_data
from src.diagnosis_context import build_diagnosis_context
from src.diagnosis_engine import run_diagnosis
from src.fake_ai_provider import FakeAIProvider
from src.providers.deepseek_provider import DeepSeekProvider
from src.providers.openai_provider import OpenAIProvider


AI_REPORT_PAGE = (
    Path(__file__).resolve().parents[1] / "pages" / "2_AI经营诊断.py"
)
PROVIDER_SESSION_KEY = "ai_report_provider"
RESULT_SESSION_KEY = "ai_report_result"


class RecordingFakeProvider(FakeAIProvider):
    def __init__(self) -> None:
        self.call_count = 0

    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        self.call_count += 1
        return super().generate_report(payload, schema)


class FailingProvider:
    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        raise RuntimeError("simulated provider failure")


class InvalidReferenceProvider(FakeAIProvider):
    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        report = json.loads(super().generate_report(payload, schema))
        report["finding_explanations"][0]["finding_id"] = "finding-unknown"
        return json.dumps(report, ensure_ascii=False)


def _loaded_app(provider=...) -> AppTest:
    app = AppTest.from_file(str(AI_REPORT_PAGE))
    app.session_state["sales_data"] = load_sample_data()
    app.session_state["sales_data_source"] = "项目示例数据"
    if provider is not ...:
        app.session_state[PROVIDER_SESSION_KEY] = provider
    return app.run(timeout=30)


def _click_generate(app: AppTest) -> AppTest:
    button = next(
        item for item in app.button if item.label == "生成 AI 经营分析报告"
    )
    return button.click().run(timeout=30)


def _markdown_content(app: AppTest) -> str:
    return "\n".join(element.value for element in app.markdown)


def _stable_no_finding_data() -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=60, freq="D")
    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "product_id": "P001",
            "product_name": "稳定款外套",
            "category": "外套",
            "price": 100.0,
            "cost": 50.0,
            "impressions": 1000,
            "visitors": 100,
            "product_clicks": 50,
            "add_to_cart": 10,
            "orders": 5,
            "units_sold": 5,
            "sales_amount": 500.0,
            "ad_spend": 50.0,
            "refund_units": 0,
            "inventory": 200,
            "rating": 4.5,
        }
    )


def _mock_openai_provider() -> tuple[OpenAIProvider, MagicMock]:
    sample = load_sample_data()
    context = build_diagnosis_context(
        sample,
        date(2026, 5, 31),
        date(2026, 6, 29),
        (),
        (),
        source_name="项目示例数据",
    )
    findings = tuple(run_diagnosis(context))
    payload = build_ai_report_payload(context, findings)
    raw_report = FakeAIProvider().generate_report(payload, AI_REPORT_SCHEMA)
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(output_text=raw_report)
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )
    return provider, client


def _mock_deepseek_provider(
    *,
    invalid_finding_reference: bool = False,
) -> tuple[DeepSeekProvider, MagicMock]:
    sample = load_sample_data()
    context = build_diagnosis_context(
        sample,
        date(2026, 5, 31),
        date(2026, 6, 29),
        (),
        (),
        source_name="项目示例数据",
    )
    findings = tuple(run_diagnosis(context))
    payload = build_ai_report_payload(context, findings)
    raw_report = FakeAIProvider().generate_report(payload, AI_REPORT_SCHEMA)
    if invalid_finding_reference:
        report = json.loads(raw_report)
        report["finding_explanations"][0]["finding_id"] = "finding-unknown"
        raw_report = json.dumps(report, ensure_ascii=False)
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=raw_report))]
    )
    provider = DeepSeekProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )
    return provider, client


def test_ai_report_area_has_scope_and_generate_button() -> None:
    app = _loaded_app()

    assert not app.exception
    assert any(item.value == "AI增强分析" for item in app.subheader)
    assert any(
        "当前分析范围" in item.value and "2026-05-31 至 2026-06-29" in item.value
        for item in app.caption
    )
    assert any(
        item.label == "生成 AI 经营分析报告" for item in app.button
    )


def test_page_resolves_default_provider_through_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = MagicMock(return_value=RecordingFakeProvider())
    monkeypatch.setattr(ai_provider_factory_module, "create_ai_provider", factory)

    app = _loaded_app()

    assert not app.exception
    assert factory.call_count == 1
    page_source = AI_REPORT_PAGE.read_text(encoding="utf-8")
    assert "create_ai_provider" in page_source
    assert "create_openai_provider" not in page_source


def test_fake_provider_success_renders_validated_ai_report() -> None:
    provider = RecordingFakeProvider()
    app = _click_generate(_loaded_app(provider))

    assert not app.exception
    assert provider.call_count == 1
    assert app.session_state[RESULT_SESSION_KEY].status == "success"
    assert any("AI 报告生成成功" in item.value for item in app.success)
    content = _markdown_content(app)
    for heading in [
        "经营摘要",
        "重点问题分析",
        "原因假设",
        "行动顺序",
        "数据限制",
    ]:
        assert heading in content
    assert "当前存在需要关注的经营问题" in content


def test_mock_openai_provider_success_renders_separated_ai_report_layers() -> None:
    provider, client = _mock_openai_provider()
    app = _click_generate(_loaded_app(provider))

    assert not app.exception
    assert client.responses.create.call_count == 1
    assert app.session_state[RESULT_SESSION_KEY].status == "success"
    content = _markdown_content(app)
    for label in [
        "【数据证据】",
        "【系统判断】",
        "AI解读",
        "原因假设",
        "行动建议",
        "数据限制",
    ]:
        assert label in content


def test_deepseek_factory_provider_generates_validated_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, client = _mock_deepseek_provider()
    factory = MagicMock(return_value=provider)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.setattr(ai_provider_factory_module, "create_ai_provider", factory)

    app = _click_generate(_loaded_app())

    assert not app.exception
    assert factory.call_count >= 1
    assert client.chat.completions.create.call_count == 1
    assert app.session_state[RESULT_SESSION_KEY].status == "success"
    assert "经营摘要" in _markdown_content(app)


def test_invalid_deepseek_report_is_rejected_without_rendering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, client = _mock_deepseek_provider(invalid_finding_reference=True)
    factory = MagicMock(return_value=provider)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.setattr(ai_provider_factory_module, "create_ai_provider", factory)

    app = _click_generate(_loaded_app())

    assert not app.exception
    assert client.chat.completions.create.call_count == 1
    assert app.session_state[RESULT_SESSION_KEY].status == "validation_error"
    assert any("AI 报告未通过校验" in item.value for item in app.error)
    assert "经营摘要" not in _markdown_content(app)


def test_default_provider_without_key_shows_configuration_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.setattr(
        ai_provider_factory_module,
        "_read_streamlit_secrets",
        lambda: {},
    )

    app = _loaded_app()

    assert not app.exception
    assert any(
        item.value == "当前未配置AI服务，仍可查看确定性诊断结果"
        for item in app.info
    )
    assert RESULT_SESSION_KEY not in app.session_state
    assert "【数据证据】" in _markdown_content(app)


def test_missing_ai_configuration_keeps_deterministic_findings_available() -> None:
    app = _click_generate(_loaded_app(None))

    assert not app.exception
    assert app.session_state[RESULT_SESSION_KEY].status == "unavailable"
    assert any(
        item.value == "当前未配置AI服务，仍可查看确定性诊断结果"
        for item in app.info
    )
    assert "【数据证据】" in _markdown_content(app)


@pytest.mark.parametrize(
    ("provider", "expected_message"),
    [
        (FailingProvider(), "AI 报告生成失败"),
        (InvalidReferenceProvider(), "AI 报告未通过校验"),
    ],
    ids=["provider-error", "validation-error"],
)
def test_failed_or_invalid_report_is_not_displayed(
    provider, expected_message: str
) -> None:
    app = _click_generate(_loaded_app(provider))

    assert not app.exception
    assert any(expected_message in item.value for item in app.error)
    assert "经营摘要" not in _markdown_content(app)


def test_filter_change_invalidates_previous_ai_report() -> None:
    app = _click_generate(_loaded_app(RecordingFakeProvider()))
    assert RESULT_SESSION_KEY in app.session_state
    assert "经营摘要" in _markdown_content(app)

    selected_category = app.multiselect[0].options[0]
    app.multiselect[0].set_value([selected_category]).run(timeout=30)

    assert not app.exception
    assert RESULT_SESSION_KEY not in app.session_state
    assert "经营摘要" not in _markdown_content(app)


def test_no_findings_does_not_call_ai_provider() -> None:
    provider = RecordingFakeProvider()
    app = AppTest.from_file(str(AI_REPORT_PAGE))
    app.session_state["sales_data"] = _stable_no_finding_data()
    app.session_state["sales_data_source"] = "无异常测试数据"
    app.session_state[PROVIDER_SESSION_KEY] = provider

    app.run(timeout=30)

    assert not app.exception
    assert provider.call_count == 0
    assert RESULT_SESSION_KEY not in app.session_state
    assert any("未触发诊断规则" in item.value for item in app.success)
    assert any("无需生成 AI 报告" in item.value for item in app.info)
