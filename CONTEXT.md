# AIssential Legal Agent - Context

## Project Overview
Agent IA juridique ("CLO virtuel") pour AIssential - analyse automatique des contrats, veille juridique Vietnam, et conseil proactif via Telegram.

## Tech Stack
- **Runtime**: Python 3.10+
- **AI**: OpenAI GPT-4o (direct) / LLM Gateway (production)
- **Storage**: Google Drive (scan récursif multi-dossiers)
- **Interface**: Telegram Bot (alertes + commandes interactives)
- **Scheduling**: Cron (batch) ou Bot (interactif)

## Current Status: OPÉRATIONNEL ✅

### Fonctionnalités actives
- [x] Analyse automatique de contrats (PDF/DOCX)
- [x] Scan Google Drive récursif (sous-dossiers inclus)
- [x] Support multi-dossiers Drive
- [x] Alertes Telegram formatées avec emojis
- [x] Bot interactif avec commandes
- [x] Contexte juridique Vietnam intégré
- [x] Veille juridique avec scoring d'impact
- [x] Surveillance des projets de loi (Quốc hội)
- [x] Conseils proactifs sans demande
- [x] Conformité Vietnam dans les analyses

### En préparation
- [ ] Connexion AI Connector (credentials centralisés)
- [ ] Connexion LLM Gateway (production)
- [ ] API REST pour inter-agents
- [ ] Connexion avec Admin Agent
- [ ] Alertes email

## Credentials Configured

### Telegram ✅
- **Bot**: @aissential_legal_bot
- **Status**: Opérationnel

### Google Drive ✅
- **Service Account**: legal-agent-drive@legal-agent-drive.iam.gserviceaccount.com
- **Dossiers configurés**: 3 dossiers (clients, travail, fournisseurs)
- **Mode**: Scan récursif (sous-dossiers inclus)

### AI Provider ✅
- **Provider**: OpenAI
- **Model**: gpt-4o / gpt-4o-mini
- **Fallback**: AI Hub multi-provider

## Architecture

```
aissential-legal-agent/
├── app/
│   ├── main.py                 # Entry point (batch scan)
│   ├── bot.py                  # Telegram bot interactif
│   ├── system_prompt.txt       # Prompt CLO Vietnam
│   │
│   ├── config/
│   │   └── settings.py         # Configuration
│   │
│   ├── services/
│   │   ├── contract_analyzer.py  # Analyse contrats + alertes
│   │   ├── legal_monitor.py      # Veille juridique Vietnam
│   │   ├── claude_client.py      # Client AI unifié
│   │   └── file_parser.py        # Extraction PDF/DOCX
│   │
│   ├── integrations/
│   │   ├── telegram_bot.py     # Envoi alertes
│   │   └── google_drive.py     # Scan Drive récursif
│   │
│   ├── lib/
│   │   ├── ai_hub/             # Multi-provider AI
│   │   ├── gateway/            # LLM Gateway client (future)
│   │   └── connector/          # AI Connector client (future)
│   │
│   └── memory/
│       └── processed_files.py  # Tracking fichiers traités
│
├── docs/
│   └── ARCHITECTURE.md         # Documentation complète
│
├── .env                        # Configuration (secrets)
├── gcp.json                    # Google credentials
├── requirements.txt
└── CONTEXT.md                  # Ce fichier
```

## Telegram Bot Commands

| Commande | Description |
|----------|-------------|
| `/start`, `/help` | Afficher l'aide |
| `/ping` | Test de connectivité |
| `/scan` | Scanner tous les dossiers Drive (récursif) |
| `/veille` | Veille juridique Vietnam avec scoring |
| `/status` | Statut du bot et statistiques |
| `/analyze` | Instructions pour analyser un fichier |
| **Envoyer fichier** | Analyse automatique PDF/DOCX |

## Veille Juridique - Scoring d'Impact

| Score | Niveau | Critères | Action |
|-------|--------|----------|--------|
| 🔴 90-100 | CRITIQUE | Lois étrangers, SME, work permits | Immédiate |
| 🟠 70-89 | ÉLEVÉ | Droit travail, data, assurance | 30 jours |
| 🟡 40-69 | MODÉRÉ | Business général | Surveiller |
| 🟢 0-39 | FAIBLE | Mises à jour mineures | Info |

### Domaines surveillés (priorité haute)
- 👤 Étrangers au Vietnam (work permits, visas, ownership)
- 🏢 Lois SME/Entreprises (licences, immatriculation)
- 🤖 Réglementation IA/Tech
- 🏛️ Projets de loi à l'Assemblée nationale

## Configuration (.env)

```bash
# AI Provider (au moins un requis)
OPENAI_API_KEY=sk-...

# Telegram
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...

# Google Drive (multi-dossiers, virgules)
GOOGLE_APPLICATION_CREDENTIALS=gcp.json
GOOGLE_DRIVE_FOLDER_IDS=id1,id2,id3

# Alertes
RISK_THRESHOLD_ALERT=60

# Future: Gateway & Connector
# GATEWAY_BASE_URL=https://gateway.aissential.pro/v1
# GATEWAY_API_KEY=...
# CONNECTOR_BASE_URL=https://connector.aissential.pro/v1
# CONNECTOR_API_KEY=...
```

## Commands

```bash
# Activer environnement
cd C:/Users/franc/projects/aissential-legal-agent
./venv/Scripts/activate

# Lancer bot interactif
python app/bot.py

# Lancer scan batch
python app/main.py
```

## Documentation

📄 **Documentation complète**: `docs/ARCHITECTURE.md`
- Architecture détaillée
- Intégration Gateway & Connector
- Communication inter-agents
- API Reference
- Schémas de données
- Déploiement
- Roadmap

## GitHub
- **Repo**: https://github.com/aissential-pro/aissential-legal-agent
- **Owner**: aissential-pro

## Progress Log
- **2026-02-02**: Création structure initiale
- **2026-02-02**: Modules Python (config, services, integrations)
- **2026-02-02**: GitHub repo créé
- **2026-02-02**: AI Hub multi-provider
- **2026-02-02**: Telegram configuré et testé ✅
- **2026-02-02**: Google Drive service account ✅
- **2026-02-02**: Premier scan réussi (2 contrats)
- **2026-02-02**: Support multi-dossiers Drive
- **2026-02-02**: Scan récursif (sous-dossiers)
- **2026-02-02**: Bot Telegram interactif
- **2026-02-02**: Contexte juridique Vietnam (CLO)
- **2026-02-02**: Veille juridique avec scoring d'impact
- **2026-02-02**: Surveillance projets de loi (Quốc hội)
- **2026-02-02**: Conseils proactifs intégrés
- **2026-02-02**: Documentation ARCHITECTURE.md

## Next Steps
1. Déployer sur VPS production
2. Activer AI Connector quand prêt
3. Activer LLM Gateway quand prêt
4. Connecter avec Admin Agent
5. Ajouter alertes email
