<div align="center">

# 🦅 OmniHawk AI
### 팀과 에이전트를 위한 글로벌 AI 인텔리전스 레이더

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

## ✨ 개요
OmniHawk AI는 AI 논문, 모델 릴리스, AI 금융 정보, 산업 리포트, 정책 및 안전, 오픈소스 개발자 신호를 하나의 플랫폼으로 통합합니다.

핵심 흐름: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 6개 독립 페이지
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

각 페이지는 설정, 필터, 구독을 독립적으로 유지합니다.

## 🚀 빠른 시작
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

## 📡 알림 채널
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: 에이전트 통합용 표준 인터페이스
- CLI: 로컬 자동화 및 스크립트 실행 (`omnihawk-ai-cli`)

## 📄 라이선스
이 프로젝트는 [MIT License](LICENSE)를 사용합니다.

## 🙏 참고
[TrendRadar](https://github.com/sansan0/TrendRadar)에서 영감을 받았습니다。
