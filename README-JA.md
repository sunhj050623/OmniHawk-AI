<div align="center">

# 🦅 オムニホークAI

### エージェント時代のグローバル AI インテリジェンス OS

論文やフロンティア モデルのリリースから資本市場、政策、OSS エコシステムまで:
エージェント ワークフロー用の MCP + CLI インターフェイスを使用して、1 つのプラットフォームからフェッチ、重複排除、分析、サブスクライブ、プッシュを実行します。

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#docker-start)
[![MCP](https://img.shields.io/badge/MCP-Enabled-111827?style=for-the-badge)](#mcp-service)
[![CLI](https://img.shields.io/badge/Agent_CLI-Ready-0ea5e9?style=for-the-badge)](#agent-cli-new)
[![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)](LICENSE)

**📣 サブスクリプションプッシュチャネル**

![Feishu](https://img.shields.io/badge/Feishu-Notify-00C95A?style=flat-square)
![WeCom](https://img.shields.io/badge/WeCom-Notify-00A1FF?style=flat-square)
![WeChat](https://img.shields.io/badge/WeChat-Notify-05C160?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-Notify-2AABEE?style=flat-square)
![DingTalk](https://img.shields.io/badge/DingTalk-Notify-1677FF?style=flat-square)
![ntfy](https://img.shields.io/badge/ntfy-Notify-5B7FFF?style=flat-square)
![Bark](https://img.shields.io/badge/Bark-Notify-FF7A59?style=flat-square)
![Slack](https://img.shields.io/badge/Slack-Notify-4A154B?style=flat-square)
![Email](https://img.shields.io/badge/Email-Notify-6366F1?style=flat-square)

**🏷️重要なタグ**

![AI Paper Radar](https://img.shields.io/badge/AI%20Paper%20Radar-Research%20Tracking-2563EB?style=flat-square)
![AI Frontier Radar](https://img.shields.io/badge/AI%20Frontier%20Radar-Model%20Releases-0EA5E9?style=flat-square)
![AI Finance](https://img.shields.io/badge/AI%20Finance-Global%20Markets-0891B2?style=flat-square)
![AI Industry Reports](https://img.shields.io/badge/AI%20Industry%20Reports-Institutional%20Insights-14B8A6?style=flat-square)
![AI Policy and Safety](https://img.shields.io/badge/AI%20Policy%20%26%20Safety-Regulation%20%26%20Risk-7C3AED?style=flat-square)
![AI OSS Signals](https://img.shields.io/badge/AI%20OSS%20Signals-Developer%20Ecosystem-1D4ED8?style=flat-square)
![Subscription Push](https://img.shields.io/badge/Subscription%20Push-Multi%20Channel-0F766E?style=flat-square)

<p align="center">
  <img src="image.png" alt="OpenHawk project banner" width="920" />
</p>

[中文](README.md) | [English](README-EN.md) | [हिन्दी](README-HI.md) | [Español](README-ES.md) | [العربية](README-AR.md) | [Français](README-FR.md) | [Português](README-PT.md) | [বাংলা](README-BN.md) | **日本語** | [한국어](README-KO.md)

</div>

## 🚀 このプロジェクトが存在する理由
AI 信号は高度に断片化されており、高速に移動します。手動追跡は通常、次の原因で失敗します。

- チャネルの断片化: 論文、ベンダーの発表、収益、ポリシーの最新情報、OSS トレンドが分断されています。
- 最新性のノイズ: 古いニュースが再浮上し続け、新しい情報がかき消されます。
- 重複排除の問題: シンジケートされた再投稿により、繰り返しの取り込みと繰り返しの通知がトリガーされます。
- 自動化のギャップ: 「インテリジェンス取得」をエージェント パイプラインに直接統合するのは困難です。

「OpenHawk」は、これを、エージェントが直接呼び出すことができる常時稼働の拡張可能なインテリジェンス層に変えます。

## 👥対象者
- AI 研究者: 論文と手法の進化を継続的に追跡します。
- 製品チームとエンジニアリング チーム: リリース、ツール、開発者のシグナルを追跡します。
- 投資および戦略チーム: 収益、設備投資、資金調達、市場の動きを追跡します。
- ポリシーおよびコンプライアンス チーム: 地域全体の規制と AI の安全性インシデントを追跡します。
- エージェント ビルダー: MCP/CLI ツールをプログラム可能な機能として使用します。

## 🧭 6 つの独立したページ (並列、ネストされていない)
| ページ | 主な用途 | 代表的な情報源 |
| --- | --- | --- |
| AIペーパーレーダー | 学術追跡と詳細な論文分析 | arXiv とリサーチフィード |
| AIフロンティア | モデル、製品、テクノロジーのアップデート | 公式サイト、ベンダーのブログ、ラボ |
| AIファイナンス | 資本市場と企業情報 | 収益、通話記録、市場フィード、資金調達/M&A |
| AI業界レポート | 業界および機関の研究 | 世界的なシンクタンク、機関、白書 |
| AI ポリシーと安全性 | 規制とリスクの監視 | 規制当局、政策機関、安全インシデントの情報源 |
| AI OSS と開発シグナル | オープンソース ツールと開発エコシステムのトレンド | GitHub Trending + README セマンティック フィルタリング |

> 6 ページはすべて独立しています。各ページには、独立した設定、サブスクリプション、プッシュ ルールがあります。

## ⚙️ コア機能
- 地域指向のソース構成によるマルチソースの取り込み。
- 永続的な履歴 + インデックスの重複除去により、フェッチ/プッシュの繰り返しを防ぎます。
- 古いアイテムを抑制するための最新性制御 (90 日のウィンドウなど)。
- タイトル、LLM 分析、プッシュ コンテンツの統合翻訳パイプライン (任意のターゲット言語)。
- マルチチャネル通知: `feishu`、`wework`、`wechat`、`telegram`、`dingtalk`、`ntfy`、`bark`、`slack`、`email`。
- スマート プッシュ戦略: `毎日` / `増分` / `リアルタイム`。
- スケジュールされたフェッチとオプションの自動プッシュ サブスクリプション ジョブ。
- プロトコルベースのエージェント統合のための MCP ツール インターフェイス。
- スクリプト可能なローカル ツールを直接呼び出すためのエージェント CLI (新機能)。

## 🌐 統合翻訳パイプライン (任意のターゲット言語)
- すべてのレイヤーにわたる 1 つのパイプライン: 「タイトル」、「LLM 概要/分析」、および「通知ペイロード」。
- ターゲット言語のサポート: 「英語」、「韓国語」、「日本語」、「フランス語」、「中国語」、「繁体字中国語」、およびカスタム言語ターゲット。
- コスト制御: バッチ変換、増分フィールド入力、および API 呼び出しの繰り返しを避けるための永続的な再利用。
- 一貫した動作: Web、MCP、および CLI は同じ `output_ language` セマンティクスを共有するため、UI とプッシュ出力は同期を保ちます。

例 (CLI):
```bash
# Set AI Finance page output language to Japanese
openhawk-ai-cli call save_scope_settings --args '{"scope":"market_finance","output_language":"Japanese"}'

# Fetch using this scope and language policy
openhawk-ai-cli call fetch_scope_items --args '{"scope":"market_finance","max_per_source":20}'
```

## 🧠 スマートプッシュ戦略
| 戦略 | トリガー | 最適な用途 | 特性 |
| --- | --- | --- | --- |
| 「毎日」 | 毎日のスケジュールされた概要 | エグゼクティブ/チームダイジェスト | 固定リズムでの完全なトピックの集約 |
| 「増分」 | スケジュールされたウィンドウ、新規のみ | 日常的なモニタリング | 重複ゼロの増分配信 |
| 「リアルタイム」 | イベントトリガーによる即時プッシュ | メジャー モデルのリリース、ポリシーの変更、資金調達のアラート | スケジュールを待たずに、最高の適時性を実現 |

注:
- 戦略はサブスクリプション ルールごとに構成され、6 ページ全体で異なる場合があります。
- フィルター (ソース、地域、イベント タイプ、キーワード) と組み合わせて、正確なアラート ルーティングを行うことができます。

## 🧱 システムアーキテクチャ
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

## ⚡ クイックスタート
### 1) 🧩 要件
- Python `>= 3.12`
- `uv` が推奨されます
- Docker ユーザー: `Docker` + `Docker Compose`

### 2) 🖥️ 地元のスタートアップ (開発)
```bash
uv sync --locked
```

1. メインのフェッチ/ランタイムを 1 回実行します。
```bash
openhawk-ai
```

2. インタラクティブな Web コンソール (6 ページの UI) を実行します。
```bash
python -m openhawk_ai.web.panel_server --port 8080 --output-dir output
```

3. MCP サービス (HTTP) を開始します。
```bash
openhawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

### 3) 🐳 Docker の起動
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

デフォルトのポート:
- Webサービス: `WEBSERVER_PORT` (デフォルト: `8080`)
- MCP エンドポイント: `http://127.0.0.1:3333/mcp`

停止：
```bash
docker compose -f docker/docker-compose.yml down
```

ログを表示する:
```bash
docker compose -f docker/docker-compose.yml logs -f
```

---

## 🤖 エージェント CLI (新規)
エージェント/スクリプトが MCP トランスポートを使用せずに OpenHawk ツールを直接呼び出せるようにするために、このリポジトリには `openhawk-ai-cli` が追加されています。

### 🎯 設計目標
- MCP ツールと同じ機能面 (同じツール名と引数セマンティクス)。
- 自動化に適した統合のための JSON 入力と JSON 出力。
- シェル スクリプト、CI パイプライン、エージェント エグゼキュータとうまく連携します。

### 🧪 基本コマンド
```bash
openhawk-ai-cli tools
```

### 📌 一般的な例
1. 利用可能なすべてのツールとパラメータをリストします。
```bash
openhawk-ai-cli tools
```

2. インライン JSON を使用してツールを呼び出します。
```bash
openhawk-ai-cli call list_scope_items --args '{"scope":"market_finance","limit":20}'
```

3. args ファイルを使用してツールを呼び出します。
```bash
openhawk-ai-cli call upsert_scope_subscription --args-file ./payload.json
```

4. プロジェクトのルートと出力ディレクトリを上書きします。
```bash
openhawk-ai-cli --project-root . --output-dir ./output call get_project_overview
```

5. コンパクトな JSON 出力 (パイプラインフレンドリー):
```bash
openhawk-ai-cli call list_scopes --compact
```

### Windows PowerShell の例 (推奨)
1. `ConvertTo-Json` を `--args-file` とともに使用します (最も信頼性が高い)。
```powershell
$payload = @{ scope = "market_finance"; limit = 20 } | ConvertTo-Json -Compress
$payload | Set-Content -Encoding utf8 .\payload.json
openhawk-ai-cli call list_scope_items --args-file .\payload.json --compact
```

2. here-string args ファイルを使用します。
```powershell
@'
{
  "scope": "frontier",
  "max_per_source": 20,
  "source_ids": ["openai-news", "anthropic-news"]
}
'@ | Set-Content -Encoding utf8 .\payload.json

openhawk-ai-cli call fetch_scope_items --args-file .\payload.json --compact
```

3. 引数を必要としないツールは直接呼び出すことができます。
```powershell
openhawk-ai-cli call get_project_overview --compact
```

### 🧾 終了コード
- `0`: 成功
- `1`: ランタイム/ツール実行エラー
- `2`: 無効なパラメータ、不明なツール、または不正な形式の JSON

### 🛠️ CLI パラメータと適用範囲
CLI の固定引数:

| レベル | パラメータ | 説明 |
| --- | --- | --- |
| グローバル | `--プロジェクトルート` | プロジェクトルートを上書きする |
| グローバル | `--出力ディレクトリ` | 出力ディレクトリをオーバーライドする |
| グローバル | 「--コンパクト」 | コンパクトな JSON を出力する |
| サブコマンド | 「ツール」 | 利用可能なツールをリストする |
| サブコマンド | `<ツール> を呼び出します` | ツールを呼び出す |
| 「呼び出し」オプション | `--args` | インライン JSON 引数 |
| 「呼び出し」オプション | `--args-file` | ファイルからJSON引数をロードします |

ツール ビジネス引数はツールごとに定義されます。使用：

```bash
openhawk-ai-cli tools --compact
```

適用範囲の境界:
- 概要、スコープのフェッチ/リスト/設定/サブスクリプション、ペーパー インテリジェンス/サブスクリプションを含む、現在公開されているすべての MCP ツール機能 (22 ツール) をカバーします。
- プロセス/コンテナーのライフサイクルを直接管理しません (例: Docker または Web サーバー プロセスの開始/停止)。
- ブラウザー UI の操作を直接実行しませんが、同等のデータ層操作 (設定、フェッチ、サブスクリプション、プッシュ) をカバーします。

---

## 🔌 MCP サービス
＃＃＃ 始める
```bash
# stdio
python -m mcp_server.server --transport stdio

# http
python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333
```

HTTP エンドポイント:

「http://127.0.0.1:3333/mcp」

### MCP ツール グループ
1. プロジェクト概要
- `get_project_overview`
- `リストページ`
- `リストスコープ`

2. グローバル設定
- `get_global_settings`
- `グローバル設定の保存`

3. データのスコープと取得
- `list_scope_sources`
- `list_scope_items`
- `fetch_scope_items`
- `get_scope_settings`
- `スコープ設定の保存`

4. サブスクリプションの範囲
- `list_scope_subscriptions`
- `upsert_scope_subscription`
- `delete_scope_subscription`
- `run_scope_subscriptions`

5. 紙のインテリジェンス
- `リスト_論文`
- `get_paper_detail`
- `deep_analyze_paper`
- `set_paper_action`

6. 紙の定期購読
- `list_paper_subscriptions`
- `upsert_paper_subscription`
- `delete_paper_subscription`
- `run_paper_subscriptions`

---

## 🧠設定
メインの設定ディレクトリ: `config/`

主要なファイル:
- `config/config.yaml`: メインのランタイム設定 (フェッチ、AI、プッシュ、ストレージ)
- `config/timeline.yaml`: スケジュールのプリセットとタイミング ルール
- `config/frequency_words.txt`: キーワードの頻度ルール
- `config/ai_interests.txt`: 興味のあるトピック
- `config/ai_analysis_prompt.txt`: 分析プロンプトのテンプレート
- `config/ai_translation_prompt.txt`: 翻訳プロンプトのテンプレート

ランタイム出力ディレクトリ: `output/`

一般的な永続ファイル:
- `output/ai_progress_items.json`
- `output/ai_progress_seen.json`
- `output/panel_settings.json`
- `output/progress_page_settings.json`
- `output/panel_subscriptions.json`
- `output/progress_subscriptions.json`
- `output/news/*.db`
- `output/rss/*.db`

---

## 📣 通知チャネル
バックエンド + フロントエンド + MCP + CLI 全体で一貫して実装:
- フェイシュ
- 「ウィーワーク」
- `wechat` (WeCom テキスト モード経由の個人 WeChat)
- 「電報」
- 「ディントーク」
- `ntfy`
- 「樹皮」
- 「たるみ」
- 「メール」

---

## 🗂️ プロジェクトの構造
```text
.
├─ openhawk_ai/                # Core runtime (fetch/analyze/push/web)
│  ├─ __main__.py             # Main entry
│  ├─ agent_cli.py            # Agent CLI entry (new)
│  └─ web/panel_server.py     # Interactive console server
├─ mcp_server/                # MCP server
├─ config/                    # Configuration and prompt templates
├─ docker/                    # Dockerfile / compose / entry scripts
├─ docs/assets/               # README visual assets (including OpenHawk SVG)
├─ output/                    # Runtime persistent data
├─ README.md
└─ README-EN.md
```

---

## ❓よくある質問
### Q1: CLI と MCP の関係は何ですか?
CLI は、同じ MCP 互換ツール関数を直接呼び出します。プロトコル統合には MCP を使用し、ローカル スクリプト/自動化には CLI を使用します。

### Q2: CLI はすべての機能をカバーできますか?
CLI は、MCP によって現在公開されているすべての機能 (22 ツール) をカバーします。 UI のアクションがデータ層操作 (フェッチ、クエリ、設定、サブスクリプション、プッシュ) にマップされている場合、通常は CLI を介して自動化できます。

### Q3: 重複したメッセージが表示されるのはなぜですか?
チェック：
- 「output/ai_progress_seen.json」が正しく永続化/マウントされているかどうか
- 重複したサブスクリプション ルールが設定されているかどうか
- 「タイムライン」とページレベルのサブスクリプションが重複ウィンドウをトリガーしているかどうか

### Q4: 最小のエージェント統合パスは何ですか?
以下から始めます:
```bash
openhawk-ai-cli call get_project_overview
```
次に、必要に応じて `list_scope_items` / `list_papers` / `run_*_subscriptions` を呼び出します。

---

## 🙏 謝辞と参照
- このプロジェクトは、[TrendRadar](https://github.com/sansan0/TrendRadar) を参照し、それに触発されています。
- OpenHawk は、6 つの並列ページ、地域化されたソース戦略、マルチチャネル サブスクリプション、および統合された MCP + Agent CLI ワークフローを備えたアーキテクチャを独自に拡張します。

---

## 📄 ライセンス
このプロジェクトは、[MIT ライセンス](LICENSE) に基づいてライセンスされています。
