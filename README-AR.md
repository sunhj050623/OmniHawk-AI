<div align="center">

# 🦅 OmniHawk AI
### رادار ذكاء اصطناعي عالمي للفرق والوكلاء

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

## ✨ نظرة عامة
يجمع OmniHawk AI في منصة واحدة تتبع أبحاث الذكاء الاصطناعي، وإصدارات النماذج، والبيانات المالية، وتقارير الصناعة، وتحديثات السياسات والسلامة، وإشارات مجتمع المصادر المفتوحة.

سير العمل الأساسي: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 ست صفحات مستقلة
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

لكل صفحة إعدادات وفلاتر واشتراكات مستقلة.

## 🚀 بدء سريع
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

## 📡 قنوات الإشعارات
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: واجهة قياسية لتكامل الوكلاء.
- CLI: للأتمتة المحلية وتشغيل السكربتات (`omnihawk-ai-cli`).

## 📄 الترخيص
هذا المشروع مرخّص بموجب [MIT License](LICENSE).

## 🙏 مرجع
مستوحى من [TrendRadar](https://github.com/sansan0/TrendRadar).
