# OpenHawk 扩展计划（中文）

本文档用于指导项目从“论文+大厂进展聚合”升级为“AI 全景情报系统”。

## 1. 目标与边界

目标：
- 覆盖 AI 关键决策信息，不做无差别资讯堆砌。
- 每条情报可追溯（来源、时间、证据）。
- 低噪声推送（去重、分级、打分）。

当前优先边界：
- 只做公开合法来源。
- 默认抓取近 90 天信息（按模块可调）。
- 先做“高价值事件”再扩展“泛资讯”。

## 2. 扩展模块总览

### 模块 A：AI 财经信息（高优先级）

采集重点：
- 财报与电话会中的 AI 业务披露
- CapEx / GPU / 算力采购和云成本变化
- 融资、并购、IPO、回购、裁员等资本事件
- AI 产品商业化里程碑（付费、客户、订单、利润口径）

事件类型建议：
- finance_earnings
- finance_capex
- finance_funding
- finance_mna
- finance_guidance_change

新增字段建议：
- company
- ticker
- amount
- currency
- quarter
- guidance_delta
- business_impact

### 模块 B：AI 产业报告（高优先级）

采集重点：
- 咨询机构/研究机构/云厂商年度与季度报告
- 行业 adoption、ROI、市场规模、渗透率数据
- 报告结论之间的分歧与反转

事件类型建议：
- report_market
- report_industry
- report_forecast

新增字段建议：
- institution
- report_name
- report_period
- methodology_note
- key_claims[]
- confidence_level

### 模块 C：AI 政策与监管（中高优先级）

采集重点：
- 法规、指南、标准、征求意见稿
- 版权/数据合规/模型备案/出口管制相关更新
- 监管机构处罚与典型案例

事件类型建议：
- policy_law
- policy_guideline
- policy_enforcement

新增字段建议：
- jurisdiction
- legal_status
- effective_date
- compliance_tags[]

### 模块 D：AI 安全与事故（中优先级）

采集重点：
- 模型越狱、数据泄露、系统故障
- 红队报告与漏洞披露
- 高影响滥用事件

事件类型建议：
- safety_incident
- safety_vulnerability
- safety_mitigation

新增字段建议：
- severity
- affected_system
- incident_window
- remediation_status

### 模块 E：AI 开源生态与开发者信号（中优先级）

采集重点：
- 关键开源仓库 release
- 模型社区（模型发布、基准变化）
- 影响选型的框架升级与兼容性变化

事件类型建议：
- oss_release
- benchmark_update
- ecosystem_breaking_change

新增字段建议：
- repo
- release_tag
- benchmark_suite
- compatibility_note

## 3. 来源策略（必须执行）

来源分级：
- Tier 1：官方文档、官方博客、官方公告
- Tier 2：主流媒体与研究机构
- Tier 3：社区与社媒（仅作补充线索）

采信规则：
- 推送优先 Tier 1 + Tier 2。
- Tier 3 必须二次验证才能进入高优先级推送。
- 每条事件必须保留原文 URL 与发布时间。

## 4. 数据结构扩展建议

在现有事件结构基础上统一扩展：
- domain（research/tech/finance/report/policy/safety/oss）
- source_tier（1/2/3）
- novelty_score（新颖度）
- impact_score（影响度）
- confidence（可信度）
- evidence[]（证据片段或关键事实）

## 5. 开发里程碑（12 周）

### Phase 1（第 1-2 周）：架构与质量底座
- 统一事件 schema v1.1（含财经/报告字段）
- 落地 source_tier 与 recency_policy
- 完成去重 v2（规则+语义）
- 增加质量监控接口（重复率、失败率、延迟）

验收：
- 重复推送率 < 5%
- 坏链接率 < 1%

### Phase 2（第 3-5 周）：AI 财经模块上线
- 接入核心财经来源连接器
- 提取结构化字段（金额、口径、指引变化）
- 支持财经专题推送

验收：
- 每周可生成“AI 财经动态摘要”
- 关键字段缺失率 < 10%

### Phase 3（第 6-8 周）：产业报告模块上线
- 接入报告类来源连接器
- 提取结论、方法、时间窗口
- 生成“报告观点对齐/冲突”摘要

