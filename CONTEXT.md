# AIssential Legal Agent - Context

## Project Overview
Agent IA juridique pour analyser automatiquement des contrats depuis Google Drive, avec alertes Telegram.

## Tech Stack
- **Runtime**: Python 3.10+ sur Ubuntu 22.04 (VPS)
- **AI**: LLM Gateway -> Claude API
- **Storage**: Google Drive (polling)
- **Alerts**: Telegram Bot
- **Scheduling**: Cron (toutes les 30 min)

## Gateway Integration

This agent integrates with the AIssential LLM Gateway for:
- Centralized AI request management
- Automatic pseudonymisation
- Usage tracking and billing
- Failover between providers

### Identity
| Level | Value |
|-------|-------|
| Client ID | aissential-internal |
| App ID | legal-agent |
| Module IDs | analyze-contract, extract-text |
| User ID | system-agent (automated) |

### Endpoints
- Gateway: https://gateway.aissential.pro/v1
- Webhook (future): /api/webhooks/gateway

## AI Connector Integration

The AI Connector centralizes credentials management across all AIssential apps.
Configure credentials once in the Connector, use them everywhere.

### How it works
1. Agent requests credentials from Connector API
2. Connector returns credentials for the requested service
3. If Connector unavailable, falls back to local .env vars

### Supported Services
| Service | Credentials |
|---------|-------------|
| telegram | token, chat_id |
| google-drive | credentials_path, folder_id |

### Endpoints
- Connector: https://connector.aissential.pro/v1
- GET /credentials/{service} - Get credentials for a service

## Architecture
```
/opt/aissential-legal-agent/
├── app/
│   ├── main.py                 # Point d'entrée, orchestrateur
│   ├── system_prompt.txt       # Prompt système pour Claude
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Variables d'environnement
│   ├── lib/
│   │   ├── gateway/
│   │   │   ├── client.py       # Gateway HTTP client
│   │   │   └── modules.py      # Module ID constants
│   │   └── connector/
│   │       ├── client.py       # Connector HTTP client
│   │       └── services.py     # Service credential helpers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claude_client.py    # Client Anthropic avec retry
│   │   ├── contract_analyzer.py # Analyse des contrats
│   │   └── file_parser.py      # Extraction texte PDF/DOCX
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── telegram_bot.py     # Envoi alertes
│   │   └── google_drive.py     # Scan Google Drive
│   └── memory/
│       ├── __init__.py
│       ├── processed_files.py  # Tracking fichiers traités
│       └── processed.json      # Persistance
├── logs/
│   ├── app.log
│   └── errors.log
├── venv/
├── .env                        # Secrets (JAMAIS commit)
├── .env.example                # Template des variables
├── gcp.json                    # Service account Google (JAMAIS commit)
├── requirements.txt
└── README.md
```

## Environment Variables
| Variable | Description |
|----------|-------------|
| **Connector (prioritaire)** | |
| CONNECTOR_BASE_URL | URL Connector (https://connector.aissential.pro/v1) |
| CONNECTOR_API_KEY | Clé API Connector (optionnel, fallback sur env vars) |
| **Gateway** | |
| GATEWAY_API_KEY | Clé API Gateway |
| GATEWAY_BASE_URL | URL base Gateway (https://gateway.aissential.pro/v1) |
| GATEWAY_CLIENT_ID | Client ID (aissential-internal) |
| **Fallback (si pas de Connector)** | |
| TELEGRAM_TOKEN | Token bot Telegram |
| TELEGRAM_CHAT_ID | ID chat pour alertes |
| GOOGLE_APPLICATION_CREDENTIALS | Chemin vers gcp.json |
| GOOGLE_DRIVE_FOLDER_ID | ID dossier Drive à scanner |
| **Autres** | |
| RISK_THRESHOLD_ALERT | Seuil d'alerte (défaut: 60) |

## Key Features
- [x] Structure projet définie
- [x] config/settings.py - Chargement .env avec validation
- [x] services/claude_client.py - Client avec retry/backoff
- [x] services/contract_analyzer.py - Analyse + parsing JSON
- [x] services/file_parser.py - Support PDF/DOCX
- [x] integrations/telegram_bot.py - Alertes
- [x] integrations/google_drive.py - Polling Drive
- [x] memory/processed_files.py - Tracking fichiers
- [x] main.py - Orchestrateur
- [x] system_prompt.txt - Prompt juridique
- [x] requirements.txt - Dépendances
- [x] .env.example - Template
- [x] lib/gateway/ - LLM Gateway client
- [x] lib/connector/ - AI Connector client (centralized credentials)
- [ ] README.md - Documentation
- [x] GitHub repo créé

## GitHub
- **Repo**: https://github.com/aissential-pro/aissential-legal-agent
- **Owner**: aissential-pro

## Progress Log
- **2026-02-02**: Création structure initiale
- **2026-02-02**: Tous les modules Python créés (config, services, integrations, memory)
- **2026-02-02**: Repo GitHub créé et push initial (17 fichiers, 808 lignes)
- **2026-02-02**: Refactored to use LLM Gateway (aligned with aissential-platform architecture)
- **2026-02-02**: Added AI Connector integration for centralized credentials management

## Next Steps
1. Register legal-agent in Gateway admin
2. Get Gateway API key
3. Test with Gateway
4. Ajouter README.md avec instructions de déploiement
5. Configurer les credentials (Telegram, Google)
6. Déployer sur VPS
