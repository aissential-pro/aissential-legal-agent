"""
AI Connector client library for centralized credential management.

Provides access to the AIssential Connector service for retrieving
credentials that are configured once and shared across all apps.
"""

from app.lib.connector.client import ConnectorClient, get_connector
from app.lib.connector.services import (
    get_telegram_credentials,
    get_google_drive_credentials,
)

__all__ = [
    "ConnectorClient",
    "get_connector",
    "get_telegram_credentials",
    "get_google_drive_credentials",
]
