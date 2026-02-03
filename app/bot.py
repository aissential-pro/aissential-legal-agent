"""
AIssential Legal Agent - Interactive Telegram Bot

Commands:
- /start, /help - Show available commands
- /scan - Trigger immediate Drive scan
- /status - Show bot status and stats
- /health - Quick health check
- /analyze - Send a file to analyze (reply to a document)
- /veille - Legal monitoring for Vietnam
- /expirations - Check upcoming contract expirations

Scheduled Jobs:
- Daily veille at 8:00 AM
- Expiration check at 9:00 AM
- Heartbeat every 6 hours
"""

import logging
import tempfile
import platform
import psutil
from pathlib import Path
from datetime import datetime, time, timedelta

from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config.settings import settings, GOOGLE_DRIVE_FOLDER_IDS
from services.contract_analyzer import analyze_contract
from services import file_parser
from memory.processed_files import get_processed_ids

logger = logging.getLogger(__name__)

# Bot state
_bot_start_time = datetime.now()
_files_analyzed_session = 0
_last_error = None
_error_count = 0

# Timezone for Vietnam (UTC+7)
VIETNAM_TZ_OFFSET = 7

# Heartbeat settings
HEARTBEAT_INTERVAL_HOURS = 6
HEARTBEAT_ENABLED = True


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command - simple test."""
    logger.info(f"Ping received from {update.effective_user.id}")
    await update.message.reply_text("Pong! Le bot fonctionne.")


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command - quick health check."""
    global _bot_start_time, _last_error, _error_count

    uptime = datetime.now() - _bot_start_time
    days = uptime.days
    hours, remainder = divmod(int(uptime.total_seconds()) % 86400, 3600)
    minutes, _ = divmod(remainder, 60)

    # System health checks
    checks = []

    # Check memory usage
    try:
        memory = psutil.virtual_memory()
        mem_ok = memory.percent < 90
        checks.append(("Memoire", mem_ok, f"{memory.percent:.0f}%"))
    except:
        checks.append(("Memoire", True, "N/A"))

    # Check disk space
    try:
        disk = psutil.disk_usage('/')
        disk_ok = disk.percent < 90
        checks.append(("Disque", disk_ok, f"{disk.percent:.0f}%"))
    except:
        checks.append(("Disque", True, "N/A"))

    # Check Google Drive connection
    try:
        from integrations.google_drive import get_drive_service
        service = get_drive_service()
        service.files().list(pageSize=1).execute()
        checks.append(("Google Drive", True, "OK"))
    except Exception as e:
        checks.append(("Google Drive", False, str(e)[:30]))

    # Check AI provider
    try:
        from lib.ai_hub import get_hub
        hub = get_hub()
        ai_ok = hub.default_provider is not None
        checks.append(("AI Provider", ai_ok, hub.default_provider or "None"))
    except Exception as e:
        checks.append(("AI Provider", False, str(e)[:30]))

    # Build health report
    all_ok = all(ok for _, ok, _ in checks)
    status_icon = "OK" if all_ok else "DEGRADED"

    lines = [
        f"*Health Check - {status_icon}*",
        f"",
        f"Uptime: {days}j {hours}h {minutes}m",
        f"Erreurs: {_error_count}",
        f"",
        "*Composants:*",
    ]

    for name, ok, detail in checks:
        icon = "[OK]" if ok else "[KO]"
        lines.append(f"  {icon} {name}: {detail}")

    if _last_error:
        lines.append(f"")
        lines.append(f"Derniere erreur: {_last_error[:50]}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start and /help commands."""
    logger.info(f"Start/help command from {update.effective_user.id}")
    help_text = """
🤖 *AIssential Legal Agent (CLO)*

Je suis votre Chief Legal Officer virtuel. Voici mes commandes:

📋 *Commandes:*
• `/scan` - Scanner les dossiers Drive
• `/veille` - Veille juridique Vietnam
• `/expirations` - Contrats expirant bientôt
• `/status` - Statut du bot

📄 *Analyser un fichier:*
Envoyez-moi un PDF ou DOCX directement.

⏰ *Tâches automatiques:*
• 8h00 - Veille juridique quotidienne
• 9h00 - Alerte expirations contrats

⚙️ *Configuration:*
• Seuil d'alerte: ≥{threshold}/100
• Dossiers surveillés: {folders}
    """.format(
        threshold=settings.RISK_THRESHOLD_ALERT,
        folders=len(GOOGLE_DRIVE_FOLDER_IDS)
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /scan command - trigger Drive scan."""
    logger.info(f"Scan command received from user {update.effective_user.id}")

    try:
        await update.message.reply_text("🔍 Lancement du scan des dossiers Drive...")
    except Exception as e:
        logger.error(f"Failed to send initial message: {e}")
        return

    try:
        from integrations.google_drive import run_drive_scan
        logger.info("Starting drive scan...")
        run_drive_scan()
        logger.info("Drive scan completed successfully")
        await update.message.reply_text("✅ Scan terminé! Vérifiez les alertes ci-dessus si des contrats à risque ont été détectés.")
    except Exception as e:
        logger.error(f"Scan error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erreur lors du scan: {str(e)}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show bot status."""
    global _bot_start_time, _files_analyzed_session

    processed_count = len(get_processed_ids())
    uptime = datetime.now() - _bot_start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Get expiration count
    try:
        from services.expiration_tracker import get_all_expirations
        expirations_count = len(get_all_expirations())
    except:
        expirations_count = 0

    status_text = f"""
📊 *Statut du Bot - CLO AIssential*

🟢 *État:* En ligne
⏱ *Uptime:* {hours}h {minutes}m {seconds}s

📁 *Dossiers surveillés:* {len(GOOGLE_DRIVE_FOLDER_IDS)}
📄 *Fichiers traités:* {processed_count}
📈 *Analysés (session):* {_files_analyzed_session}
📅 *Contrats suivis (expirations):* {expirations_count}

⏰ *Tâches programmées:*
• Veille juridique: 8h00 (Vietnam)
• Check expirations: 9h00 (Vietnam)

⚙️ *Configuration:*
• Seuil d'alerte: ≥{settings.RISK_THRESHOLD_ALERT}/100
• Provider AI: OpenAI
• Scan: Récursif (sous-dossiers inclus)
    """
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command."""
    await update.message.reply_text(
        "📄 Pour analyser un contrat, envoyez-moi directement le fichier (PDF ou DOCX)."
    )


async def veille_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /veille command - legal monitoring for Vietnam."""
    logger.info(f"Veille command received from user {update.effective_user.id}")

    await update.message.reply_text("🔍 Recherche des actualités juridiques Vietnam en cours...")

    try:
        from services.legal_monitor import get_legal_updates
        updates = await get_legal_updates()

        if updates:
            await update.message.reply_text(updates, parse_mode="Markdown")
        else:
            await update.message.reply_text("✅ Aucune mise à jour juridique majeure détectée.")

    except Exception as e:
        logger.error(f"Veille error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erreur lors de la veille: {str(e)}")


async def expirations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /expirations command - check upcoming contract expirations."""
    logger.info(f"Expirations command received from user {update.effective_user.id}")

    try:
        from services.expiration_tracker import get_upcoming_expirations
        report = get_upcoming_expirations()

        if report:
            await update.message.reply_text(report, parse_mode="Markdown")
        else:
            await update.message.reply_text("✅ Aucune expiration de contrat à venir dans les 30 prochains jours.")

    except Exception as e:
        logger.error(f"Expirations error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erreur: {str(e)}")


# ============================================
# SCHEDULED JOBS
# ============================================

async def scheduled_veille(context: ContextTypes.DEFAULT_TYPE):
    """Daily scheduled legal monitoring at 8:00 AM Vietnam time."""
    logger.info("Running scheduled daily veille...")

    try:
        from services.legal_monitor import get_legal_updates
        from integrations.telegram_bot import send_alert

        updates = await get_legal_updates()

        if updates:
            header = "🌅 *VEILLE JURIDIQUE QUOTIDIENNE*\n\n"
            send_alert(header + updates)
            logger.info("Daily veille sent successfully")

    except Exception as e:
        logger.error(f"Scheduled veille error: {e}", exc_info=True)


async def scheduled_expiration_check(context: ContextTypes.DEFAULT_TYPE):
    """Daily expiration check at 9:00 AM Vietnam time."""
    logger.info("Running scheduled expiration check...")

    try:
        from services.expiration_tracker import get_upcoming_expirations, get_critical_expirations
        from integrations.telegram_bot import send_alert

        # Check for critical expirations (7 days or less)
        critical = get_critical_expirations()

        if critical:
            send_alert(critical)
            logger.info("Critical expiration alert sent")

    except Exception as e:
        logger.error(f"Scheduled expiration check error: {e}", exc_info=True)


async def scheduled_heartbeat(context: ContextTypes.DEFAULT_TYPE):
    """Periodic heartbeat to confirm bot is alive."""
    global _bot_start_time, _files_analyzed_session, _error_count

    if not HEARTBEAT_ENABLED:
        return

    logger.info("Sending heartbeat...")

    try:
        from integrations.telegram_bot import send_alert

        uptime = datetime.now() - _bot_start_time
        days = uptime.days
        hours, remainder = divmod(int(uptime.total_seconds()) % 86400, 3600)
        minutes, _ = divmod(remainder, 60)

        # Get memory info
        try:
            memory = psutil.virtual_memory()
            mem_info = f"{memory.percent:.0f}%"
        except:
            mem_info = "N/A"

        processed_count = len(get_processed_ids())

        message = (
            f"*Heartbeat - Bot Legal Agent*\n\n"
            f"Statut: En ligne\n"
            f"Uptime: {days}j {hours}h {minutes}m\n"
            f"Memoire: {mem_info}\n"
            f"Fichiers analyses (session): {_files_analyzed_session}\n"
            f"Total fichiers traites: {processed_count}\n"
            f"Erreurs: {_error_count}\n"
            f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        send_alert(message)
        logger.info("Heartbeat sent successfully")

    except Exception as e:
        logger.error(f"Heartbeat error: {e}", exc_info=True)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads for analysis."""
    global _files_analyzed_session

    document: Document = update.message.document
    file_name = document.file_name

    # Check file type
    if not (file_name.lower().endswith('.pdf') or file_name.lower().endswith('.docx')):
        await update.message.reply_text(
            "⚠️ Format non supporté. Envoyez un fichier PDF ou DOCX."
        )
        return

    await update.message.reply_text(f"📥 Réception de: {file_name}\n⏳ Analyse en cours...")

    try:
        # Download file
        file = await context.bot.get_file(document.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp:
            await file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        # Read file content
        with open(tmp_path, 'rb') as f:
            content = f.read()

        # Extract text
        extracted_text = file_parser.extract_text(content, file_name)

        if not extracted_text:
            await update.message.reply_text("❌ Impossible d'extraire le texte du fichier.")
            return

        # Analyze
        result = analyze_contract(extracted_text, file_name)
        _files_analyzed_session += 1

        # Format response
        response = _format_analysis_response(file_name, result)
        await update.message.reply_text(response, parse_mode="Markdown")

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Document analysis error: {e}")
        await update.message.reply_text(f"❌ Erreur lors de l'analyse: {str(e)}")


def _format_analysis_response(name: str, result: dict) -> str:
    """Format analysis result for Telegram response."""
    score = result["risk_score"]

    # Risk level
    if score >= 80:
        level = "🔴 CRITIQUE"
    elif score >= 60:
        level = "🟠 ÉLEVÉ"
    elif score >= 40:
        level = "🟡 MODÉRÉ"
    else:
        level = "🟢 FAIBLE"

    lines = [
        f"📋 *Analyse terminée*",
        f"",
        f"📄 *Fichier:* {name}",
        f"📊 *Score de risque:* {score}/100 ({level})",
        f"",
    ]

    # Risks
    if result.get("risks"):
        lines.append("🚨 *Risques identifiés:*")
        for risk in result["risks"][:5]:  # Limit to 5
            if isinstance(risk, dict):
                severity = risk.get("severity", "").upper()
                desc = risk.get("description", str(risk))
                icon = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}.get(severity, "⚪")
                lines.append(f"  {icon} {desc}")
            else:
                lines.append(f"  • {risk}")
        lines.append("")

    # Missing clauses
    if result.get("missing_clauses"):
        lines.append("📋 *Clauses manquantes:*")
        for clause in result["missing_clauses"][:5]:
            lines.append(f"  • {clause}")
        lines.append("")

    # Recommendations
    if result.get("recommendations"):
        lines.append("💡 *Recommandations:*")
        for rec in result["recommendations"][:3]:
            lines.append(f"  • {rec}")

    return "\n".join(lines)


def run_bot():
    """Start the Telegram bot."""
    from lib.connector.services import get_telegram_credentials

    # Get token
    token, chat_id = get_telegram_credentials()
    if not token:
        token = settings.TELEGRAM_TOKEN

    if not token:
        raise ValueError("TELEGRAM_TOKEN not configured")

    logger.info("Starting Telegram bot...")

    # Create application
    app = Application.builder().token(token).build()

    # Add command handlers
    app.add_handler(CommandHandler(["start", "help"], start_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("veille", veille_command))
    app.add_handler(CommandHandler("expirations", expirations_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Add scheduled jobs
    job_queue = app.job_queue

    # Daily veille at 8:00 AM Vietnam time (1:00 AM UTC)
    job_queue.run_daily(
        scheduled_veille,
        time=time(hour=1, minute=0),  # UTC time (8:00 AM Vietnam = 1:00 AM UTC)
        name="daily_veille"
    )
    logger.info("Scheduled daily veille at 8:00 AM Vietnam time")

    # Daily expiration check at 9:00 AM Vietnam time (2:00 AM UTC)
    job_queue.run_daily(
        scheduled_expiration_check,
        time=time(hour=2, minute=0),  # UTC time (9:00 AM Vietnam = 2:00 AM UTC)
        name="daily_expiration_check"
    )
    logger.info("Scheduled daily expiration check at 9:00 AM Vietnam time")

    # Heartbeat every 6 hours
    if HEARTBEAT_ENABLED:
        job_queue.run_repeating(
            scheduled_heartbeat,
            interval=timedelta(hours=HEARTBEAT_INTERVAL_HOURS),
            first=timedelta(minutes=5),  # First heartbeat 5 min after start
            name="heartbeat"
        )
        logger.info(f"Scheduled heartbeat every {HEARTBEAT_INTERVAL_HOURS} hours")

    # Start polling
    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Use improved logging configuration
    try:
        from utils.logging_config import setup_logging
        setup_logging(log_level="INFO")
    except ImportError:
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    run_bot()
