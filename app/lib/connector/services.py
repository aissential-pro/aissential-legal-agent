"""
Service-specific credential helpers.

These functions provide easy access to credentials for each integrated service.
They use the Connector when available, with fallback to environment variables.
"""
from typing import Tuple, Optional
from .client import get_connector


def get_telegram_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Telegram bot credentials.

    Returns:
        Tuple of (token, chat_id)
    """
    creds = get_connector().get_credentials("telegram")
    return creds.get("token"), creds.get("chat_id")


def get_google_drive_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Google Drive credentials.

    Returns:
        Tuple of (credentials_path, folder_id)
    """
    creds = get_connector().get_credentials("google-drive")
    return creds.get("credentials_path"), creds.get("folder_id")
