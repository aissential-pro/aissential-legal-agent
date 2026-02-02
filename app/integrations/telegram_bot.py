import logging

import requests

from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


def send_alert(message: str) -> bool:
    """
    Send an alert message via Telegram bot.

    Args:
        message: The message to send. Will be truncated to 4000 chars if longer.

    Returns:
        True on success, False on failure.
    """
    try:
        # Truncate message to 4000 characters (Telegram limit is 4096)
        truncated_message = message[:4000] if len(message) > 4000 else message

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": truncated_message,
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        logger.info("Telegram alert sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram alert: {e}")
        return False
