"""DeepSeek implementation of the provider-neutral AI report interface."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.ai_prompt import build_ai_report_prompt


DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_TIMEOUT_SECONDS = 30.0
_CONFIG_KEYS = ("AI_API_KEY", "AI_MODEL", "AI_BASE_URL")


class DeepSeekProviderResponseError(RuntimeError):
    """Raised when DeepSeek returns no usable report text."""


@dataclass(frozen=True, slots=True)
class DeepSeekProviderConfig:
    """Runtime-only DeepSeek configuration without embedded credentials."""

    api_key: str
    model: str = DEFAULT_DEEPSEEK_MODEL
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL
    timeout: float = DEFAULT_TIMEOUT_SECONDS


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


def load_deepseek_provider_config(
    *,
    environ: Mapping[str, str] | None = None,
    secrets: Mapping[str, object] | None = None,
) -> DeepSeekProviderConfig | None:
    """Load DeepSeek settings, preferring environment variables over secrets."""
    environment = os.environ if environ is None else environ
    secret_values = _read_streamlit_secrets() if secrets is None else secrets

    api_key = _get_config_value("AI_API_KEY", environment, secret_values)
    if api_key is None:
        return None

    model = (
        _get_config_value("AI_MODEL", environment, secret_values)
        or DEFAULT_DEEPSEEK_MODEL
    )
    base_url = (
        _get_config_value("AI_BASE_URL", environment, secret_values)
        or DEFAULT_DEEPSEEK_BASE_URL
    )
    return DeepSeekProviderConfig(
        api_key=api_key,
        model=model,
        base_url=base_url,
    )


class DeepSeekProvider:
    """Call DeepSeek Chat Completions and return untrusted JSON text."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        client: Any | None = None,
    ) -> None:
        self._model = model
        if client is not None:
            self._client = client
            return

        from openai import OpenAI

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        """Generate JSON text without validating business-level references."""
        system_prompt, user_prompt = build_ai_report_prompt(payload)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        _ = schema
        choices = getattr(response, "choices", None)
        if not choices:
            raise DeepSeekProviderResponseError(
                "DeepSeek returned an empty report response."
            )
        message = getattr(choices[0], "message", None)
        output_text = getattr(message, "content", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise DeepSeekProviderResponseError(
                "DeepSeek returned an empty report response."
            )
        return output_text


def create_deepseek_provider(
    *,
    environ: Mapping[str, str] | None = None,
    secrets: Mapping[str, object] | None = None,
    client: Any | None = None,
) -> DeepSeekProvider | None:
    """Create the DeepSeek provider, or return ``None`` without an API key."""
    config = load_deepseek_provider_config(environ=environ, secrets=secrets)
    if config is None:
        return None
    return DeepSeekProvider(
        api_key=config.api_key,
        model=config.model,
        base_url=config.base_url,
        timeout=config.timeout,
        client=client,
    )


__all__ = [
    "DEFAULT_DEEPSEEK_BASE_URL",
    "DEFAULT_DEEPSEEK_MODEL",
    "DeepSeekProvider",
    "DeepSeekProviderConfig",
    "DeepSeekProviderResponseError",
    "create_deepseek_provider",
    "load_deepseek_provider_config",
]
