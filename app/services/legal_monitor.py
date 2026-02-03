"""
Legal monitoring service for Vietnam.

Monitors Vietnamese legal sources for updates relevant to AIssential's business:
- AI/Technology regulations
- Labor law changes
- Business/Enterprise law updates
- Cybersecurity regulations
- Investment law changes
"""

import logging
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

# Search queries for different legal topics
SEARCH_QUERIES = [
    "Vietnam AI regulation law 2024 2025 2026",
    "Vietnam labor law update nghị định lao động mới",
    "Vietnam cybersecurity data protection law update",
    "Vietnam enterprise business law decree mới nhất",
    "Vietnam foreign investment law update",
    "luật mới việt nam doanh nghiệp công nghệ",
    "dự thảo luật việt nam quốc hội",  # Draft laws being voted
    "Vietnam National Assembly bill draft law",
    "quốc hội việt nam thông qua luật mới",  # Laws being passed
]


async def _search_web(query: str) -> str:
    """Search the web using DuckDuckGo for legal updates."""
    try:
        # Use DuckDuckGo HTML for simple search
        url = f"https://html.duckduckgo.com/html/?q={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
    except Exception as e:
        logger.error(f"Web search error: {e}")
    return ""


async def get_legal_updates() -> str:
    """
    Get recent legal updates relevant to AIssential.

    Uses AI analysis to find current legal news.
    Optimized for speed with gpt-4o-mini.
    """
    import time
    from lib.ai_hub import ask_ai

    start_time = time.time()
    logger.info("Starting legal updates analysis...")

    # Simplified prompt for faster response
    prompt = f"""Date: {datetime.now().strftime('%d/%m/%Y')}

Analyse les actualités juridiques Vietnam pour AIssential (société de conseil IA, HCMC, employés vietnamiens et étrangers).

Domaines prioritaires:
1. Permis de travail / visa étrangers
2. Loi entreprises / SME
3. Réglementation IA / tech / données
4. Droit du travail
5. Fiscalité

Pour chaque mise à jour importante:
[emoji] **Titre** - Score: XX/100
- Loi/Décret: [numéro]
- Date effet: [date]
- Impact: [1 ligne]
- Action: [1 ligne]

Termine par:
⚠️ TOP 3 ACTIONS PRIORITAIRES

Scores: 🔴90+ critique | 🟠70-89 élevé | 🟡40-69 modéré | 🟢0-39 faible"""

    try:
        logger.info("Calling OpenAI API...")
        response = ask_ai(
            prompt=prompt,
            system="Expert juridique Vietnam. Concis et pratique. Cite les numéros de loi.",
            provider="openai",
            model="gpt-4o-mini",  # Fast model - 10x faster than gpt-4o
        )

        elapsed = time.time() - start_time
        logger.info(f"OpenAI response received in {elapsed:.1f}s")

        # Format the response
        header = f"🇻🇳 *VEILLE JURIDIQUE VIETNAM*\n📅 _{datetime.now().strftime('%d/%m/%Y %H:%M')}_\n\n"

        # Check if there are critical alerts (🔴) and add warning header
        if "🔴" in response or "CRITIQUE" in response.upper():
            header = f"🚨 *ALERTE JURIDIQUE CRITIQUE*\n📅 _{datetime.now().strftime('%d/%m/%Y %H:%M')}_\n\n"

        footer = "\n\n---\n💡 _/veille pour actualiser | Alertes: 🔴Critique 🟠Élevé 🟡Modéré 🟢Faible_"

        return header + response + footer

    except Exception as e:
        logger.error(f"Error getting legal updates: {e}")
        raise


async def check_critical_updates() -> tuple[bool, str]:
    """
    Check for critical legal updates that require immediate attention.

    Returns:
        Tuple of (has_critical, message)
    """
    try:
        updates = await get_legal_updates()

        # Check for critical indicators
        critical_keywords = [
            "🔴", "CRITIQUE", "Score: 9", "Score: 10",
            "action immédiate", "urgent", "deadline",
            "foreigner", "étranger", "work permit",
            "foreign-owned", "SME law change"
        ]

        has_critical = any(kw.lower() in updates.lower() for kw in critical_keywords)

        return has_critical, updates

    except Exception as e:
        logger.error(f"Error checking critical updates: {e}")
        return False, str(e)


def get_impact_description(score: int) -> str:
    """Get impact level description from score."""
    if score >= 90:
        return "🔴 CRITIQUE - Action immédiate requise"
    elif score >= 70:
        return "🟠 ÉLEVÉ - Action dans 30 jours"
    elif score >= 40:
        return "🟡 MODÉRÉ - À surveiller"
    else:
        return "🟢 FAIBLE - Information"


async def check_specific_topic(topic: str) -> str:
    """
    Check for updates on a specific legal topic.

    Args:
        topic: The topic to research (e.g., "labor law", "AI regulation")

    Returns:
        Formatted summary of relevant legal information
    """
    from lib.ai_hub import ask_ai

    prompt = f"""Research Vietnamese legal requirements and recent changes regarding: {topic}

For AIssential (AI consulting company in Vietnam), provide:
1. Current applicable laws and regulations
2. Recent changes (if any)
3. Compliance requirements
4. Recommended actions

Be specific and practical. Include decree/law numbers when relevant."""

    try:
        response = ask_ai(
            prompt=prompt,
            system="You are a Vietnamese legal expert.",
            provider="openai",
        )
        return response

    except Exception as e:
        logger.error(f"Error checking topic {topic}: {e}")
        raise


def get_monitored_topics() -> list:
    """Return list of topics being monitored."""
    return [
        "AI & Technology Regulation",
        "Labor Law (Bộ luật Lao động)",
        "Cybersecurity Law (Luật An ninh mạng)",
        "Enterprise Law (Luật Doanh nghiệp)",
        "Investment Law (Luật Đầu tư)",
        "Tax & Finance",
        "Data Protection & Privacy",
    ]
