# AIssential Legal Agent - Guide de Fiabilité

## Améliorations v2.0 (2026-02-03)

### Problèmes résolus

| Problème | Solution | Fichier |
|----------|----------|---------|
| Bot crash sans redémarrage | Supervisor avec restart automatique | `app/supervisor.py` |
| Erreurs réseau causent des échecs | Retry avec exponential backoff | `app/utils/reliability.py` |
| Impossible de savoir si bot est mort | Health check + Heartbeat toutes les 6h | `app/bot.py` |
| Logs deviennent énormes | Rotation automatique (10MB max, 5 backups) | `app/utils/logging_config.py` |
| Perte de données processed.json | Sauvegardes atomiques + backup auto | `app/memory/processed_files.py` |

---

## Architecture de fiabilité

```
┌─────────────────────────────────────────────────────────┐
│                    SUPERVISOR                            │
│  - Démarre le bot                                       │
│  - Détecte les crashs                                   │
│  - Redémarre avec backoff (5s → 5min max)              │
│  - Notifie via Telegram en cas de crash/recovery        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      BOT.PY                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ /health     │  │ /veille     │  │ /scan       │     │
│  │ /status     │  │ /expirations│  │ /analyze    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  Jobs programmés:                                       │
│  - 08:00 Veille juridique                              │
│  - 09:00 Check expirations                             │
│  - Toutes les 6h: Heartbeat                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 COUCHE FIABILITÉ                        │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ @retry_backoff  │  │ CircuitBreaker  │              │
│  │ 5 retries max   │  │ (si nécessaire) │              │
│  │ 1s → 60s delay  │  │                 │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## Commandes de maintenance

### Démarrage

```bash
# Mode simple (développement)
cd app && python bot.py

# Mode production (avec supervision)
python app/supervisor.py

# Ou via les scripts
./start_bot.bat       # Windows CMD
./start_bot.ps1       # PowerShell
```

### Installation comme service Windows

```powershell
# En tant qu'administrateur
.\install_service.ps1
```

### Vérification de l'état

```bash
# Logs en temps réel
tail -f logs/app.log

# Erreurs uniquement
tail -f logs/error.log

# Sur Telegram
/health    # Diagnostic complet
/status    # Statistiques
/ping      # Test rapide
```

### Arrêt

```bash
# Windows
taskkill /F /IM python.exe

# Ou Ctrl+C si lancé en foreground
```

---

## Fichiers de logs

| Fichier | Contenu | Rotation |
|---------|---------|----------|
| `logs/app.log` | Tous les logs | 10 MB, 5 backups |
| `logs/error.log` | Erreurs uniquement | 10 MB, 5 backups |
| `logs/supervisor.log` | Logs du supervisor | 5 MB, 3 backups |

---

## Persistance des données

| Fichier | Contenu | Backup |
|---------|---------|--------|
| `app/memory/processed.json` | IDs fichiers traités | Auto toutes les 10 écritures |
| `app/memory/processed.backup.json` | Backup automatique | - |
| `app/memory/expirations.json` | Dates d'expiration contrats | - |

### Récupération en cas de corruption

```python
from memory.processed_files import invalidate_cache, get_processed_ids

# Forcer rechargement depuis backup
invalidate_cache()
ids = get_processed_ids()  # Récupère auto depuis backup si corrompu
```

---

## Monitoring

### Heartbeat

Le bot envoie un message de statut automatique toutes les 6 heures contenant :
- Uptime
- Utilisation mémoire
- Nombre de fichiers analysés
- Nombre d'erreurs

### Alertes automatiques

Le supervisor envoie une alerte Telegram quand :
- Le bot crash (avec code d'erreur)
- Le bot redémarre après crash
- Le bot démarre

---

## Troubleshooting

### "Conflict: terminated by other getUpdates request"

**Cause:** Plusieurs instances du bot tournent en même temps.

**Solution:**
```bash
taskkill /F /IM python.exe
python app/supervisor.py
```

### Le bot ne répond plus

1. Vérifier les logs: `tail -f logs/app.log`
2. Vérifier le processus: `tasklist | grep python`
3. Redémarrer: `python app/supervisor.py`

### Erreurs Google Drive

**Cause possible:** Token expiré ou permissions manquantes.

**Solution:** Vérifier `gcp.json` et les permissions du service account.

### Erreurs OpenAI/AI

**Cause possible:** Quota dépassé ou clé API invalide.

**Solution:** Vérifier `OPENAI_API_KEY` dans `.env`

---

## Probabilité de crash

Avec les améliorations v2.0, la probabilité de **downtime prolongé** est très faible :

| Scénario | Avant | Après |
|----------|-------|-------|
| Erreur réseau temporaire | Crash | Retry auto (5 tentatives) |
| API Telegram indisponible | Crash | Retry avec backoff |
| Crash inattendu | Bot mort | Restart auto par supervisor |
| Corruption processed.json | Données perdues | Récupération depuis backup |

**Estimation fiabilité:** 99%+ uptime avec supervisor actif.

---

## Contact

Pour toute question de maintenance, consulter ce fichier ou les logs.
