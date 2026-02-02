"""
Claude client service using the LLM Gateway.

Provides a simple interface for making Claude AI requests through
the AIssential LLM Gateway.
"""

import logging

from app.config.settings import settings
from app.lib.gateway.client import GatewayClient, GatewayError

logger = logging.getLogger(__name__)

# Default user ID for automated system operations
SYSTEM_USER_ID = "system-agent"

# Initialize Gateway client
_gateway_client = GatewayClient(
    base_url=settings.GATEWAY_BASE_URL,
    api_key=settings.GATEWAY_API_KEY,
    client_id=settings.GATEWAY_CLIENT_ID,
    app_id=settings.APP_ID,
)


def ask_claude(
    system_prompt: str,
    user_prompt: str,
    module_id: str,
    user_id: str = SYSTEM_USER_ID,
    retries: int = 3,
) -> str:
    """
    Send a prompt to Claude via the LLM Gateway and return the response.

    Args:
        system_prompt: The system prompt to set Claude's behavior
        user_prompt: The user's message/query
        module_id: The module identifier for Gateway tracking
        user_id: The user identifier (default: "system-agent" for automated scans)
        retries: Number of retry attempts on failure (default: 3)

    Returns:
        The text response from Claude

    Raises:
        GatewayError: If the request fails after all retries
    """
    messages = [{"role": "user", "content": user_prompt}]

    try:
        response = _gateway_client.request(
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

        return _gateway_client.get_content(response)

    except GatewayError as e:
        logger.error(f"Gateway request failed: {e}")
        raise
