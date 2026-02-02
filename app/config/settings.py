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

# API Keys and Credentials
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Risk threshold for alerts (default: 60)
RISK_THRESHOLD_ALERT = int(os.getenv("RISK_THRESHOLD_ALERT", "60"))

# Claude model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def validate_config() -> None:
    """
    Validate that all required configuration variables are set.

    Raises:
        ValueError: If any required configuration variable is missing.
    """
    required_vars = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
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
