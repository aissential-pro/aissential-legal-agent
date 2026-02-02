# AIssential Legal Agent - Context

## Project Overview
Agent IA juridique pour analyser automatiquement des contrats depuis Google Drive, avec alertes Telegram.

## Tech Stack
- **Runtime**: Python 3.10+ sur Ubuntu 22.04 (VPS)
- **AI**: Claude API (claude-3-5-sonnet)
- **Storage**: Google Drive (polling)
- **Alerts**: Telegram Bot
- **Scheduling**: Cron (toutes les 30 min)

## Architecture
```
/opt/aissential-legal-agent/
├── app/
│   ├── main.py                 # Point d'entrée, orchestrateur
│   ├── system_prompt.txt       # Prompt système pour Claude
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Variables d'environnement
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
| ANTHROPIC_API_KEY | Clé API Anthropic |
| TELEGRAM_TOKEN | Token bot Telegram |
| TELEGRAM_CHAT_ID | ID chat pour alertes |
| GOOGLE_APPLICATION_CREDENTIALS | Chemin vers gcp.json |
| GOOGLE_DRIVE_FOLDER_ID | ID dossier Drive à scanner |
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
- [ ] README.md - Documentation
- [ ] GitHub repo créé

## Progress Log
- **2026-02-02**: Création structure initiale
- **2026-02-02**: Tous les modules Python créés (config, services, integrations, memory)

## Next Steps
1. Obtenir token GitHub de l'utilisateur
2. Créer repo GitHub
3. Push initial
4. Ajouter README.md