验收：
- 每周可生成“产业报告周报”
- 报告摘要可追溯到原文

### Phase 4（第 9-12 周）：政策 + 安全 + 开源生态
- 接入政策/安全/开源信号
- 增加事件严重度与风险标签
- 完成多模块仪表盘和订阅模板

验收：
- 至少 4 个域可独立订阅
- 高影响事件支持即时预警

## 6. KPI 与停机线

核心 KPI：
- 覆盖率：目标来源命中率
- 时效性：发布到入库中位延迟
- 质量：重复率、解析失败率、坏链接率
- 有效性：推送点击率、订阅留存率

停机线（触发回滚/降频）：
- 重复率连续 3 天 > 12%
- 解析失败率连续 3 天 > 20%
- 高优先级来源失败超过阈值

## 7. 近期执行清单（本周）

- 定稿扩展字段并写入代码 schema。
- 建立财经与报告连接器模板。
- 增加“领域订阅”配置项（finance/report/policy/safety/oss）。
- 新增每周两类摘要模板：财经周报、产业报告周报。

## 8. 开源协作机制

- 新连接器 PR 必须附：来源说明、字段映射、去重策略、样例输出。
- 统一使用 `docs/CONNECTOR-SDK.md` 作为接口契约。
- 每月发布一次“覆盖/质量”透明报告，提升社区信任。

## 9. 已落地来源与质控（2026-04-25）

### 9.1 已上线来源（按领域）

- 大厂官方进展（global/cn）：
  - OpenAI News、Google AI Blog、Google DeepMind Blog、Microsoft Research Feed、NVIDIA Technical Blog、Hugging Face Blog、Anthropic News
  - Qwen Blog、Qwen3.6 Updates（GitHub Atom）、DeepSeek News、Z.AI Release Notes、01.AI Newsroom、MiniMax Release Notes、ERNIE Blog
- AI 财经 + 资本市场（global major markets）：
  - Yahoo Finance AI Stocks（含美股/港股/韩股/日股 AI 相关篮子）
  - AMD Investor Press、Broadcom Investor News、NVIDIA Press Releases
- AI 产业报告（global）：
  - CB Insights Research、MIT Technology Review AI、IEEE Spectrum AI、Sequoia Capital Insights
- AI 政策 + 安全（合并域）：
  - NIST News（policy_safety）
- AI 开源生态（GitHub）：
  - vLLM / Transformers / MLC-LLM / Ollama releases（README 语义门控）

### 9.2 时效策略（严格近 3 个月）

- 全局默认 `max_age_days=90`。
- 高频资本市场源可更短（如 Yahoo Finance 30 天）。
- 超过窗口的内容在抓取与展示链路都被过滤，不进入结果集。

### 9.3 去重与持久化

- 持久化去重索引：`output/ai_progress_seen.json`
- URL 归一化签名去重 + 标题近重复（相似度/jaccard/包含关系）双层去重。
- 保留策略：同一条候选按来源优先级、发布时间、信息完整度择优保留。
- 历史去重窗口：`SEEN_HISTORY_RETENTION_DAYS=365`，避免重复回流。

### 9.4 质量管控（反垃圾）

- 低质量拦截：
  - Cookie/登录/条款页关键词拦截
  - 短标题默认拦截，但 GitHub 版本号标题（如 `v0.21.3`）放行
- 关键词命中修正：
  - 对短英文词（如 `ai`）采用词边界匹配，避免 `Britain` 误命中 `ai`
- 来源级规则：
  - 支持 `required_keywords` / `blocked_keywords`
  - 资本市场源支持 `ticker_allowlist` + `entity_keywords` + 严格标题实体匹配
- GitHub 质量门：
  - 仓库 README 语义评分（高/中权重关键词）
  - 低于阈值仓库直接剔除，避免“名字像 AI 但内容不相关”的仓库进入流

### 9.5 当前已知权衡

- 政策/监管高质量 RSS 天然较少，当前先保证“低噪声”优先，后续再扩充多法域官方源。
- 资本市场新闻以“AI 相关股票 + AI 语义命中”为准，不追求覆盖全部财经新闻。

