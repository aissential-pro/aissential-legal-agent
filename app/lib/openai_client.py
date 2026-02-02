"""
OpenAI client for local testing.

This module provides a direct OpenAI interface for testing
when the Gateway is not available.
"""

import os
import time
import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Simple OpenAI API client for local testing."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        retries: int = 3,
    ) -> str:
        """
        Send a chat completion request to OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            retries: Number of retry attempts

        Returns:
            The assistant's response text
        """
        # Build messages with system prompt if provided
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": full_messages,
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
                return data["choices"][0]["message"]["content"]

            except requests.exceptions.RequestException as e:
                logger.warning(f"OpenAI request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

        return ""


# Singleton instance
_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create the OpenAI client singleton."""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client


def ask_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Simple function to ask OpenAI a question.

    Args:
        system_prompt: System instructions
        user_prompt: User's question
        model: OpenAI model to use

    Returns:
        Response text
    """
    client = get_openai_client()
    client.model = model
    return client.chat(
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
