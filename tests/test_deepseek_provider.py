from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.ai_provider import AI_REPORT_SCHEMA, AIProvider
from src.providers.deepseek_provider import (
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODEL,
    DeepSeekProvider,
    DeepSeekProviderResponseError,
    create_deepseek_provider,
    load_deepseek_provider_config,
)


def make_mock_client(content: str = '{"executive_summary":"test"}') -> MagicMock:
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    return client


def test_deepseek_provider_implements_existing_provider_contract() -> None:
    provider = DeepSeekProvider(
        api_key="test-key",
        model="test-model",
        client=make_mock_client(),
    )

    assert isinstance(provider, AIProvider)


def test_deepseek_provider_calls_chat_completions_with_json_output() -> None:
    client = make_mock_client('{"executive_summary":"test"}')
    provider = DeepSeekProvider(
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
    call = client.chat.completions.create.call_args.kwargs
    assert call["model"] == "test-model"
    assert call["messages"][0]["role"] == "system"
    assert call["messages"][1]["role"] == "user"
    assert '"schema_version": "phase3-ai-report-v0.3"' in call["messages"][1][
        "content"
    ]
    assert call["response_format"] == {"type": "json_object"}
    assert payload == original_payload
    assert schema == original_schema


def test_deepseek_provider_propagates_api_errors() -> None:
    client = make_mock_client()
    client.chat.completions.create.side_effect = RuntimeError("simulated api failure")
    provider = DeepSeekProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(RuntimeError, match="simulated api failure"):
        provider.generate_report({}, AI_REPORT_SCHEMA)


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(choices=[]),
        SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="  "))]
        ),
    ],
    ids=["no-choices", "blank-content"],
)
def test_deepseek_provider_rejects_empty_responses(response: object) -> None:
    client = make_mock_client()
    client.chat.completions.create.return_value = response
    provider = DeepSeekProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(DeepSeekProviderResponseError, match="empty"):
        provider.generate_report({}, AI_REPORT_SCHEMA)


def test_deepseek_environment_configuration_takes_precedence_over_secrets() -> None:
    config = load_deepseek_provider_config(
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


def test_deepseek_configuration_uses_provider_defaults() -> None:
    config = load_deepseek_provider_config(
        environ={"AI_API_KEY": "test-key"},
        secrets={},
    )

    assert config is not None
    assert config.model == DEFAULT_DEEPSEEK_MODEL
    assert config.base_url == DEFAULT_DEEPSEEK_BASE_URL


def test_deepseek_streamlit_secrets_configuration_is_supported() -> None:
    config = load_deepseek_provider_config(
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


def test_missing_deepseek_api_key_returns_no_provider() -> None:
    provider = create_deepseek_provider(
        environ={},
        secrets={},
        client=make_mock_client(),
    )

    assert provider is None
