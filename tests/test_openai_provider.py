from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from httpx import Request
from openai import APIConnectionError, APITimeoutError

from src.ai_provider import AI_REPORT_SCHEMA, AIProvider
from src.ai_report_service import generate_ai_report
from src.providers.openai_provider import (
    OpenAIProvider,
    OpenAIProviderResponseError,
    create_openai_provider,
    load_openai_provider_config,
)
from tests.test_ai_report_payload import make_context, make_findings


def make_mock_client(output_text: str = '{"status":"ok"}') -> MagicMock:
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(output_text=output_text)
    return client


def test_openai_provider_implements_existing_provider_contract() -> None:
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=make_mock_client(),
    )

    assert isinstance(provider, AIProvider)


def test_openai_provider_calls_responses_api_with_frozen_prompt_and_schema() -> None:
    client = make_mock_client('{"executive_summary":"test"}')
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )
    payload = {
        "schema_version": "phase3-ai-report-v0.3",
        "findings": [{"finding_id": "finding-sales"}],
    }
    original_payload = deepcopy(payload)
    schema = deepcopy(AI_REPORT_SCHEMA)
    original_schema = deepcopy(schema)

    result = provider.generate_report(payload, schema)

    assert result == '{"executive_summary":"test"}'
    call = client.responses.create.call_args.kwargs
    assert call["model"] == "test-model"
    assert call["input"][0]["role"] == "system"
    assert call["input"][1]["role"] == "user"
    assert '"schema_version": "phase3-ai-report-v0.3"' in call["input"][1][
        "content"
    ]
    assert call["text"] == {
        "format": {
            "type": "json_schema",
            "name": AI_REPORT_SCHEMA["name"],
            "schema": AI_REPORT_SCHEMA["schema"],
            "strict": True,
        }
    }
    assert payload == original_payload
    assert schema == original_schema


def test_openai_provider_propagates_api_errors_to_the_service_layer() -> None:
    client = make_mock_client()
    api_error = APIConnectionError(
        message="simulated api failure",
        request=Request("POST", "https://api.openai.com/v1/responses"),
    )
    client.responses.create.side_effect = api_error
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(APIConnectionError, match="simulated api failure"):
        provider.generate_report({}, AI_REPORT_SCHEMA)


def test_openai_provider_propagates_timeout_errors_to_the_service_layer() -> None:
    client = make_mock_client()
    timeout_error = APITimeoutError(
        Request("POST", "https://api.openai.com/v1/responses")
    )
    client.responses.create.side_effect = timeout_error
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(APITimeoutError):
        provider.generate_report({}, AI_REPORT_SCHEMA)


def test_openai_provider_rejects_an_empty_model_response() -> None:
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=make_mock_client("  "),
    )

    with pytest.raises(OpenAIProviderResponseError, match="empty"):
        provider.generate_report({}, AI_REPORT_SCHEMA)


def test_environment_configuration_takes_precedence_over_secrets() -> None:
    config = load_openai_provider_config(
        environ={
            "AI_API_KEY": " env-test-key ",
            "AI_MODEL": " env-test-model ",
            "AI_BASE_URL": " https://env.example/v1 ",
        },
        secrets={
            "AI_API_KEY": "secret-test-key",
            "AI_MODEL": "secret-test-model",
            "AI_BASE_URL": "https://secret.example/v1",
        },
    )

    assert config is not None
    assert config.api_key == "env-test-key"
    assert config.model == "env-test-model"
    assert config.base_url == "https://env.example/v1"


def test_streamlit_secrets_configuration_is_supported_without_environment() -> None:
    config = load_openai_provider_config(
        environ={},
        secrets={
            "AI_API_KEY": "secret-test-key",
            "AI_MODEL": "secret-test-model",
            "AI_BASE_URL": "https://secret.example/v1",
        },
    )

    assert config is not None
    assert config.api_key == "secret-test-key"
    assert config.model == "secret-test-model"
    assert config.base_url == "https://secret.example/v1"


def test_missing_api_key_returns_no_provider_and_service_is_unavailable() -> None:
    provider = create_openai_provider(
        environ={},
        secrets={},
        client=make_mock_client(),
    )

    result = generate_ai_report(make_context(), make_findings(), provider)

    assert provider is None
    assert result.status == "unavailable"
    assert result.report is None
