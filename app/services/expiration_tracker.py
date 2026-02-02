"""
Contract expiration tracking service.

Tracks contract expiration dates and sends alerts before expiration.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Storage file for contract expirations
EXPIRATIONS_FILE = Path(__file__).parent.parent / "memory" / "expirations.json"


def _load_expirations() -> dict:
    """Load expirations from JSON file."""
    if not EXPIRATIONS_FILE.exists():
        return {}

    try:
        with open(EXPIRATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading expirations: {e}")
        return {}


def _save_expirations(data: dict):
    """Save expirations to JSON file."""
    try:
        EXPIRATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(EXPIRATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving expirations: {e}")


def add_contract_expiration(
    contract_id: str,
    contract_name: str,
    expiration_date: str,
    contract_type: str = "unknown",
    parties: list = None
):
    """
    Add or update a contract expiration.

    Args:
        contract_id: Unique identifier (e.g., Drive file ID)
        contract_name: Name of the contract
        expiration_date: Expiration date in YYYY-MM-DD format
        contract_type: Type of contract (employee, client, supplier)
        parties: List of parties involved
    """
    data = _load_expirations()

    data[contract_id] = {
        "name": contract_name,
        "expiration_date": expiration_date,
        "contract_type": contract_type,
        "parties": parties or [],
        "added_at": datetime.now().isoformat(),
        "alerts_sent": []
    }

    _save_expirations(data)
    logger.info(f"Added expiration for {contract_name}: {expiration_date}")


def get_upcoming_expirations(days: int = 30) -> Optional[str]:
    """
    Get contracts expiring within the specified number of days.

    Returns:
        Formatted string report of upcoming expirations, or None if none found.
    """
    data = _load_expirations()
    today = datetime.now().date()
    cutoff = today + timedelta(days=days)

    upcoming = []

    for contract_id, info in data.items():
        try:
            exp_date = datetime.strptime(info["expiration_date"], "%Y-%m-%d").date()

            if today <= exp_date <= cutoff:
                days_left = (exp_date - today).days
                upcoming.append({
                    "id": contract_id,
                    "name": info["name"],
                    "date": exp_date,
                    "days_left": days_left,
                    "type": info.get("contract_type", "unknown"),
                    "parties": info.get("parties", [])
                })
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid expiration data for {contract_id}: {e}")

    if not upcoming:
        return None

    # Sort by days left
    upcoming.sort(key=lambda x: x["days_left"])

    # Format report
    lines = [
        "📅 *EXPIRATIONS DE CONTRATS À VENIR*",
        f"_Période: {days} prochains jours_",
        ""
    ]

    for contract in upcoming:
        # Urgency indicator
        if contract["days_left"] <= 7:
            icon = "🔴"
            urgency = "URGENT"
        elif contract["days_left"] <= 15:
            icon = "🟠"
            urgency = "BIENTÔT"
        else:
            icon = "🟡"
            urgency = ""

        type_icon = {
            "employee": "👤",
            "client": "🤝",
            "supplier": "📦",
            "unknown": "📄"
        }.get(contract["type"], "📄")

        lines.append(f"{icon} *{contract['name']}*")
        lines.append(f"   {type_icon} Type: {contract['type'].capitalize()}")
        lines.append(f"   📆 Expire: {contract['date'].strftime('%d/%m/%Y')}")
        lines.append(f"   ⏰ Dans: {contract['days_left']} jours {urgency}")
        if contract["parties"]:
            lines.append(f"   👥 Parties: {', '.join(contract['parties'])}")
        lines.append("")

    lines.append("---")
    lines.append("💡 _Utilisez /scan pour re-analyser les contrats_")

    return "\n".join(lines)


def get_critical_expirations(days: int = 7) -> Optional[str]:
    """
    Get contracts expiring within 7 days (critical).

    Returns:
        Formatted alert string for critical expirations.
    """
    data = _load_expirations()
    today = datetime.now().date()
    cutoff = today + timedelta(days=days)

    critical = []

    for contract_id, info in data.items():
        try:
            exp_date = datetime.strptime(info["expiration_date"], "%Y-%m-%d").date()

            if today <= exp_date <= cutoff:
                days_left = (exp_date - today).days
                critical.append({
                    "name": info["name"],
                    "date": exp_date,
                    "days_left": days_left,
                    "type": info.get("contract_type", "unknown")
                })
        except (ValueError, KeyError):
            pass

    if not critical:
        return None

    # Sort by days left
    critical.sort(key=lambda x: x["days_left"])

    lines = [
        "🚨 *ALERTE: CONTRATS EXPIRANT BIENTÔT*",
        ""
    ]

    for contract in critical:
        if contract["days_left"] == 0:
            urgency = "EXPIRE AUJOURD'HUI!"
        elif contract["days_left"] == 1:
            urgency = "EXPIRE DEMAIN!"
        else:
            urgency = f"Expire dans {contract['days_left']} jours"

        lines.append(f"🔴 *{contract['name']}*")
        lines.append(f"   📆 {contract['date'].strftime('%d/%m/%Y')} - {urgency}")
        lines.append("")

    lines.append("⚠️ *Action requise: Renouveler ou clôturer ces contrats*")

    return "\n".join(lines)


def remove_expiration(contract_id: str):
    """Remove a contract from tracking."""
    data = _load_expirations()

    if contract_id in data:
        del data[contract_id]
        _save_expirations(data)
        logger.info(f"Removed expiration tracking for {contract_id}")


def get_all_expirations() -> dict:
    """Get all tracked expirations."""
    return _load_expirations()
