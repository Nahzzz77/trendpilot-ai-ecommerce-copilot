"""Create the configured AI provider without coupling callers to a vendor."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from src.ai_provider import AIProvider
from src.providers.deepseek_provider import create_deepseek_provider
from src.providers.openai_provider import create_openai_provider


DEFAULT_AI_PROVIDER = "deepseek"
_CONFIG_KEYS = ("AI_PROVIDER", "AI_API_KEY", "AI_MODEL", "AI_BASE_URL")


class UnsupportedAIProviderError(ValueError):
    """Raised when ``AI_PROVIDER`` names an unsupported provider."""


def _clean_config_value(value: object) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _read_streamlit_secrets() -> Mapping[str, object]:
    try:
        import streamlit as st

        return {key: st.secrets.get(key) for key in _CONFIG_KEYS}
    except Exception:
        return {}


def _get_config_value(
    name: str,
    environ: Mapping[str, str],
    secrets: Mapping[str, object],
) -> str | None:
    return _clean_config_value(environ.get(name)) or _clean_config_value(
        secrets.get(name)
    )


def create_ai_provider(
    *,
    environ: Mapping[str, str] | None = None,
    secrets: Mapping[str, object] | None = None,
    client: Any | None = None,
) -> AIProvider | None:
    """Create the configured provider, defaulting to DeepSeek."""
    environment = os.environ if environ is None else environ
    secret_values = _read_streamlit_secrets() if secrets is None else secrets
    provider_name = (
        _get_config_value("AI_PROVIDER", environment, secret_values)
        or DEFAULT_AI_PROVIDER
    ).lower()

    if provider_name == "deepseek":
        return create_deepseek_provider(
            environ=environment,
            secrets=secret_values,
            client=client,
        )
    if provider_name == "openai":
        return create_openai_provider(
            environ=environment,
            secrets=secret_values,
            client=client,
        )
    raise UnsupportedAIProviderError(
        f"Unsupported AI provider: {provider_name}"
    )


__all__ = [
    "DEFAULT_AI_PROVIDER",
    "UnsupportedAIProviderError",
    "create_ai_provider",
]
