"""
Configuration settings for AIssential Legal Agent.

Loads environment variables and provides configuration validation.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Logs directory
LOGS_DIR = BASE_DIR / "logs"

# Gateway Configuration
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "https://gateway.aissential.pro/v1")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY")
GATEWAY_CLIENT_ID = os.getenv("GATEWAY_CLIENT_ID", "aissential-internal")

# Application identifier (hardcoded)
APP_ID = "legal-agent"

# API Keys and Credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Risk threshold for alerts (default: 60)
RISK_THRESHOLD_ALERT = int(os.getenv("RISK_THRESHOLD_ALERT", "60"))

# Claude model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"


class _Settings:
    """Settings class to provide attribute-style access to configuration."""

    def __init__(self):
        self.BASE_DIR = BASE_DIR
        self.LOGS_DIR = LOGS_DIR
        self.GATEWAY_BASE_URL = GATEWAY_BASE_URL
        self.GATEWAY_API_KEY = GATEWAY_API_KEY
        self.GATEWAY_CLIENT_ID = GATEWAY_CLIENT_ID
        self.APP_ID = APP_ID
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        self.GOOGLE_DRIVE_FOLDER_ID = GOOGLE_DRIVE_FOLDER_ID
        self.GOOGLE_APPLICATION_CREDENTIALS = GOOGLE_APPLICATION_CREDENTIALS
        self.RISK_THRESHOLD_ALERT = RISK_THRESHOLD_ALERT
        self.CLAUDE_MODEL = CLAUDE_MODEL


# Singleton settings instance
settings = _Settings()


def validate_config() -> None:
    """
    Validate that all required configuration variables are set.

    Raises:
        ValueError: If any required configuration variable is missing.
    """
    required_vars = {
        "GATEWAY_BASE_URL": GATEWAY_BASE_URL,
        "GATEWAY_API_KEY": GATEWAY_API_KEY,
        "GATEWAY_CLIENT_ID": GATEWAY_CLIENT_ID,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "GOOGLE_DRIVE_FOLDER_ID": GOOGLE_DRIVE_FOLDER_ID,
        "GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_APPLICATION_CREDENTIALS,
    }

    missing_vars = [name for name, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(
            f"Missing required configuration variables: {', '.join(missing_vars)}"
        )
