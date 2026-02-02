"""
AIssential Legal Agent - Main Application Entry Point
"""

import logging

from config.settings import validate_config, LOGS_DIR
from integrations.google_drive import run_drive_scan

# Setup logging
logging.basicConfig(
    filename=LOGS_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the AIssential Legal Agent."""
    logger.info("Starting AIssential Legal Agent")

    try:
        validate_config()
        logger.info("Configuration validated successfully")

        run_drive_scan()
        logger.info("Drive scan completed")

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
