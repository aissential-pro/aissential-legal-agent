"""
AI Connector Client

Retrieves credentials from the centralized AIssential Connector service.
This allows credentials to be configured once and shared across apps.
"""
import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ConnectorClient:
    """Client for the AIssential AI Connector service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        app_id: str = "legal-agent"
    ):
        self.base_url = base_url or os.getenv("CONNECTOR_BASE_URL", "https://connector.aissential.pro/v1")
        self.api_key = api_key or os.getenv("CONNECTOR_API_KEY")
        self.app_id = app_id
        self._cache: Dict[str, Any] = {}

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-App-Id": self.app_id,
            "Content-Type": "application/json"
        }

    def get_credentials(self, service: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get credentials for a service (telegram, google-drive, etc.)

        Args:
            service: Service name (telegram, google-drive, anthropic, etc.)
            use_cache: Whether to use cached credentials

        Returns:
            Dict with credentials for the service
        """
        cache_key = f"creds_{service}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_key:
            logger.warning(f"No Connector API key, falling back to env vars for {service}")
            return self._fallback_to_env(service)

        try:
            response = requests.get(
                f"{self.base_url}/credentials/{service}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            creds = response.json()
            self._cache[cache_key] = creds
            return creds
        except Exception as e:
            logger.warning(f"Failed to get {service} creds from Connector: {e}, using env fallback")
            return self._fallback_to_env(service)

    def _fallback_to_env(self, service: str) -> Dict[str, Any]:
        """Fallback to environment variables if Connector unavailable."""
        fallbacks = {
            "telegram": {
                "token": os.getenv("TELEGRAM_TOKEN"),
                "chat_id": os.getenv("TELEGRAM_CHAT_ID")
            },
            "google-drive": {
                "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                "folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID")
            }
        }
        return fallbacks.get(service, {})

    def clear_cache(self):
        """Clear the credentials cache."""
        self._cache.clear()


# Singleton instance
_connector: Optional[ConnectorClient] = None

def get_connector() -> ConnectorClient:
    """Get the global Connector client instance."""
    global _connector
    if _connector is None:
        _connector = ConnectorClient()
    return _connector
