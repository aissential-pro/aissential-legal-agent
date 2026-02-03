"""
Logging configuration for the Legal Agent bot.

Provides:
- Rotating file logs (prevents disk overflow)
- Console output with colors
- Separate error log file
- Structured logging format
"""

import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logging(
    log_dir: Path = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB per file
    backup_count: int = 5,
    console_output: bool = True,
):
    """
    Configure logging for the application.

    Args:
        log_dir: Directory for log files (defaults to project/logs)
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to also log to console
    """
    # Determine log directory
    if log_dir is None:
        # Try to find project root
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / ".env").exists() or (parent / "app").exists():
                log_dir = parent / "logs"
                break
        if log_dir is None:
            log_dir = Path.cwd() / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file paths
    main_log = log_dir / "app.log"
    error_log = log_dir / "error.log"

    # Log format
    detailed_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    simple_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Main rotating file handler
    main_handler = RotatingFileHandler(
        main_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(detailed_format)
    root_logger.addHandler(main_handler)

    # Error-only rotating file handler
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_format)
    root_logger.addHandler(error_handler)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_format)
        root_logger.addHandler(console_handler)

    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    logging.info(f"Logging configured: {log_dir}")
    logging.info(f"Log level: {log_level}")

    return root_logger


class ErrorTracker:
    """
    Track errors for monitoring and alerting.
    """

    def __init__(self, max_errors: int = 100):
        self.errors = []
        self.max_errors = max_errors
        self.total_count = 0

    def record(self, error: Exception, context: str = None):
        """Record an error."""
        from datetime import datetime

        self.total_count += 1
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
        }

        self.errors.append(error_info)

        # Keep only recent errors
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]

    def get_recent(self, count: int = 10):
        """Get recent errors."""
        return self.errors[-count:]

    def get_summary(self):
        """Get error summary."""
        from collections import Counter

        if not self.errors:
            return {"total": 0, "by_type": {}}

        types = Counter(e["type"] for e in self.errors)
        return {
            "total": self.total_count,
            "recent_count": len(self.errors),
            "by_type": dict(types),
        }


# Global error tracker
error_tracker = ErrorTracker()
