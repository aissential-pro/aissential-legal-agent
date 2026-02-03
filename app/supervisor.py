"""
Bot Supervisor - Ensures the bot stays running 24/7.

This module provides:
- Automatic restart on crash
- Exponential backoff for restarts
- Health monitoring
- Startup notification
- Crash notification

Usage:
    python supervisor.py

The supervisor will:
1. Start the bot
2. Monitor for crashes
3. Send notification on crash
4. Restart with backoff
5. Send notification on recovery
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from logging.handlers import RotatingFileHandler
from config.settings import settings, LOGS_DIR

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging with rotation
log_file = LOGS_DIR / "supervisor.log"
handler = RotatingFileHandler(
    log_file,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

logger = logging.getLogger("supervisor")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class BotSupervisor:
    """
    Supervisor that keeps the bot running and handles restarts.
    """

    def __init__(
        self,
        bot_script: str = "bot.py",
        max_restart_delay: int = 300,  # 5 minutes
        initial_restart_delay: int = 5,
        restart_backoff_factor: float = 2.0,
        reset_backoff_after: int = 600,  # 10 minutes of stable running
    ):
        self.bot_script = bot_script
        self.max_restart_delay = max_restart_delay
        self.initial_restart_delay = initial_restart_delay
        self.restart_backoff_factor = restart_backoff_factor
        self.reset_backoff_after = reset_backoff_after

        self.process = None
        self.running = False
        self.restart_count = 0
        self.current_delay = initial_restart_delay
        self.last_start_time = None
        self.total_restarts = 0

        # Statistics
        self.stats = {
            "start_time": None,
            "last_crash": None,
            "total_crashes": 0,
            "current_uptime": 0,
        }

    def _send_telegram_notification(self, message: str) -> bool:
        """Send a notification via Telegram."""
        try:
            import requests

            token = settings.TELEGRAM_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID

            if not token or not chat_id:
                logger.warning("Telegram credentials not configured")
                return False

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=30)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def _notify_start(self):
        """Notify that the bot is starting."""
        message = (
            f"*Bot Legal Agent - Demarrage*\n\n"
            f"Le bot demarre...\n"
            f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_telegram_notification(message)

    def _notify_crash(self, exit_code: int):
        """Notify that the bot crashed."""
        message = (
            f"*Bot Legal Agent - CRASH*\n\n"
            f"Le bot a plante!\n"
            f"Code de sortie: {exit_code}\n"
            f"Nombre de crashes: {self.stats['total_crashes']}\n"
            f"Redemarrage dans: {self.current_delay}s\n"
            f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_telegram_notification(message)

    def _notify_recovery(self):
        """Notify that the bot recovered after crashes."""
        if self.restart_count > 0:
            message = (
                f"*Bot Legal Agent - Recuperation*\n\n"
                f"Le bot a redémarre avec succes!\n"
                f"Apres {self.restart_count} tentative(s)\n"
                f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self._send_telegram_notification(message)

    def _start_bot(self):
        """Start the bot process."""
        script_path = Path(__file__).parent / self.bot_script

        logger.info(f"Starting bot: {script_path}")

        self.process = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self.last_start_time = time.time()
        self.stats["start_time"] = datetime.now()

        # Start output reader thread
        def read_output():
            while self.process and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    # Forward to logger (info level)
                    logger.info(f"[BOT] {line.rstrip()}")

        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()

        return self.process

    def _check_if_stable(self):
        """Check if the bot has been running stably, reset backoff if so."""
        if self.last_start_time:
            uptime = time.time() - self.last_start_time
            if uptime >= self.reset_backoff_after:
                if self.restart_count > 0:
                    logger.info(
                        f"Bot stable for {uptime:.0f}s, resetting backoff"
                    )
                    self._notify_recovery()
                    self.restart_count = 0
                    self.current_delay = self.initial_restart_delay

    def run(self):
        """Main supervisor loop."""
        logger.info("=" * 50)
        logger.info("Bot Supervisor starting")
        logger.info("=" * 50)

        self.running = True
        self._notify_start()

        # Handle signals for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            if self.process:
                self.process.terminate()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while self.running:
            try:
                # Start the bot
                self._start_bot()
                logger.info(f"Bot started with PID: {self.process.pid}")

                # Wait for the process to complete
                while self.running and self.process.poll() is None:
                    time.sleep(1)
                    self._check_if_stable()

                if not self.running:
                    break

                # Process exited
                exit_code = self.process.returncode
                self.stats["total_crashes"] += 1
                self.stats["last_crash"] = datetime.now()
                self.total_restarts += 1

                if exit_code == 0:
                    logger.info("Bot exited normally (code 0)")
                    # Normal exit, maybe user stopped it
                    continue
                else:
                    logger.error(f"Bot crashed with exit code: {exit_code}")
                    self._notify_crash(exit_code)

                    # Apply backoff
                    self.restart_count += 1
                    self.current_delay = min(
                        self.initial_restart_delay
                        * (self.restart_backoff_factor ** self.restart_count),
                        self.max_restart_delay,
                    )

                    logger.info(
                        f"Restart attempt #{self.restart_count}, "
                        f"waiting {self.current_delay:.0f}s..."
                    )
                    time.sleep(self.current_delay)

            except Exception as e:
                logger.error(f"Supervisor error: {e}")
                time.sleep(5)

        # Cleanup
        if self.process and self.process.poll() is None:
            logger.info("Terminating bot process...")
            self.process.terminate()
            self.process.wait(timeout=10)

        logger.info("Supervisor stopped")


def main():
    """Entry point for the supervisor."""
    supervisor = BotSupervisor()
    supervisor.run()


if __name__ == "__main__":
    main()
