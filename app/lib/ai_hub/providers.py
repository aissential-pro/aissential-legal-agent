"""
AI Provider implementations.

Each provider implements the AIProvider interface for consistent usage.
"""

import os
import time
import logging
from typing import List, Optional, Dict, Any

import requests

from .base import AIProvider, AIMessage, AIResponse, ProviderType

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API provider (GPT-4, GPT-4o, etc.)"""

    provider_type = ProviderType.OPENAI

    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4o-mini",
        **kwargs
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self._default_model = default_model

        if not self.api_key:
            raise ValueError("OpenAI API key required (set OPENAI_API_KEY)")

    @property
    def default_model(self) -> str:
        return self._default_model

    def list_models(self) -> List[str]:
        return self.MODELS.copy()

    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        retries: int = 3,
        **kwargs
    ) -> AIResponse:
        model = model or self.default_model

        # Build messages
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})

        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

                return AIResponse(
                    content=data["choices"][0]["message"]["content"],
                    provider=self.name,
                    model=model,
                    usage={
                        "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                        "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                        "total_tokens": data.get("usage", {}).get("total_tokens", 0),
                    },
                    raw_response=data,
                )

            except requests.exceptions.RequestException as e:
                logger.warning(f"OpenAI request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise


class AnthropicProvider(AIProvider):
    """Anthropic API provider (Claude models) - Direct API access."""

    provider_type = ProviderType.ANTHROPIC

    MODELS = [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.anthropic.com/v1",
        default_model: str = "claude-sonnet-4-20250514",
        **kwargs
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url
        self._default_model = default_model

        if not self.api_key:
            raise ValueError("Anthropic API key required (set ANTHROPIC_API_KEY)")

    @property
    def default_model(self) -> str:
        return self._default_model

    def list_models(self) -> List[str]:
        return self.MODELS.copy()

    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        retries: int = 3,
        **kwargs
    ) -> AIResponse:
        model = model or self.default_model

        # Build messages (Anthropic format)
        api_messages = []
        for msg in messages:
            if msg.role != "system":  # System is separate in Anthropic
                api_messages.append({"role": msg.role, "content": msg.content})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }

        if system:
            payload["system"] = system

        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

                return AIResponse(
                    content=data["content"][0]["text"],
                    provider=self.name,
                    model=model,
                    usage={
                        "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                        "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                        "total_tokens": (
                            data.get("usage", {}).get("input_tokens", 0) +
                            data.get("usage", {}).get("output_tokens", 0)
                        ),
                    },
                    raw_response=data,
                )

            except requests.exceptions.RequestException as e:
                logger.warning(f"Anthropic request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise


class MistralProvider(AIProvider):
    """Mistral AI provider (for future use)."""

    provider_type = ProviderType.MISTRAL

    MODELS = [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "codestral-latest",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.mistral.ai/v1",
        default_model: str = "mistral-small-latest",
        **kwargs
    ):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.base_url = base_url
        self._default_model = default_model

        if not self.api_key:
            raise ValueError("Mistral API key required (set MISTRAL_API_KEY)")

    @property
    def default_model(self) -> str:
        return self._default_model

    def list_models(self) -> List[str]:
        return self.MODELS.copy()

    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        retries: int = 3,
        **kwargs
    ) -> AIResponse:
        model = model or self.default_model

        # Mistral uses OpenAI-compatible format
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})

        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

                return AIResponse(
                    content=data["choices"][0]["message"]["content"],
                    provider=self.name,
                    model=model,
                    usage={
                        "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                        "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                        "total_tokens": data.get("usage", {}).get("total_tokens", 0),
                    },
                    raw_response=data,
                )

            except requests.exceptions.RequestException as e:
                logger.warning(f"Mistral request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise


# Provider registry
PROVIDERS: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "mistral": MistralProvider,
}


def get_provider_class(provider_name: str) -> type:
    """Get provider class by name."""
    if provider_name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
    return PROVIDERS[provider_name]
