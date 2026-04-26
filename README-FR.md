<div align="center">

# 🦅 OmniHawk AI
### Radar mondial d’intelligence IA pour équipes et agents

</div>

## Language Versions (Top 10)
- [Chinese (Simplified)](README.md)
- [English](README-EN.md)
- [Hindi](README-HI.md)
- [Spanish](README-ES.md)
- [Arabic](README-AR.md)
- [French](README-FR.md)
- [Portuguese](README-PT.md)
- [Bengali](README-BN.md)
- [Japanese](README-JA.md)
- [Korean](README-KO.md)

## ✨ Vue d’ensemble
OmniHawk AI réunit sur une seule plateforme le suivi des papers IA, des releases de modèles, des données financières, des rapports sectoriels, des politiques/sécurité et des signaux open source.

Flux principal : fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 Six pages indépendantes
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

Chaque page possède ses propres paramètres, filtres et abonnements.

## 🚀 Démarrage rapide
```bash
uv sync --locked
omnihawk-ai
python -m omnihawk_ai.web.panel_server --port 8080 --output-dir output
omnihawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

## 🐳 Docker
```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml logs -f
docker compose -f docker/docker-compose.yml down
```

## 📡 Canaux de notification
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP : interface standard pour l’intégration d’agents.
- CLI : automatisation locale et scripts (`omnihawk-ai-cli`).

## 📄 Licence
Ce projet est sous [MIT License](LICENSE).

## 🙏 Référence
Inspiré de [TrendRadar](https://github.com/sansan0/TrendRadar).
