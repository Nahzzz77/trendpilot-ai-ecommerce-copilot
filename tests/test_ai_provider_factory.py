from unittest.mock import MagicMock

import pytest

from src.ai_provider_factory import (
    DEFAULT_AI_PROVIDER,
    UnsupportedAIProviderError,
    create_ai_provider,
)
from src.providers.deepseek_provider import DeepSeekProvider
from src.providers.openai_provider import OpenAIProvider


def test_factory_defaults_to_deepseek() -> None:
    provider = create_ai_provider(
        environ={"AI_API_KEY": "test-key"},
        secrets={},
        client=MagicMock(),
    )

    assert DEFAULT_AI_PROVIDER == "deepseek"
    assert isinstance(provider, DeepSeekProvider)


def test_factory_selects_openai_explicitly() -> None:
    provider = create_ai_provider(
        environ={
            "AI_PROVIDER": "openai",
            "AI_API_KEY": "test-key",
            "AI_MODEL": "test-model",
        },
        secrets={},
        client=MagicMock(),
    )

    assert isinstance(provider, OpenAIProvider)


def test_factory_normalizes_provider_name() -> None:
    provider = create_ai_provider(
        environ={
            "AI_PROVIDER": " DeepSeek ",
            "AI_API_KEY": "test-key",
        },
        secrets={},
        client=MagicMock(),
    )

    assert isinstance(provider, DeepSeekProvider)


def test_factory_environment_provider_takes_precedence_over_secrets() -> None:
    provider = create_ai_provider(
        environ={
            "AI_PROVIDER": "openai",
            "AI_API_KEY": "env-key",
            "AI_MODEL": "env-model",
        },
        secrets={
            "AI_PROVIDER": "deepseek",
            "AI_API_KEY": "secret-key",
        },
        client=MagicMock(),
    )

    assert isinstance(provider, OpenAIProvider)


def test_factory_supports_streamlit_secrets() -> None:
    provider = create_ai_provider(
        environ={},
        secrets={
            "AI_PROVIDER": "deepseek",
            "AI_API_KEY": "secret-key",
            "AI_MODEL": "secret-model",
            "AI_BASE_URL": "https://secret.example/v1",
        },
        client=MagicMock(),
    )

    assert isinstance(provider, DeepSeekProvider)


@pytest.mark.parametrize("provider_name", ["deepseek", "openai"])
def test_factory_returns_none_without_api_key(provider_name: str) -> None:
    provider = create_ai_provider(
        environ={"AI_PROVIDER": provider_name},
        secrets={},
        client=MagicMock(),
    )

    assert provider is None


def test_factory_rejects_unknown_provider_without_silent_fallback() -> None:
    with pytest.raises(UnsupportedAIProviderError, match="unsupported-provider"):
        create_ai_provider(
            environ={
                "AI_PROVIDER": "unsupported-provider",
                "AI_API_KEY": "test-key",
            },
            secrets={},
            client=MagicMock(),
        )
