"""
Base classes and interfaces for AI providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ProviderType(Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GATEWAY = "gateway"  # AIssential Gateway (routes to best provider)
    MISTRAL = "mistral"
    GOOGLE = "google"
    OLLAMA = "ollama"  # Local models


@dataclass
class AIMessage:
    """Represents a message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None  # Optional name for multi-agent scenarios


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    content: str
    provider: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)  # tokens used
    raw_response: Optional[Dict[str, Any]] = None  # Original provider response

    @property
    def total_tokens(self) -> int:
        """Total tokens used (prompt + completion)."""
        return self.usage.get("total_tokens", 0)


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All providers must implement this interface to be usable through the AI Hub.
    """

    provider_type: ProviderType

    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider (or from env)
            **kwargs: Provider-specific configuration
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        **kwargs
    ) -> AIResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of messages in the conversation
            model: Model to use (provider-specific)
            system: System prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            **kwargs: Provider-specific options

        Returns:
            AIResponse with the completion
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.

        Returns:
            List of model identifiers
        """
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model to use if none specified."""
        pass

    @property
    def name(self) -> str:
        """Human-readable provider name."""
        return self.provider_type.value


class ProviderConfig:
    """Configuration for a provider."""

    def __init__(
        self,
        provider_type: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs
    ):
        self.provider_type = provider_type
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.extra = kwargs
