"""
Gateway client for LLM Gateway API.

Provides a client class for making requests to the AIssential LLM Gateway.
"""

import logging
import time
from typing import Any, Optional

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class GatewayError(Exception):
    """Exception raised for Gateway API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GatewayClient:
    """
    Client for interacting with the AIssential LLM Gateway.

    The Gateway provides centralized LLM access with authentication,
    rate limiting, and usage tracking.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        client_id: str,
        app_id: str,
        timeout: int = 120,
    ):
        """
        Initialize the Gateway client.

        Args:
            base_url: The base URL of the Gateway API (e.g., https://gateway.aissential.pro/v1)
            api_key: The Gateway API key for authentication
            client_id: The client identifier (e.g., "aissential-internal")
            app_id: The application identifier (e.g., "legal-agent")
            timeout: Request timeout in seconds (default: 120)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client_id = client_id
        self.app_id = app_id
        self.timeout = timeout

    def _build_headers(self, user_id: str, module_id: str) -> dict[str, str]:
        """
        Build the required headers for Gateway requests.

        Args:
            user_id: The user identifier making the request
            module_id: The module identifier for the operation

        Returns:
            Dictionary of headers required by the Gateway
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Client-Id": self.client_id,
            "X-User-Id": user_id,
            "X-App-Id": self.app_id,
            "X-Module-Id": module_id,
        }

    def request(
        self,
        model: str,
        messages: list[dict[str, Any]],
        user_id: str,
        module_id: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        priority: int = 3,
        sync: bool = True,
        retries: int = 3,
    ) -> dict[str, Any]:
        """
        Make a request to the Gateway chat completions endpoint.

        Args:
            model: The model to use (e.g., "claude-sonnet-4-20250514")
            messages: List of message dictionaries with 'role' and 'content'
            user_id: The user identifier making the request
            module_id: The module identifier for tracking
            system: Optional system prompt
            max_tokens: Maximum tokens in the response (default: 4096)
            priority: Request priority 1-5, lower is higher priority (default: 3)
            sync: Whether to wait for completion (default: True)
            retries: Number of retry attempts on failure (default: 3)

        Returns:
            The Gateway API response as a dictionary

        Raises:
            GatewayError: If the request fails after all retries
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers(user_id, module_id)

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "priority": priority,
            "sync": sync,
        }

        if system:
            payload["system"] = system

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                logger.debug(
                    f"Gateway request attempt {attempt + 1}/{retries} to {url}"
                )

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response.json()

                # Handle specific error codes
                if response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(
                        f"Rate limited by Gateway, waiting {retry_after}s"
                    )
                    time.sleep(retry_after)
                    continue

                if response.status_code >= 500:
                    # Server error - retry with backoff
                    logger.warning(
                        f"Gateway server error {response.status_code}, retrying..."
                    )
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                    continue

                # Client error - don't retry
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get(
                        "message", response.text
                    )
                except Exception:
                    pass

                raise GatewayError(
                    f"Gateway request failed: {error_detail}",
                    status_code=response.status_code,
                )

            except RequestException as e:
                last_error = e
                logger.warning(f"Gateway request error: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                continue

        error_msg = f"Gateway request failed after {retries} attempts"
        if last_error:
            error_msg = f"{error_msg}: {last_error}"
        raise GatewayError(error_msg)

    def get_content(self, response: dict[str, Any]) -> str:
        """
        Extract the text content from a Gateway response.

        Args:
            response: The Gateway API response dictionary

        Returns:
            The text content from the response

        Raises:
            GatewayError: If the response format is unexpected
        """
        try:
            # Handle standard OpenAI-style response format
            if "choices" in response:
                return response["choices"][0]["message"]["content"]

            # Handle Anthropic-style response format
            if "content" in response:
                content = response["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "")
                if isinstance(content, str):
                    return content

            raise GatewayError("Unexpected response format from Gateway")

        except (KeyError, IndexError, TypeError) as e:
            raise GatewayError(f"Failed to parse Gateway response: {e}")
