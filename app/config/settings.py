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

# AI Provider API Keys (at least one required)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# API Keys and Credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Google credentials - convert relative path to absolute
_gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if _gcp_creds and not Path(_gcp_creds).is_absolute():
    GOOGLE_APPLICATION_CREDENTIALS = str(BASE_DIR / _gcp_creds)
else:
    GOOGLE_APPLICATION_CREDENTIALS = _gcp_creds

# Google Drive folders (supports multiple, comma-separated)
_folder_ids_raw = os.getenv("GOOGLE_DRIVE_FOLDER_IDS", "") or os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
GOOGLE_DRIVE_FOLDER_IDS = [f.strip() for f in _folder_ids_raw.split(",") if f.strip()]

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
        self.GOOGLE_DRIVE_FOLDER_IDS = GOOGLE_DRIVE_FOLDER_IDS
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
    # Required variables
    required_vars = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_APPLICATION_CREDENTIALS,
    }

    missing_vars = [name for name, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(
            f"Missing required configuration variables: {', '.join(missing_vars)}"
        )

    # At least one Drive folder required
    if not GOOGLE_DRIVE_FOLDER_IDS:
        raise ValueError(
            "At least one Google Drive folder ID is required: "
            "Set GOOGLE_DRIVE_FOLDER_IDS (comma-separated for multiple)"
        )

    # At least one AI provider required
    ai_providers = {
        "GATEWAY_API_KEY": GATEWAY_API_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "MISTRAL_API_KEY": MISTRAL_API_KEY,
    }

    if not any(ai_providers.values()):
        raise ValueError(
            "At least one AI provider API key is required: "
            "GATEWAY_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or MISTRAL_API_KEY"
        )
