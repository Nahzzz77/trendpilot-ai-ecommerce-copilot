"""OpenAI implementation of the provider-neutral AI report interface."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.ai_prompt import build_ai_report_prompt


DEFAULT_OPENAI_MODEL = "gpt-5-mini"
DEFAULT_TIMEOUT_SECONDS = 30.0


class OpenAIProviderResponseError(RuntimeError):
    """Raised when OpenAI returns no usable report text."""


@dataclass(frozen=True, slots=True)
class OpenAIProviderConfig:
    """Runtime-only OpenAI configuration without any embedded credentials."""

    api_key: str
    model: str = DEFAULT_OPENAI_MODEL
    base_url: str | None = None
    timeout: float = DEFAULT_TIMEOUT_SECONDS


def _clean_config_value(value: object) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _read_streamlit_secrets() -> Mapping[str, object]:
    try:
        import streamlit as st

        return st.secrets
    except Exception:
        # Streamlit raises when no secrets file is configured. Missing optional
        # configuration is a supported state for the deterministic experience.
        return {}


def _get_config_value(
    name: str,
    environ: Mapping[str, str],
    secrets: Mapping[str, object],
) -> str | None:
    return _clean_config_value(environ.get(name)) or _clean_config_value(
        secrets.get(name)
    )


def load_openai_provider_config(
    *,
    environ: Mapping[str, str] | None = None,
    secrets: Mapping[str, object] | None = None,
) -> OpenAIProviderConfig | None:
    """Load OpenAI settings, preferring environment variables over secrets."""
    environment = os.environ if environ is None else environ
    secret_values = _read_streamlit_secrets() if secrets is None else secrets

    api_key = _get_config_value("AI_API_KEY", environment, secret_values)
    if api_key is None:
        return None

    model = (
        _get_config_value("AI_MODEL", environment, secret_values)
        or DEFAULT_OPENAI_MODEL
    )
    base_url = _get_config_value("AI_BASE_URL", environment, secret_values)
    return OpenAIProviderConfig(
        api_key=api_key,
        model=model,
        base_url=base_url,
    )


class OpenAIProvider:
    """Call OpenAI and return its untrusted structured report as text."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        client: Any | None = None,
    ) -> None:
        self._model = model
        if client is not None:
            self._client = client
            return

        from openai import OpenAI

        client_options: dict[str, object] = {
            "api_key": api_key,
            "timeout": timeout,
        }
        if base_url is not None:
            client_options["base_url"] = base_url
        self._client = OpenAI(**client_options)

    def generate_report(
        self,
        payload: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        """Generate one schema-constrained report without changing its inputs."""
        system_prompt, user_prompt = build_ai_report_prompt(payload)
        response = self._client.responses.create(
            model=self._model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema["name"],
                    "schema": schema["schema"],
                    "strict": True,
                }
            },
        )
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise OpenAIProviderResponseError(
                "OpenAI returned an empty report response."
            )
        return output_text


def create_openai_provider(
    *,
    environ: Mapping[str, str] | None = None,
    secrets: Mapping[str, object] | None = None,
    client: Any | None = None,
) -> OpenAIProvider | None:
    """Create the real provider, or return ``None`` when no key is configured."""
    config = load_openai_provider_config(environ=environ, secrets=secrets)
    if config is None:
        return None
    return OpenAIProvider(
        api_key=config.api_key,
        model=config.model,
        base_url=config.base_url,
        timeout=config.timeout,
        client=client,
    )


__all__ = [
    "DEFAULT_OPENAI_MODEL",
    "OpenAIProvider",
    "OpenAIProviderConfig",
    "OpenAIProviderResponseError",
    "create_openai_provider",
    "load_openai_provider_config",
]
