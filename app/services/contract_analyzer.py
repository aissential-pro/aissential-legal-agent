import json
import logging

from app.services.claude_client import ask_claude
from app.integrations.telegram_bot import send_alert
from app.config.settings import settings, BASE_DIR
from app.lib.gateway.modules import MODULES


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
    user_prompt = f"""Analyze the following contract and provide your analysis as a JSON object with these exact keys:
- "risk_score": an integer from 0 to 100 indicating overall risk level (0 = no risk, 100 = extreme risk)
- "risks": a list of strings describing identified risks
- "missing_clauses": a list of strings describing important clauses that are missing
- "recommendations": a list of strings with recommendations for improvement

Contract Name: {name}

Contract Text:
{text}

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

        # Check if risk score exceeds threshold and send alert
        if result["risk_score"] >= settings.RISK_THRESHOLD_ALERT:
            logger.warning(
                f"High risk contract detected: {name} (score: {result['risk_score']})"
            )
            alert_message = (
                f"HIGH RISK CONTRACT ALERT\n\n"
                f"Contract: {name}\n"
                f"Risk Score: {result['risk_score']}/100\n\n"
                f"Identified Risks:\n" +
                "\n".join(f"- {risk}" for risk in result["risks"])
            )
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
