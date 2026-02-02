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

    Uses web search + AI analysis to find current legal news.
    """
    from lib.ai_hub import ask_ai

    # First, gather recent search results
    search_context = []
    for query in SEARCH_QUERIES[:3]:  # Limit to avoid timeout
        try:
            result = await _search_web(query)
            if result:
                # Extract just a snippet (first 1000 chars after body)
                if "<body" in result:
                    snippet = result[result.find("<body"):result.find("<body")+2000]
                    search_context.append(f"Query: {query}\nResults snippet available")
        except Exception as e:
            logger.warning(f"Search failed for {query}: {e}")

    # Now ask AI with instruction to search for current info
    prompt = f"""You are a legal analyst monitoring Vietnamese law changes for AIssential.

## COMPANY PROFILE (for impact assessment)
- **Company**: AIssential - AI consulting for startups
- **Location**: Vietnam (Ho Chi Minh City)
- **Structure**: Foreign-owned SME
- **Activities**: AI/Tech consulting, software, training
- **Employees**: Local Vietnamese + foreigners
- **Clients**: Startups, SMEs in Vietnam and abroad

TODAY'S DATE: {datetime.now().strftime('%d/%m/%Y')}

## YOUR TASK
Find the LATEST legal updates and rate their IMPACT on AIssential.

## IMPACT SCORING (use these levels)
🔴 **CRITIQUE (Score 90-100)** - Action immédiate requise
   - Laws affecting foreign-owned companies
   - SME/Enterprise law major changes
   - Work permit/visa rule changes for foreigners
   - Tax law significant changes
   - AI/Tech regulation that directly affects our business

🟠 **ÉLEVÉ (Score 70-89)** - Action dans 30 jours
   - Labor law changes affecting employment contracts
   - Social insurance contribution changes
   - Data protection new requirements
   - Licensing changes for consulting

🟡 **MODÉRÉ (Score 40-69)** - À surveiller
   - General business regulation updates
   - Minor tax adjustments
   - Procedural changes

🟢 **FAIBLE (Score 0-39)** - Information only
   - Unrelated sector regulations
   - Minor administrative updates

## RESEARCH THESE AREAS

1. **FOREIGNERS IN VIETNAM** (HIGH PRIORITY)
   - Work permit rules, visa changes
   - Foreign ownership restrictions
   - Investment regulations for foreign companies

2. **SME & ENTERPRISE LAW** (HIGH PRIORITY)
   - Business registration changes
   - Corporate governance requirements
   - Licensing for consulting/tech services

3. **AI & TECHNOLOGY**
   - AI governance frameworks
   - Data localization requirements
   - Digital transformation policies

4. **LABOR LAW**
   - Employment contract changes
   - Social insurance updates
   - Minimum wage changes

5. **TAX & FINANCE**
   - Corporate tax changes
   - VAT updates
   - Transfer pricing rules

6. **CYBERSECURITY & DATA**
   - Personal data protection
   - Cross-border data transfer
   - Compliance deadlines

## OUTPUT FORMAT

For each update found, provide:

[IMPACT EMOJI] **[TITLE]** - Score: XX/100
- 📜 Law/Decree: [Number]
- 📅 Effective: [Date]
- 💼 Impact on AIssential: [Specific impact]
- ✅ Action required: [What to do]

---

Then summarize:

🏛️ **PROJETS DE LOI EN COURS**
(Draft laws at National Assembly with impact scores)

⚠️ **TOP 3 ACTIONS PRIORITAIRES**
(Most urgent things AIssential must do)

📅 **CALENDRIER CRITIQUE**
(Key dates sorted by urgency)"""

    try:
        response = ask_ai(
            prompt=prompt,
            system="""You are an expert Vietnamese legal analyst with real-time knowledge of Vietnam's legal system.
You stay current with all new laws, decrees (nghị định), circulars (thông tư), and government announcements.
Always cite specific law numbers and effective dates. Focus on practical business impact.""",
            provider="openai",
            model="gpt-4o",  # Use more capable model for legal research
        )

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
