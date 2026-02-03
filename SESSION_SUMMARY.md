# Session de Maintenance - 3 Février 2026

## Problèmes résolus

### 1. Fiabilité du bot (crash fréquents)
- **Ajouté:** Supervisor avec restart automatique (`app/supervisor.py`)
- **Ajouté:** Retry avec exponential backoff pour les appels API
- **Ajouté:** Health check (`/health`) et heartbeat quotidien à 7h00
- **Ajouté:** Logs rotatifs (10 MB max)
- **Ajouté:** Persistance robuste avec backup automatique

### 2. Lenteur de /veille (15 min → 15 sec)
- **Changé:** GPT-4o → GPT-4o-mini (10x plus rapide)
- **Réduit:** Prompt de 160 lignes → 30 lignes
- **Supprimé:** Recherches web DuckDuckGo (souvent bloquées)

### 3. Bot ne répondait pas en privé
- **Cause:** Multiples instances en conflit
- **Solution:** Tuer toutes les instances et relancer UNE seule

---

## Fichiers créés/modifiés

| Fichier | Description |
|---------|-------------|
| `app/supervisor.py` | Supervision avec restart auto + alertes Telegram |
| `app/utils/reliability.py` | Décorateurs retry avec backoff |
| `app/utils/logging_config.py` | Configuration logs rotatifs |
| `app/memory/processed_files.py` | Persistance robuste avec backup |
| `start_bot.bat` | Script de démarrage Windows |
| `start_bot.ps1` | Script PowerShell |
| `install_service.ps1` | Installation comme service Windows |
| `RELIABILITY.md` | Guide de maintenance complet |

---

## Comment lancer le bot

### Mode simple (développement)
```
Double-cliquez sur: C:\Users\franc\projects\aissential-legal-agent\start_bot.bat
```

### Mode production (avec supervision)
```cmd
cd C:\Users\franc\projects\aissential-legal-agent
venv\Scripts\python.exe app\supervisor.py
```

### Comme service Windows (démarrage auto)
```powershell
# En administrateur
.\install_service.ps1
```

---

## Commandes Telegram

| Commande | Description |
|----------|-------------|
| `/ping` | Test rapide |
| `/health` | Diagnostic complet (nouveau) |
| `/status` | Statistiques |
| `/veille` | Veille juridique Vietnam |
| `/scan` | Scanner Google Drive |
| `/expirations` | Contrats qui expirent |

---

## Heartbeat automatique

Le bot envoie un message de statut **chaque jour à 7h00 (heure Vietnam)** avec:
- Uptime
- Utilisation mémoire du PC
- Nombre de fichiers analysés
- Nombre d'erreurs

**Note:** "Mémoire 85%" = RAM totale du VPS, pas du bot.

---

## Déploiement VPS Production

| Info | Valeur |
|------|--------|
| **IP** | 72.60.104.129 |
| **User** | frawan |
| **Path** | `/home/frawan/aissential-legal-agent` |
| **Process Manager** | pm2 (name: `legal-agent`) |

### Connexion SSH
```bash
ssh -i C:\Users\franc\.ssh\id_ed25519_vps_francis_hcm frawan@72.60.104.129
```

### Commandes pm2 (sur VPS)
```bash
pm2 status              # Voir status
pm2 logs legal-agent    # Voir logs
pm2 restart legal-agent # Redémarrer
```

---

## En cas de problème

1. **Bot ne répond pas:** Vérifier qu'une seule instance tourne
   ```cmd
   tasklist | findstr python
   ```

2. **Multiples instances:** Tout tuer et relancer
   ```cmd
   taskkill /F /IM python.exe
   start_bot.bat
   ```

3. **Logs:** `C:\Users\franc\projects\aissential-legal-agent\logs\app.log`

---

## Git commits effectués

1. `feat: Add reliability improvements for 99%+ uptime`
2. `perf: Optimize /veille command for 10x faster response`
3. `docs: Add VPS deployment info to CONTEXT.md`
4. `chore: Schedule heartbeat daily at 7:00 AM Vietnam time`

Repo: https://github.com/aissential-pro/aissential-legal-agent
