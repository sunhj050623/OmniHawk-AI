<div align="center">

# 🦅 OmniHawk AI
### チームとエージェント向けグローバルAIインテリジェンスレーダー

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

## ✨ 概要
OmniHawk AI は、AI論文、モデルリリース、AI金融情報、産業レポート、政策と安全、オープンソース開発者シグナルを1つのプラットフォームに統合します。

主要フロー: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 6つの独立ページ
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

各ページは設定・フィルター・購読を独立して持ちます。

## 🚀 クイックスタート
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

## 📡 通知チャネル
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: エージェント連携向け標準インターフェース
- CLI: ローカル自動化とスクリプト実行 (`omnihawk-ai-cli`)

## 📄 ライセンス
このプロジェクトは [MIT License](LICENSE) を採用しています。

## 🙏 参照
[TrendRadar](https://github.com/sansan0/TrendRadar) に着想を得ています。
