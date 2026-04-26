<div align="center">

# 🦅 OmniHawk AI
### Radar global de inteligencia de IA para equipos y agentes

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

## ✨ Resumen
OmniHawk AI integra en una sola plataforma el seguimiento de papers de IA, lanzamientos de modelos, información financiera, reportes de industria, política y seguridad, y señales de ecosistema open-source.

Flujo principal: capturar -> deduplicar -> analizar -> suscribirse -> notificar.

## 🔭 Seis páginas independientes
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

Cada página mantiene configuración, filtros y suscripciones propias.

## 🚀 Inicio rápido
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

## 📡 Canales de notificación
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: interfaz estándar para integrar agentes.
- CLI: automatización local y ejecución por scripts (`omnihawk-ai-cli`).

## 📄 Licencia
Este proyecto usa [MIT License](LICENSE).

## 🙏 Referencia
Inspirado en [TrendRadar](https://github.com/sansan0/TrendRadar).
