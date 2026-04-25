<div align="center">

# 🦅 OmniHawk AI

### 面向智能体时代的全球 AI 情报操作系统

从论文、模型发布到资本市场、政策监管与开源生态，
统一抓取、去重、分析、订阅、推送，并通过 MCP + CLI 对外提供可编排接口。

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#docker-启动)
[![MCP](https://img.shields.io/badge/MCP-Enabled-111827?style=for-the-badge)](#mcp-服务)
[![CLI](https://img.shields.io/badge/Agent_CLI-Ready-0ea5e9?style=for-the-badge)](#agent-cli-接口新增)
[![License](https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge)](LICENSE)

**📣 多渠道订阅推送**

![Feishu](https://img.shields.io/badge/飞书-通知-00C95A?style=flat-square)
![WeCom](https://img.shields.io/badge/企业微信-通知-00A1FF?style=flat-square)
![WeChat](https://img.shields.io/badge/个人微信-通知-05C160?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-通知-2AABEE?style=flat-square)
![DingTalk](https://img.shields.io/badge/钉钉-通知-1677FF?style=flat-square)
![ntfy](https://img.shields.io/badge/ntfy-通知-5B7FFF?style=flat-square)
![Bark](https://img.shields.io/badge/Bark-通知-FF7A59?style=flat-square)
![Slack](https://img.shields.io/badge/Slack-通知-4A154B?style=flat-square)
![Email](https://img.shields.io/badge/Email-通知-6366F1?style=flat-square)

**🏷️ 重要标签**

![AI论文雷达](https://img.shields.io/badge/AI论文雷达-学术追踪-2563EB?style=flat-square)
![AI前沿雷达](https://img.shields.io/badge/AI前沿雷达-模型发布-0EA5E9?style=flat-square)
![AI财经信息](https://img.shields.io/badge/AI财经信息-全球市场-0891B2?style=flat-square)
![AI产业报告](https://img.shields.io/badge/AI产业报告-机构研究-14B8A6?style=flat-square)
![AI政策与安全](https://img.shields.io/badge/AI政策与安全-监管与风险-7C3AED?style=flat-square)
![AI开源生态](https://img.shields.io/badge/AI开源生态-开发者信号-1D4ED8?style=flat-square)
![订阅推送](https://img.shields.io/badge/订阅推送-多渠道触达-0F766E?style=flat-square)

<p align="center">
  <img src="docs/assets/omnihawk.svg" alt="OmniHawk AI emblem" width="920" />
</p>

**中文** | [English](README-EN.md)

</div>

## 🚀 为什么做这个项目
AI 信息分散在不同来源，且更新速度极快。单靠手动跟踪，通常会遇到：

- 信号分散：论文、厂商公告、财报、政策、开源趋势互相割裂。
- 时效噪声：旧新闻反复出现，难以筛出真正增量。
- 去重困难：跨源转载导致重复抓取、重复推送。
- 自动化不足：很难把“信息获取”直接接入 Agent 工作流。

`OmniHawk AI` 的目标是把这些环节做成一套可持续运行、可扩展、可被智能体直接调用的情报基础设施。

## 👥 适合哪些人
- AI 研究者：持续跟踪论文与方法演化。
- 产品/工程团队：跟踪模型发布、开源工具链与开发者信号。
- 投研与商业分析团队：跟踪 AI 相关财报、资本市场与产业报告。
- 政策与合规团队：跟踪多地区监管与安全事件。
- Agent Builder：需要可编排的 MCP/CLI 工具接口。

## 🧭 六大独立页面（并列关系）
| 页面 | 主要用途 | 典型来源 |
| --- | --- | --- |
| AI论文雷达 | 学术追踪与论文深度分析 | arXiv 等学术 RSS |
| AI 前沿雷达 | 模型/产品/技术进展 | 厂商官网、技术博客、官方新闻 |
| AI 财经信息 | 资本市场与公司动态 | 财报、电话会、市场资讯、投融资 |
| AI 产业报告 | 产业研究洞察 | 全球机构报告、白皮书 |
| AI 政策与安全 | 监管与风险事件 | 政策机构、监管公告、安全事件源 |
| AI 开源生态与开发者信号 | 开源工具与社区信号 | GitHub Trending、开源项目动态 |

> 这 6 个页面互不隶属。每个页面都有独立参数、独立订阅、独立推送配置。

## ⚙️ 核心能力
- 多源抓取 + 区域化组织（按国家/地区与来源类型组织渠道）。
- 历史持久化与去重（避免重复抓取、重复推送）。
- 默认新鲜度控制（如 90 天窗口）减少陈旧信息噪声。
- LLM 摘要/分析（中英文双模式）。
- 多渠道通知：`feishu`、`wework`、`wechat`、`telegram`、`dingtalk`、`ntfy`、`bark`、`slack`、`email`。
- 定时抓取与自动订阅推送。
- MCP 工具化接口。
- Agent CLI（本次新增）支持脚本化直接调用工具。

## 🧱 系统结构
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

## ⚡ Quick Start
### 1) 🧩 环境要求
- Python `>= 3.12`
- 推荐使用 `uv`
- Docker 用户需安装 `Docker` + `Docker Compose`

### 2) 🖥️ 本地启动（开发模式）
```bash
uv sync --locked
```

1. 运行爬取主程序（一次执行）：
```bash
omnihawk-ai
```

2. 运行交互式 Web 控制台（6 页面 UI）：
```bash
python -m trendradar.web.panel_server --port 8080 --output-dir output
```

3. 启动 MCP 服务（HTTP）：
```bash
omnihawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

### 3) 🐳 Docker 启动
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

默认端口：
- 主服务（容器内 Web 端口映射）：`WEBSERVER_PORT`（默认 8080）
- MCP：`http://127.0.0.1:3333/mcp`

停止：
```bash
docker compose -f docker/docker-compose.yml down
```

查看日志：
```bash
docker compose -f docker/docker-compose.yml logs -f
```

---

## 🤖 Agent CLI 接口（新增）
为了让智能体或脚本不走 MCP transport 也能直接调用工具，新增了 `omnihawk-ai-cli`。

### 🎯 设计目标
- 与 MCP 工具保持同构（同名工具、同参数语义）。
- JSON 输入 / JSON 输出，便于自动化编排。
- 适合 Shell、CI、Python subprocess、Agent 执行器。

### 🧪 安装后命令
```bash
omnihawk-ai-cli tools
```

### 📌 常用示例
1. 列出所有可调用工具及参数：
```bash
omnihawk-ai-cli tools
```

2. 调用工具（内联 JSON 参数）：
```bash
omnihawk-ai-cli call list_scope_items --args '{"scope":"market_finance","limit":20}'
```

3. 调用工具（参数文件）：
```bash
omnihawk-ai-cli call upsert_scope_subscription --args-file ./payload.json
```

4. 指定项目根目录和输出目录：
```bash
omnihawk-ai-cli --project-root . --output-dir ./output call get_project_overview
```

5. 紧凑 JSON 输出（适合管道处理）：
```bash
omnihawk-ai-cli call list_scopes --compact
```

### Windows PowerShell 示例（推荐）
1. 使用 `ConvertTo-Json` + `--args-file`（最稳妥）：
```powershell
$payload = @{ scope = "market_finance"; limit = 20 } | ConvertTo-Json -Compress
$payload | Set-Content -Encoding utf8 .\payload.json
omnihawk-ai-cli call list_scope_items --args-file .\payload.json --compact
```

2. 使用 Here-String 写参数文件：
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

3. 不带参数的工具可直接调用：
```powershell
omnihawk-ai-cli call get_project_overview --compact
```

### 🧾 退出码约定
- `0`：调用成功。
- `1`：执行期异常。
- `2`：参数错误 / 工具不存在 / JSON 格式错误。

### 🛠️ CLI 参数与覆盖范围
CLI 本身的固定参数如下：

| 级别 | 参数 | 说明 |
| --- | --- | --- |
| 全局 | `--project-root` | 覆盖项目根目录 |
| 全局 | `--output-dir` | 覆盖运行输出目录 |
| 全局 | `--compact` | 输出紧凑 JSON |
| 子命令 | `tools` | 列出可调用工具 |
| 子命令 | `call <tool>` | 调用指定工具 |
| `call` 选项 | `--args` | 内联 JSON 参数 |
| `call` 选项 | `--args-file` | 从 JSON 文件读参数 |

CLI 业务参数由具体工具决定，直接执行以下命令可查看全部工具参数定义：

```bash
omnihawk-ai-cli tools --compact
```

覆盖边界：
- 已覆盖当前 MCP 暴露的全部 22 个工具能力（项目概览、页面抓取、页面设置、页面订阅、论文分析等）。
- 不直接覆盖进程/容器生命周期管理（例如启动或停止 Docker、启动 Web 服务进程）。
- 不直接覆盖前端交互行为本身（例如浏览器点击），但可覆盖其对应的数据层操作（设置、抓取、订阅、推送）。

---

## 🔌 MCP 服务
### 启动
```bash
# stdio
python -m mcp_server.server --transport stdio

# http
python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333
```

HTTP Endpoint:

`http://127.0.0.1:3333/mcp`

### MCP 工具分组
1. 项目概览
- `get_project_overview`
- `list_pages`
- `list_scopes`

2. 全局设置
- `get_global_settings`
- `save_global_settings`

3. 页面数据与抓取
- `list_scope_sources`
- `list_scope_items`
- `fetch_scope_items`
- `get_scope_settings`
- `save_scope_settings`

4. 页面订阅
- `list_scope_subscriptions`
- `upsert_scope_subscription`
- `delete_scope_subscription`
- `run_scope_subscriptions`

5. 论文能力
- `list_papers`
- `get_paper_detail`
- `deep_analyze_paper`
- `set_paper_action`

6. 论文订阅
- `list_paper_subscriptions`
- `upsert_paper_subscription`
- `delete_paper_subscription`
- `run_paper_subscriptions`

---

## 🧠 配置说明
主要配置目录：`config/`

关键文件：
- `config/config.yaml`：主配置（抓取、推送、AI、存储等）
- `config/timeline.yaml`：定时策略（预设与自定义）
- `config/frequency_words.txt`：关键词规则
- `config/ai_interests.txt`：兴趣方向定义
- `config/ai_analysis_prompt.txt`：分析提示词
- `config/ai_translation_prompt.txt`：翻译提示词

运行输出目录：`output/`

常见持久化数据：
- `output/ai_progress_items.json`
- `output/ai_progress_seen.json`
- `output/panel_settings.json`
- `output/progress_page_settings.json`
- `output/panel_subscriptions.json`
- `output/progress_subscriptions.json`
- `output/news/*.db`
- `output/rss/*.db`

---

## 📣 推送渠道
已支持并在后端 + 前端 + MCP + CLI 统一：
- `feishu`
- `wework`
- `wechat`（个人微信，基于 WeCom text）
- `telegram`
- `dingtalk`
- `ntfy`
- `bark`
- `slack`
- `email`

---

## 🗂️ 项目结构
```text
.
├─ trendradar/                # 核心能力（抓取/分析/通知/Web）
│  ├─ __main__.py             # 主程序入口
│  ├─ agent_cli.py            # Agent CLI 入口（新增）
│  └─ web/panel_server.py     # 交互式控制台服务
├─ mcp_server/                # MCP 服务
├─ config/                    # 配置与提示词
├─ docker/                    # Dockerfile / compose / 入口脚本
├─ docs/assets/               # README 视觉资源（含 OmniHawk SVG）
├─ output/                    # 运行时持久化数据
├─ README.md
└─ README-EN.md
```

---

## ❓常见问题
### Q1: CLI 和 MCP 有什么关系？
CLI 直接调用 MCP 同构工具函数；MCP 适合协议接入，CLI 适合脚本与本地自动化。

### Q2: CLI 能覆盖全部功能吗？
CLI 能覆盖当前 MCP 已暴露的全部能力（22 个工具）。如果你在 UI 上能做的是数据层操作（抓取、查阅、设置、订阅、推送），通常都可以通过 CLI 实现。

### Q3: 为什么我看到重复消息？
请检查：
- `output/ai_progress_seen.json` 是否被挂载并持久化。
- 是否开启了多个重复订阅规则。
- `timeline` 与页面级订阅是否在同一时间窗重复触发。

### Q4: 如何最小化接入 Agent？
最简单方式：让 Agent 先调用
```bash
omnihawk-ai-cli call get_project_overview
```
然后按需调用 `list_scope_items` / `list_papers` / `run_*_subscriptions`。

---

## 🧭 路线图与贡献
- 路线图：见 [ROADMAP.md](ROADMAP.md)
- 扩展规划：见 [docs/EXPANSION-PLAN-ZH.md](docs/EXPANSION-PLAN-ZH.md)
- 贡献指南：见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🙏 致谢与参考
- 本项目在产品思路与工程实践上参考并致谢 [TrendRadar](https://github.com/sansan0/TrendRadar)。
- OmniHawk AI 在此基础上进行了独立演进，包括 6 页面并列体系、区域化数据源、多渠道订阅推送、MCP + Agent CLI 一体化等。

---

## 📄 许可证
本项目采用 [MIT License](LICENSE)。
