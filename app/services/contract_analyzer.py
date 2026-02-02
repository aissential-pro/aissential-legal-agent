import json
import logging

from services.claude_client import ask_claude
from integrations.telegram_bot import send_alert
from config.settings import settings, BASE_DIR
from lib.gateway.modules import MODULES


logger = logging.getLogger(__name__)

# Load system prompt once at module level
_system_prompt_path = BASE_DIR / "app" / "system_prompt.txt"
try:
    with open(_system_prompt_path, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    logger.warning(f"System prompt file not found at {_system_prompt_path}")
    SYSTEM_PROMPT = "You are a legal contract analysis assistant."


def analyze_contract(text: str, name: str) -> dict:
    """
    Analyze a contract using Claude AI.

    Args:
        text: The extracted text content of the contract
        name: The name/identifier of the contract

    Returns:
        A dictionary containing:
            - risk_score: int (0-100)
            - risks: list of identified risks
            - missing_clauses: list of missing important clauses
            - recommendations: list of recommendations
    """
    user_prompt = f"""Analyze the following contract for AIssential (Vietnam-based AI consulting company).

Contract Name: {name}

Contract Text:
{text}

Provide your analysis as a JSON object following the format specified in your instructions.
Include vietnam_compliance and proactive_advice sections.
Respond ONLY with the JSON object, no additional text."""

    try:
        response = ask_claude(SYSTEM_PROMPT, user_prompt, module_id=MODULES["ANALYZE_CONTRACT"])

        # Parse JSON response
        # Handle potential markdown code blocks
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        result = json.loads(response_text)

        # Ensure all expected keys exist
        result.setdefault("risk_score", 0)
        result.setdefault("risks", [])
        result.setdefault("missing_clauses", [])
        result.setdefault("recommendations", [])
        result.setdefault("vietnam_compliance", {})
        result.setdefault("proactive_advice", {})
        result.setdefault("contract_metadata", {})

        # Extract and save expiration date if present
        metadata = result.get("contract_metadata", {})
        if metadata.get("end_date"):
            try:
                from services.expiration_tracker import add_contract_expiration
                add_contract_expiration(
                    contract_id=name,  # Use name as ID for now
                    contract_name=name,
                    expiration_date=metadata["end_date"],
                    contract_type=metadata.get("type", "unknown"),
                    parties=metadata.get("parties", [])
                )
                logger.info(f"Tracked expiration for {name}: {metadata['end_date']}")
            except Exception as e:
                logger.warning(f"Failed to track expiration: {e}")

        # Always send alert with full analysis (proactive advisor mode)
        contract_type = metadata.get("type", "unknown")
        logger.info(f"Contract analyzed: {name} (type: {contract_type}, score: {result['risk_score']})")
        alert_message = _format_alert_message(name, result)
        send_alert(alert_message)

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        return {
            "risk_score": 0,
            "risks": ["Error: Could not parse analysis response"],
            "missing_clauses": [],
            "recommendations": ["Please try analyzing the contract again"]
        }
    except Exception as e:
        logger.error(f"Error analyzing contract {name}: {e}")
        raise


def _format_alert_message(name: str, result: dict) -> str:
    """Format the analysis result into a readable Telegram message."""
    score = result["risk_score"]

    # Determine risk level emoji and label
    if score >= 80:
        level = "🔴 CRITIQUE"
        header = "🚨 ALERTE CRITIQUE"
    elif score >= 60:
        level = "🟠 ÉLEVÉ"
        header = "⚠️ ALERTE CONTRAT À RISQUE"
    elif score >= 40:
        level = "🟡 MODÉRÉ"
        header = "📋 ANALYSE CONTRAT"
    else:
        level = "🟢 FAIBLE"
        header = "✅ ANALYSE CONTRAT"

    # Get contract metadata
    metadata = result.get("contract_metadata", {})
    contract_type = metadata.get("type", "unknown")

    # Contract type icons
    type_icons = {
        "employee": "👤 Employé",
        "client": "🤝 Client",
        "supplier": "📦 Fournisseur",
        "partnership": "🤝 Partenariat",
        "nda": "🔒 NDA",
        "other": "📄 Autre",
        "unknown": "📄 Non classé"
    }
    type_display = type_icons.get(contract_type, "📄 " + contract_type)

    lines = [
        header,
        f"",
        f"📄 {name}",
        f"🏷️ Type: {type_display}",
        f"📊 Score: {score}/100 ({level})",
    ]

    # Add dates if available
    if metadata.get("start_date") or metadata.get("end_date"):
        date_info = []
        if metadata.get("start_date"):
            date_info.append(f"Début: {metadata['start_date']}")
        if metadata.get("end_date"):
            date_info.append(f"Fin: {metadata['end_date']}")
        lines.append(f"📅 {' | '.join(date_info)}")

    # Add parties if available
    if metadata.get("parties"):
        lines.append(f"👥 Parties: {', '.join(metadata['parties'][:3])}")

    lines.append("")

    # Format risks
    if result.get("risks"):
        lines.append("🚨 RISQUES IDENTIFIÉS:")
        for risk in result["risks"][:5]:  # Limit to 5
            if isinstance(risk, dict):
                severity = risk.get("severity", "").upper()
                desc = risk.get("description", str(risk))
                ref = risk.get("vietnam_law_reference", "")
                severity_icon = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}.get(severity, "⚪")
                line = f"  {severity_icon} {desc}"
                if ref:
                    line += f" [{ref}]"
                lines.append(line)
            else:
                lines.append(f"  • {risk}")
        lines.append("")

    # Vietnam Compliance
    vietnam = result.get("vietnam_compliance", {})
    if vietnam:
        compliant = vietnam.get("compliant", True)
        status = "✅ Conforme" if compliant else "❌ Non conforme"
        lines.append(f"🇻🇳 CONFORMITÉ VIETNAM: {status}")
        if vietnam.get("issues"):
            for issue in vietnam["issues"][:3]:
                lines.append(f"  ⚠️ {issue}")
        if vietnam.get("required_actions"):
            lines.append("  Actions requises:")
            for action in vietnam["required_actions"][:3]:
                lines.append(f"    • {action}")
        lines.append("")

    # Format missing clauses
    if result.get("missing_clauses"):
        lines.append("📋 CLAUSES MANQUANTES:")
        for clause in result["missing_clauses"][:5]:
            lines.append(f"  • {clause}")
        lines.append("")

    # Format recommendations
    if result.get("recommendations"):
        lines.append("💡 RECOMMANDATIONS:")
        for rec in result["recommendations"][:5]:
            lines.append(f"  • {rec}")
        lines.append("")

    # Proactive Advice
    advice = result.get("proactive_advice", {})
    if advice:
        if advice.get("strategic_recommendations"):
            lines.append("🎯 CONSEIL STRATÉGIQUE:")
            for rec in advice["strategic_recommendations"][:3]:
                lines.append(f"  → {rec}")
            lines.append("")
        if advice.get("upcoming_risks"):
            lines.append("⏰ RISQUES À ANTICIPER:")
            for risk in advice["upcoming_risks"][:3]:
                lines.append(f"  ⚡ {risk}")

    return "\n".join(lines)
