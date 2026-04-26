<div align="center">

# 🦅 OmniHawk AI
### Radar global de inteligência em IA para equipes e agentes

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

## ✨ Visão geral
O OmniHawk AI centraliza em uma única plataforma o acompanhamento de papers de IA, lançamentos de modelos, dados financeiros, relatórios da indústria, política/segurança e sinais de ecossistema open source.

Fluxo principal: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 Seis páginas independentes
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

Cada página possui configurações, filtros e assinaturas independentes.

## 🚀 Início rápido
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

## 📡 Canais de notificação
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: interface padrão para integração de agentes.
- CLI: automação local e execução via scripts (`omnihawk-ai-cli`).

## 📄 Licença
Este projeto utiliza [MIT License](LICENSE).

## 🙏 Referência
Inspirado em [TrendRadar](https://github.com/sansan0/TrendRadar).
