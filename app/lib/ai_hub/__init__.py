"""
AI Hub - Multi-provider AI abstraction layer.

Supports multiple AI providers with a unified interface:
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude) - via Gateway or direct
- Mistral (future)
- Google (Gemini) - future
- Local models (Ollama) - future

Usage:
    from app.lib.ai_hub import get_ai_client, ask_ai

    # Simple usage
    response = ask_ai("Analyze this contract...", provider="openai")

    # Advanced usage
    client = get_ai_client("openai")
    response = client.chat(messages=[...])
"""

from .hub import AIHub, get_ai_client, ask_ai, get_hub
from .base import AIProvider, AIMessage, AIResponse
from .providers import OpenAIProvider

__all__ = [
    "AIHub",
    "get_hub",
    "get_ai_client",
    "ask_ai",
    "AIProvider",
    "AIMessage",
    "AIResponse",
    "OpenAIProvider",
]
