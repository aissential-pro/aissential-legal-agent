"""
AI Hub - Central manager for AI providers.

The Hub provides a unified interface to multiple AI providers,
with automatic provider selection, caching, and fallback support.
"""

import os
import logging
from typing import Optional, Dict, List

from .base import AIProvider, AIMessage, AIResponse, ProviderType
from .providers import PROVIDERS, get_provider_class

logger = logging.getLogger(__name__)


class AIHub:
    """
    Central hub for managing AI providers.

    Features:
    - Unified interface for all providers
    - Automatic provider selection based on available API keys
    - Provider caching (singleton per provider type)
    - Easy provider switching via configuration

    Usage:
        hub = AIHub()
        response = hub.chat("openai", messages=[...])

        # Or with auto-selection
        response = hub.auto_chat(messages=[...])
    """

    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        self._default_provider: Optional[str] = None
        self._detect_available_providers()

    def _detect_available_providers(self):
        """Detect which providers have API keys configured."""
        env_to_provider = {
            "OPENAI_API_KEY": "openai",
            "ANTHROPIC_API_KEY": "anthropic",
            "MISTRAL_API_KEY": "mistral",
            "GATEWAY_API_KEY": "gateway",
        }

        available = []
        for env_var, provider in env_to_provider.items():
            if os.getenv(env_var):
                available.append(provider)
                if self._default_provider is None:
                    self._default_provider = provider

        if available:
            logger.info(f"AI Hub: Available providers: {', '.join(available)}")
            logger.info(f"AI Hub: Default provider: {self._default_provider}")
        else:
            logger.warning("AI Hub: No AI providers configured!")

    def get_provider(self, provider_name: str) -> AIProvider:
        """
        Get or create a provider instance.

        Args:
            provider_name: Provider identifier (openai, anthropic, etc.)

        Returns:
            AIProvider instance
        """
        if provider_name not in self._providers:
            provider_class = get_provider_class(provider_name)
            self._providers[provider_name] = provider_class()
            logger.debug(f"AI Hub: Created {provider_name} provider")

        return self._providers[provider_name]

    def chat(
        self,
        provider_name: str,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        Send a chat request to a specific provider.

        Args:
            provider_name: Provider to use
            messages: Conversation messages
            model: Model override (uses provider default if not specified)
            system: System prompt
            **kwargs: Provider-specific options

        Returns:
            AIResponse with the completion
        """
        provider = self.get_provider(provider_name)
        return provider.chat(messages, model=model, system=system, **kwargs)

    def auto_chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        Send a chat request, automatically selecting the best provider.

        Uses preferred_provider if specified, otherwise the default.

        Args:
            messages: Conversation messages
            model: Model override
            system: System prompt
            preferred_provider: Preferred provider (if available)
            **kwargs: Provider-specific options

        Returns:
            AIResponse with the completion
        """
        provider_name = preferred_provider or self._default_provider

        if not provider_name:
            raise ValueError("No AI provider configured. Set an API key (OPENAI_API_KEY, etc.)")

        return self.chat(provider_name, messages, model=model, system=system, **kwargs)

    def list_providers(self) -> List[str]:
        """List all available provider names."""
        return list(PROVIDERS.keys())

    def list_available_providers(self) -> List[str]:
        """List providers that have API keys configured."""
        available = []
        env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        for provider, env_var in env_map.items():
            if os.getenv(env_var):
                available.append(provider)
        return available

    @property
    def default_provider(self) -> Optional[str]:
        """Get the default provider name."""
        return self._default_provider

    @default_provider.setter
    def default_provider(self, provider_name: str):
        """Set the default provider."""
        if provider_name not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")
        self._default_provider = provider_name


# Global hub instance
_hub: Optional[AIHub] = None


def get_hub() -> AIHub:
    """Get the global AI Hub instance."""
    global _hub
    if _hub is None:
        _hub = AIHub()
    return _hub


def get_ai_client(provider_name: str) -> AIProvider:
    """
    Get an AI provider client.

    Args:
        provider_name: Provider identifier (openai, anthropic, mistral)

    Returns:
        AIProvider instance
    """
    return get_hub().get_provider(provider_name)


def ask_ai(
    prompt: str,
    system: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    Simple function to ask AI a question.

    This is the easiest way to use the AI Hub.

    Args:
        prompt: The question/prompt to send
        system: Optional system prompt
        provider: Provider to use (auto-selects if not specified)
        model: Model to use (provider default if not specified)
        **kwargs: Additional options

    Returns:
        Response text from the AI

    Example:
        response = ask_ai("What is 2+2?")
        response = ask_ai("Analyze this contract...", provider="openai")
    """
    hub = get_hub()
    messages = [AIMessage(role="user", content=prompt)]

    if provider:
        response = hub.chat(provider, messages, system=system, model=model, **kwargs)
    else:
        response = hub.auto_chat(messages, system=system, model=model, **kwargs)

    return response.content
