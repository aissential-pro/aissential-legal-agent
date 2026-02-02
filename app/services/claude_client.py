"""
AI client service using the AI Hub.

Provides a unified interface for contract analysis,
supporting multiple AI providers (OpenAI, Anthropic, etc.)
"""

import os
import logging

from app.lib.ai_hub import ask_ai, get_hub, AIMessage

logger = logging.getLogger(__name__)

# Default user ID for automated system operations
SYSTEM_USER_ID = "system-agent"

# Preferred provider order (will use first available)
PROVIDER_PRIORITY = ["gateway", "openai", "anthropic", "mistral"]


def _get_preferred_provider() -> str:
    """Determine the best provider to use based on available keys."""
    env_map = {
        "gateway": "GATEWAY_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "mistral": "MISTRAL_API_KEY",
    }

    for provider in PROVIDER_PRIORITY:
        if os.getenv(env_map.get(provider, "")):
            return provider

    raise ValueError("No AI provider configured. Set OPENAI_API_KEY or similar.")


def ask_claude(
    system_prompt: str,
    user_prompt: str,
    module_id: str = "analyze-contract",
    user_id: str = SYSTEM_USER_ID,
    retries: int = 3,
    provider: str = None,
    model: str = None,
) -> str:
    """
    Send a prompt to AI and return the response.

    Uses the AI Hub to route to the best available provider.

    Args:
        system_prompt: The system prompt to set AI behavior
        user_prompt: The user's message/query
        module_id: The module identifier for tracking (Gateway only)
        user_id: The user identifier (Gateway only)
        retries: Number of retry attempts on failure
        provider: Force a specific provider (auto-selects if None)
        model: Force a specific model (provider default if None)

    Returns:
        The text response from AI
    """
    # Determine provider
    if provider is None:
        provider = _get_preferred_provider()

    logger.info(f"Using AI provider: {provider}")

    # Use Gateway if available (has additional features)
    if provider == "gateway":
        return _ask_via_gateway(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            module_id=module_id,
            user_id=user_id,
            retries=retries,
        )

    # Use AI Hub for other providers
    return ask_ai(
        prompt=user_prompt,
        system=system_prompt,
        provider=provider,
        model=model,
        retries=retries,
    )


def _ask_via_gateway(
    system_prompt: str,
    user_prompt: str,
    module_id: str,
    user_id: str,
    retries: int,
) -> str:
    """Route request through the AIssential Gateway."""
    from app.config.settings import settings
    from app.lib.gateway.client import GatewayClient, GatewayError

    client = GatewayClient(
        base_url=settings.GATEWAY_BASE_URL,
        api_key=settings.GATEWAY_API_KEY,
        client_id=settings.GATEWAY_CLIENT_ID,
        app_id=settings.APP_ID,
    )

    messages = [{"role": "user", "content": user_prompt}]

    try:
        response = client.request(
            model=settings.CLAUDE_MODEL,
            messages=messages,
            user_id=user_id,
            module_id=module_id,
            system=system_prompt,
            max_tokens=4096,
            priority=3,
            sync=True,
            retries=retries,
        )
        return client.get_content(response)

    except GatewayError as e:
        logger.error(f"Gateway request failed: {e}")
        raise
