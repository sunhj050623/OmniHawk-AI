<div align="center">

# 🦅 OmniHawk IA

### Système d'exploitation mondial d'intelligence artificielle pour l'ère des agents

Des articles et versions de modèles pionniers aux marchés de capitaux, en passant par les politiques et les écosystèmes OSS :
récupérez, déduisez, analysez, abonnez-vous et envoyez depuis une seule plateforme, avec les interfaces MCP + CLI pour les flux de travail des agents.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#docker-start)
[![MCP](https://img.shields.io/badge/MCP-Enabled-111827?style=for-the-badge)](#mcp-service)
[![CLI](https://img.shields.io/badge/Agent_CLI-Ready-0ea5e9?style=for-the-badge)](#agent-cli-new)
[![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)](LICENSE)

**📣 Canaux push d'abonnement**

![Feishu](https://img.shields.io/badge/Feishu-Notify-00C95A?style=flat-square)
![WeCom](https://img.shields.io/badge/WeCom-Notify-00A1FF?style=flat-square)
![WeChat](https://img.shields.io/badge/WeChat-Notify-05C160?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-Notify-2AABEE?style=flat-square)
![DingTalk](https://img.shields.io/badge/DingTalk-Notify-1677FF?style=flat-square)
![ntfy](https://img.shields.io/badge/ntfy-Notify-5B7FFF?style=flat-square)
![Bark](https://img.shields.io/badge/Bark-Notify-FF7A59?style=flat-square)
![Slack](https://img.shields.io/badge/Slack-Notify-4A154B?style=flat-square)
![Email](https://img.shields.io/badge/Email-Notify-6366F1?style=flat-square)

**🏷️ Balises importantes**

![AI Paper Radar](https://img.shields.io/badge/AI%20Paper%20Radar-Research%20Tracking-2563EB?style=flat-square)
![AI Frontier Radar](https://img.shields.io/badge/AI%20Frontier%20Radar-Model%20Releases-0EA5E9?style=flat-square)
![AI Finance](https://img.shields.io/badge/AI%20Finance-Global%20Markets-0891B2?style=flat-square)
![AI Industry Reports](https://img.shields.io/badge/AI%20Industry%20Reports-Institutional%20Insights-14B8A6?style=flat-square)
![AI Policy and Safety](https://img.shields.io/badge/AI%20Policy%20%26%20Safety-Regulation%20%26%20Risk-7C3AED?style=flat-square)
![AI OSS Signals](https://img.shields.io/badge/AI%20OSS%20Signals-Developer%20Ecosystem-1D4ED8?style=flat-square)
![Subscription Push](https://img.shields.io/badge/Subscription%20Push-Multi%20Channel-0F766E?style=flat-square)

<p align="center">
  <img src="image.png" alt="OmniHawk AI project banner" width="920" />
</p>

[中文](README.md) | [English](README-EN.md) | [हिन्दी](README-HI.md) | [Español](README-ES.md) | [العربية](README-AR.md) | **Français** | [Português](README-PT.md) | [বাংলা](README-BN.md) | [日本語](README-JA.md) | [한국어](README-KO.md)

</div>

## 🚀 Pourquoi ce projet existe
Les signaux de l’IA sont très fragmentés et évoluent rapidement. Le suivi manuel échoue généralement en raison de :

- Canaux fragmentés : les articles, les annonces des fournisseurs, les revenus, les mises à jour des politiques et les tendances des logiciels libres sont déconnectés.
- Bruit de récence : les informations périmées ne cessent de refaire surface et évincent les nouveaux signaux.
- Problème de déduplication : les reposts syndiqués déclenchent des ingestions répétées et des notifications répétées.
- Lacune en matière d'automatisation : difficile d'intégrer le "intelligence fetching" directement dans les pipelines d'agents.

« OmniHawk AI » transforme cela en une couche de renseignement extensible et permanente que les agents peuvent appeler directement.

## 👥 À qui s'adresse-t-il
- Chercheurs en IA : suivre l'évolution des articles et des méthodes en continu.
- Équipes produit et d'ingénierie : suivre les versions, les outils et les signaux des développeurs.
- Équipes d'investissement et de stratégie : suivre les bénéfices, les investissements, le financement et les mouvements de marché.
- Équipes chargées des politiques et de la conformité : suivez les incidents de réglementation et de sécurité de l'IA dans les régions.
- Générateurs d'agents : utilisez les outils MCP/CLI comme capacités programmables.

## 🧭 Six pages indépendantes (parallèles, non imbriquées)
| Page | Utilisation principale | Sources typiques |
| --- | --- | --- |
| Radar papier IA | Suivi académique et analyse approfondie des documents | arXiv et flux de recherche |
| Frontière de l'IA | Mises à jour de modèles, de produits et de technologies | sites officiels, blogs de fournisseurs, laboratoires |
| Financement de l'IA | Marché des capitaux et intelligence des entreprises | résultats, transcriptions d'appels, flux de marché, financement/M&A |
| Rapports sur l'industrie de l'IA | Recherche industrielle et institutionnelle | groupes de réflexion mondiaux, institutions, livres blancs |
| Politique et sécurité de l'IA | Réglementation et surveillance des risques | régulateurs, organismes politiques, sources d’incidents de sécurité |
| AI OSS et signaux de développement | Outils open source et tendances de l'écosystème de développement | GitHub Trending + filtrage sémantique README |

> Les six pages sont indépendantes. Chaque page comporte des paramètres, des abonnements et des règles push isolés.

## ⚙️ Capacités de base
- Ingestion multi-sources avec une organisation des sources orientée région.
- Historique persistant + index de déduplication pour éviter les récupérations/pushs répétés.
- Contrôle de récence (par exemple, une fenêtre de 90 jours) pour supprimer les éléments obsolètes.
- Pipeline de traduction unifié (n'importe quelle langue cible) pour les titres, l'analyse LLM et le contenu push.
- Notifications multicanaux : `feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`.
- Stratégies push intelligentes : "quotidiennement" / "incrémentale" / "en temps réel".
- Récupération planifiée et tâches d'abonnement automatique en option.
- Interface de l'outil MCP pour l'intégration d'agents basés sur un protocole.
- Agent CLI (nouveau) pour l'invocation directe et scriptable d'outils locaux.

## 🌐 Pipeline de traduction unifié (n'importe quelle langue cible)
- Un pipeline sur toutes les couches : « titre », « résumé/analyse LLM » et « charge utile de notification ».
- Prise en charge des langues cibles : « Anglais », « Coréen », « Japonais », « Français », « Chinois », « Chinois traditionnel », ainsi que des cibles linguistiques personnalisées.
- Contrôle des coûts : traduction par lots, remplissage incrémentiel des champs et réutilisation persistante pour éviter les appels API répétés.
- Comportement cohérent : Web, MCP et CLI partagent la même sémantique « output_langage », de sorte que les sorties de l'interface utilisateur et du push restent synchronisées.

Exemple (CLI) :
```bash
# Set AI Finance page output language to Japanese
omnihawk-ai-cli call save_scope_settings --args '{"scope":"market_finance","output_language":"Japanese"}'

# Fetch using this scope and language policy
omnihawk-ai-cli call fetch_scope_items --args '{"scope":"market_finance","max_per_source":20}'
```

## 🧠 Stratégie Push intelligente
| Stratégie | Déclenchement | Idéal pour | Caractéristiques |
| --- | --- | --- | --- |
| 'quotidiennement' | Résumé programmé quotidiennement | Résumé de la direction/de l'équipe | Agrégation complète de sujets à cadence fixe |
| « incrémental » | Fenêtre planifiée, nouveaux uniquement | Surveillance de routine | Livraison incrémentielle sans duplication |
| "en temps réel" | Push immédiat déclenché par un événement | Publications majeures de modèles, ruptures de politique, alertes de financement | Pas d'attente pour le calendrier, rapidité maximale |

Remarques :
- La stratégie est configurée par règle d'abonnement et peut différer sur les 6 pages.
- Peut être combiné avec des filtres (source, région, type d'événement, mots-clés) pour un routage précis des alertes.

## 🧱Architecture système
```text
             +---------------------------+
             |      Data Sources         |
             | papers / frontier / ...   |
             +-------------+-------------+
                           |
                           v
+----------------+   +------------+   +-------------------+
| Fetch & Dedupe |-->| Persistence|-->| Analysis & Routing|
+----------------+   +------------+   +-------------------+
                           |                    |
                           v                    v
                    +-------------+     +------------------+
                    | Web Console |     | Notification Push |
                    +------+------+     +------------------+
                           |
                +----------+----------+
                | MCP Server / CLI    |
                | (agent automation)  |
                +---------------------+
```

---

## ⚡ Démarrage rapide
### 1) 🧩 Exigences
-Python `>= 3.12`
- `uv` est recommandé
- Utilisateurs Docker : `Docker` + `Docker Compose`

### 2) 🖥️ Startup Locale (Développement)
```bash
uv sync --locked
```

1. Exécutez le moteur d'exécution/extraction principal une fois :
```bash
omnihawk-ai
```

2. Exécutez la console Web interactive (interface utilisateur de 6 pages) :
```bash
python -m omnihawk_ai.web.panel_server --port 8080 --output-dir output
```

3. Démarrez le service MCP (HTTP) :
```bash
omnihawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

### 3) 🐳 Démarrage Docker
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Ports par défaut :
- Service Web : `WEBSERVER_PORT` (par défaut : `8080`)
- Point de terminaison MCP : `http://127.0.0.1:3333/mcp`

Arrêt:
```bash
docker compose -f docker/docker-compose.yml down
```

Afficher les journaux :
```bash
docker compose -f docker/docker-compose.yml logs -f
```

---

## 🤖 Agent CLI (Nouveau)
Pour permettre aux agents/scripts d'appeler directement les outils OmniHawk sans transport MCP, ce référentiel ajoute « omnihawk-ai-cli ».

### 🎯 Objectifs de conception
- Même surface de fonctionnalités que les outils MCP (mêmes noms d'outils et même sémantique d'argument).
- Entrée JSON et sortie JSON pour une intégration conviviale.
- Fonctionne bien avec les scripts shell, les pipelines CI et les exécuteurs d'agents.

### 🧪 Commande de base
```bash
omnihawk-ai-cli tools
```

### 📌 Exemples courants
1. Répertoriez tous les outils et paramètres disponibles :
```bash
omnihawk-ai-cli tools
```

2. Appelez un outil avec JSON en ligne :
```bash
omnihawk-ai-cli call list_scope_items --args '{"scope":"market_finance","limit":20}'
```

3. Appelez un outil avec le fichier args :
```bash
omnihawk-ai-cli call upsert_scope_subscription --args-file ./payload.json
```

4. Remplacez la racine du projet et le répertoire de sortie :
```bash
omnihawk-ai-cli --project-root . --output-dir ./output call get_project_overview
```

5. Sortie JSON compacte (compatible avec les pipelines) :
```bash
omnihawk-ai-cli call list_scopes --compact
```

### Exemples Windows PowerShell (recommandé)
1. Utilisez `ConvertTo-Json` avec `--args-file` (le plus fiable) :
```powershell
$payload = @{ scope = "market_finance"; limit = 20 } | ConvertTo-Json -Compress
$payload | Set-Content -Encoding utf8 .\payload.json
omnihawk-ai-cli call list_scope_items --args-file .\payload.json --compact
```

2. Utilisez un fichier args ici :
```powershell
@'
{
  "scope": "frontier",
  "max_per_source": 20,
  "source_ids": ["openai-news", "anthropic-news"]
}
'@ | Set-Content -Encoding utf8 .\payload.json

omnihawk-ai-cli call fetch_scope_items --args-file .\payload.json --compact
```

3. Les outils qui ne nécessitent aucun argument peuvent être appelés directement :
```powershell
omnihawk-ai-cli call get_project_overview --compact
```

### 🧾Codes de sortie
- '0' : succès
- `1` : erreur d'exécution/exécution de l'outil
- `2` : paramètres invalides, outil inconnu ou JSON mal formé

### 🛠️ Paramètres et couverture CLI
Arguments corrigés de la CLI :

| Niveau | Paramètre | Description |
| --- | --- | --- |
| Mondial | `--racine-du projet` | Remplacer la racine du projet |
| Mondial | `--rép-sortie` | Remplacer le répertoire de sortie |
| Mondial | `--compact` | Émettre du JSON compact |
| Sous-commande | `outils` | Liste des outils disponibles |
| Sous-commande | `appeler <outil>` | Invoquer un outil |
| option « appeler » | `--arguments` | Arguments JSON en ligne |
| option « appeler » | `--fichier-args` | Charger les arguments JSON à partir du fichier |

Les arguments métier des outils sont définis par outil. Utiliser:

```bash
omnihawk-ai-cli tools --compact
```

Limite de couverture :
- Couvre toutes les fonctionnalités des outils MCP actuellement exposées (22 outils), y compris la présentation, la récupération/liste/paramètres/abonnements de portée et l'intelligence papier/abonnements.
- Ne gère pas directement le cycle de vie des processus/conteneurs (par exemple démarrage/arrêt des processus Docker ou du serveur Web).
- N'effectue pas directement les interactions avec l'interface utilisateur du navigateur, mais couvre les opérations équivalentes au niveau de la couche de données (paramètres, récupération, abonnements, push).

---

## 🔌Service MCP
### Commencer
```bash
# stdio
python -m mcp_server.server --transport stdio

# http
python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333
```

Point de terminaison HTTP :

`http://127.0.0.1:3333/mcp`

### Groupes d'outils MCP
1. Aperçu du projet
- `get_project_overview`
- `liste_pages`
- `list_scopes`

2. Paramètres globaux
- `get_global_settings`
- `save_global_settings`

3. Portée des données et récupération
- `list_scope_sources`
- `list_scope_items`
- `fetch_scope_items`
- `get_scope_settings`
- `save_scope_settings`

4. Portée des abonnements
- `list_scope_subscriptions`
- `upsert_scope_subscription`
- `delete_scope_subscription`
- `run_scope_subscriptions`

5. Intelligence papier
- `list_papers`
- `get_paper_detail`
- `deep_analyze_paper`
- `set_paper_action`

6. Abonnements papier
- `list_paper_subscriptions`
- `upsert_paper_subscription`
- `delete_paper_subscription`
- `run_paper_subscriptions`

---

## 🧠Configuration
Répertoire de configuration principal : `config/`

Fichiers clés :
- `config/config.yaml` : configuration principale du runtime (récupération, IA, push, stockage)
- `config/timeline.yaml` : préréglages de planification et règles de timing
- `config/ Frequency_words.txt` : règles de fréquence des mots clés
- `config/ai_interests.txt` : intérêts du sujet
- `config/ai_analysis_prompt.txt` : modèle d'invite d'analyse
- `config/ai_translation_prompt.txt` : modèle d'invite de traduction

Répertoire de sortie du runtime : `output/`

Fichiers persistants courants :
- `output/ai_progress_items.json`
- `output/ai_progress_seen.json`
- `output/panel_settings.json`
- `output/progress_page_settings.json`
- `output/panel_subscriptions.json`
- `output/progress_subscriptions.json`
- `sortie/nouvelles/*.db`
- `sortie/rss/*.db`

---

## 📣 Canaux de notification
Implémenté de manière cohérente sur backend + frontend + MCP + CLI :
- `feishu`
- 'nous travaillons'
- `wechat` (WeChat personnel via le mode texte WeCom)
- `télégramme`
- `dingtalk`
- `ntfy`
- 'aboiement'
- 'relâchement'
- `e-mail`

---

## 🗂️ Structure du projet
```text
.
├─ omnihawk_ai/                # Core runtime (fetch/analyze/push/web)
│  ├─ __main__.py             # Main entry
│  ├─ agent_cli.py            # Agent CLI entry (new)
│  └─ web/panel_server.py     # Interactive console server
├─ mcp_server/                # MCP server
├─ config/                    # Configuration and prompt templates
├─ docker/                    # Dockerfile / compose / entry scripts
├─ docs/assets/               # README visual assets (including OmniHawk SVG)
├─ output/                    # Runtime persistent data
├─ README.md
└─ README-EN.md
```

---

## ❓FAQ
### Q1 : Quelle est la relation entre CLI et MCP ?
CLI appelle directement les mêmes fonctions d’outil compatibles MCP. Utilisez MCP pour l'intégration de protocole et CLI pour les scripts/automatisations locaux.

### Q2 : La CLI peut-elle couvrir toutes les fonctionnalités ?
CLI couvre toutes les fonctionnalités actuellement exposées par MCP (22 outils). Si une action dans l'interface utilisateur correspond à des opérations de couche de données (récupération, requête, paramètres, abonnements, push), elle est généralement automatisable via CLI.

### Q3 : Pourquoi est-ce que je vois des messages en double ?
Vérifier:
- si `output/ai_progress_seen.json` est persistant/monté correctement
- si des règles d'abonnement dupliquées sont configurées
- si les abonnements « timeline » et au niveau de la page déclenchent des fenêtres qui se chevauchent

### Q4 : Quel est le chemin d'intégration minimum de l'agent ?
Commencez par :
```bash
omnihawk-ai-cli call get_project_overview
```
Appelez ensuite `list_scope_items` / `list_papers` / `run_*_subscriptions` selon vos besoins.

---

## 🙏 Remerciements et référence
- Ce projet fait référence et s'inspire de [TrendRadar](https://github.com/sansan0/TrendRadar).
- OmniHawk AI étend indépendamment l'architecture avec six pages parallèles, une stratégie source régionalisée, des abonnements multicanaux et des flux de travail MCP + Agent CLI intégrés.

---

## 📄 Licence
Ce projet est sous licence [Licence MIT] (LICENSE).
