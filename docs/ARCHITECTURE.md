# AIssential Legal Agent - Architecture & Documentation

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture actuelle](#architecture-actuelle)
3. [Fonctionnalités](#fonctionnalités)
4. [Configuration](#configuration)
5. [Intégration Gateway & Connector](#intégration-gateway--connector)
6. [Communication inter-agents](#communication-inter-agents)
7. [API Reference](#api-reference)
8. [Schémas de données](#schémas-de-données)
9. [Déploiement](#déploiement)
10. [Roadmap](#roadmap)

---

## Vue d'ensemble

### Mission
Legal Agent est le **Chief Legal Officer (CLO) virtuel** d'AIssential. Il agit comme un conseiller juridique proactif disponible 24/7, comparable à avoir McKinsey Legal en interne.

### Périmètre
- **Analyse automatique** de tous les contrats (clients, employés, fournisseurs)
- **Veille juridique** sur les lois vietnamiennes impactant l'entreprise
- **Alertes proactives** sur les risques et actions requises
- **Conseil stratégique** sans attendre qu'on lui demande

### Stack technique
| Composant | Technologie |
|-----------|-------------|
| Runtime | Python 3.10+ |
| AI Provider | OpenAI GPT-4o (direct) / LLM Gateway (production) |
| Storage | Google Drive (scan) |
| Interface | Telegram Bot |
| Scheduling | Cron / Bot interactif |

---

## Architecture actuelle

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LEGAL AGENT SYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    TELEGRAM BOT (bot.py)                     │   │
│  │  Commands: /start /scan /veille /status /ping /analyze       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                │
│         ▼                    ▼                    ▼                │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│  │   Google    │     │  Contract   │     │   Legal     │          │
│  │   Drive     │     │  Analyzer   │     │  Monitor    │          │
│  │   Scanner   │     │             │     │  (Veille)   │          │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘          │
│         │                   │                   │                  │
│         └───────────────────┴───────────────────┘                  │
│                             │                                      │
│                    ┌────────┴────────┐                             │
│                    ▼                 ▼                             │
│             ┌─────────────┐   ┌─────────────┐                      │
│             │   AI Hub    │   │  Telegram   │                      │
│             │  (OpenAI)   │   │   Alerts    │                      │
│             └─────────────┘   └─────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Structure des fichiers

```
aissential-legal-agent/
├── app/
│   ├── main.py                 # Entry point (batch scan)
│   ├── bot.py                  # Telegram bot interactif
│   ├── system_prompt.txt       # Prompt CLO Vietnam
│   │
│   ├── config/
│   │   └── settings.py         # Configuration centralisée
│   │
│   ├── services/
│   │   ├── contract_analyzer.py  # Analyse de contrats
│   │   ├── legal_monitor.py      # Veille juridique Vietnam
│   │   ├── claude_client.py      # Client AI unifié
│   │   └── file_parser.py        # Extraction PDF/DOCX
│   │
│   ├── integrations/
│   │   ├── telegram_bot.py     # Envoi alertes Telegram
│   │   └── google_drive.py     # Scan Google Drive
│   │
│   ├── lib/
│   │   ├── ai_hub/             # Multi-provider AI
│   │   ├── gateway/            # LLM Gateway client
│   │   └── connector/          # AI Connector client
│   │
│   └── memory/
│       └── processed_files.py  # Tracking fichiers traités
│
├── docs/                       # Documentation
├── deploy/                     # Scripts déploiement
├── .env                        # Configuration (secrets)
├── gcp.json                    # Google credentials
└── requirements.txt            # Dépendances Python
```

---

## Fonctionnalités

### 1. Analyse de contrats

**Déclencheurs:**
- Upload fichier dans Telegram
- Nouveau fichier dans Google Drive
- Commande `/scan`

**Output:**
```json
{
  "risk_score": 75,
  "risks": [
    {
      "description": "Période d'essai de 90 jours dépasse le maximum légal",
      "severity": "high",
      "vietnam_law_reference": "Bộ luật Lao động 2019, Article 25"
    }
  ],
  "missing_clauses": [
    "Clause de force majeure",
    "Clause RGPD/Data protection"
  ],
  "recommendations": [
    "Réduire période d'essai à 60 jours maximum",
    "Ajouter clause de confidentialité conforme à la loi cybersécurité"
  ],
  "vietnam_compliance": {
    "compliant": false,
    "issues": ["Période d'essai non conforme"],
    "required_actions": ["Modifier Article 3.2"]
  },
  "proactive_advice": {
    "strategic_recommendations": [
      "Renégocier avant renouvellement en Q2"
    ],
    "upcoming_risks": [
      "Nouvelle loi sur les données personnelles en discussion"
    ]
  }
}
```

### 2. Veille juridique Vietnam

**Commande:** `/veille`

**Domaines surveillés:**
| Domaine | Priorité | Exemples |
|---------|----------|----------|
| Étrangers au Vietnam | 🔴 Critique | Work permits, visas, ownership |
| Lois SME/Entreprises | 🔴 Critique | Licences, immatriculation |
| IA & Technologies | 🔴 Critique | Réglementation IA, data |
| Droit du travail | 🟠 Élevé | Contrats, assurance sociale |
| Cybersécurité | 🟠 Élevé | Data protection, localisation |
| Fiscalité | 🟠 Élevé | TVA, impôt société |
| Investissement | 🟡 Modéré | Règles investissement étranger |

**Scoring d'impact:**
| Score | Niveau | Action requise |
|-------|--------|----------------|
| 90-100 | 🔴 CRITIQUE | Immédiate |
| 70-89 | 🟠 ÉLEVÉ | Sous 30 jours |
| 40-69 | 🟡 MODÉRÉ | Surveiller |
| 0-39 | 🟢 FAIBLE | Information |

### 3. Commandes Telegram

| Commande | Description |
|----------|-------------|
| `/start`, `/help` | Afficher l'aide |
| `/ping` | Test de connectivité |
| `/scan` | Scanner tous les dossiers Drive (récursif) |
| `/veille` | Lancer veille juridique Vietnam |
| `/status` | Statut du bot et statistiques |
| `/analyze` | Instructions pour analyser un fichier |
| **Envoyer fichier** | Analyse automatique PDF/DOCX |

---

## Configuration

### Variables d'environnement (.env)

```bash
# ============================================
# AI PROVIDER (au moins un requis)
# ============================================
OPENAI_API_KEY=sk-...                    # OpenAI direct
ANTHROPIC_API_KEY=sk-ant-...             # Anthropic direct (optionnel)
MISTRAL_API_KEY=...                      # Mistral direct (optionnel)

# ============================================
# TELEGRAM BOT
# ============================================
TELEGRAM_TOKEN=1234567890:ABC...         # Token du bot
TELEGRAM_CHAT_ID=1234567890              # Chat ID pour alertes

# ============================================
# GOOGLE DRIVE
# ============================================
GOOGLE_APPLICATION_CREDENTIALS=gcp.json  # Chemin vers credentials
GOOGLE_DRIVE_FOLDER_IDS=id1,id2,id3      # Dossiers à scanner (virgules)

# ============================================
# ALERTES
# ============================================
RISK_THRESHOLD_ALERT=60                  # Score minimum pour alerte (0-100)

# ============================================
# AISSENTIAL GATEWAY (Production)
# ============================================
GATEWAY_BASE_URL=https://gateway.aissential.pro/v1
GATEWAY_API_KEY=...                      # Clé API Gateway
GATEWAY_CLIENT_ID=aissential-internal    # Client ID

# ============================================
# AISSENTIAL CONNECTOR (Production)
# ============================================
CONNECTOR_BASE_URL=https://connector.aissential.pro/v1
CONNECTOR_API_KEY=...                    # Clé API Connector
```

### Google Drive Setup

1. Créer un Service Account dans Google Cloud Console
2. Activer l'API Google Drive
3. Télécharger le fichier JSON credentials (`gcp.json`)
4. Partager les dossiers Drive avec l'email du service account

---

## Intégration Gateway & Connector

### Architecture cible (Production)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AISSENTIAL PLATFORM                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Legal   │ │  Admin   │ │  Sales   │ │ Finance  │ │   ...    │ │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agents  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │            │        │
│       └────────────┴────────────┴────────────┴────────────┘        │
│                              │                                      │
│              ┌───────────────┴───────────────┐                     │
│              ▼                               ▼                     │
│     ┌─────────────────┐            ┌─────────────────┐             │
│     │  AI CONNECTOR   │            │   LLM GATEWAY   │             │
│     │                 │            │                 │             │
│     │ • Credentials   │            │ • Model routing │             │
│     │ • API keys      │            │ • Rate limiting │             │
│     │ • Service auth  │            │ • Usage tracking│             │
│     │ • Secrets mgmt  │            │ • Cost control  │             │
│     └─────────────────┘            └─────────────────┘             │
│              │                               │                     │
│              ▼                               ▼                     │
│     ┌─────────────────┐            ┌─────────────────┐             │
│     │ External APIs   │            │   LLM Providers │             │
│     │ • Telegram      │            │ • OpenAI        │             │
│     │ • Google Drive  │            │ • Anthropic     │             │
│     │ • Email         │            │ • Mistral       │             │
│     └─────────────────┘            └─────────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### AI Connector

**Rôle:** Gestion centralisée des credentials pour tous les agents.

**Endpoints prévus:**
```
GET  /v1/credentials/{service}     # Obtenir credentials
POST /v1/credentials/{service}     # Enregistrer credentials
GET  /v1/services                  # Lister services disponibles
```

**Services supportés:**
- `telegram` - Token et Chat ID
- `google-drive` - Service account credentials
- `openai` - API key
- `anthropic` - API key
- `email` - SMTP credentials

**Code existant:** `app/lib/connector/client.py`

### LLM Gateway

**Rôle:** Routing centralisé des appels LLM avec contrôle des coûts.

**Fonctionnalités:**
- Routing vers OpenAI, Anthropic, Mistral
- Rate limiting par client/app
- Tracking d'usage et coûts
- File d'attente avec priorités
- Retry automatique
- Caching (optionnel)

**Endpoint principal:**
```
POST /v1/chat/completions
```

**Headers requis:**
```
Authorization: Bearer {api_key}
X-Client-Id: {client_id}
X-User-Id: {user_id}
X-App-Id: {app_id}
X-Module-Id: {module_id}
```

**Code existant:** `app/lib/gateway/client.py`

---

## Communication inter-agents

### Event Bus (Architecture future)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EVENT BUS                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   legal.contract.analyzed ──────────────────► Admin Agent           │
│   legal.alert.critical ─────────────────────► All Agents            │
│   legal.veille.update ──────────────────────► Admin Agent           │
│                                                                     │
│   admin.document.uploaded ──────────────────► Legal Agent           │
│   admin.task.assigned ──────────────────────► Legal Agent           │
│                                                                     │
│   finance.contract.created ─────────────────► Legal Agent           │
│   finance.invoice.overdue ──────────────────► Admin Agent           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Events émis par Legal Agent

```json
// Contrat analysé
{
  "event": "legal.contract.analyzed",
  "agent": "legal-agent",
  "timestamp": "2026-02-02T19:15:00Z",
  "data": {
    "contract_id": "drive_file_id",
    "contract_name": "Contract_Client_ABC.pdf",
    "risk_score": 75,
    "risk_level": "high",
    "vietnam_compliant": false,
    "requires_action": true,
    "action_deadline": "2026-02-15",
    "summary": "Contrat client avec risques élevés sur IP et confidentialité"
  },
  "notify": ["admin-agent", "telegram"]
}

// Alerte critique
{
  "event": "legal.alert.critical",
  "agent": "legal-agent",
  "timestamp": "2026-02-02T19:15:00Z",
  "priority": "critical",
  "data": {
    "alert_type": "law_change",
    "title": "Nouvelle loi sur les entreprises étrangères",
    "impact_score": 95,
    "effective_date": "2026-04-01",
    "action_required": "Mise à jour statuts société avant 01/04",
    "deadline": "2026-03-15"
  },
  "notify": ["admin-agent", "finance-agent", "telegram", "email"]
}

// Mise à jour veille
{
  "event": "legal.veille.update",
  "agent": "legal-agent",
  "timestamp": "2026-02-02T19:15:00Z",
  "data": {
    "updates_count": 3,
    "critical_count": 1,
    "high_count": 2,
    "topics": ["labor_law", "foreign_investment", "ai_regulation"],
    "summary": "1 changement critique sur work permits"
  },
  "notify": ["admin-agent"]
}
```

### Events écoutés par Legal Agent

```json
// Nouveau document uploadé
{
  "event": "admin.document.uploaded",
  "source": "admin-agent",
  "data": {
    "document_id": "xxx",
    "document_type": "contract",
    "file_path": "drive://folder/file.pdf",
    "uploaded_by": "user@aissential.pro",
    "requires_legal_review": true
  }
}

// Tâche assignée
{
  "event": "admin.task.assigned",
  "source": "admin-agent",
  "data": {
    "task_id": "xxx",
    "task_type": "contract_review",
    "priority": "high",
    "deadline": "2026-02-05",
    "context": "Nouveau contrat client à valider avant signature"
  }
}
```

---

## API Reference

### API REST (Future)

#### Analyser un contrat
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

file: [binary]
options: {
  "priority": "high",
  "notify": ["telegram", "email"],
  "callback_url": "https://..."
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "result": {
    "risk_score": 75,
    "risks": [...],
    "recommendations": [...],
    "vietnam_compliance": {...},
    "proactive_advice": {...}
  }
}
```

#### Lancer veille juridique
```http
POST /api/v1/veille
Content-Type: application/json

{
  "topics": ["labor_law", "foreign_investment"],
  "priority_filter": "high",
  "notify": ["telegram"]
}
```

#### Obtenir statut
```http
GET /api/v1/status

Response:
{
  "status": "healthy",
  "uptime": "24h 15m",
  "contracts_analyzed": 156,
  "alerts_sent": 23,
  "last_veille": "2026-02-02T18:00:00Z"
}
```

#### Webhook pour alertes
```http
POST /api/v1/webhook/alert
Content-Type: application/json

{
  "source": "admin-agent",
  "event": "document.uploaded",
  "data": {...}
}
```

---

## Schémas de données

### Contract Analysis Result
```typescript
interface ContractAnalysis {
  // Identification
  contract_id: string;
  contract_name: string;
  analyzed_at: string; // ISO 8601

  // Risk Assessment
  risk_score: number; // 0-100
  risk_level: "critical" | "high" | "medium" | "low";

  // Detailed Findings
  risks: Risk[];
  missing_clauses: string[];
  recommendations: string[];

  // Vietnam Specific
  vietnam_compliance: {
    compliant: boolean;
    issues: string[];
    required_actions: string[];
    law_references: string[];
  };

  // Proactive Advice
  proactive_advice: {
    strategic_recommendations: string[];
    upcoming_risks: string[];
    competitive_insights: string[];
  };
}

interface Risk {
  description: string;
  severity: "high" | "medium" | "low";
  vietnam_law_reference?: string;
  clause_reference?: string;
  recommended_action?: string;
}
```

### Legal Update
```typescript
interface LegalUpdate {
  // Identification
  update_id: string;
  detected_at: string;

  // Classification
  topic: string;
  impact_score: number; // 0-100
  impact_level: "critical" | "high" | "medium" | "low";

  // Details
  title: string;
  description: string;
  law_reference?: string;
  effective_date?: string;

  // Actions
  action_required: boolean;
  recommended_actions: string[];
  deadline?: string;

  // Relevance to AIssential
  relevance: {
    affects_foreigners: boolean;
    affects_sme: boolean;
    affects_tech: boolean;
    affects_labor: boolean;
  };
}
```

### Agent Event
```typescript
interface AgentEvent {
  // Metadata
  event: string; // e.g., "legal.contract.analyzed"
  agent: string; // e.g., "legal-agent"
  timestamp: string; // ISO 8601

  // Priority
  priority?: "critical" | "high" | "normal" | "low";

  // Payload
  data: Record<string, any>;

  // Routing
  notify?: string[]; // ["admin-agent", "telegram", "email"]
  callback_url?: string;
}
```

---

## Déploiement

### Local (Development)
```bash
cd C:/Users/franc/projects/aissential-legal-agent
./venv/Scripts/activate
python app/bot.py
```

### VPS (Production)

#### Systemd Service
```ini
# /etc/systemd/system/legal-agent.service
[Unit]
Description=AIssential Legal Agent
After=network.target

[Service]
Type=simple
User=aissential
WorkingDirectory=/opt/aissential-legal-agent
ExecStart=/opt/aissential-legal-agent/venv/bin/python app/bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

#### Cron pour scan automatique
```bash
# Scan toutes les 30 minutes
*/30 * * * * cd /opt/aissential-legal-agent && ./venv/bin/python app/main.py >> /var/log/legal-agent.log 2>&1

# Veille juridique quotidienne à 8h
0 8 * * * cd /opt/aissential-legal-agent && ./venv/bin/python -c "import asyncio; from app.services.legal_monitor import get_legal_updates; print(asyncio.run(get_legal_updates()))"
```

### Docker (Future)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY .env .

CMD ["python", "app/bot.py"]
```

---

## Roadmap

### Phase 1 - MVP (Actuel) ✅
- [x] Analyse de contrats automatique
- [x] Scan Google Drive récursif
- [x] Alertes Telegram
- [x] Bot interactif (/scan, /veille, /status)
- [x] Contexte juridique Vietnam
- [x] Scoring d'impact pour veille
- [x] Conseils proactifs

### Phase 2 - Intégration
- [ ] Connexion AI Connector
- [ ] Connexion LLM Gateway
- [ ] API REST pour autres agents
- [ ] Event bus inter-agents
- [ ] Connexion Admin Agent

### Phase 3 - Enrichissement
- [ ] Alertes email
- [ ] Dashboard web
- [ ] Historique des analyses
- [ ] Rapports périodiques automatiques
- [ ] Multi-langue (VN/EN/FR)

### Phase 4 - Intelligence
- [ ] Apprentissage des préférences
- [ ] Détection de patterns dans les contrats
- [ ] Suggestions de templates
- [ ] Benchmarking contrats vs marché

---

## Support

### Logs
```bash
# Bot logs
tail -f /opt/aissential-legal-agent/logs/app.log

# Systemd logs
journalctl -u legal-agent -f
```

### Debug
```bash
# Activer mode debug
DEBUG_MODE=true python app/bot.py
```

### Contact
- **Repo:** https://github.com/aissential-pro/aissential-legal-agent
- **Team:** AIssential Engineering

---

*Documentation générée le 2026-02-02*
*Version: 1.0.0*
