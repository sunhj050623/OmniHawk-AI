# coding=utf-8
"""
HTML template builders for the PaperScope web panel.

This module keeps large inline HTML/JS/CSS strings out of panel_server.py
to improve readability and maintainability.
"""

def build_panel_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PaperScope Research Radar</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --primary: #0f766e;
      --primary-2: #115e59;
      --line: #e5e7eb;
      --badge: #ecfeff;
      --danger: #b91c1c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Circular Std", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: radial-gradient(circle at 20% -20%, #dbeafe 0, transparent 40%), var(--bg);
      color: var(--text);
    }
    .wrap { max-width: 1880px; margin: 0 auto; padding: 12px 8px 14px; }
    .top {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      position: sticky;
      top: 10px;
      z-index: 5;
    }
    .top-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 12px;
    }
    .top-left {
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-width: 0;
      overflow: visible;
    }
    .page-tabs {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .page-tab {
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 10px 18px;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.96px;
      text-transform: uppercase;
      color: var(--muted);
      text-decoration: none;
      background: var(--input-bg);
      transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease;
    }
    .page-tab:hover { border-color: var(--line-strong); color: var(--text); text-decoration: none; }
    .page-tab.active {
      border-color: var(--primary);
      color: #111;
      background: var(--primary);
    }
    .top-left {
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-width: 0;
    }
    .page-tabs {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .page-tab {
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 600;
      color: var(--muted);
      text-decoration: none;
      background: var(--input-bg);
      transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease;
    }
    .page-tab:hover { border-color: var(--line-strong); color: var(--text); text-decoration: none; }
    .page-tab.active {
      border-color: var(--primary);
      color: var(--primary);
      background: rgba(20, 184, 166, 0.08);
    }
    .top-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .row {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      align-items: center;
      margin-top: 2px;
    }
    .row label, .toolbar label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: var(--muted);
    }
    .title {
      font-size: 34px;
      font-weight: 760;
      margin: 0;
      letter-spacing: 1px;
      text-transform: uppercase;
      line-height: 1.08;
    }
    .muted { color: var(--muted); font-size: 14px; }
    button, select, .toolbar input[type="text"], .toolbar input[type="number"], .toolbar input[type="date"] {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 9px 12px;
      background: #fff;
      font-size: 14px;
    }
    button, select { cursor: pointer; }
    .toolbar input[type="text"], .toolbar input[type="number"], .toolbar input[type="date"] { min-width: 130px; }
    button:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }
    button.primary {
      border-color: var(--primary);
      background: var(--primary);
      color: #111;
    }
    button.primary:hover { background: var(--primary-2); }
    .status {
      margin-top: 10px;
      font-size: 14px;
      color: var(--muted);
      white-space: pre-wrap;
    }
    .toolbar {
      margin-top: 14px;
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .toolbar .subtle {
      color: var(--muted);
      font-size: 12px;
    }
    .subscription-list {
      margin-top: 8px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }
    .subscription-item {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--card);
      padding: 8px 10px;
      font-size: 12px;
      color: var(--text);
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: var(--card-shadow);
    }
    .subscription-item .line {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .toolbar .subtle {
      color: var(--muted);
      font-size: 12px;
    }
    .subscription-list {
      margin-top: 8px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }
    .subscription-item {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
      padding: 8px 10px;
      font-size: 12px;
      color: #374151;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .subscription-item .line {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
      align-items: start;
      grid-auto-rows: 1fr;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    .card h3 { margin: 0 0 6px; font-size: 21px; line-height: 1.35; }
    .meta {
      display: grid;
      grid-template-columns: 1fr;
      gap: 3px;
      font-size: 15px;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .badges { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0; }
    .badge {
      background: var(--badge);
      border: 1px solid #99f6e4;
      color: #115e59;
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 12px;
    }
    .sec { margin-top: 6px; font-size: 15px; line-height: 1.55; }
    .sec b { display: inline-block; min-width: 120px; color: #374151; }
    .sec.abstract { white-space: normal; line-height: 1.6; }
    .actions {
      margin-top: 8px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .btn-sm {
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 12px;
    }
    .btn-star {
      background: #fff7ed;
      border-color: #fed7aa;
      color: #9a3412;
    }
    .btn-ignore {
      background: #f3f4f6;
      border-color: #d1d5db;
      color: #374151;
    }
    .btn-deep {
      background: #eef2ff;
      border-color: #c7d2fe;
      color: #3730a3;
    }
    .deep-block {
      margin-top: 10px;
      border: 1px solid #dbeafe;
      background: #f8fbff;
      border-radius: 10px;
      padding: 10px;
    }
    .deep-block .rowx {
      margin-top: 6px;
      font-size: 13px;
      line-height: 1.6;
    }
    .score {
      display: inline-block;
      background: #ecfccb;
      color: #3f6212;
      border: 1px solid #bef264;
      border-radius: 8px;
      font-size: 12px;
      padding: 2px 8px;
      margin-left: 8px;
    }
    .clamp-2, .clamp-3, .clamp-5, .clamp-8 {
      display: -webkit-box;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .clamp-2 { -webkit-line-clamp: 2; }
    .clamp-3 { -webkit-line-clamp: 3; }
    .clamp-5 { -webkit-line-clamp: 5; }
    .clamp-8 { -webkit-line-clamp: 8; }
    .settings {
      margin-top: 12px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fafafa;
      display: none;
    }
    .settings.open { display: block; }
    .settings .grid2 {
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 8px 10px;
      align-items: center;
    }
    .settings input[type="text"], .settings input[type="password"], .settings input[type="number"], .settings select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 13px;
      background: #fff;
    }
    .settings-actions {
      margin-top: 10px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    a { color: #0369a1; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .empty {
      border: 1px dashed var(--line);
      border-radius: 12px;
      padding: 24px;
      text-align: center;
      color: var(--muted);
      background: #fff;
    }
    .error { color: var(--danger); }
    @media (max-width: 1280px) {
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .top-head { flex-direction: column; align-items: flex-start; }
      .top-right { width: 100%; justify-content: flex-end; }
      .grid { grid-template-columns: 1fr; }
      .settings .grid2 { grid-template-columns: 1fr; }
      .subscription-list { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <p class="title">OmniHawk AI 论文面板</p>
      <div class="row">
        <button id="runNow" class="primary">立即抓取</button>
        <label>抓取间隔
          <select id="interval">
            <option value="5">5 分钟</option>
            <option value="10">10 分钟</option>
            <option value="15">15 分钟</option>
            <option value="20">20 分钟</option>
            <option value="30">30 分钟</option>
            <option value="60">60 分钟</option>
            <option value="120">120 分钟</option>
            <option value="180">180 分钟</option>
            <option value="240">240 分钟</option>
            <option value="360">360 分钟</option>
            <option value="720">720 分钟</option>
            <option value="1440">1440 分钟</option>
          </select>
        </label>
        <button id="saveInterval">保存间隔</button>
        <button id="toggleSettings">参数设置</button>
        <button id="refreshNow">刷新</button>
      </div>
      <div class="toolbar">
        <label>视图
          <select id="viewMode">
            <option value="all">已分析论文</option>
            <option value="favorites">仅收藏</option>
            <option value="ignored">忽略列表</option>
          </select>
        </label>
        <label>排序
          <select id="sortMode">
            <option value="score">按推荐分</option>
            <option value="time">按时间</option>
            <option value="title">按标题</option>
          </select>
        </label>
        <label>顺序
          <select id="sortOrder">
            <option value="desc">降序</option>
            <option value="asc">升序</option>
          </select>
        </label>
        <label>历史
          <select id="historyMode">
            <option value="latest">最近一次分析</option>
            <option value="all">全部历史</option>
          </select>
        </label>
        <span id="favSummary" class="muted"></span>
      </div>
      <div class="toolbar">
        <input id="searchQ" type="text" placeholder="全字段检索（标题/摘要/作者/方法）" />
        <select id="filterCategory">
          <option value="">分类不限</option>
          <option value="cs.AI">cs.AI</option>
          <option value="cs.CL">cs.CL</option>
          <option value="cs.CV">cs.CV</option>
          <option value="cs.LG">cs.LG</option>
          <option value="cs.RO">cs.RO</option>
          <option value="cs.IR">cs.IR</option>
          <option value="cs.NE">cs.NE</option>
          <option value="cs.SE">cs.SE</option>
          <option value="cs.CR">cs.CR</option>
          <option value="cs.DB">cs.DB</option>
          <option value="cs.DC">cs.DC</option>
          <option value="cs.HC">cs.HC</option>
          <option value="cs.PL">cs.PL</option>
          <option value="cs.CY">cs.CY</option>
        </select>
        <input id="dateFrom" type="date" />
        <input id="scoreMin" type="number" min="0" max="100" placeholder="分数>= " />
        <button id="applyFilters">筛选</button>
        <button id="clearFilters">清空筛选</button>
        <button id="copyFilterLink">复制筛选链接</button>
      </div>
      <div class="toolbar">
        <label>导出
          <select id="exportFormat">
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="md">Markdown</option>
          </select>
        </label>
        <button id="exportNow">导出当前结果</button>
        <input id="subscriptionName" type="text" placeholder="订阅名称（可选）" />
        <label>通知渠道
          <select id="subscriptionChannel">
            <option value="feishu">飞书</option>
            <option value="wework">企业微信</option>
            <option value="email">邮箱</option>
          </select>
        </label>
        <button id="saveSubscription">保存为订阅</button>
        <button id="runSubscriptions">执行全部订阅推送</button>
        <span class="subtle">订阅会保存当前筛选+排序条件，仅推送新增命中论文</span>
      </div>
      <div id="subscriptionList" class="subscription-list"></div>
      <div id="settingsPanel" class="settings">
        <div class="grid2">
          <label for="paperPrimaryCategory">论文主分类</label>
          <select id="paperPrimaryCategory">
            <option value="">全部分类</option>
            <option value="cs.AI">cs.AI</option>
            <option value="cs.CL">cs.CL</option>
            <option value="cs.CV">cs.CV</option>
            <option value="cs.LG">cs.LG</option>
            <option value="cs.RO">cs.RO</option>
            <option value="cs.IR">cs.IR</option>
            <option value="cs.NE">cs.NE</option>
            <option value="cs.SE">cs.SE</option>
            <option value="cs.CR">cs.CR</option>
            <option value="cs.DB">cs.DB</option>
            <option value="cs.DC">cs.DC</option>
            <option value="cs.HC">cs.HC</option>
            <option value="cs.PL">cs.PL</option>
            <option value="cs.CY">cs.CY</option>
          </select>

          <label for="paperSubtopics">子领域关键词</label>
          <input id="paperSubtopics" type="text" placeholder="例如：agent, llm, rag, reasoning（逗号分隔）" />

          <label for="aiModel">LLM 模型</label>
          <input id="aiModel" type="text" placeholder="例如：qwen3.5-35b-a3b" />

          <label for="aiBase">LLM Base URL</label>
          <input id="aiBase" type="text" placeholder="例如：https://novaapi.top/v1" />

          <label for="aiKey">LLM API Key</label>
          <input id="aiKey" type="password" placeholder="sk-..." />

          <label for="paperMax">每次分析篇数</label>
          <input id="paperMax" type="number" min="1" max="200" />

          <label for="feishuWebhook">飞书 Webhook</label>
          <input id="feishuWebhook" type="text" placeholder="https://open.feishu.cn/..." />

          <label for="weworkWebhook">企业微信 Webhook</label>
          <input id="weworkWebhook" type="text" placeholder="https://qyapi.weixin.qq.com/..." />

          <label for="emailFrom">邮箱发件人</label>
          <input id="emailFrom" type="text" placeholder="example@qq.com" />

          <label for="emailPassword">邮箱授权码/密码</label>
          <input id="emailPassword" type="password" placeholder="邮箱授权码" />

          <label for="emailTo">邮箱收件人</label>
          <input id="emailTo" type="text" placeholder="a@xx.com;b@yy.com" />

          <label for="emailSmtpServer">SMTP 服务器</label>
          <input id="emailSmtpServer" type="text" placeholder="smtp.qq.com" />

          <label for="emailSmtpPort">SMTP 端口</label>
          <input id="emailSmtpPort" type="text" placeholder="465" />
        </div>
        <div class="settings-actions">
          <button id="saveSettings">保存设置</button>
          <button id="reloadSettings">重载设置</button>
          <label>通知测试
            <select id="testChannel">
              <option value="feishu">飞书</option>
              <option value="wework">企业微信</option>
              <option value="email">邮箱</option>
            </select>
          </label>
          <button id="testNotify">测试发送</button>
        </div>
      </div>
      <div id="actionMsg" class="status"></div>
      <div id="status" class="status">加载中...</div>
      <div id="error" class="status error"></div>
    </div>

    <div id="papers" class="grid"></div>
  </div>

  <script>
    const state = {
      status: null,
      papers: [],
      paperStats: null,
      settings: null,
      viewMode: "all",
      sortMode: "score",
      historyMode: "all",
      sortOrder: "desc",
      subscriptions: [],
      appliedQuery: null,
      deepRunningKeys: Object.create(null)
    };

    function esc(v) {
      return (v ?? "").toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function setError(msg) {
      document.getElementById("error").textContent = msg || "";
    }

    function setMessage(msg) {
      document.getElementById("actionMsg").textContent = msg || "";
    }

    function setRunButtonState(running) {
      const btn = document.getElementById("runNow");
      if (!btn) return;
      btn.disabled = !!running;
      btn.textContent = running ? "抓取中..." : "立即抓取";
    }

    function setDeepButtonState(paperKey, running) {
      const key = (paperKey || "").toString();
      if (!key) return;
      const buttons = document.querySelectorAll("button.act-deep");
      buttons.forEach((btn) => {
        if ((btn.getAttribute("data-key") || "") !== key) return;
        btn.disabled = !!running;
        btn.textContent = running ? "深入分析中..." : "深入分析";
      });
    }

    function normalizeSubtopicsText(value) {
      const parts = (value || "").split(",").map(v => v.trim()).filter(Boolean);
      const seen = new Set();
      const out = [];
      for (const item of parts) {
        const k = item.toLowerCase();
        if (seen.has(k)) continue;
        seen.add(k);
        out.push(item);
      }
      return out.join(", ");
    }

    function buildResearchTopicFromForm() {
      const category = (document.getElementById("paperPrimaryCategory")?.value || "").trim();
      const subtopics = normalizeSubtopicsText(document.getElementById("paperSubtopics")?.value || "");
      if (category && subtopics) return `${category} / ${subtopics}`;
      if (category) return category;
      return subtopics;
    }

    function collectFilterInputs() {
      return {
        q: (document.getElementById("searchQ")?.value || "").trim(),
        category: (document.getElementById("filterCategory")?.value || "").trim(),
        date_from: (document.getElementById("dateFrom")?.value || "").trim(),
        score_min: (document.getElementById("scoreMin")?.value || "").trim()
      };
    }

    function applyFilterInputs(data) {
      const f = data || {};
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value || "";
      };
      set("searchQ", f.q || "");
      set("filterCategory", f.category || "");
      set("dateFrom", f.date_from || "");
      set("scoreMin", f.score_min ?? "");
    }

    function captureQueryFromInputs(overrides = {}) {
      return {
        limit: Number(overrides.limit || 100),
        mode: overrides.mode || document.getElementById("viewMode")?.value || "all",
        sort_by: overrides.sort_by || document.getElementById("sortMode")?.value || "score",
        sort_order: overrides.sort_order || document.getElementById("sortOrder")?.value || "desc",
        history: overrides.history || document.getElementById("historyMode")?.value || "all",
        filters: { ...collectFilterInputs(), ...(overrides.filters || {}) }
      };
    }

    function buildPaperQueryParams(queryObj = null) {
      const query = queryObj || state.appliedQuery || captureQueryFromInputs();
      const params = new URLSearchParams();
      params.set("limit", String(query.limit || 100));
      params.set("mode", query.mode || "all");
      params.set("sort_by", query.sort_by || "score");
      params.set("sort_order", query.sort_order || "desc");
      params.set("history", query.history || "all");
      const filters = query.filters || {};
      const keys = ["q", "category", "date_from", "score_min"];
      for (const key of keys) {
        const value = (filters[key] ?? "").toString().trim();
        if (!value) continue;
        params.set(key, value);
      }
      return params;
    }

    async function applyFiltersAndRefresh(showMessage = false) {
      state.appliedQuery = captureQueryFromInputs();
      await refreshPapers();
      if (showMessage) setMessage("筛选条件已应用");
    }

    function syncFiltersFromUrl() {
      const params = new URLSearchParams(window.location.search || "");
      applyFilterInputs({
        q: params.get("q") || "",
        category: params.get("category") || "",
        date_from: params.get("date_from") || "",
        score_min: params.get("score_min") || ""
      });
      const mode = params.get("mode");
      const sortBy = params.get("sort_by");
      const sortOrder = params.get("sort_order");
      const history = params.get("history");
      if (mode && document.getElementById("viewMode")) document.getElementById("viewMode").value = mode;
      if (sortBy && document.getElementById("sortMode")) document.getElementById("sortMode").value = sortBy;
      if (sortOrder && document.getElementById("sortOrder")) document.getElementById("sortOrder").value = sortOrder;
      if (history && document.getElementById("historyMode")) document.getElementById("historyMode").value = history;
      state.appliedQuery = captureQueryFromInputs({
        mode: mode || undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder || undefined,
        history: history || undefined
      });
    }

    async function fetchJSON(url, options) {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      return data;
    }

    function renderStatus() {
      const s = state.status || {};
      const lines = [];
      lines.push(`运行中: ${s.running ? "是" : "否"}`);
      lines.push(`当前调度: ${s.cron_expr || "-"}`);
      lines.push(`间隔(分钟): ${s.interval_minutes ?? "-"}`);
      lines.push(`最近启动: ${s.started_at || "-"}`);
      lines.push(`最近完成: ${s.finished_at || "-"}`);
      lines.push(`最近退出码: ${s.last_exit_code ?? "-"}`);
      lines.push(`主分类: ${s.paper_primary_category || "-"}`);
      lines.push(`子领域: ${s.paper_subtopics || "-"}`);
      lines.push(`研究方向: ${s.research_topic || "-"}`);
      lines.push(`论文分析上限/次: ${s.paper_max_papers_per_run ?? "-"}`);
      if (s.ai_model) lines.push(`LLM模型: ${s.ai_model}`);
      if (s.last_error) lines.push(`错误: ${s.last_error}`);
      if (s.db_path) lines.push(`DB: ${s.db_path}`);
      if (s.server_time) lines.push(`服务端时间: ${s.server_time}`);
      document.getElementById("status").textContent = lines.join("\\n");
      if (s.interval_minutes) {
        document.getElementById("interval").value = String(s.interval_minutes);
      }
      setRunButtonState(!!s.running);
    }

    function buildEmptyHint() {
      const st = state.paperStats || {};
      const tips = [];
        if ((st.total_candidates || 0) <= 0) {
          tips.push("暂无候选论文。先点击“立即抓取”。");
        } else if ((st.returned || 0) === 0) {
        if (Number(st.filtered_unanalyzed || 0) > 0) tips.push(`有 ${st.filtered_unanalyzed} 篇尚未完成 LLM 分析，当前不展示`);
        if (Number(st.filtered_category || 0) > 0) tips.push(`有 ${st.filtered_category} 篇不在当前主分类筛选内`);
        if (Number(st.filtered_subtopics || 0) > 0) tips.push(`有 ${st.filtered_subtopics} 篇未命中子领域关键词`);
        if (Number(st.filtered_search || 0) > 0) tips.push(`有 ${st.filtered_search} 篇未命中全字段检索`);
        if (Number(st.filtered_filter_category || 0) > 0) tips.push(`有 ${st.filtered_filter_category} 篇未命中分类筛选`);
        if (Number(st.filtered_date || 0) > 0) tips.push(`有 ${st.filtered_date} 篇不在时间范围内`);
        if (Number(st.filtered_score || 0) > 0) tips.push(`有 ${st.filtered_score} 篇不在分数范围内`);
        if (Number(st.filtered_ignored || 0) > 0) tips.push(`有 ${st.filtered_ignored} 篇在忽略列表中`);
        if (st.mode === "favorites" && Number(st.filtered_favorites_mode || 0) > 0) tips.push("当前是“仅收藏”模式，未命中收藏记录");
        if (st.mode === "ignored" && Number(st.filtered_ignored_mode || 0) > 0) tips.push("当前是“忽略列表”模式，暂无忽略记录");
      }
      if (!tips.length) tips.push("暂无结果，请调整筛选条件或先执行一次抓取与分析。");
      return tips;
    }

    function renderFavoriteSummary() {
      const el = document.getElementById("favSummary");
      if (!el) return;
      const count = Number(state.paperStats?.favorite_records || 0);
      el.textContent = `收藏记录: ${count} 条`;
    }

    function renderSubscriptions() {
      const root = document.getElementById("subscriptionList");
      if (!root) return;
      const items = state.subscriptions || [];
      if (!items.length) {
        root.innerHTML = `<div class="muted">暂无订阅，可在当前筛选条件下点击“保存为订阅”。</div>`;
        return;
      }
      root.innerHTML = items.map((item) => {
        const id = esc(item.id || "");
        const filters = item.filters || {};
        const preview = [
          filters.q ? `关键词:${filters.q}` : "",
          filters.category ? `分类:${filters.category}` : "",
          filters.date_from ? `起始:${filters.date_from}` : "",
          filters.score_min ? `分数>=${filters.score_min}` : ""
        ].filter(Boolean).join(" | ") || "无额外筛选";
        return `
          <div class="subscription-item">
            <div class="line">
              <b>${esc(item.name || "订阅")}</b>
              <span class="badge">${esc(item.channel || "-")}</span>
              <span class="badge">${item.enabled ? "启用" : "停用"}</span>
            </div>
            <div class="line">${esc(preview)}</div>
            <div class="line">最近推送: ${esc(item.last_notified_at || "-")} / 上次命中: ${Number(item.last_match_count || 0)}</div>
            <div class="line">
              <button class="btn-sm sub-apply" data-id="${id}">套用筛选</button>
              <button class="btn-sm sub-run" data-id="${id}">推送一次</button>
              <button class="btn-sm sub-toggle" data-id="${id}" data-enabled="${item.enabled ? "1" : "0"}">${item.enabled ? "停用" : "启用"}</button>
              <button class="btn-sm sub-delete" data-id="${id}">删除</button>
            </div>
          </div>
        `;
      }).join("");
    }

    function renderCards() {
      const root = document.getElementById("papers");
      const papers = state.papers || [];
      if (!papers.length) {
        const tips = buildEmptyHint().map(x => `<div>• ${esc(x)}</div>`).join("");
        root.innerHTML = `
          <div class="empty">
            <div>当前没有可展示论文。</div>
            <div style="margin-top:8px;">${tips}</div>
          </div>
        `;
        return;
      }

      root.innerHTML = papers.map((p, idx) => {
        const tags = (p.tags || []).map(t => `<span class="badge">${esc(t)}</span>`).join("");
        const aff = (p.affiliations || []).join("；");
        const kws = (p.insight?.keywords || []).join(", ");
        const action = p.action || {};
        const pdf = p.pdf_url ? `<a href="${esc(p.pdf_url)}" target="_blank">PDF</a>` : "-";
        const doi = p.doi ? `<a href="https://doi.org/${esc(p.doi)}" target="_blank">${esc(p.doi)}</a>` : "-";
        const source = p.url ? `<a href="${esc(p.url)}" target="_blank">原文</a>` : "-";
        const favText = action.favorite ? "取消收藏" : "收藏";
        const ignoreText = action.ignored ? "取消忽略" : "忽略";
        const favoriteAt = action.favorite_at ? `<div class="sec"><b>收藏时间</b>${esc(action.favorite_at)}</div>` : "";
        const runId = p.insight?.analysis_run_id || "-";
        const deep = (p.insight && p.insight.deep_analysis) ? p.insight.deep_analysis : null;
        const paperKey = esc(p.paper_key || "");
        const deepRunning = !!state.deepRunningKeys[(p.paper_key || "").toString()];
        const deepFollowups = Array.isArray(deep?.recommended_followups) ? deep.recommended_followups.filter(Boolean).map((x) => esc(x)).join("；") : "";
        const deepQuestions = Array.isArray(deep?.reading_questions) ? deep.reading_questions.filter(Boolean).map((x) => esc(x)).join("；") : "";
        const deepHtml = deep ? `
          <div class="deep-block">
            <div class="rowx"><b>深入结论</b> ${esc(deep.one_line_verdict || "-")}</div>
            <div class="rowx"><b>方法细节</b> ${esc(deep.method_deep_dive || "-")}</div>
            <div class="rowx"><b>实验与评测</b> ${esc(deep.experimental_design || "-")}</div>
            <div class="rowx"><b>优势</b> ${esc(deep.strengths || "-")}</div>
            <div class="rowx"><b>不足与风险</b> ${esc(deep.weaknesses || "-")}</div>
            <div class="rowx"><b>复现评估</b> ${esc(deep.reproducibility || "-")}</div>
            <div class="rowx"><b>后续实验建议</b> ${deepFollowups || "-"}</div>
            <div class="rowx"><b>延伸阅读问题</b> ${deepQuestions || "-"}</div>
            <div class="rowx"><b>深入分析时间</b> ${esc(deep.analyzed_at || "-")}</div>
          </div>
        ` : "";
        return `
          <div class="card">
            <h3 class="clamp-3">${esc(p.title)}<span class="score">推荐阅读分 ${Number(p.recommendation_score || 0)}</span></h3>
            <div class="meta">
              <span class="clamp-2">作者: ${esc((p.authors || []).join(", ") || "-")}</span>
              <span class="clamp-2">作者单位: ${esc(aff || "-")}</span>
              <span>发布时间: ${esc(p.published_at || "-")}</span>
              <span>主分类: ${esc(p.primary_category || "-")}</span>
              <span>arXiv ID: ${esc(p.arxiv_id || "-")}</span>
              <span>分析批次: ${esc(runId)}</span>
            </div>
            <div class="badges">${tags}</div>
            <div class="sec abstract"><b>摘要</b><span>${esc(p.abstract || "-")}</span></div>
            <div class="sec"><b>PDF</b>${pdf}</div>
            <div class="sec"><b>DOI</b>${doi}</div>
            <div class="sec"><b>链接</b>${source}</div>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:10px 0;" />
            <div class="sec"><b>一句话摘要</b><span class="clamp-3">${esc(p.insight?.one_sentence_summary || "-")}</span></div>
            <div class="sec"><b>关键词</b><span class="clamp-3">${esc(kws || "-")}</span></div>
            <div class="sec"><b>方法</b><span class="clamp-5">${esc(p.insight?.method || "-")}</span></div>
            <div class="sec"><b>结论</b><span class="clamp-5">${esc(p.insight?.conclusion || "-")}</span></div>
            <div class="sec"><b>创新点</b><span class="clamp-5">${esc(p.insight?.innovation || "-")}</span></div>
            ${deepHtml}
            ${favoriteAt}
            <div class="actions">
              <button class="btn-sm btn-deep act-deep" data-key="${paperKey}" ${deepRunning ? "disabled" : ""}>${deepRunning ? "深入分析中..." : "深入分析"}</button>
              <button class="btn-sm btn-star act-fav" data-key="${paperKey}" data-fav="${action.favorite ? "1" : "0"}">${favText}</button>
              <button class="btn-sm btn-ignore act-ignore" data-key="${paperKey}" data-ignored="${action.ignored ? "1" : "0"}">${ignoreText}</button>
            </div>
          </div>
        `;
      }).join("");
    }

    function fillSettingsForm(s) {
      const data = s || {};
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value || "";
      };
      set("paperPrimaryCategory", data.paper_primary_category || "");
      set("paperSubtopics", data.paper_subtopics || "");
      set("aiModel", data.ai_model || "");
      set("aiBase", data.ai_api_base || "");
      set("aiKey", data.ai_api_key || "");
      set("paperMax", data.paper_max_papers_per_run || 20);
      set("paperMaxPerSource", data.max_per_source || 20);
      set("paperNotifyChannel", data.notify_channel || "feishu");
      set("paperNotifyLimit", data.notify_limit || 8);
      set("paperAutoEnabled", data.auto_enabled ? "1" : "0");
      set("paperAutoInterval", data.auto_interval_minutes || 60);
      set("paperAutoPushEnabled", data.auto_push_enabled ? "1" : "0");
      const q = data.query || {};
      set("paperDefaultQ", q.q || "");
      set("paperDefaultSourceId", q.source_id || "");
      set("paperDefaultRegion", q.region || "");
      set("paperDefaultEventType", q.event_type || "");
      set("feishuWebhook", data.feishu_webhook_url || "");
      set("weworkWebhook", data.wework_webhook_url || "");
      set("weworkMsgType", data.wework_msg_type || "markdown");
      set("dingtalkWebhook", data.dingtalk_webhook_url || "");
      set("telegramBotToken", data.telegram_bot_token || "");
      set("telegramChatId", data.telegram_chat_id || "");
      set("ntfyServerUrl", data.ntfy_server_url || "https://ntfy.sh");
      set("ntfyTopic", data.ntfy_topic || "");
      set("ntfyToken", data.ntfy_token || "");
      set("barkUrl", data.bark_url || "");
      set("slackWebhook", data.slack_webhook_url || "");
      set("emailFrom", data.email_from || "");
      set("emailPassword", data.email_password || "");
      set("emailTo", data.email_to || "");
      set("emailSmtpServer", data.email_smtp_server || "");
      set("emailSmtpPort", data.email_smtp_port || "");
    }

    async function loadSettings() {
      const settings = await fetchJSON("/api/settings");
      state.settings = settings;
      fillSettingsForm(settings);
    }

    async function saveSettings() {
      const normalizedSubtopics = normalizeSubtopicsText(document.getElementById("paperSubtopics").value);
      document.getElementById("paperSubtopics").value = normalizedSubtopics;
      const payload = {
        paper_primary_category: document.getElementById("paperPrimaryCategory").value.trim(),
        paper_subtopics: normalizedSubtopics,
        research_topic: buildResearchTopicFromForm(),
        ai_model: document.getElementById("aiModel").value.trim(),
        ai_api_base: document.getElementById("aiBase").value.trim(),
        ai_api_key: document.getElementById("aiKey").value.trim(),
        paper_max_papers_per_run: Number(document.getElementById("paperMax").value || 20),
        feishu_webhook_url: document.getElementById("feishuWebhook").value.trim(),
        wework_webhook_url: document.getElementById("weworkWebhook").value.trim(),
        email_from: document.getElementById("emailFrom").value.trim(),
        email_password: document.getElementById("emailPassword").value.trim(),
        email_to: document.getElementById("emailTo").value.trim(),
        email_smtp_server: document.getElementById("emailSmtpServer").value.trim(),
        email_smtp_port: document.getElementById("emailSmtpPort").value.trim()
      };
      const data = await fetchJSON("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (data.settings) {
        state.settings = data.settings;
        fillSettingsForm(data.settings);
      }
      if (state.status) {
        state.status.interval_minutes = data.interval_minutes ?? state.status.interval_minutes;
        state.status.cron_expr = data.cron_expr || state.status.cron_expr;
      }
      setMessage(`设置已保存，当前调度 ${data.cron_expr || "-"}`);
      await Promise.all([refreshStatus(), refreshPapers()]);
    }

    async function refreshStatus() {
      state.status = await fetchJSON("/api/status");
      renderStatus();
    }

    async function refreshPapers() {
      if (!state.appliedQuery) {
        state.appliedQuery = captureQueryFromInputs();
      }
      state.viewMode = state.appliedQuery.mode || "all";
      state.sortMode = state.appliedQuery.sort_by || "score";
      state.sortOrder = state.appliedQuery.sort_order || "desc";
      state.historyMode = state.appliedQuery.history || "all";
      const params = buildPaperQueryParams(state.appliedQuery);
      try {
        window.history.replaceState(null, "", `?${params.toString()}`);
      } catch (_) {}
      const data = await fetchJSON(`/api/papers?${params.toString()}`);
      state.papers = data.papers || [];
      state.paperStats = data.stats || null;
      if (state.status) {
        state.status.db_path = data.db_path || state.status.db_path;
      }
      renderFavoriteSummary();
      renderCards();
    }

    async function runNow() {
      setError("");
      setMessage("");
      try {
        await fetchJSON("/api/run-now", {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        await refreshStatus();
        setMessage("已触发立即抓取");
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function saveInterval() {
      setError("");
      setMessage("");
      const val = Number(document.getElementById("interval").value);
      try {
        const data = await fetchJSON("/api/schedule", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ interval_minutes: val })
        });
        if (state.status) {
          state.status.interval_minutes = data.interval_minutes ?? state.status.interval_minutes;
          state.status.cron_expr = data.cron_expr || state.status.cron_expr;
        }
        await refreshStatus();
        setMessage(`抓取间隔已更新为 ${data.interval_minutes} 分钟`);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function refreshNow() {
      setError("");
      setMessage("");
      try {
        await Promise.all([refreshStatus(), refreshPapers(), loadSubscriptions()]);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    function openPanel(panelType) {
      const settings = document.getElementById("settingsDrawer");
      const subs = document.getElementById("subscriptionDrawer");
      if (!settings || !subs) return;
      if (panelType === "settings") {
        const willOpen = !settings.classList.contains("open");
        settings.classList.toggle("open", willOpen);
        subs.classList.remove("open");
      } else if (panelType === "subscriptions") {
        const willOpen = !subs.classList.contains("open");
        subs.classList.toggle("open", willOpen);
        settings.classList.remove("open");
      } else {
        settings.classList.remove("open");
        subs.classList.remove("open");
      }
    }

    function closePanels() {
      openPanel("");
    }

    async function savePaperAction(paperKey, payload) {
      await fetchJSON("/api/paper-actions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_key: paperKey, ...payload })
      });
      await refreshPapers();
    }

    async function deepAnalyzePaper(paperKey) {
      const key = (paperKey || "").trim();
      if (!key) return;
      if (state.deepRunningKeys[key]) return;
      state.deepRunningKeys[key] = true;
      setDeepButtonState(key, true);
      setError("");
      setMessage("正在执行深入分析，请稍候...");
      try {
        const data = await fetchJSON("/api/papers/deep-analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            paper_key: key,
            force: true
          })
        });
        await refreshPapers();
        setMessage(data.message || "深入分析完成");
      } finally {
        delete state.deepRunningKeys[key];
        setDeepButtonState(key, false);
      }
    }

    async function testNotify() {
      setError("");
      setMessage("");
      const channel = document.getElementById("testChannel")?.value || "feishu";
      try {
        const data = await fetchJSON("/api/notify-test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channel })
        });
        setMessage(`${channel} 测试成功：${data.message || ""}`);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function loadSubscriptions() {
      const data = await fetchJSON("/api/subscriptions");
      state.subscriptions = data.items || [];
      renderSubscriptions();
    }

    async function saveSubscription() {
      if (state.savingSubscription) return;
      state.savingSubscription = true;
      setSubscriptionSaveButtonState(true);
      const name = (document.getElementById("subscriptionName")?.value || "").trim();
      const channel = document.getElementById("subscriptionChannel")?.value || "feishu";
      const payload = {
        name,
        channel,
        enabled: true,
        mode: document.getElementById("viewMode")?.value || "all",
        sort_by: document.getElementById("sortMode")?.value || "score",
        sort_order: document.getElementById("sortOrder")?.value || "desc",
        history: document.getElementById("historyMode")?.value || "all",
        filters: collectFilterInputs()
      };
      const data = await fetchJSON("/api/subscriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      state.subscriptions = data.items || [];
      renderSubscriptions();
      setMessage("已保存当前筛选为订阅");
    }

    async function runSubscriptions(id = "") {
      const data = await fetchJSON("/api/subscriptions/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(id ? { id } : {})
      });
      await loadSubscriptions();
      const parts = (data.results || []).map((r) => `${r.name}: ${r.message}`).join(" | ");
      setMessage(parts || `订阅执行完成 (${data.success_count || 0}/${data.total || 0})`);
    }

    async function deleteSubscription(id) {
      await fetchJSON("/api/subscriptions/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      await loadSubscriptions();
      setMessage("订阅已删除");
    }

    async function toggleSubscription(id, enabledNow) {
      const item = (state.subscriptions || []).find((x) => (x.id || "") === id);
      if (!item) return;
      const payload = {
        id,
        name: item.name || "",
        channel: item.channel || "feishu",
        enabled: !enabledNow,
        mode: item.mode || "all",
        sort_by: item.sort_by || "score",
        sort_order: item.sort_order || "desc",
        history: item.history || "all",
        filters: item.filters || {}
      };
      const data = await fetchJSON("/api/subscriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      state.subscriptions = data.items || [];
      renderSubscriptions();
      setMessage(!enabledNow ? "订阅已启用" : "订阅已停用");
    }

    function applySubscription(id) {
      const item = (state.subscriptions || []).find((x) => (x.id || "") === id);
      if (!item) return;
      const filters = item.filters || {};
      applyFilterInputs(filters);
      if (item.mode && document.getElementById("viewMode")) document.getElementById("viewMode").value = item.mode;
      if (item.sort_by && document.getElementById("sortMode")) document.getElementById("sortMode").value = item.sort_by;
      if (item.sort_order && document.getElementById("sortOrder")) document.getElementById("sortOrder").value = item.sort_order;
      if (item.history && document.getElementById("historyMode")) document.getElementById("historyMode").value = item.history;
      state.appliedQuery = captureQueryFromInputs();
      refreshPapers().catch((e) => setError(e.message || String(e)));
      setMessage(`已套用订阅：${item.name || "-"}`);
    }

    function clearFilters() {
      applyFilterInputs({
        q: "",
        category: "",
        date_from: "",
        score_min: ""
      });
    }

    async function copyFilterLink() {
      const params = buildPaperQueryParams(state.appliedQuery || captureQueryFromInputs());
      const link = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
      await navigator.clipboard.writeText(link);
      setMessage("筛选链接已复制");
    }

    function exportCurrent() {
      const format = document.getElementById("exportFormat")?.value || "json";
      const params = buildPaperQueryParams(state.appliedQuery || captureQueryFromInputs());
      params.set("format", format);
      window.open(`/api/export?${params.toString()}`, "_blank");
    }

    document.getElementById("runNow").addEventListener("click", runNow);
    document.getElementById("saveInterval").addEventListener("click", saveInterval);
    document.getElementById("refreshNow").addEventListener("click", refreshNow);
    document.getElementById("toggleSettings").addEventListener("click", toggleSettings);
    document.getElementById("testNotify").addEventListener("click", testNotify);
    document.getElementById("applyFilters").addEventListener("click", async () => {
      await applyFiltersAndRefresh(true);
    });
    document.getElementById("clearFilters").addEventListener("click", async () => {
      clearFilters();
      await applyFiltersAndRefresh(true);
      setMessage("筛选已清空");
    });
    document.getElementById("copyFilterLink").addEventListener("click", async () => {
      try { await copyFilterLink(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("exportNow").addEventListener("click", exportCurrent);
    document.getElementById("saveSubscription").addEventListener("click", async () => {
      setError("");
      try { await saveSubscription(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("runSubscriptions").addEventListener("click", async () => {
      setError("");
      try { await runSubscriptions(""); } catch (e) { setError(e.message || String(e)); }
    });
    ["searchQ", "scoreMin", "dateFrom"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          applyFiltersAndRefresh(true).catch((e) => setError(e.message || String(e)));
        }
      });
    });
    document.getElementById("saveSettings").addEventListener("click", async () => {
      setError("");
      try { await saveSettings(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("reloadSettings").addEventListener("click", async () => {
      setError("");
      try {
        await loadSettings();
        setMessage("设置已重载");
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("papers").addEventListener("click", async (event) => {
      const target = event.target;
      if (!target || !(target instanceof HTMLElement)) return;
      const btn = target.closest("button");
      if (!btn) return;
      const paperKey = btn.getAttribute("data-key");
      if (!paperKey) return;

      try {
        if (btn.classList.contains("act-deep")) {
          await deepAnalyzePaper(paperKey);
        } else if (btn.classList.contains("act-fav")) {
          const current = btn.getAttribute("data-fav") === "1";
          await savePaperAction(paperKey, { favorite: !current });
          setMessage(!current ? "已加入收藏" : "已取消收藏");
        } else if (btn.classList.contains("act-ignore")) {
          const current = btn.getAttribute("data-ignored") === "1";
          await savePaperAction(paperKey, { ignored: !current });
          setMessage(!current ? "已加入忽略列表" : "已从忽略列表移除");
        }
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("subscriptionList").addEventListener("click", async (event) => {
      const target = event.target;
      if (!target || !(target instanceof HTMLElement)) return;
      const btn = target.closest("button");
      if (!btn) return;
      const subId = btn.getAttribute("data-id");
      if (!subId) return;
      try {
        if (btn.classList.contains("sub-apply")) {
          applySubscription(subId);
        } else if (btn.classList.contains("sub-run")) {
          await runSubscriptions(subId);
        } else if (btn.classList.contains("sub-delete")) {
          await deleteSubscription(subId);
        } else if (btn.classList.contains("sub-toggle")) {
          const enabledNow = btn.getAttribute("data-enabled") === "1";
          await toggleSubscription(subId, enabledNow);
        }
      } catch (e) {
        setError(e.message || String(e));
      }
    });

    async function boot() {
      syncFiltersFromUrl();
      await Promise.all([loadSettings(), refreshNow(), loadSubscriptions()]);
    }

    boot();
  </script>
</body>
</html>
"""


def build_settings_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OmniHawk AI 参数设置</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --card: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --primary: #0f766e;
      --line: #e5e7eb;
      --danger: #b91c1c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .wrap {
      max-width: 860px;
      margin: 24px auto;
      padding: 0 16px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 18px;
    }
    h1 {
      margin: 0 0 14px;
      font-size: 24px;
    }
    .desc {
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 13px;
    }
    .row {
      display: grid;
      grid-template-columns: 160px 1fr;
      gap: 10px;
      align-items: center;
      margin-top: 10px;
    }
    label { font-size: 14px; }
    input[type="text"], input[type="password"], input[type="number"] {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
      background: #fff;
    }
    .actions {
      margin-top: 16px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    button {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 14px;
      background: #fff;
      cursor: pointer;
      font-size: 14px;
    }
    button.primary {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }
    .status {
      margin-top: 12px;
      color: var(--muted);
      white-space: pre-wrap;
      font-size: 13px;
    }
    .error { color: var(--danger); }
    @media (max-width: 680px) {
      .row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>参数设置</h1>
      <p class="desc">保存后，立即抓取会使用这些设置；定时抓取命令也会同步更新。</p>

      <div class="row">
        <label for="researchTopic">研究方向名称</label>
        <input id="researchTopic" type="text" placeholder="例如：LLM Agent、RAG、Reasoning" />
      </div>
      <div class="row">
        <label for="aiModel">LLM 模型</label>
        <input id="aiModel" type="text" placeholder="例如：qwen3.5-35b-a3b" />
      </div>
      <div class="row">
        <label for="aiBase">LLM Base URL</label>
        <input id="aiBase" type="text" placeholder="例如：https://novaapi.top/v1" />
      </div>
      <div class="row">
        <label for="aiKey">LLM API Key</label>
        <input id="aiKey" type="password" placeholder="sk-..." />
      </div>
      <div class="row">
        <label for="paperMax">每次分析篇数</label>
        <input id="paperMax" type="number" min="1" max="200" />
      </div>
      <div class="row">
        <label for="hideUnanalyzed">仅显示已分析论文</label>
        <input id="hideUnanalyzed" type="checkbox" />
      </div>

      <div class="actions">
        <button id="saveBtn" class="primary">保存设置</button>
        <button id="reloadBtn">重新加载</button>
        <a href="/" target="_blank">返回论文面板</a>
      </div>
      <div id="status" class="status"></div>
      <div id="error" class="status error"></div>
    </div>
  </div>

  <script>
    function setStatus(msg) {
      document.getElementById("status").textContent = msg || "";
    }
    function setError(msg) {
      document.getElementById("error").textContent = msg || "";
    }
    async function fetchJSON(url, options) {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      return data;
    }
    function fillForm(data) {
      document.getElementById("researchTopic").value = data.research_topic || "";
      document.getElementById("aiModel").value = data.ai_model || "";
      document.getElementById("aiBase").value = data.ai_api_base || "";
      document.getElementById("aiKey").value = data.ai_api_key || "";
      document.getElementById("paperMax").value = data.paper_max_papers_per_run || 20;
      document.getElementById("hideUnanalyzed").checked = !!data.hide_unanalyzed;
    }
    async function loadSettings() {
      setError("");
      const data = await fetchJSON("/api/settings");
      fillForm(data);
      setStatus("已加载当前设置");
    }
    async function saveSettings() {
      setError("");
      const payload = {
        research_topic: document.getElementById("researchTopic").value.trim(),
        ai_model: document.getElementById("aiModel").value.trim(),
        ai_api_base: document.getElementById("aiBase").value.trim(),
        ai_api_key: document.getElementById("aiKey").value.trim(),
        paper_max_papers_per_run: Number(document.getElementById("paperMax").value || 20),
        hide_unanalyzed: !!document.getElementById("hideUnanalyzed").checked
      };
      const data = await fetchJSON("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      fillForm(data.settings || {});
      setStatus("设置已保存，并已同步到抓取任务");
    }

    document.getElementById("saveBtn").addEventListener("click", async () => {
      try { await saveSettings(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("reloadBtn").addEventListener("click", async () => {
      try { await loadSettings(); } catch (e) { setError(e.message || String(e)); }
    });

    loadSettings().catch((e) => setError(e.message || String(e)));
  </script>
</body>
</html>
"""


def build_panel_html_v2() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OmniHawk AI | Paper Radar</title>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Silkscreen:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap");
    :root {
      --bg: #121212;
      --bg-grad-1: rgba(255, 255, 255, 0.02);
      --bg-grad-2: rgba(30, 215, 96, 0.16);
      --card: #181818;
      --input-bg: #1f1f1f;
      --text: #ffffff;
      --muted: #b3b3b3;
      --line: #303030;
      --line-strong: #4d4d4d;
      --primary: #1ed760;
      --primary-2: #1db954;
      --danger: #f3727f;
      --badge-bg: rgba(30, 215, 96, 0.16);
      --badge-border: rgba(30, 215, 96, 0.35);
      --badge-text: #bcf9d2;
      --deep-btn-bg: #1f1f1f;
      --deep-btn-border: #1ed760;
      --deep-btn-text: #ffffff;
      --open-btn-bg: #252525;
      --open-btn-border: #4d4d4d;
      --open-btn-text: #ffffff;
      --panel-shadow: rgba(0, 0, 0, 0.5) 0 8px 24px;
      --card-shadow: rgba(0, 0, 0, 0.3) 0 8px 8px;
      --title-glow: rgba(30, 215, 96, 0.34);
    }
    :root[data-theme="light"] {
      --bg: #f4f7fb;
      --bg-grad-1: rgba(29, 185, 84, 0.12);
      --bg-grad-2: rgba(21, 128, 61, 0.08);
      --card: #ffffff;
      --input-bg: #eef2f8;
      --text: #0f172a;
      --muted: #475569;
      --line: #d5deea;
      --line-strong: #9fb2cc;
      --primary: #1db954;
      --primary-2: #15803d;
      --danger: #dc2626;
      --badge-bg: rgba(34, 197, 94, 0.12);
      --badge-border: rgba(34, 197, 94, 0.28);
      --badge-text: #15803d;
      --deep-btn-bg: #e8effa;
      --deep-btn-border: #15803d;
      --deep-btn-text: #0f172a;
      --open-btn-bg: #edf1f7;
      --open-btn-border: #c6d2e2;
      --open-btn-text: #0f172a;
      --panel-shadow: rgba(15, 23, 42, 0.08) 0 8px 24px;
      --card-shadow: rgba(15, 23, 42, 0.08) 0 8px 12px;
      --title-glow: rgba(21, 128, 61, 0.2);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Circular Std", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(1200px 700px at 5% -10%, var(--bg-grad-1), transparent 55%),
        radial-gradient(1000px 650px at 95% -15%, var(--bg-grad-2), transparent 50%),
        var(--bg);
      color: var(--text);
      min-height: 100vh;
      opacity: 0;
      transform: translateY(16px);
      transition:
        background-color 0.35s ease,
        color 0.2s ease,
        opacity 0.28s ease,
        transform 0.34s cubic-bezier(.22,1,.36,1);
    }
    body.page-ready {
      opacity: 1;
      transform: translateY(0);
    }
    body.page-leaving {
      opacity: 0;
      transform: translateX(28px);
      pointer-events: none;
    }
    .wrap { max-width: 1700px; margin: 0 auto; padding: 18px 16px 24px; }
    .top {
      background: transparent;
      border: none;
      border-radius: 0;
      padding: 0 0 12px;
      position: static;
      top: auto;
      z-index: 5;
      backdrop-filter: none;
      box-shadow: none;
    }
    .main-layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      margin-top: 16px;
      align-items: start;
    }
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: static;
      top: auto;
      align-self: start;
    }
    .main-area { min-width: 0; }
    .panel {
      background: rgba(255, 255, 255, 0.02);
      border: none;
      border-radius: 10px;
      padding: 14px;
      box-shadow: none;
    }
    .panel-title {
      margin: 0 0 10px;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.2px;
    }
    .config-toggle-row {
      margin-top: 10px;
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    .panel-box {
      display: none;
      margin-top: 10px;
      padding: 12px;
      background: var(--card);
      border-radius: 10px;
      box-shadow: var(--card-shadow);
    }
    .panel-box.open { display: block; }
    .panel-box h4 {
      margin: 0 0 10px;
      font-size: 16px;
      letter-spacing: 0.2px;
    }
    .top-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 12px;
    }
    .top-left {
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-width: 0;
      overflow: visible;
    }
    .page-tabs {
      display: inline-flex;
      align-items: center;
      gap: 18px;
      flex-wrap: wrap;
    }
    .page-tab {
      display: inline-flex;
      align-items: center;
      border: none;
      border-radius: 0;
      padding: 6px 0;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.2px;
      text-transform: none;
      color: var(--muted);
      text-decoration: none;
      background: transparent;
      transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease;
    }
    .page-tab:hover { border-color: transparent; color: var(--text); text-decoration: none; }
    .page-tab.active {
      border-color: transparent;
      color: var(--text);
      background: transparent;
      border-bottom: 2px solid var(--primary);
    }
    .top-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .row {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      align-items: center;
      margin-top: 2px;
    }
    .row label, .toolbar label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: var(--muted);
    }
    .title {
      font-size: 34px;
      font-weight: 760;
      margin: 0;
      letter-spacing: 1px;
      text-transform: uppercase;
      line-height: 1.22;
      padding: 4px 0 6px;
      display: block;
      overflow: visible;
      font-family: "Orbitron", "Rajdhani", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: linear-gradient(120deg, #ffffff 0%, #e8fff0 36%, var(--primary) 78%, #8ef4b6 100%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      text-shadow: 0 0 18px var(--title-glow), 0 8px 24px rgba(0, 0, 0, 0.38);
    }
    :root[data-theme="light"] .title {
      background: none;
      -webkit-background-clip: initial;
      background-clip: initial;
      -webkit-text-fill-color: #0f7a3a;
      color: #0f7a3a;
      text-shadow: 0 1px 0 rgba(15, 23, 42, 0.16), 0 0 4px rgba(21, 128, 61, 0.12);
    }
    .muted { color: var(--muted); font-size: 14px; }
    .status {
      margin-top: 10px;
      font-size: 14px;
      color: var(--muted);
      white-space: pre-wrap;
    }
    .toolbar {
      margin-top: 14px;
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .panel .toolbar { margin-top: 10px; }
    .panel .toolbar:first-of-type { margin-top: 0; }
    .subtle {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
      margin-top: 8px;
      display: inline-block;
    }
    button, select, input[type="text"], input[type="number"], input[type="date"], input[type="password"] {
      border: none;
      border-radius: 10px;
      padding: 10px 14px;
      background: var(--input-bg);
      color: var(--text);
      font-size: 15px;
      transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.18s ease, box-shadow 0.2s ease;
    }
    button, select { cursor: pointer; }
    button:hover, select:hover { background: #2a2a2a; }
    button:active { transform: translateY(1px); }
    input[type="text"], input[type="number"], input[type="date"] { min-width: 152px; }
    #searchQ { min-width: 320px; }
    button:disabled { cursor: not-allowed; opacity: 0.65; }
    button.primary {
      border-color: var(--primary);
      background: var(--primary);
      color: #111;
    }
    button.primary:hover { background: var(--primary-2); }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      margin: 14px 0 0;
      align-items: start;
      grid-auto-rows: 1fr;
    }
    .grid > .empty {
      grid-column: 1 / -1;
      justify-self: center;
    }
    .grid > .card:only-child {
      grid-column: 1 / -1;
      justify-self: stretch;
    }
    .card {
      background: var(--card);
      border-radius: 12px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      height: 100%;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s ease, box-shadow 0.24s ease;
    }
    .card:hover { transform: translateY(-4px); }
    :root[data-theme="light"] .card:hover { box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12); }
    :root[data-theme="dark"] .card:hover { box-shadow: 0 16px 34px rgba(0, 0, 0, 0.5); }
    .card h3 { margin: 0 0 8px; font-size: 24px; line-height: 1.35; }
    .meta {
      display: grid;
      grid-template-columns: 1fr;
      gap: 4px;
      font-size: 16px;
      color: var(--muted);
      margin-bottom: 8px;
    }
    .badges { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }
    .badge {
      background: var(--badge-bg);
      color: var(--badge-text);
      border-radius: 8px;
      padding: 3px 10px;
      font-size: 14px;
    }
    .sec { margin-top: 8px; font-size: 17px; line-height: 1.64; }
    .sec b { display: inline-block; min-width: 130px; color: var(--text); opacity: 0.9; }
    .sec.abstract { white-space: normal; line-height: 1.6; }
    .actions {
      margin-top: 10px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .btn-sm { border-radius: 10px; padding: 8px 14px; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }
    .btn-star { background: rgba(30,215,96,0.16); border-color: rgba(30,215,96,0.4); color: #ffffff; }
    .btn-ignore { background: #252525; border-color: #4d4d4d; color: #cbcbcb; }
    .btn-deep { background: var(--deep-btn-bg); border-color: var(--deep-btn-border); color: var(--deep-btn-text); }
    .btn-open { background: var(--open-btn-bg); border-color: var(--open-btn-border); color: var(--open-btn-text); }
    .score {
      display: inline-block;
      background: rgba(30, 215, 96, 0.16);
      color: #ffffff;
      border-radius: 8px;
      font-size: 13px;
      padding: 2px 8px;
      margin-left: 8px;
    }
    .clamp-2, .clamp-3 {
      display: -webkit-box;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .clamp-2 { -webkit-line-clamp: 2; }
    .clamp-3 { -webkit-line-clamp: 3; }
    .settings {
      margin-top: 0;
      padding: 0;
      border: none;
      border-radius: 0;
      background: transparent;
      display: block;
      max-height: none;
      opacity: 1;
      overflow: visible;
      pointer-events: auto;
      box-shadow: none;
      transition: none;
    }
    .settings.open {
      margin-top: 0;
      padding: 0;
      max-height: none;
      opacity: 1;
      pointer-events: auto;
      overflow: visible;
    }
    .settings .grid2 {
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 8px 10px;
      align-items: center;
    }
    .settings input[type="text"], .settings input[type="password"], .settings input[type="number"], .settings select {
      width: 100%;
      border: none;
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 13px;
      background: var(--input-bg);
      color: var(--text);
    }
    .settings-actions {
      margin-top: 10px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .input-with-action {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      width: 100%;
    }
    .input-with-action button {
      width: 40px;
      min-width: 40px;
      padding: 8px 0;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }
    .icon-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-width: 104px;
      justify-content: center;
      padding: 10px 14px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.7px;
      text-transform: uppercase;
    }
    .icon-btn svg { width: 16px; height: 16px; }
    .icon-btn:hover { border-color: transparent; }
    .subscription-list {
      margin-top: 10px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }
    .subscription-item {
      border: none;
      border-radius: 10px;
      background: var(--input-bg);
      padding: 10px 11px;
      font-size: 13px;
      color: var(--text);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .subscription-item .line {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      line-height: 1.4;
    }
    .subscription-item .line:last-child { padding-top: 2px; }
    .empty {
      border-radius: 12px;
      padding: 24px;
      text-align: center;
      color: var(--muted);
      background: var(--card);
    }
    .error { color: var(--danger); }
    a { color: #1ed760; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; transition: none !important; }
    }
    @media (max-width: 1440px) {
      .main-layout { grid-template-columns: 1fr; }
    }
    @media (max-width: 1200px) {
      .main-layout { grid-template-columns: 1fr; }
      .sidebar { position: static; top: auto; }
    }
    @media (max-width: 1280px) {
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .wrap { padding: 12px 10px 16px; }
      .grid { grid-template-columns: minmax(0, 1fr); }
      .settings .grid2 { grid-template-columns: 1fr; }
      .subscription-list { grid-template-columns: 1fr; }
      .main-layout { gap: 12px; margin-top: 12px; }
      .panel { padding: 12px; }
      .title { font-size: 28px; }
      #searchQ { min-width: 100%; }
      }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="top-head">
        <div class="top-left">
          <p class="title" data-i18n="title">OmniHawk AI · 论文雷达</p>
          <div class="page-tabs">
            <a class="page-tab" href="/" data-i18n="tab_home">首页</a>
            <a class="page-tab active" href="/panel" data-i18n="tab_papers">论文雷达</a>
            <a class="page-tab" href="/progress" data-i18n="tab_progress">AI 前沿雷达</a>
            <a class="page-tab" href="/finance" data-i18n="tab_finance">AI 财经信息</a>
            <a class="page-tab" href="/reports" data-i18n="tab_reports">AI 产业报告</a>
            <a class="page-tab" href="/policy-safety" data-i18n="tab_policy_safety">AI 政策与安全</a>
            <a class="page-tab" href="/oss" data-i18n="tab_oss">AI 开源生态与开发者信号</a>
          </div>
        </div>
        <div class="top-right">
          <button id="langToggle" class="icon-btn" type="button" title="Language">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 5h12M9 3v2M7 5a17 17 0 0 0 5 10M9 5a17 17 0 0 1-5 10"></path>
              <path d="M14 13h7M17.5 10v3M16 21l1.5-3 1.5 3"></path>
            </svg>
            <span id="langShort">ZH</span>
          </button>
          <button id="themeToggle" class="icon-btn" type="button" title="Theme">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 1 0 9.8 9.8Z"></path>
            </svg>
            <span id="themeShort">Dark</span>
          </button>
        </div>
      </div>
    </div>
      <div class="row">
        <button id="runNow" class="primary" data-i18n="run_now">立即抓取</button>
        <label><span data-i18n="interval">抓取间隔</span>
          <select id="interval">
            <option value="5">5 min</option>
            <option value="10">10 min</option>
            <option value="15">15 min</option>
            <option value="20">20 min</option>
            <option value="30">30 min</option>
            <option value="60">60 min</option>
            <option value="120">120 min</option>
            <option value="180">180 min</option>
            <option value="240">240 min</option>
            <option value="360">360 min</option>
            <option value="720">720 min</option>
            <option value="1440">1440 min</option>
          </select>
        </label>
        <button id="saveInterval" data-i18n="save_interval">保存间隔</button>
        <button id="refreshNow" data-i18n="refresh">刷新</button>
      </div>

      <div class="toolbar">
        <label><span data-i18n="view_mode">视图</span>
          <select id="viewMode">
            <option value="all" data-i18n="view_all">已分析论文</option>
            <option value="favorites" data-i18n="view_favorites">仅收藏</option>
            <option value="ignored" data-i18n="view_ignored">忽略列表</option>
          </select>
        </label>
        <label><span data-i18n="sort_mode">排序</span>
          <select id="sortMode">
            <option value="score" data-i18n="sort_score">按推荐分</option>
            <option value="time" data-i18n="sort_time">按时间</option>
            <option value="title" data-i18n="sort_title">按标题</option>
          </select>
        </label>
        <input id="searchQ" type="text" data-i18n-ph="search_ph" placeholder="关键词（标题/摘要/作者/方法）" />
        <select id="filterCategory">
          <option value="" data-i18n="cat_any">分类不限</option>
          <option value="cs.AI">cs.AI</option>
          <option value="cs.CL">cs.CL</option>
          <option value="cs.CV">cs.CV</option>
          <option value="cs.LG">cs.LG</option>
          <option value="cs.RO">cs.RO</option>
          <option value="cs.IR">cs.IR</option>
          <option value="cs.NE">cs.NE</option>
          <option value="cs.SE">cs.SE</option>
          <option value="cs.CR">cs.CR</option>
          <option value="cs.DB">cs.DB</option>
          <option value="cs.DC">cs.DC</option>
          <option value="cs.HC">cs.HC</option>
          <option value="cs.PL">cs.PL</option>
          <option value="cs.CY">cs.CY</option>
        </select>
        <button id="applyFilters" data-i18n="apply_filters">筛选</button>
        <button id="clearFilters" data-i18n="clear_filters">清空筛选</button>
        <span id="favSummary" class="muted"></span>
      </div>
      <div class="config-toggle-row">
        <button id="openSettingsPanel" type="button" data-i18n="open_settings_panel">参数设置</button>
        <button id="openSubscriptionPanel" type="button" data-i18n="open_subscription_panel">订阅设置</button>
      </div>
      <div id="settingsDrawer" class="panel-box">
        <h4 data-i18n="settings">参数设置</h4>
        <div id="settingsPanel" class="settings open">
          <div class="grid2">
          <label for="paperPrimaryCategory" data-i18n="cfg_primary_category">论文主分类</label>
          <select id="paperPrimaryCategory">
            <option value="">all</option>
            <option value="cs.AI">cs.AI</option>
            <option value="cs.CL">cs.CL</option>
            <option value="cs.CV">cs.CV</option>
            <option value="cs.LG">cs.LG</option>
            <option value="cs.RO">cs.RO</option>
            <option value="cs.IR">cs.IR</option>
            <option value="cs.NE">cs.NE</option>
            <option value="cs.SE">cs.SE</option>
            <option value="cs.CR">cs.CR</option>
            <option value="cs.DB">cs.DB</option>
            <option value="cs.DC">cs.DC</option>
            <option value="cs.HC">cs.HC</option>
            <option value="cs.PL">cs.PL</option>
            <option value="cs.CY">cs.CY</option>
          </select>

          <label for="paperSubtopics" data-i18n="cfg_subtopics">子领域关键词</label>
          <input id="paperSubtopics" type="text" placeholder="agent, llm, rag, reasoning" />

          <label for="analysisLanguage" data-i18n="cfg_output_language">输出语言</label>
          <input id="analysisLanguage" type="text" placeholder="Chinese / English / Korean / Japanese / French / Traditional Chinese" />

          <label for="aiModel">LLM Model</label>
          <input id="aiModel" type="text" placeholder="qwen3.5-35b-a3b" />

          <label for="aiBase">LLM Base URL</label>
          <input id="aiBase" type="text" placeholder="https://novaapi.top/v1" />

          <label for="aiKey">LLM API Key</label>
          <div class="input-with-action">
            <input id="aiKey" type="password" placeholder="sk-..." />
            <button id="toggleAiKey" type="button" title="show">
              <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
          </div>

          <label for="paperMax" data-i18n="cfg_paper_max">每次分析篇数</label>
          <input id="paperMax" type="number" min="1" max="200" />

          <label for="paperMaxPerSource" data-i18n="cfg_max_per_source">每源抓取条数</label>
          <input id="paperMaxPerSource" type="number" min="1" max="120" />

          <label for="paperNotifyChannel" data-i18n="cfg_notify_channel">默认推送渠道</label>
          <select id="paperNotifyChannel">
            <option value="feishu">Feishu</option>
            <option value="wework">WeCom</option>
            <option value="wechat">WeChat Personal</option>
            <option value="telegram">Telegram</option>
            <option value="dingtalk">DingTalk</option>
            <option value="ntfy">ntfy</option>
            <option value="bark">Bark</option>
            <option value="slack">Slack</option>
            <option value="email">Email</option>
          </select>

          <label for="paperNotifyLimit" data-i18n="cfg_notify_limit">默认推送条数</label>
          <input id="paperNotifyLimit" type="number" min="1" max="30" />

          <label for="paperAutoEnabled" data-i18n="cfg_auto_enabled">启用定时抓取</label>
          <select id="paperAutoEnabled">
            <option value="0" data-i18n="opt_no">否</option>
            <option value="1" data-i18n="opt_yes">是</option>
          </select>

          <label for="paperAutoInterval" data-i18n="cfg_auto_interval">定时抓取(分钟)</label>
          <input id="paperAutoInterval" type="number" min="5" max="1440" />

          <label for="paperAutoPushEnabled" data-i18n="cfg_auto_push_enabled">抓取后自动推送订阅</label>
          <select id="paperAutoPushEnabled">
            <option value="0" data-i18n="opt_no">否</option>
            <option value="1" data-i18n="opt_yes">是</option>
          </select>

          <label for="paperDefaultQ" data-i18n="cfg_default_q">默认关键词</label>
          <input id="paperDefaultQ" type="text" placeholder="AI, LLM, agent..." />

          <label for="paperDefaultSourceId" data-i18n="cfg_default_source_id">默认来源ID</label>
          <input id="paperDefaultSourceId" type="text" placeholder="source id" />

          <label for="paperDefaultRegion" data-i18n="cfg_default_region">默认区域</label>
          <select id="paperDefaultRegion">
            <option value="" data-i18n="region_any">全部</option>
            <option value="global" data-i18n="region_global">全球</option>
            <option value="cn" data-i18n="region_cn">中国大陆</option>
          </select>

          <label for="paperDefaultEventType" data-i18n="cfg_default_event_type">默认类型</label>
          <select id="paperDefaultEventType">
            <option value="" data-i18n="event_any">全部</option>
            <option value="release" data-i18n="event_release">版本发布</option>
            <option value="report" data-i18n="event_report">技术报告</option>
            <option value="benchmark" data-i18n="event_benchmark">评测基准</option>
            <option value="safety" data-i18n="event_safety">安全治理</option>
            <option value="update" data-i18n="event_update">一般更新</option>
          </select>

          <label for="feishuWebhook" data-i18n="cfg_feishu_webhook">Feishu Webhook</label>
          <input id="feishuWebhook" type="text" placeholder="https://open.feishu.cn/..." />

          <label for="weworkWebhook" data-i18n="cfg_wework_webhook">WeCom Webhook</label>
          <input id="weworkWebhook" type="text" placeholder="https://qyapi.weixin.qq.com/..." />

          <label for="weworkMsgType" data-i18n="cfg_wework_msg_type">WeCom Message Type</label>
          <select id="weworkMsgType">
            <option value="markdown" data-i18n="cfg_wework_msg_markdown">Markdown (Group Bot)</option>
            <option value="text" data-i18n="cfg_wework_msg_text">Text (Personal WeChat)</option>
          </select>

          <label for="dingtalkWebhook" data-i18n="cfg_dingtalk_webhook">DingTalk Webhook</label>
          <input id="dingtalkWebhook" type="text" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />

          <label for="telegramBotToken" data-i18n="cfg_telegram_bot_token">Telegram Bot Token</label>
          <input id="telegramBotToken" type="text" placeholder="123456:ABC..." />

          <label for="telegramChatId" data-i18n="cfg_telegram_chat_id">Telegram Chat ID</label>
          <input id="telegramChatId" type="text" placeholder="-1001234567890" />

          <label for="ntfyServerUrl" data-i18n="cfg_ntfy_server_url">ntfy Server URL</label>
          <input id="ntfyServerUrl" type="text" placeholder="https://ntfy.sh" />

          <label for="ntfyTopic" data-i18n="cfg_ntfy_topic">ntfy Topic</label>
          <input id="ntfyTopic" type="text" placeholder="omnihawk-ai" />

          <label for="ntfyToken" data-i18n="cfg_ntfy_token">ntfy Token</label>
          <input id="ntfyToken" type="password" placeholder="optional token" />

          <label for="barkUrl" data-i18n="cfg_bark_url">Bark URL</label>
          <input id="barkUrl" type="text" placeholder="https://api.day.app/<device_key>" />

          <label for="slackWebhook" data-i18n="cfg_slack_webhook">Slack Webhook</label>
          <input id="slackWebhook" type="text" placeholder="https://hooks.slack.com/services/..." />

          <label for="emailFrom" data-i18n="cfg_email_from">邮箱发件人</label>
          <input id="emailFrom" type="text" placeholder="example@qq.com" />

          <label for="emailPassword" data-i18n="cfg_email_password">邮箱授权码</label>
          <input id="emailPassword" type="password" placeholder="password/token" />

          <label for="emailTo" data-i18n="cfg_email_to">邮箱收件人</label>
          <input id="emailTo" type="text" placeholder="a@xx.com;b@yy.com" />

          <label for="emailSmtpServer" data-i18n="cfg_email_smtp_server">SMTP Server</label>
          <input id="emailSmtpServer" type="text" placeholder="smtp.qq.com" />

          <label for="emailSmtpPort" data-i18n="cfg_email_smtp_port">SMTP Port</label>
          <input id="emailSmtpPort" type="text" placeholder="465" />
          </div>
          <div class="settings-actions">
            <button id="saveSettings" data-i18n="save_settings">保存设置</button>
            <button id="reloadSettings" data-i18n="reload_settings">重载设置</button>
            <label><span data-i18n="notify_test">通知测试</span>
              <select id="testChannel">
                <option value="feishu">Feishu</option>
                <option value="wework">WeCom</option>
                <option value="wechat">WeChat Personal</option>
                <option value="telegram">Telegram</option>
                <option value="dingtalk">DingTalk</option>
                <option value="ntfy">ntfy</option>
                <option value="bark">Bark</option>
                <option value="slack">Slack</option>
                <option value="email">Email</option>
              </select>
            </label>
            <button id="testNotify" data-i18n="send_test">测试发送</button>
          </div>
        </div>
      </div>
      <div id="subscriptionDrawer" class="panel-box">
        <h4 data-i18n="sub_panel_title">订阅设置</h4>
        <div class="toolbar">
        <input id="subscriptionName" type="text" data-i18n-ph="sub_name_ph" placeholder="订阅名称（可选）" />
        <label><span data-i18n="sub_channel">通知渠道</span>
          <select id="subscriptionChannel">
            <option value="feishu">Feishu</option>
            <option value="wework">WeCom</option>
            <option value="wechat">WeChat Personal</option>
            <option value="telegram">Telegram</option>
            <option value="dingtalk">DingTalk</option>
            <option value="ntfy">ntfy</option>
            <option value="bark">Bark</option>
            <option value="slack">Slack</option>
            <option value="email">Email</option>
          </select>
        </label>
        <label><span data-i18n="sub_strategy">推送策略</span>
          <select id="subscriptionStrategy">
            <option value="incremental" data-i18n="strategy_incremental">增量监控</option>
            <option value="daily" data-i18n="strategy_daily">当日汇总</option>
            <option value="realtime" data-i18n="strategy_realtime">实时告警</option>
          </select>
        </label>
        <label><span data-i18n="sub_limit">订阅条数</span>
          <input id="subscriptionLimit" type="number" min="1" max="500" value="120" />
        </label>
        <label><span data-i18n="sub_enabled">启用</span>
          <select id="subscriptionEnabled">
            <option value="1" data-i18n="opt_yes">是</option>
            <option value="0" data-i18n="opt_no">否</option>
          </select>
        </label>
      </div>
      <div class="toolbar">
        <input id="subSourceId" type="text" data-i18n-ph="sub_source_ph" placeholder="来源ID（可选）" />
        <label><span data-i18n="region">区域</span>
          <select id="subRegion">
            <option value="" data-i18n="region_any">全部</option>
            <option value="global" data-i18n="region_global">全球</option>
            <option value="cn" data-i18n="region_cn">中国大陆</option>
          </select>
        </label>
        <label><span data-i18n="event_type">类型</span>
          <select id="subEventType">
            <option value="" data-i18n="event_any">全部</option>
            <option value="release" data-i18n="event_release">版本发布</option>
            <option value="report" data-i18n="event_report">技术报告</option>
            <option value="benchmark" data-i18n="event_benchmark">评测基准</option>
            <option value="safety" data-i18n="event_safety">安全治理</option>
            <option value="update" data-i18n="event_update">一般更新</option>
          </select>
        </label>
      </div>
      <div class="toolbar">
        <button id="saveSubscription" data-i18n="sub_save">保存为订阅</button>
        <button id="runSubscriptions" data-i18n="sub_run_all">执行全部订阅推送</button>
      </div>
        <span class="subtle" data-i18n="sub_hint">订阅会保存当前筛选条件，仅推送新增命中论文</span>
        <div id="subscriptionList" class="subscription-list"></div>
      </div>
      <div id="actionMsg" class="status"></div>
      <div id="error" class="status error"></div>
    </div>
    <div id="papers" class="grid"></div>
  </div>

  <script>
    const I18N = {
      "zh-CN": {
        title: "OmniHawk AI · 论文雷达",
        tab_home: "首页",
        tab_papers: "论文雷达",
        tab_progress: "AI 前沿雷达",
        tab_finance: "AI 财经信息",
        tab_reports: "AI 产业报告",
        tab_policy_safety: "AI 政策与安全",
        tab_oss: "AI 开源生态与开发者信号",
        run_now: "立即抓取",
        run_running: "抓取中...",
        interval: "抓取间隔",
        save_interval: "保存间隔",
        settings: "参数设置",
        panel_run: "抓取与状态",
        sub_panel_title: "订阅设置",
        open_settings_panel: "参数设置",
        open_subscription_panel: "订阅设置",
        refresh: "刷新",
        language: "语言",
        theme: "主题",
        lang_short_zh: "ZH",
        lang_short_en: "EN",
        theme_short_light: "Light",
        theme_short_dark: "Dark",
        tip_lang_to_zh: "切换到中文",
        tip_lang_to_en: "Switch to English",
        tip_theme_to_light: "切换到浅色",
        tip_theme_to_dark: "Switch to Dark",
        tip_key_show: "显示密钥",
        tip_key_hide: "隐藏密钥",
        view_mode: "视图",
        sort_mode: "排序",
        view_all: "已分析论文",
        view_favorites: "仅收藏",
        view_ignored: "忽略列表",
        sort_score: "按推荐分",
        sort_time: "按时间",
        sort_title: "按标题",
        cat_any: "分类不限",
        search_ph: "关键词（标题/摘要/作者/方法）",
        apply_filters: "筛选",
        clear_filters: "清空筛选",
        sub_name_ph: "订阅名称（可选）",
        sub_source_ph: "来源ID（可选）",
        sub_channel: "通知渠道",
        sub_strategy: "推送策略",
        sub_limit: "订阅条数",
        strategy_incremental: "增量监控 (incremental)",
        strategy_daily: "当日汇总 (daily)",
        strategy_realtime: "实时告警 (real-time)",
        sub_save: "保存为订阅",
        sub_saving: "保存中...",
        sub_run_all: "执行全部订阅推送",
        sub_hint: "订阅支持当日汇总/增量监控/实时告警三种策略",
        sub_empty: "暂无订阅，可在当前筛选下点击“保存为订阅”。",
        sub_default_name: "订阅",
        sub_enabled: "启用",
        sub_disabled: "停用",
        sub_preview_none: "无额外筛选",
        sub_last_notified: "最近推送",
        sub_last_match: "上次命中",
        sub_apply: "套用筛选",
        sub_run_once: "推送一次",
        sub_disable: "停用",
        sub_enable: "启用",
        sub_delete: "删除",
        opt_yes: "是",
        opt_no: "否",
        region: "区域",
        region_any: "全部",
        region_global: "全球",
        region_us: "美国",
        region_cn: "中国大陆",
        region_jp: "日本",
        region_apac: "亚太",
        region_eu: "欧洲",
        region_uk: "英国",
        region_fr: "法国",
        event_type: "类型",
        event_any: "全部",
        event_release: "版本发布",
        event_report: "技术报告",
        event_benchmark: "评测基准",
        event_safety: "安全治理",
        event_update: "一般更新",
        cfg_primary_category: "论文主分类",
        cfg_subtopics: "子领域关键词",
        cfg_output_language: "输出语言",
        cfg_paper_max: "每次分析篇数",
        cfg_max_per_source: "每源抓取条数",
        cfg_notify_channel: "默认推送渠道",
        cfg_notify_limit: "默认推送条数",
        cfg_auto_enabled: "启用定时抓取",
        cfg_auto_interval: "定时抓取(分钟)",
        cfg_auto_push_enabled: "抓取后自动推送订阅",
        cfg_default_q: "默认关键词",
        cfg_default_source_id: "默认来源ID",
        cfg_default_region: "默认区域",
        cfg_default_event_type: "默认类型",
        cfg_feishu_webhook: "Feishu Webhook",
        cfg_wework_webhook: "WeCom Webhook",
        cfg_wework_msg_type: "WeCom 消息类型",
        cfg_wework_msg_markdown: "Markdown（群机器人）",
        cfg_wework_msg_text: "Text（个人微信）",
        cfg_dingtalk_webhook: "DingTalk Webhook",
        cfg_telegram_bot_token: "Telegram Bot Token",
        cfg_telegram_chat_id: "Telegram Chat ID",
        cfg_ntfy_server_url: "ntfy Server URL",
        cfg_ntfy_topic: "ntfy Topic",
        cfg_ntfy_token: "ntfy Token",
        cfg_bark_url: "Bark URL",
        cfg_slack_webhook: "Slack Webhook",
        cfg_email_from: "邮箱发件人",
        cfg_email_password: "邮箱授权码",
        cfg_email_to: "邮箱收件人",
        cfg_email_smtp_server: "SMTP Server",
        cfg_email_smtp_port: "SMTP Port",
        save_settings: "保存设置",
        reload_settings: "重载设置",
        notify_test: "通知测试",
        send_test: "测试发送",
        msg_filter_applied: "筛选条件已应用",
        msg_filter_cleared: "筛选已清空",
        msg_run_now: "已触发立即抓取",
        msg_interval_updated: "抓取间隔已更新为 {n} 分钟",
        msg_analyzing: "正在执行深入分析，请稍候...",
        msg_analyzed: "深入分析完成",
        msg_added_fav: "已加入收藏",
        msg_removed_fav: "已取消收藏",
        msg_added_ignore: "已加入忽略列表",
        msg_removed_ignore: "已从忽略列表移除",
        msg_settings_saved: "设置已保存",
        msg_settings_reloaded: "设置已重载",
        msg_sub_saved: "已保存当前筛选为订阅",
        msg_sub_deleted: "订阅已删除",
        msg_sub_enabled: "订阅已启用",
        msg_sub_disabled: "订阅已停用",
        msg_sub_applied: "已套用订阅：{name}",
        status_running: "运行中",
        status_schedule: "当前调度",
        status_interval: "间隔(分钟)",
        status_started: "最近启动",
        status_finished: "最近完成",
        status_exit_code: "最近退出码",
        status_primary_category: "主分类",
        status_subtopics: "子领域",
        status_research_topic: "研究方向",
        status_max_per_run: "论文分析上限/次",
        status_model: "LLM模型",
        status_error: "错误",
        status_db: "DB",
        status_server_time: "服务端时间",
        label_author: "作者",
        label_aff: "作者单位",
        label_published: "发布时间",
        label_primary_category: "主分类",
        label_arxiv: "arXiv ID",
        label_batch: "分析批次",
        label_abstract: "摘要",
        label_pdf: "PDF",
        label_doi: "DOI",
        label_source: "链接",
        label_one_line: "一句话摘要",
        label_keywords: "关键词",
        label_method: "方法",
        label_conclusion: "结论",
        label_innovation: "创新点",
        btn_open_deep: "打开深入分析页",
        btn_view_deep: "查看深入分析",
        btn_run_deep: "一键深入分析",
        btn_analyzing: "深入分析中...",
        btn_fav: "收藏",
        btn_unfav: "取消收藏",
        btn_ignore: "忽略",
        btn_unignore: "取消忽略",
        score_prefix: "推荐阅读分",
        empty_title: "当前没有可展示论文。",
        empty_hint: "请先点击“立即抓取”或调整筛选条件。"
      },
      "en-US": {
        title: "OmniHawk AI · Paper Radar",
        tab_home: "Home",
        tab_papers: "Papers",
        tab_progress: "AI Frontier",
        tab_finance: "AI Finance",
        tab_reports: "AI Industry Reports",
        tab_policy_safety: "AI Policy & Safety",
        tab_oss: "AI OSS & Dev Signals",
        run_now: "Run Now",
        run_running: "Running...",
        interval: "Interval",
        save_interval: "Save Interval",
        settings: "Settings",
        panel_run: "Run & Status",
        sub_panel_title: "Subscriptions",
        open_settings_panel: "Settings",
        open_subscription_panel: "Subscriptions",
        refresh: "Refresh",
        language: "Language",
        theme: "Theme",
        lang_short_zh: "ZH",
        lang_short_en: "EN",
        theme_short_light: "Light",
        theme_short_dark: "Dark",
        tip_lang_to_zh: "Switch to Chinese",
        tip_lang_to_en: "Switch to English",
        tip_theme_to_light: "Switch to Light",
        tip_theme_to_dark: "Switch to Dark",
        tip_key_show: "Show API Key",
        tip_key_hide: "Hide API Key",
        view_mode: "View",
        sort_mode: "Sort",
        view_all: "Analyzed",
        view_favorites: "Favorites",
        view_ignored: "Ignored",
        sort_score: "By Score",
        sort_time: "By Time",
        sort_title: "By Title",
        cat_any: "Any Category",
        search_ph: "Keyword (title/abstract/author/method)",
        apply_filters: "Apply",
        clear_filters: "Clear",
        sub_name_ph: "Subscription Name (Optional)",
        sub_source_ph: "Source ID (Optional)",
        sub_channel: "Channel",
        sub_strategy: "Strategy",
        sub_limit: "Subscription Limit",
        strategy_incremental: "Incremental",
        strategy_daily: "Daily",
        strategy_realtime: "Real-time",
        sub_save: "Save as Subscription",
        sub_saving: "Saving...",
        sub_run_all: "Run All Subscriptions",
        sub_hint: "Subscriptions support Daily, Incremental, and Real-time alert strategies.",
        sub_empty: "No subscriptions yet. Save current filters as a subscription.",
        sub_default_name: "Subscription",
        sub_enabled: "Enabled",
        sub_disabled: "Disabled",
        sub_preview_none: "No extra filter",
        sub_last_notified: "Last Notified",
        sub_last_match: "Last Match",
        sub_apply: "Apply",
        sub_run_once: "Run Once",
        sub_disable: "Disable",
        sub_enable: "Enable",
        sub_delete: "Delete",
        opt_yes: "Yes",
        opt_no: "No",
        region: "Region",
        region_any: "All",
        region_global: "Global",
        region_us: "United States",
        region_cn: "Mainland China",
        region_jp: "Japan",
        region_apac: "APAC",
        region_eu: "Europe",
        region_uk: "UK",
        region_fr: "France",
        event_type: "Event Type",
        event_any: "All",
        event_release: "Release",
        event_report: "Technical Report",
        event_benchmark: "Benchmark",
        event_safety: "Safety & Policy",
        event_update: "General Update",
        cfg_primary_category: "Primary Category",
        cfg_subtopics: "Subtopics",
        cfg_output_language: "Output Language",
        cfg_paper_max: "Max Papers/Run",
        cfg_max_per_source: "Items per Source",
        cfg_notify_channel: "Default Push Channel",
        cfg_notify_limit: "Default Push Count",
        cfg_auto_enabled: "Enable Auto Fetch",
        cfg_auto_interval: "Auto Fetch Interval (min)",
        cfg_auto_push_enabled: "Auto push subscriptions after fetch",
        cfg_default_q: "Default Keyword",
        cfg_default_source_id: "Default Source ID",
        cfg_default_region: "Default Region",
        cfg_default_event_type: "Default Event Type",
        cfg_feishu_webhook: "Feishu Webhook",
        cfg_wework_webhook: "WeCom Webhook",
        cfg_wework_msg_type: "WeCom Message Type",
        cfg_wework_msg_markdown: "Markdown (Group Bot)",
        cfg_wework_msg_text: "Text (Personal WeChat)",
        cfg_dingtalk_webhook: "DingTalk Webhook",
        cfg_telegram_bot_token: "Telegram Bot Token",
        cfg_telegram_chat_id: "Telegram Chat ID",
        cfg_ntfy_server_url: "ntfy Server URL",
        cfg_ntfy_topic: "ntfy Topic",
        cfg_ntfy_token: "ntfy Token",
        cfg_bark_url: "Bark URL",
        cfg_slack_webhook: "Slack Webhook",
        cfg_email_from: "Email Sender",
        cfg_email_password: "Email Password",
        cfg_email_to: "Email Recipients",
        cfg_email_smtp_server: "SMTP Server",
        cfg_email_smtp_port: "SMTP Port",
        save_settings: "Save",
        reload_settings: "Reload",
        notify_test: "Notify Test",
        send_test: "Send Test",
        msg_filter_applied: "Filters applied",
        msg_filter_cleared: "Filters cleared",
        msg_run_now: "Run triggered",
        msg_interval_updated: "Interval updated to {n} minutes",
        msg_analyzing: "Deep analysis is running...",
        msg_analyzed: "Deep analysis completed",
        msg_added_fav: "Added to favorites",
        msg_removed_fav: "Removed from favorites",
        msg_added_ignore: "Added to ignored list",
        msg_removed_ignore: "Removed from ignored list",
        msg_settings_saved: "Settings saved",
        msg_settings_reloaded: "Settings reloaded",
        msg_sub_saved: "Subscription saved",
        msg_sub_deleted: "Subscription deleted",
        msg_sub_enabled: "Subscription enabled",
        msg_sub_disabled: "Subscription disabled",
        msg_sub_applied: "Subscription applied: {name}",
        status_running: "Running",
        status_schedule: "Schedule",
        status_interval: "Interval(min)",
        status_started: "Last Started",
        status_finished: "Last Finished",
        status_exit_code: "Last Exit Code",
        status_primary_category: "Primary Category",
        status_subtopics: "Subtopics",
        status_research_topic: "Research Topic",
        status_max_per_run: "Max Papers/Run",
        status_model: "LLM Model",
        status_error: "Error",
        status_db: "DB",
        status_server_time: "Server Time",
        label_author: "Authors",
        label_aff: "Affiliations",
        label_published: "Published",
        label_primary_category: "Category",
        label_arxiv: "arXiv ID",
        label_batch: "Analysis Batch",
        label_abstract: "Abstract",
        label_pdf: "PDF",
        label_doi: "DOI",
        label_source: "Source",
        label_one_line: "One-line Summary",
        label_keywords: "Keywords",
        label_method: "Method",
        label_conclusion: "Conclusion",
        label_innovation: "Innovation",
        btn_open_deep: "Open Deep Page",
        btn_view_deep: "View Deep Analysis",
        btn_run_deep: "Run Deep Analysis",
        btn_analyzing: "Analyzing...",
        btn_fav: "Favorite",
        btn_unfav: "Unfavorite",
        btn_ignore: "Ignore",
        btn_unignore: "Unignore",
        score_prefix: "Score",
        empty_title: "No papers to display.",
        empty_hint: "Run fetch or adjust filters."
      }
    };

    const state = {
      status: null,
      papers: [],
      paperStats: null,
      settings: null,
      viewMode: "all",
      sortMode: "score",
      subscriptions: [],
      sortOrder: "desc",
      historyMode: "all",
      appliedQuery: null,
      deepRunningKeys: Object.create(null),
      paperTranslatingKeys: Object.create(null),
      paperTranslationRunning: false,
      statusPollTimer: null,
      lang: localStorage.getItem("panel_lang") || "zh-CN",
      theme: localStorage.getItem("panel_theme") || "dark",
      aiKeyVisible: false,
      savingSubscription: false
    };

    function t(key, vars = {}) {
      const table = I18N[state.lang] || I18N["zh-CN"];
      let txt = table[key] || key;
      for (const [k, v] of Object.entries(vars || {})) {
        txt = txt.replace(new RegExp(`\\\\{${k}\\\\}`, "g"), String(v));
      }
      return txt;
    }

    function esc(v) {
      return (v ?? "").toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function normalizeModelName(value) {
      const raw = (value || "").toString().trim();
      if (!raw) return "";
      const idx = raw.lastIndexOf("/");
      if (idx > -1 && idx < raw.length - 1) return raw.slice(idx + 1).trim();
      return raw;
    }

    function currentOutputLanguage() {
      const explicit = (document.getElementById("analysisLanguage")?.value || state.settings?.analysis_language || "").toString().trim();
      if (explicit) return explicit;
      return state.lang === "en-US" ? "English" : "Chinese";
    }

    function updateTopToggles() {
      const langShort = document.getElementById("langShort");
      const themeShort = document.getElementById("themeShort");
      const langToggle = document.getElementById("langToggle");
      const themeToggle = document.getElementById("themeToggle");
      if (langShort) langShort.textContent = state.lang === "zh-CN" ? t("lang_short_zh") : t("lang_short_en");
      if (themeShort) themeShort.textContent = state.theme === "dark" ? t("theme_short_dark") : t("theme_short_light");
      if (langToggle) langToggle.title = state.lang === "zh-CN" ? t("tip_lang_to_en") : t("tip_lang_to_zh");
      if (themeToggle) themeToggle.title = state.theme === "dark" ? t("tip_theme_to_light") : t("tip_theme_to_dark");
    }

    function updateAiKeyToggle() {
      const input = document.getElementById("aiKey");
      const btn = document.getElementById("toggleAiKey");
      if (!input || !btn) return;
      input.type = state.aiKeyVisible ? "text" : "password";
      btn.title = state.aiKeyVisible ? t("tip_key_hide") : t("tip_key_show");
    }

    function applyTheme() {
      document.documentElement.setAttribute("data-theme", state.theme === "dark" ? "dark" : "light");
      updateTopToggles();
    }

    function initPageShellMotion() {
      const body = document.body;
      if (!body) return;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => body.classList.add("page-ready"));
      });
      document.querySelectorAll(".page-tab[href]").forEach((link) => {
        link.addEventListener("click", (event) => {
          const href = link.getAttribute("href") || "";
          if (!href || link.classList.contains("active")) return;
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          body.classList.add("page-leaving");
          window.setTimeout(() => {
            window.location.href = href;
          }, 180);
        });
      });
    }

    function applyI18n() {
      document.documentElement.lang = state.lang === "en-US" ? "en" : "zh-CN";
      document.title = t("title");
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (key) el.textContent = t(key);
      });
      document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
        const key = el.getAttribute("data-i18n-ph");
        if (key) el.setAttribute("placeholder", t(key));
      });
      renderStatus();
      renderFavoriteSummary();
      renderCards();
      renderSubscriptions();
      updateTopToggles();
      updateAiKeyToggle();
      setSubscriptionSaveButtonState(!!state.savingSubscription);
    }

    function setError(msg) {
      document.getElementById("error").textContent = msg || "";
    }

    function setMessage(msg) {
      document.getElementById("actionMsg").textContent = msg || "";
    }

    function setRunButtonState(running) {
      const btn = document.getElementById("runNow");
      if (!btn) return;
      btn.disabled = !!running;
      btn.textContent = running ? t("run_running") : t("run_now");
    }

    function setSubscriptionSaveButtonState(running) {
      const btn = document.getElementById("saveSubscription");
      if (!btn) return;
      btn.disabled = !!running;
      btn.textContent = running ? t("sub_saving") : t("sub_save");
    }

    function setDeepButtonState(paperKey, running) {
      const key = (paperKey || "").toString();
      if (!key) return;
      const buttons = document.querySelectorAll(`button.act-deep[data-key="${key}"]`);
      buttons.forEach((btn) => {
        btn.disabled = !!running;
        btn.textContent = running ? t("btn_analyzing") : t("btn_run_deep");
      });
    }

    function normalizeSubtopicsText(value) {
      const parts = (value || "").split(",").map(v => v.trim()).filter(Boolean);
      const seen = new Set();
      const out = [];
      for (const item of parts) {
        const k = item.toLowerCase();
        if (seen.has(k)) continue;
        seen.add(k);
        out.push(item);
      }
      return out.join(", ");
    }

    function buildResearchTopicFromForm() {
      const category = (document.getElementById("paperPrimaryCategory")?.value || "").trim();
      const subtopics = normalizeSubtopicsText(document.getElementById("paperSubtopics")?.value || "");
      if (category && subtopics) return `${category} / ${subtopics}`;
      if (category) return category;
      return subtopics;
    }

    function collectFilterInputs() {
      return {
        q: (document.getElementById("searchQ")?.value || "").trim(),
        category: (document.getElementById("filterCategory")?.value || "").trim(),
        source_id: (document.getElementById("subSourceId")?.value || "").trim(),
        region: (document.getElementById("subRegion")?.value || "").trim(),
        event_type: (document.getElementById("subEventType")?.value || "").trim()
      };
    }

    function applyFilterInputs(data) {
      const f = data || {};
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value || "";
      };
      set("searchQ", f.q || "");
      set("filterCategory", f.category || "");
      set("subSourceId", f.source_id || "");
      set("subRegion", f.region || "");
      set("subEventType", f.event_type || "");
    }

    function captureQueryFromInputs(overrides = {}) {
      return {
        limit: Number(overrides.limit || 100),
        mode: overrides.mode || document.getElementById("viewMode")?.value || "all",
        sort_by: overrides.sort_by || document.getElementById("sortMode")?.value || "score",
        sort_order: "desc",
        history: "all",
        filters: { ...collectFilterInputs(), ...(overrides.filters || {}) }
      };
    }

    function buildPaperQueryParams(queryObj = null) {
      const query = queryObj || state.appliedQuery || captureQueryFromInputs();
      const params = new URLSearchParams();
      params.set("limit", String(query.limit || 100));
      params.set("mode", query.mode || "all");
      params.set("sort_by", query.sort_by || "score");
      params.set("sort_order", "desc");
      params.set("history", query.history || "all");
      params.set("output_language", currentOutputLanguage());
      const filters = query.filters || {};
      ["q", "category", "source_id", "region", "event_type"].forEach((key) => {
        const value = (filters[key] ?? "").toString().trim();
        if (value) params.set(key, value);
      });
      return params;
    }

    async function applyFiltersAndRefresh(showMessage = false) {
      state.appliedQuery = captureQueryFromInputs();
      await refreshPapers();
      if (showMessage) setMessage(t("msg_filter_applied"));
    }

    function syncFiltersFromUrl() {
      const params = new URLSearchParams(window.location.search || "");
      applyFilterInputs({
        q: params.get("q") || "",
        category: params.get("category") || "",
        source_id: params.get("source_id") || "",
        region: params.get("region") || "",
        event_type: params.get("event_type") || "",
      });
      const mode = params.get("mode");
      const sortBy = params.get("sort_by");
      if (mode && document.getElementById("viewMode")) document.getElementById("viewMode").value = mode;
      if (sortBy && document.getElementById("sortMode")) document.getElementById("sortMode").value = sortBy;
      state.appliedQuery = captureQueryFromInputs({
        mode: mode || undefined,
        sort_by: sortBy || undefined
      });
    }

    async function fetchJSON(url, options) {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      return data;
    }

    function stopStatusPolling() {
      if (!state.statusPollTimer) return;
      window.clearInterval(state.statusPollTimer);
      state.statusPollTimer = null;
    }

    function startStatusPolling() {
      if (state.statusPollTimer) return;
      state.statusPollTimer = window.setInterval(async () => {
        try {
          await refreshStatus();
          if (!state.status?.running) stopStatusPolling();
        } catch (_) {
          // Ignore transient polling errors; next round retries.
        }
      }, 4000);
    }

    function renderStatus() {
      const s = state.status || {};
      if (s.interval_minutes) {
        const interval = document.getElementById("interval");
        if (interval) interval.value = String(s.interval_minutes);
      }
      const running = !!(s.running || s.paper_job?.running);
      setRunButtonState(running);
      if (running) startStatusPolling();
      else stopStatusPolling();
    }

    function renderFavoriteSummary() {
      const el = document.getElementById("favSummary");
      if (!el) return;
      const count = Number(state.paperStats?.favorite_records || 0);
      el.textContent = `${t("view_favorites")}: ${count}`;
    }

    function renderSubscriptions() {
      const root = document.getElementById("subscriptionList");
      if (!root) return;
      const items = state.subscriptions || [];
      if (!items.length) {
        root.innerHTML = `<div class="muted">${esc(t("sub_empty"))}</div>`;
        return;
      }
      root.innerHTML = items.map((item) => {
        const id = esc(item.id || "");
        const filters = item.filters || {};
        const preview = [
          filters.q ? `q:${filters.q}` : "",
          filters.category ? `category:${filters.category}` : "",
          filters.source_id ? `source:${filters.source_id}` : "",
          filters.region ? `region:${filters.region}` : "",
          filters.event_type ? `type:${filters.event_type}` : "",
        ].filter(Boolean).join(" | ") || t("sub_preview_none");
        return `
          <div class="subscription-item">
            <div class="line">
              <b>${esc(item.name || t("sub_default_name"))}</b>
              <span class="badge">${esc(item.channel || "-")}</span>
              <span class="badge">${esc(item.strategy || "incremental")}</span>
              <span class="badge">limit:${Number(item.limit || 120)}</span>
              <span class="badge">${item.enabled ? esc(t("sub_enabled")) : esc(t("sub_disabled"))}</span>
            </div>
            <div class="line">${esc(preview)}</div>
            <div class="line">${esc(t("sub_last_notified"))}: ${esc(item.last_notified_at || "-")} / ${esc(t("sub_last_match"))}: ${Number(item.last_match_count || 0)}</div>
            <div class="line">
              <button class="btn-sm sub-apply" data-id="${id}">${esc(t("sub_apply"))}</button>
              <button class="btn-sm sub-run" data-id="${id}">${esc(t("sub_run_once"))}</button>
              <button class="btn-sm sub-toggle" data-id="${id}" data-enabled="${item.enabled ? "1" : "0"}">${item.enabled ? esc(t("sub_disable")) : esc(t("sub_enable"))}</button>
              <button class="btn-sm sub-delete" data-id="${id}">${esc(t("sub_delete"))}</button>
            </div>
          </div>
        `;
      }).join("");
    }

    async function loadSubscriptions() {
      const data = await fetchJSON("/api/subscriptions");
      state.subscriptions = data.items || [];
      renderSubscriptions();
    }

    async function saveSubscription() {
      if (state.savingSubscription) return;
      state.savingSubscription = true;
      setSubscriptionSaveButtonState(true);
      const name = (document.getElementById("subscriptionName")?.value || "").trim();
      const channel = document.getElementById("subscriptionChannel")?.value || "feishu";
      const strategy = document.getElementById("subscriptionStrategy")?.value || "incremental";
      const limit = Number(document.getElementById("subscriptionLimit")?.value || 120);
      const enabled = (document.getElementById("subscriptionEnabled")?.value || "1") === "1";
      const payload = {
        name,
        channel,
        strategy,
        enabled,
        limit,
        mode: document.getElementById("viewMode")?.value || "all",
        sort_by: document.getElementById("sortMode")?.value || "score",
        sort_order: "desc",
        history: "all",
        filters: collectFilterInputs()
      };
      try {
        const data = await fetchJSON("/api/subscriptions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        state.subscriptions = data.items || [];
        renderSubscriptions();
        setMessage(t("msg_sub_saved"));
      } finally {
        state.savingSubscription = false;
        setSubscriptionSaveButtonState(false);
      }
    }

    async function runSubscriptions(id = "") {
      const data = await fetchJSON("/api/subscriptions/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(id ? { id } : {})
      });
      await loadSubscriptions();
      const parts = (data.results || []).map((r) => `${r.name}: ${r.message}`).join(" | ");
      setMessage(parts || `ok: ${data.success_count || 0}/${data.total || 0}`);
    }

    async function deleteSubscription(id) {
      await fetchJSON("/api/subscriptions/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      await loadSubscriptions();
      setMessage(t("msg_sub_deleted"));
    }

    async function toggleSubscription(id, enabledNow) {
      const item = (state.subscriptions || []).find((x) => (x.id || "") === id);
      if (!item) return;
      const payload = {
        id,
        name: item.name || "",
        channel: item.channel || "feishu",
        strategy: item.strategy || "incremental",
        limit: Number(item.limit || 120),
        enabled: !enabledNow,
        mode: item.mode || "all",
        sort_by: item.sort_by || "score",
        sort_order: item.sort_order || "desc",
        history: item.history || "all",
        filters: item.filters || {}
      };
      const data = await fetchJSON("/api/subscriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      state.subscriptions = data.items || [];
      renderSubscriptions();
      setMessage(!enabledNow ? t("msg_sub_enabled") : t("msg_sub_disabled"));
    }

    function applySubscription(id) {
      const item = (state.subscriptions || []).find((x) => (x.id || "") === id);
      if (!item) return;
      const filters = item.filters || {};
      applyFilterInputs(filters);
      const limitEl = document.getElementById("subscriptionLimit");
      if (limitEl) limitEl.value = String(Number(item.limit || 120));
      const strategyEl = document.getElementById("subscriptionStrategy");
      if (strategyEl) strategyEl.value = String(item.strategy || "incremental");
      const enabledEl = document.getElementById("subscriptionEnabled");
      if (enabledEl) enabledEl.value = item.enabled ? "1" : "0";
      if (item.mode && document.getElementById("viewMode")) document.getElementById("viewMode").value = item.mode;
      if (item.sort_by && document.getElementById("sortMode")) document.getElementById("sortMode").value = item.sort_by;
      state.appliedQuery = captureQueryFromInputs();
      refreshPapers().catch((e) => setError(e.message || String(e)));
      setMessage(t("msg_sub_applied", { name: item.name || "-" }));
    }

    function openDeepPage(paperKey) {
      const key = (paperKey || "").trim();
      if (!key) return;
      window.open(`/deep-analysis?paper_key=${encodeURIComponent(key)}`, "_blank");
    }

    function renderCards() {
      const root = document.getElementById("papers");
      const papers = state.papers || [];
      if (!papers.length) {
        root.innerHTML = `
          <div class="empty">
            <div>${esc(t("empty_title"))}</div>
            <div style="margin-top:8px;">${esc(t("empty_hint"))}</div>
          </div>
        `;
        return;
      }
      root.innerHTML = papers.map((p) => {
        const tags = (p.tags || []).map(tg => `<span class="badge">${esc(tg)}</span>`).join("");
        const aff = (p.affiliations || []).join("；");
        const kws = (p.insight?.keywords || []).join(", ");
        const action = p.action || {};
        const paperKeyRaw = (p.paper_key || "").toString();
        const paperKey = esc(paperKeyRaw);
        const pdf = p.pdf_url ? `<a href="${esc(p.pdf_url)}" target="_blank">PDF</a>` : "-";
        const doi = p.doi ? `<a href="https://doi.org/${esc(p.doi)}" target="_blank">${esc(p.doi)}</a>` : "-";
        const source = p.url ? `<a href="${esc(p.url)}" target="_blank">${esc(p.url)}</a>` : "-";
        const favText = action.favorite ? t("btn_unfav") : t("btn_fav");
        const ignoreText = action.ignored ? t("btn_unignore") : t("btn_ignore");
        const runId = p.insight?.analysis_run_id || "-";
        const deep = (p.insight && p.insight.deep_analysis) ? p.insight.deep_analysis : null;
        const hasDeep = !!(deep && Object.keys(deep).length);
        const deepRunning = !!state.deepRunningKeys[paperKeyRaw];
        return `
          <div class="card">
            <h3 class="clamp-3">${esc(p.title)}<span class="score">${esc(t("score_prefix"))} ${Number(p.recommendation_score || 0)}</span></h3>
            <div class="meta">
              <span class="clamp-2">${esc(t("label_author"))}: ${esc((p.authors || []).join(", ") || "-")}</span>
              <span class="clamp-2">${esc(t("label_aff"))}: ${esc(aff || "-")}</span>
              <span>${esc(t("label_published"))}: ${esc(p.published_at || "-")}</span>
              <span>${esc(t("label_primary_category"))}: ${esc(p.primary_category || "-")}</span>
              <span>${esc(t("label_arxiv"))}: ${esc(p.arxiv_id || "-")}</span>
              <span>${esc(t("label_batch"))}: ${esc(runId)}</span>
            </div>
            <div class="badges">${tags}</div>
            <div class="sec abstract"><b>${esc(t("label_abstract"))}</b><span>${esc(p.abstract || "-")}</span></div>
            <div class="sec"><b>${esc(t("label_pdf"))}</b>${pdf}</div>
            <div class="sec"><b>${esc(t("label_doi"))}</b>${doi}</div>
            <div class="sec"><b>${esc(t("label_source"))}</b>${source}</div>
            <hr style="border:none;border-top:1px solid var(--line);margin:10px 0;" />
            <div class="sec"><b>${esc(t("label_one_line"))}</b><span>${esc(p.insight?.one_sentence_summary || "-")}</span></div>
            <div class="sec"><b>${esc(t("label_keywords"))}</b><span>${esc(kws || "-")}</span></div>
            <div class="sec"><b>${esc(t("label_method"))}</b><span>${esc(p.insight?.method || "-")}</span></div>
            <div class="sec"><b>${esc(t("label_conclusion"))}</b><span>${esc(p.insight?.conclusion || "-")}</span></div>
            <div class="sec"><b>${esc(t("label_innovation"))}</b><span>${esc(p.insight?.innovation || "-")}</span></div>
            <div class="actions">
              <button class="btn-sm btn-open act-open-deep" data-key="${paperKey}">${hasDeep ? esc(t("btn_view_deep")) : esc(t("btn_open_deep"))}</button>
              <button class="btn-sm btn-deep act-deep" data-key="${paperKey}" ${deepRunning ? "disabled" : ""}>${deepRunning ? esc(t("btn_analyzing")) : esc(t("btn_run_deep"))}</button>
              <button class="btn-sm btn-star act-fav" data-key="${paperKey}" data-fav="${action.favorite ? "1" : "0"}">${esc(favText)}</button>
              <button class="btn-sm btn-ignore act-ignore" data-key="${paperKey}" data-ignored="${action.ignored ? "1" : "0"}">${esc(ignoreText)}</button>
            </div>
          </div>
        `;
      }).join("");
    }

    function fillSettingsForm(s) {
      const data = s || {};
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value ?? "";
      };
      set("paperPrimaryCategory", data.paper_primary_category || "");
      set("paperSubtopics", data.paper_subtopics || "");
      set("analysisLanguage", data.analysis_language || (state.lang === "en-US" ? "English" : "Chinese"));
      set("aiModel", normalizeModelName(data.ai_model || ""));
      set("aiBase", data.ai_api_base || "");
      set("aiKey", data.ai_api_key || "");
      set("paperMax", data.paper_max_papers_per_run || 20);
      set("paperMaxPerSource", data.max_per_source || 20);
      set("paperNotifyChannel", data.notify_channel || "feishu");
      set("paperNotifyLimit", data.notify_limit || 8);
      set("paperAutoEnabled", data.auto_enabled ? "1" : "0");
      set("paperAutoInterval", data.auto_interval_minutes || 60);
      set("paperAutoPushEnabled", data.auto_push_enabled ? "1" : "0");
      const q = data.query || {};
      set("paperDefaultQ", q.q || "");
      set("paperDefaultSourceId", q.source_id || "");
      set("paperDefaultRegion", q.region || "");
      set("paperDefaultEventType", q.event_type || "");
      set("feishuWebhook", data.feishu_webhook_url || "");
      set("weworkWebhook", data.wework_webhook_url || "");
      set("emailFrom", data.email_from || "");
      set("emailPassword", data.email_password || "");
      set("emailTo", data.email_to || "");
      set("emailSmtpServer", data.email_smtp_server || "smtp.qq.com");
      set("emailSmtpPort", data.email_smtp_port || "465");
    }

    async function loadSettings() {
      const settings = await fetchJSON("/api/settings");
      state.settings = settings;
      fillSettingsForm(settings);
    }

    async function saveSettings() {
      const normalizedSubtopics = normalizeSubtopicsText(document.getElementById("paperSubtopics").value);
      document.getElementById("paperSubtopics").value = normalizedSubtopics;
      const payload = {
        paper_primary_category: document.getElementById("paperPrimaryCategory").value.trim(),
        paper_subtopics: normalizedSubtopics,
        research_topic: buildResearchTopicFromForm(),
        analysis_language: currentOutputLanguage(),
        ai_model: normalizeModelName(document.getElementById("aiModel").value.trim()),
        ai_api_base: document.getElementById("aiBase").value.trim(),
        ai_api_key: document.getElementById("aiKey").value.trim(),
        paper_max_papers_per_run: Number(document.getElementById("paperMax").value || 20),
        max_per_source: Number(document.getElementById("paperMaxPerSource").value || 20),
        notify_channel: document.getElementById("paperNotifyChannel").value || "feishu",
        notify_limit: Number(document.getElementById("paperNotifyLimit").value || 8),
        auto_enabled: (document.getElementById("paperAutoEnabled").value || "0") === "1",
        auto_interval_minutes: Number(document.getElementById("paperAutoInterval").value || 60),
        auto_push_enabled: (document.getElementById("paperAutoPushEnabled").value || "0") === "1",
        query: {
          q: document.getElementById("paperDefaultQ").value.trim(),
          source_id: document.getElementById("paperDefaultSourceId").value.trim(),
          region: document.getElementById("paperDefaultRegion").value.trim(),
          event_type: document.getElementById("paperDefaultEventType").value.trim(),
          category: document.getElementById("paperPrimaryCategory").value.trim(),
        },
        feishu_webhook_url: document.getElementById("feishuWebhook").value.trim(),
        wework_webhook_url: document.getElementById("weworkWebhook").value.trim(),
        wework_msg_type: document.getElementById("weworkMsgType").value || "markdown",
        dingtalk_webhook_url: document.getElementById("dingtalkWebhook").value.trim(),
        telegram_bot_token: document.getElementById("telegramBotToken").value.trim(),
        telegram_chat_id: document.getElementById("telegramChatId").value.trim(),
        ntfy_server_url: document.getElementById("ntfyServerUrl").value.trim(),
        ntfy_topic: document.getElementById("ntfyTopic").value.trim(),
        ntfy_token: document.getElementById("ntfyToken").value.trim(),
        bark_url: document.getElementById("barkUrl").value.trim(),
        slack_webhook_url: document.getElementById("slackWebhook").value.trim(),
        email_from: document.getElementById("emailFrom").value.trim(),
        email_password: document.getElementById("emailPassword").value.trim(),
        email_to: document.getElementById("emailTo").value.trim(),
        email_smtp_server: document.getElementById("emailSmtpServer").value.trim(),
        email_smtp_port: document.getElementById("emailSmtpPort").value.trim()
      };
      const data = await fetchJSON("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (data.settings) {
        state.settings = data.settings;
        fillSettingsForm(data.settings);
      }
      setMessage(t("msg_settings_saved"));
      await Promise.all([refreshStatus(), refreshPapers()]);
    }

    async function syncAnalysisLanguageSetting() {
      try {
        await fetchJSON("/api/settings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ analysis_language: currentOutputLanguage() })
        });
      } catch (_) {
        // Best-effort sync; ignore transient errors.
      }
    }

    async function refreshStatus() {
      state.status = await fetchJSON("/api/status");
      renderStatus();
    }

    async function triggerPaperTranslation() {
      if (state.paperTranslationRunning) return;
      const outputLanguage = currentOutputLanguage();
      const keys = [];
      for (const row of state.papers || []) {
        if (!row || typeof row !== "object") continue;
        const key = String(row.paper_key || "").trim();
        if (!key || state.paperTranslatingKeys[key]) continue;
        state.paperTranslatingKeys[key] = true;
        keys.push(key);
        if (keys.length >= 12) break;
      }
      if (!keys.length) return;
      state.paperTranslationRunning = true;
      try {
        const data = await fetchJSON("/api/papers/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            keys,
            output_language: outputLanguage,
            force: false,
            max_workers: 2
          })
        });
        if (Number(data.changed || 0) > 0) {
          await refreshPapers({ skipTranslation: true });
        }
      } catch (_) {
        // Ignore translation failures here; original content remains available.
      } finally {
        state.paperTranslationRunning = false;
        for (const key of keys) {
          delete state.paperTranslatingKeys[key];
        }
      }
    }

    async function refreshPapers(options = {}) {
      if (!state.appliedQuery) state.appliedQuery = captureQueryFromInputs();
      const params = buildPaperQueryParams(state.appliedQuery);
      try {
        window.history.replaceState(null, "", `?${params.toString()}`);
      } catch (_) {}
      const data = await fetchJSON(`/api/papers?${params.toString()}`);
      state.papers = data.papers || [];
      state.paperStats = data.stats || null;
      if (state.status) state.status.db_path = data.db_path || state.status.db_path;
      renderFavoriteSummary();
      renderCards();
      if (!options.skipTranslation) {
        triggerPaperTranslation().catch(() => {});
      }
    }

    async function runNow() {
      setError("");
      setMessage("");
      try {
        await fetchJSON("/api/run-now", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ analysis_language: currentOutputLanguage() })
        });
        await refreshStatus();
        setMessage(t("msg_run_now"));
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function saveInterval() {
      setError("");
      setMessage("");
      const val = Number(document.getElementById("interval").value);
      try {
        const data = await fetchJSON("/api/schedule", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ interval_minutes: val })
        });
        if (state.status) {
          state.status.interval_minutes = data.interval_minutes ?? state.status.interval_minutes;
          state.status.cron_expr = data.cron_expr || state.status.cron_expr;
        }
        await refreshStatus();
        setMessage(t("msg_interval_updated", { n: data.interval_minutes }));
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function refreshNow() {
      setError("");
      setMessage("");
      try {
        await Promise.all([refreshStatus(), refreshPapers(), loadSubscriptions()]);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    function openPanel(panelType) {
      const settings = document.getElementById("settingsDrawer");
      const subs = document.getElementById("subscriptionDrawer");
      if (!settings || !subs) return;
      if (panelType === "settings") {
        const willOpen = !settings.classList.contains("open");
        settings.classList.toggle("open", willOpen);
        subs.classList.remove("open");
      } else if (panelType === "subscriptions") {
        const willOpen = !subs.classList.contains("open");
        subs.classList.toggle("open", willOpen);
        settings.classList.remove("open");
      } else {
        settings.classList.remove("open");
        subs.classList.remove("open");
      }
    }

    function closePanels() {
      openPanel("");
    }

    async function savePaperAction(paperKey, payload) {
      await fetchJSON("/api/paper-actions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_key: paperKey, ...payload })
      });
      await refreshPapers();
    }

    async function deepAnalyzePaper(paperKey, openAfter = false) {
      const key = (paperKey || "").trim();
      if (!key) return;
      if (state.deepRunningKeys[key]) return;
      state.deepRunningKeys[key] = true;
      setDeepButtonState(key, true);
      setError("");
      setMessage(t("msg_analyzing"));
      try {
        const data = await fetchJSON("/api/papers/deep-analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            paper_key: key,
            force: true,
            output_language: currentOutputLanguage()
          })
        });
        await refreshPapers();
        setMessage(data.message || t("msg_analyzed"));
        if (openAfter) openDeepPage(key);
      } finally {
        delete state.deepRunningKeys[key];
        setDeepButtonState(key, false);
      }
    }

    async function testNotify() {
      setError("");
      setMessage("");
      const channel = document.getElementById("testChannel")?.value || "feishu";
      try {
        const data = await fetchJSON("/api/notify-test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channel })
        });
        setMessage(`${channel}: ${data.message || "ok"}`);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    function clearFilters() {
      applyFilterInputs({ q: "", category: "", source_id: "", region: "", event_type: "" });
    }

    document.getElementById("runNow")?.addEventListener("click", runNow);
    document.getElementById("saveInterval")?.addEventListener("click", saveInterval);
    document.getElementById("refreshNow")?.addEventListener("click", refreshNow);
    document.getElementById("openSettingsPanel")?.addEventListener("click", () => openPanel("settings"));
    document.getElementById("openSubscriptionPanel")?.addEventListener("click", () => openPanel("subscriptions"));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closePanels();
    });
    document.getElementById("applyFilters").addEventListener("click", async () => { await applyFiltersAndRefresh(true); });
    document.getElementById("clearFilters").addEventListener("click", async () => {
      clearFilters();
      await applyFiltersAndRefresh(true);
      setMessage(t("msg_filter_cleared"));
    });
    document.getElementById("saveSettings").addEventListener("click", async () => {
      setError("");
      try { await saveSettings(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("reloadSettings").addEventListener("click", async () => {
      setError("");
      try {
        await loadSettings();
        setMessage(t("msg_settings_reloaded"));
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("testNotify").addEventListener("click", testNotify);
    document.getElementById("saveSubscription").addEventListener("click", async () => {
      setError("");
      try { await saveSubscription(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("runSubscriptions").addEventListener("click", async () => {
      setError("");
      try { await runSubscriptions(""); } catch (e) { setError(e.message || String(e)); }
    });

    document.getElementById("searchQ").addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        applyFiltersAndRefresh(true).catch((e) => setError(e.message || String(e)));
      }
    });

    document.getElementById("papers").addEventListener("click", async (event) => {
      const target = event.target;
      if (!target || !(target instanceof HTMLElement)) return;
      const btn = target.closest("button");
      if (!btn) return;
      const paperKey = btn.getAttribute("data-key");
      if (!paperKey) return;
      try {
        if (btn.classList.contains("act-open-deep")) {
          openDeepPage(paperKey);
        } else if (btn.classList.contains("act-deep")) {
          await deepAnalyzePaper(paperKey, true);
        } else if (btn.classList.contains("act-fav")) {
          const current = btn.getAttribute("data-fav") === "1";
          await savePaperAction(paperKey, { favorite: !current });
          setMessage(!current ? t("msg_added_fav") : t("msg_removed_fav"));
        } else if (btn.classList.contains("act-ignore")) {
          const current = btn.getAttribute("data-ignored") === "1";
          await savePaperAction(paperKey, { ignored: !current });
          setMessage(!current ? t("msg_added_ignore") : t("msg_removed_ignore"));
        }
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("subscriptionList").addEventListener("click", async (event) => {
      const target = event.target;
      if (!target || !(target instanceof HTMLElement)) return;
      const btn = target.closest("button");
      if (!btn) return;
      const subId = btn.getAttribute("data-id");
      if (!subId) return;
      try {
        if (btn.classList.contains("sub-apply")) {
          applySubscription(subId);
        } else if (btn.classList.contains("sub-run")) {
          await runSubscriptions(subId);
        } else if (btn.classList.contains("sub-delete")) {
          await deleteSubscription(subId);
        } else if (btn.classList.contains("sub-toggle")) {
          const enabledNow = btn.getAttribute("data-enabled") === "1";
          await toggleSubscription(subId, enabledNow);
        }
      } catch (e) {
        setError(e.message || String(e));
      }
    });

    document.getElementById("langToggle").addEventListener("click", async () => {
      state.lang = state.lang === "zh-CN" ? "en-US" : "zh-CN";
      localStorage.setItem("panel_lang", state.lang);
      applyI18n();
      syncAnalysisLanguageSetting();
      try {
        await refreshPapers();
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("themeToggle").addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      localStorage.setItem("panel_theme", state.theme);
      applyTheme();
      renderCards();
      renderSubscriptions();
    });
    document.getElementById("toggleAiKey").addEventListener("click", () => {
      state.aiKeyVisible = !state.aiKeyVisible;
      updateAiKeyToggle();
    });
    document.getElementById("viewMode").addEventListener("change", async () => { await applyFiltersAndRefresh(false); });
    document.getElementById("sortMode").addEventListener("change", async () => { await applyFiltersAndRefresh(false); });
    window.addEventListener("beforeunload", () => stopStatusPolling());

    initPageShellMotion();

    async function boot() {
      applyTheme();
      applyI18n();
      syncFiltersFromUrl();
      await Promise.all([loadSettings(), refreshNow()]);
      await syncAnalysisLanguageSetting();
    }

    boot().catch((e) => setError(e.message || String(e)));
  </script>
</body>
</html>
"""


def build_deep_analysis_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PaperScope Deep Analysis</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --bg-grad-1: rgba(56, 189, 248, 0.15);
      --bg-grad-2: rgba(14, 165, 233, 0.10);
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --line: #e5e7eb;
      --line-strong: #d6deea;
      --primary: #0f766e;
      --danger: #b91c1c;
      --panel-shadow: 0 12px 30px rgba(15, 23, 42, 0.10);
      --card-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      --group-bg: rgba(148, 163, 184, 0.08);
    }
    :root[data-theme="dark"] {
      --bg: #06080d;
      --bg-grad-1: rgba(56, 189, 248, 0.18);
      --bg-grad-2: rgba(6, 182, 212, 0.12);
      --card: #0d1118;
      --text: #e7edf7;
      --muted: #9aa8be;
      --line: #1d2633;
      --line-strong: #304057;
      --primary: #14b8a6;
      --danger: #f87171;
      --panel-shadow: 0 18px 42px rgba(0, 0, 0, 0.48);
      --card-shadow: 0 12px 28px rgba(0, 0, 0, 0.38);
      --group-bg: rgba(148, 163, 184, 0.06);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(1200px 700px at 6% -10%, var(--bg-grad-1), transparent 56%),
        radial-gradient(980px 650px at 95% -15%, var(--bg-grad-2), transparent 50%),
        var(--bg);
      color: var(--text);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      min-height: 100vh;
      transition: background-color 0.35s ease, color 0.2s ease;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 20px; }
    .top, .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      box-shadow: var(--card-shadow);
    }
    .top {
      position: sticky;
      top: 10px;
      z-index: 5;
      backdrop-filter: blur(10px);
      box-shadow: var(--panel-shadow);
    }
    .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    button, select {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px 12px;
      background: var(--card);
      color: var(--text);
      cursor: pointer;
      transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.18s ease, box-shadow 0.2s ease;
    }
    button:hover, select:hover { border-color: var(--line-strong); }
    button:active { transform: translateY(1px); }
    button.primary {
      border-color: var(--primary);
      background: var(--primary);
      color: #fff;
    }
    .status { margin-top: 10px; color: var(--muted); font-size: 13px; white-space: pre-wrap; }
    .error { color: var(--danger); }
    .main { margin-top: 16px; display: grid; gap: 12px; }
    .title { font-size: 26px; font-weight: 700; margin: 0; line-height: 1.35; }
    .meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 12px;
      font-size: 14px;
      color: var(--muted);
      margin-top: 10px;
    }
    .section { margin-top: 8px; animation: riseIn 0.42s ease both; }
    .section h3 { margin: 0 0 8px; font-size: 17px; }
    .content {
      line-height: 1.7;
      font-size: 15px;
      white-space: normal;
      word-break: break-word;
    }
    .content p { margin: 0 0 10px; }
    .content ul, .content ol { margin: 6px 0 8px 20px; padding: 0; }
    .content li { margin: 4px 0; }
    .group {
      margin-top: 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--group-bg);
      overflow: hidden;
      animation: riseIn 0.42s ease both;
    }
    .group summary {
      cursor: pointer;
      list-style: none;
      font-size: 16px;
      font-weight: 600;
      padding: 12px 14px;
      border-bottom: 1px solid transparent;
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    .group summary::-webkit-details-marker { display: none; }
    .group[open] summary {
      border-bottom-color: var(--line);
      background: rgba(148, 163, 184, 0.08);
    }
    .group-body { padding: 12px 14px; }
    .subsec { margin-bottom: 12px; }
    .subsec:last-child { margin-bottom: 0; }
    .subsec b {
      display: block;
      margin-bottom: 6px;
      font-size: 14px;
      color: var(--text);
    }
    .list { margin: 0; padding-left: 18px; line-height: 1.7; }
    .muted { color: var(--muted); }
    .footnote {
      margin-top: 12px;
      border-top: 1px dashed var(--line);
      padding-top: 10px;
      font-size: 13px;
    }
    a { color: #0284c7; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @keyframes riseIn {
      from { opacity: 0; transform: translateY(8px) scale(0.995); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; transition: none !important; }
    }
    @media (max-width: 860px) {
      .meta { grid-template-columns: 1fr; }
    }
  </style>
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
        displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]]
      },
      svg: { fontCache: "global" }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="row">
        <a href="/" id="backLink">← Back</a>
        <button id="runDeep" class="primary">Run Deep Analysis</button>
        <label>Language
          <select id="langMode">
            <option value="zh-CN">中文</option>
            <option value="en-US">English</option>
          </select>
        </label>
        <label>Theme
          <select id="themeMode">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>
      </div>
      <div id="msg" class="status"></div>
      <div id="err" class="status error"></div>
    </div>
    <div id="main" class="main"></div>
  </div>

  <script>
    const I18N = {
      "zh-CN": {
        back: "← 返回面板",
        run: "一键深入分析",
        loading: "加载中...",
        not_found: "未找到论文详情",
        need_key: "缺少 paper_key 参数",
        running: "正在执行深入分析，请稍候...",
        done: "深入分析完成",
        title_meta: "论文元数据",
        authors: "作者",
        affiliations: "作者单位",
        published: "发布时间",
        category: "主分类",
        tags: "标签",
        arxiv: "arXiv ID",
        doi: "DOI",
        score: "推荐阅读分",
        source: "原文",
        pdf: "PDF",
        abstract: "摘要",
        deep_title: "深入分析",
        one_line: "核心结论摘要（非一句话）",
        sec_exec: "执行摘要",
        sec_why: "Why：问题与动机",
        sec_what: "What：挑战与核心思想",
        sec_how: "How：方法与机制",
        sec_eval: "So What：实验与证据",
        sec_risk: "影响、边界与风险",
        sec_next: "后续研究建议",
        background: "领域背景与现状",
        motivation: "研究动机与价值（Why）",
        problem_constraints: "问题定义与硬约束",
        running_example: "Running Example（场景+失败案例+影响）",
        problem: "研究问题与背景",
        technical_challenges: "技术挑战（What）",
        core_idea: "核心思想",
        method_overview: "方法概述（How）",
        method_details: "方法细节",
        method: "方法细节与关键机制",
        formula: "关键公式（LaTeX）",
        contributions: "贡献总结",
        exp: "实验设计与评测",
        evidence: "结果与证据",
        main_results_expectation: "主实验验证目标",
        ablation_plan: "消融实验建议",
        in_depth_analysis_plan: "深度分析建议",
        insight_hypotheses: "效果原因解释",
        strengths: "优势",
        weaknesses: "不足与风险",
        limits: "局限与失败案例",
        reproducibility: "可复现性",
        confidence: "结论可信度依据",
        practical: "应用价值",
        followups: "后续实验建议",
        questions: "延伸阅读问题",
        open_problems: "仍待解决问题",
        so_what_summary: "So What 总结",
        analyzed_at: "深入分析时间",
        workflow: "流程模式",
        framework: "分析框架",
        input_source: "输入来源",
        input_chars: "输入长度(字符)",
        no_deep: "尚未生成深入分析，点击上方按钮开始。"
      },
      "en-US": {
        back: "← Back to Panel",
        run: "Run Deep Analysis",
        loading: "Loading...",
        not_found: "Paper detail not found",
        need_key: "paper_key is required",
        running: "Deep analysis is running...",
        done: "Deep analysis completed",
        title_meta: "Paper Metadata",
        authors: "Authors",
        affiliations: "Affiliations",
        published: "Published",
        category: "Primary Category",
        tags: "Tags",
        arxiv: "arXiv ID",
        doi: "DOI",
        score: "Recommendation Score",
        source: "Source",
        pdf: "PDF",
        abstract: "Abstract",
        deep_title: "Deep Analysis",
        one_line: "Executive Summary (Not One Sentence)",
        sec_exec: "Executive Summary",
        sec_why: "Why: Problem & Motivation",
        sec_what: "What: Challenges & Core Idea",
        sec_how: "How: Method & Mechanism",
        sec_eval: "So What: Evidence & Validation",
        sec_risk: "Impact, Limits & Risks",
        sec_next: "Next-step Suggestions",
        background: "Background & Field Context",
        motivation: "Motivation & Why",
        problem_constraints: "Problem Definition & Constraints",
        running_example: "Running Example",
        problem: "Problem & Context",
        technical_challenges: "Technical Challenges",
        core_idea: "Core Idea",
        method_overview: "Method Overview",
        method_details: "Method Details",
        method: "Method Deep Dive",
        formula: "Key Formulae (LaTeX)",
        contributions: "Contributions",
        exp: "Experimental Design",
        evidence: "Results & Evidence",
        main_results_expectation: "Main Results Expectation",
        ablation_plan: "Ablation Plan",
        in_depth_analysis_plan: "In-depth Analysis Plan",
        insight_hypotheses: "Why It Works",
        strengths: "Strengths",
        weaknesses: "Weaknesses",
        limits: "Limitations & Failure Cases",
        reproducibility: "Reproducibility",
        confidence: "Confidence Rationale",
        practical: "Practical Value",
        followups: "Recommended Follow-ups",
        questions: "Reading Questions",
        open_problems: "Open Problems",
        so_what_summary: "So What Summary",
        analyzed_at: "Analyzed At",
        workflow: "Workflow Mode",
        framework: "Framework",
        input_source: "Input Source",
        input_chars: "Input Size(chars)",
        no_deep: "No deep analysis yet. Click the button above to start."
      }
    };

    const state = {
      lang: localStorage.getItem("panel_lang") || "zh-CN",
      theme: localStorage.getItem("panel_theme") || "light",
      paperKey: "",
      paper: null
    };

    function t(key) {
      const tab = I18N[state.lang] || I18N["zh-CN"];
      return tab[key] || key;
    }

    function esc(v) {
      return (v ?? "").toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function textBlock(v) {
      return esc(v || "-").replace(/\\n/g, "<br />");
    }

    function richBlock(v) {
      const raw = (v || "").toString().trim();
      if (!raw) return "<p>-</p>";
      const lines = raw.split(/\\r?\\n/);
      const chunks = [];
      let listBuf = [];
      let orderedBuf = [];

      const flushList = () => {
        if (listBuf.length) {
          chunks.push(`<ul>${listBuf.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`);
          listBuf = [];
        }
        if (orderedBuf.length) {
          chunks.push(`<ol>${orderedBuf.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>`);
          orderedBuf = [];
        }
      };

      for (const lineRaw of lines) {
        const line = lineRaw.trim();
        if (!line) {
          flushList();
          continue;
        }
        const m1 = line.match(/^[-*•]\\s+(.+)$/);
        if (m1) {
          listBuf.push(m1[1]);
          continue;
        }
        const m2 = line.match(/^\\d+[\\.|、]\\s+(.+)$/);
        if (m2) {
          orderedBuf.push(m2[1]);
          continue;
        }
        flushList();
        chunks.push(`<p>${esc(line)}</p>`);
      }
      flushList();
      return chunks.join("") || "<p>-</p>";
    }

    function nonEmptyText(v) {
      return (v ?? "").toString().trim();
    }

    function pickFirstText(...values) {
      for (const item of values) {
        const text = nonEmptyText(item);
        if (text) return text;
      }
      return "";
    }

    function mergeTextBlocks(values) {
      return (values || []).map((v) => nonEmptyText(v)).filter(Boolean).join("\\n\\n");
    }

    function normalizeTextList(value) {
      if (Array.isArray(value)) return value.map((x) => nonEmptyText(x)).filter(Boolean);
      const text = nonEmptyText(value);
      return text ? [text] : [];
    }

    function renderList(items) {
      if (!items || !items.length) return "<div>-</div>";
      return `<ul class="list">${items.map((x) => `<li>${textBlock(x)}</li>`).join("")}</ul>`;
    }

    function setMsg(v) { document.getElementById("msg").textContent = v || ""; }
    function setErr(v) { document.getElementById("err").textContent = v || ""; }

    async function fetchJSON(url, options) {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      return data;
    }

    function applyTheme() {
      document.documentElement.setAttribute("data-theme", state.theme === "dark" ? "dark" : "light");
      document.getElementById("themeMode").value = state.theme;
    }

    function applyLangUI() {
      document.getElementById("langMode").value = state.lang;
      document.getElementById("backLink").textContent = t("back");
      document.getElementById("runDeep").textContent = t("run");
      render();
    }

    function render() {
      const root = document.getElementById("main");
      if (!state.paper) {
        root.innerHTML = `<div class="card muted">${esc(t("loading"))}</div>`;
        return;
      }
      const p = state.paper;
      const deep = (p.insight && p.insight.deep_analysis) ? p.insight.deep_analysis : null;
      const tags = (p.tags || []).map((x) => esc(x)).join(", ") || "-";
      const authors = (p.authors || []).map((x) => esc(x)).join(", ") || "-";
      const aff = (p.affiliations || []).map((x) => esc(x)).join("；") || "-";
      const formulaList = normalizeTextList(deep?.key_formulae);
      const technicalChallenges = normalizeTextList(deep?.technical_challenges);
      const contributions = normalizeTextList(deep?.contribution_claims);
      const followups = normalizeTextList(deep?.recommended_followups);
      const questions = normalizeTextList(deep?.reading_questions);
      const doi = p.doi ? `<a target="_blank" href="https://doi.org/${esc(p.doi)}">${esc(p.doi)}</a>` : "-";
      const source = p.url ? `<a target="_blank" href="${esc(p.url)}">${esc(p.url)}</a>` : "-";
      const pdf = p.pdf_url ? `<a target="_blank" href="${esc(p.pdf_url)}">${esc(p.pdf_url)}</a>` : "-";
      let executiveSummary = pickFirstText(
        deep?.executive_summary,
        deep?.one_line_verdict,
        deep?.so_what_summary
      );
      let problemLandscape = pickFirstText(
        deep?.problem_landscape,
        mergeTextBlocks([
          deep?.background_and_field_context,
          deep?.motivation_and_why_now,
          deep?.problem_definition_and_constraints,
          deep?.running_example,
          deep?.problem_and_context
        ])
      );
      let methodMechanism = pickFirstText(
        deep?.method_and_mechanism,
        mergeTextBlocks([
          deep?.method_overview,
          deep?.method_details,
          deep?.method_deep_dive,
          deep?.core_idea
        ])
      );
      let evidenceTrust = pickFirstText(
        deep?.evidence_and_trustworthiness,
        mergeTextBlocks([
          deep?.experimental_design,
          deep?.results_and_evidence,
          deep?.main_results_expectation,
          deep?.ablation_plan,
          deep?.in_depth_analysis_plan
        ])
      );
      let impactRoadmap = pickFirstText(
        deep?.impact_and_roadmap,
        mergeTextBlocks([
          deep?.practical_value,
          deep?.strengths,
          deep?.weaknesses,
          deep?.limitations_and_failure_cases,
          deep?.so_what_summary
        ])
      );
      let confidenceRationale = pickFirstText(
        deep?.confidence_rationale,
        deep?.insight_hypotheses,
        deep?.reproducibility
      );
      let openProblems = pickFirstText(deep?.open_problems, "");
      const rawResponseFallback = pickFirstText(deep?.raw_response, "");
      const hasStructuredContent = (
        nonEmptyText(executiveSummary) ||
        nonEmptyText(problemLandscape) ||
        nonEmptyText(methodMechanism) ||
        nonEmptyText(evidenceTrust) ||
        nonEmptyText(impactRoadmap) ||
        nonEmptyText(confidenceRationale) ||
        nonEmptyText(openProblems) ||
        formulaList.length ||
        technicalChallenges.length ||
        contributions.length ||
        followups.length ||
        questions.length
      );
      if (!hasStructuredContent && rawResponseFallback) {
        executiveSummary = rawResponseFallback;
      }

      const deepHtml = deep ? `
        <div class="card section">
          <h3>${esc(t("deep_title"))}</h3>
          <details class="group" open>
            <summary>${esc(t("sec_exec"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("one_line"))}</b>${richBlock(executiveSummary)}</div>
            </div>
          </details>
          <details class="group" open>
            <summary>${esc(t("sec_why"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("problem"))}</b>${richBlock(problemLandscape)}</div>
              <div class="subsec content"><b>${esc(t("technical_challenges"))}</b>${renderList(technicalChallenges)}</div>
            </div>
          </details>
          <details class="group" open>
            <summary>${esc(t("sec_how"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("method"))}</b>${richBlock(methodMechanism)}</div>
              <div class="subsec content"><b>${esc(t("contributions"))}</b>${renderList(contributions)}</div>
              <div class="subsec content"><b>${esc(t("formula"))}</b>${renderList(formulaList)}</div>
            </div>
          </details>
          <details class="group" open>
            <summary>${esc(t("sec_eval"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("evidence"))}</b>${richBlock(evidenceTrust)}</div>
              <div class="subsec content"><b>${esc(t("confidence"))}</b>${richBlock(confidenceRationale)}</div>
            </div>
          </details>
          <details class="group" open>
            <summary>${esc(t("sec_risk"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("practical"))}</b>${richBlock(impactRoadmap)}</div>
              <div class="subsec content"><b>${esc(t("open_problems"))}</b>${richBlock(openProblems)}</div>
            </div>
          </details>
          <details class="group" open>
            <summary>${esc(t("sec_next"))}</summary>
            <div class="group-body">
              <div class="subsec content"><b>${esc(t("followups"))}</b>${renderList(followups)}</div>
              <div class="subsec content"><b>${esc(t("questions"))}</b>${renderList(questions)}</div>
            </div>
          </details>
          <div class="content footnote muted">
            ${esc(t("input_source"))}: ${esc(deep.input_context_source || "-")} |
            ${esc(t("input_chars"))}: ${esc(deep.input_context_chars || "-")} |
            ${esc(t("analyzed_at"))}: ${esc(deep.analyzed_at || "-")} |
            ${esc(t("workflow"))}: ${esc(deep.workflow_mode || "-")} |
            ${esc(t("framework"))}: ${esc(deep.analysis_framework_version || "legacy")}
          </div>
        </div>
      ` : `<div class="card muted">${esc(t("no_deep"))}</div>`;

      root.innerHTML = `
        <div class="card">
          <h1 class="title">${esc(p.title || "-")}</h1>
          <div class="meta">
            <div><b>${esc(t("authors"))}</b>: ${authors}</div>
            <div><b>${esc(t("affiliations"))}</b>: ${aff}</div>
            <div><b>${esc(t("published"))}</b>: ${esc(p.published_at || "-")}</div>
            <div><b>${esc(t("category"))}</b>: ${esc(p.primary_category || "-")}</div>
            <div><b>${esc(t("tags"))}</b>: ${tags}</div>
            <div><b>${esc(t("arxiv"))}</b>: ${esc(p.arxiv_id || "-")}</div>
            <div><b>${esc(t("doi"))}</b>: ${doi}</div>
            <div><b>${esc(t("score"))}</b>: ${esc(p.recommendation_score || 0)}</div>
            <div><b>${esc(t("source"))}</b>: ${source}</div>
            <div><b>${esc(t("pdf"))}</b>: ${pdf}</div>
          </div>
          <div class="section">
            <h3>${esc(t("abstract"))}</h3>
            <div class="content">${textBlock(p.abstract || "-")}</div>
          </div>
        </div>
        ${deepHtml}
      `;
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([root]).catch(() => {});
      }
    }

    async function loadPaper() {
      setErr("");
      if (!state.paperKey) {
        setErr(t("need_key"));
        return;
      }
      setMsg(t("loading"));
      const params = new URLSearchParams();
      params.set("paper_key", state.paperKey);
      params.set("output_language", state.lang === "en-US" ? "English" : "Chinese");
      const data = await fetchJSON(`/api/paper-detail?${params.toString()}`);
      state.paper = data.paper || null;
      if (!state.paper) setErr(t("not_found"));
      setMsg("");
      render();
    }

    async function runDeepNow() {
      if (!state.paperKey) return;
      setErr("");
      setMsg(t("running"));
      try {
        await fetchJSON("/api/papers/deep-analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            paper_key: state.paperKey,
            force: true,
            output_language: state.lang === "en-US" ? "English" : "Chinese"
          })
        });
        setMsg(t("done"));
        await loadPaper();
      } catch (e) {
        setErr(e.message || String(e));
      }
    }

    document.getElementById("runDeep").addEventListener("click", runDeepNow);
    document.getElementById("langMode").addEventListener("change", async (e) => {
      state.lang = e.target.value || "zh-CN";
      localStorage.setItem("panel_lang", state.lang);
      fetchJSON("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_language: state.lang === "en-US" ? "English" : "Chinese" })
      }).catch(() => {});
      applyLangUI();
      try {
        await loadPaper();
      } catch (err) {
        setErr(err.message || String(err));
      }
    });
    document.getElementById("themeMode").addEventListener("change", (e) => {
      state.theme = e.target.value || "light";
      localStorage.setItem("panel_theme", state.theme);
      applyTheme();
    });

    (async function boot() {
      const params = new URLSearchParams(window.location.search || "");
      state.paperKey = (params.get("paper_key") || "").trim();
      applyTheme();
      applyLangUI();
      await loadPaper();
    })().catch((e) => setErr(e.message || String(e)));
  </script>
</body>
</html>
"""


def build_home_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OmniHawk AI</title>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Orbitron:wght@700;800;900&family=Rajdhani:wght@500;600;700&display=swap");
    :root {
      --bg: #121212;
      --surface: #181818;
      --surface-2: #1f1f1f;
      --surface-3: #252525;
      --text: #ffffff;
      --muted: #b3b3b3;
      --line: #343434;
      --line-strong: #4d4d4d;
      --accent: #1ed760;
      --accent-strong: #1db954;
      --brand-core: #1ed760;
      --brand-glow: rgba(30, 215, 96, 0.35);
      --shadow-heavy: rgba(0, 0, 0, 0.5) 0 8px 24px;
      --shadow-mid: rgba(0, 0, 0, 0.3) 0 8px 8px;
      --radius-pill: 10px;
      --radius-card: 10px;
    }
    :root[data-theme="light"] {
      --bg: #f6f7f8;
      --surface: #ffffff;
      --surface-2: #f2f3f5;
      --surface-3: #eceef1;
      --text: #101010;
      --muted: #5f6165;
      --line: #d8d9dc;
      --line-strong: #bec0c5;
      --accent: #1db954;
      --accent-strong: #15803d;
      --brand-core: #15803d;
      --brand-glow: rgba(21, 128, 61, 0.22);
      --shadow-heavy: rgba(0, 0, 0, 0.12) 0 8px 24px;
      --shadow-mid: rgba(0, 0, 0, 0.08) 0 8px 8px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Circular Std", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      min-height: 100vh;
      opacity: 0;
      transform: translateY(16px);
      transition: opacity 0.28s ease, transform 0.28s ease, background-color 0.22s ease, color 0.2s ease;
    }
    body.page-ready {
      opacity: 1;
      transform: translateY(0);
    }
    body.page-leaving {
      opacity: 0;
      transform: translateX(24px);
      pointer-events: none;
    }
    .wrap {
      width: min(1560px, 100%);
      margin: 0 auto;
      padding: 0 18px 28px;
    }
    .shell {
      background: transparent;
      border-radius: 0;
      box-shadow: none;
      border: none;
      overflow: visible;
    }
    .head {
      padding: 18px 0 14px;
      border-bottom: none;
      background: linear-gradient(180deg, rgba(255,255,255,0.02), transparent 70%);
      display: flex;
      justify-content: center;
      gap: 14px;
      align-items: center;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(6px);
    }
    .brand-wrap {
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 10px;
      align-items: center;
      text-align: center;
      padding: 8px 0 6px;
      overflow: visible;
    }
    .brand {
      margin: 0;
      font-size: clamp(34px, 5.2vw, 58px);
      line-height: 1.22;
      letter-spacing: 1.6px;
      text-transform: uppercase;
      font-weight: 400;
      font-family: "Press Start 2P", "Silkscreen", "Rajdhani", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--brand-core);
      text-shadow:
        1px 0 0 rgba(0, 0, 0, 0.45),
        0 1px 0 rgba(0, 0, 0, 0.45),
        2px 2px 0 rgba(0, 0, 0, 0.28),
        0 0 14px var(--brand-glow);
      padding: 3px 8px 6px;
      white-space: nowrap;
    }
    :root[data-theme="light"] .brand {
      color: #0f7a3a;
      text-shadow:
        1px 0 0 rgba(2, 6, 23, 0.2),
        0 1px 0 rgba(2, 6, 23, 0.2),
        2px 2px 0 rgba(21, 128, 61, 0.24),
        0 0 8px rgba(21, 128, 61, 0.16);
    }
    .brand-sub {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      letter-spacing: 0.3px;
    }
    .tabs {
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
      justify-content: center;
    }
    .tab {
      border: none;
      background: transparent;
      color: var(--muted);
      text-decoration: none;
      padding: 7px 0;
      border-radius: 0;
      font-size: 15px;
      text-transform: none;
      letter-spacing: 0.2px;
      font-weight: 650;
      transition: color 0.18s ease;
      position: relative;
    }
    .tab:hover {
      color: var(--text);
    }
    .tab.active {
      color: var(--text);
    }
    .tab.active::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: -2px;
      height: 2px;
      border-radius: 2px;
      background: var(--accent);
    }
    .ctrl {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: center;
      width: 100%;
    }
    .icon-btn {
      border: none;
      background: transparent;
      color: var(--text);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 13px;
      text-transform: none;
      letter-spacing: 0.2px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }
    .icon-btn:hover {
      background: rgba(255, 255, 255, 0.06);
    }
    .hero {
      padding: 26px 0 18px;
      background:
        radial-gradient(1200px 360px at 100% 0%, rgba(30, 215, 96, 0.2), transparent 65%),
        radial-gradient(900px 320px at 0% 0%, rgba(255,255,255,0.04), transparent 70%);
      text-align: center;
    }
    .kicker {
      margin: 0;
      color: var(--accent);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1.6px;
      font-weight: 700;
    }
    .hero h2 {
      margin: 10px 0 0;
      font-size: 44px;
      line-height: 1.06;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .hero p {
      margin: 14px 0 0;
      max-width: 980px;
      font-size: 17px;
      line-height: 1.65;
      color: var(--muted);
      margin-left: auto;
      margin-right: auto;
    }
    .hero-actions {
      margin-top: 18px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: center;
    }
    .cta {
      text-decoration: none;
      border-radius: 10px;
      padding: 10px 16px;
      text-transform: none;
      letter-spacing: 0.2px;
      font-size: 14px;
      font-weight: 700;
      border: none;
      color: var(--text);
      background: var(--surface-2);
    }
    .cta.primary {
      background: var(--accent);
      color: #111;
    }
    .cta:hover {
      background: var(--surface-3);
    }
    .cta.primary:hover {
      background: var(--accent-strong);
    }
    .content {
      padding: 14px 0 20px;
      display: grid;
      gap: 12px;
    }
    .section {
      background: var(--surface-2);
      border-radius: var(--radius-card);
      padding: 14px 16px;
      box-shadow: var(--shadow-mid);
    }
    .section h3 {
      margin: 0;
      font-size: 17px;
      text-transform: uppercase;
      letter-spacing: 0.9px;
      line-height: 1.24;
    }
    .section p {
      margin: 9px 0 0;
      color: var(--muted);
      line-height: 1.65;
      font-size: 14px;
    }
    .flow {
      display: grid;
      grid-template-columns: 172px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 10px 0;
      box-shadow: inset 0 1px 0 var(--line);
    }
    .flow:first-of-type {
      box-shadow: none;
      padding-top: 2px;
    }
    .flow-code {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--accent);
      font-weight: 700;
    }
    .flow-desc {
      font-size: 14px;
      color: var(--muted);
      line-height: 1.5;
    }
    .flow-go {
      text-decoration: none;
      color: var(--text);
      background: var(--surface-3);
      border-radius: 9px;
      padding: 7px 12px;
      font-size: 13px;
      text-transform: none;
      letter-spacing: 0.2px;
      font-weight: 700;
    }
    .flow-go:hover {
      color: var(--accent);
    }
    .stat-row {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .stat {
      padding: 12px;
      border-radius: 10px;
      background: var(--surface-3);
    }
    .stat b {
      display: block;
      font-size: 20px;
      line-height: 1.1;
      color: var(--accent);
      letter-spacing: 0.4px;
    }
    .stat span {
      display: block;
      margin-top: 6px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1.1px;
      color: var(--muted);
    }
    @media (max-width: 1080px) {
      .hero h2 { font-size: 34px; }
      .stat-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .flow {
        grid-template-columns: 1fr;
        gap: 6px;
        align-items: flex-start;
      }
      .flow-go { margin-top: 2px; }
    }
    @media (max-width: 780px) {
      .wrap { padding: 8px; }
      .head { padding: 14px 0 12px; }
      .hero { padding: 18px 14px 14px; }
      .hero h2 { font-size: 28px; }
      .hero p { font-size: 15px; }
      .content { padding: 10px 14px 14px; }
      .stat-row { grid-template-columns: 1fr; }
      .brand { font-size: 30px; }
    }
    @media (prefers-reduced-motion: reduce) {
      body { transition: none; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="shell">
      <div class="head">
        <div class="brand-wrap">
          <p class="brand" data-i18n="site_title">OmniHawk AI</p>
          <p class="brand-sub" data-i18n="site_sub">Hawk-level sensing for the full AI ecosystem.</p>
          <div class="tabs">
            <a class="tab active" href="/" data-i18n="tab_home">Home</a>
            <a class="tab" href="/panel" data-i18n="tab_papers">Papers</a>
            <a class="tab" href="/progress" data-i18n="tab_progress">AI Frontier</a>
            <a class="tab" href="/finance" data-i18n="tab_finance">AI Finance</a>
            <a class="tab" href="/reports" data-i18n="tab_reports">Industry Reports</a>
            <a class="tab" href="/policy-safety" data-i18n="tab_policy_safety">Policy & Safety</a>
            <a class="tab" href="/oss" data-i18n="tab_oss">OSS Signals</a>
          </div>
        </div>
        <div class="ctrl">
          <button id="langToggle" class="icon-btn" type="button" title="Language">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 5h12M9 3v2M7 5a17 17 0 0 0 5 10M9 5a17 17 0 0 1-5 10"></path>
              <path d="M14 13h7M17.5 10v3M16 21l1.5-3 1.5 3"></path>
            </svg>
            <span id="langShort">ZH</span>
          </button>
          <button id="themeToggle" class="icon-btn" type="button" title="Theme">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 1 0 9.8 9.8Z"></path>
            </svg>
            <span id="themeShort">Dark</span>
          </button>
        </div>
      </div>

      <section class="hero">
        <p class="kicker" data-i18n="hero_kicker">All-in AI Intelligence Platform</p>
        <h2 data-i18n="hero_title">From weak signals to strategic decisions.</h2>
        <p data-i18n="hero_sub">
          OmniHawk AI scans global papers, official launches, market disclosures, policy risk, and open-source developer momentum in one continuous intelligence loop.
        </p>
        <div class="hero-actions">
          <a class="cta primary" href="/progress" data-i18n="hero_cta_primary">Start Monitoring</a>
          <a class="cta" href="/panel" data-i18n="hero_cta_secondary">Explore Paper Radar</a>
        </div>
      </section>

      <div class="content">
        <section class="section">
          <h3 data-i18n="overview_title">Project Overview</h3>
          <p data-i18n="overview_desc">
            Built for teams that need complete AI situational awareness: not just model news, but the full chain from research signal to market impact and policy risk.
          </p>
          <div class="stat-row">
            <div class="stat"><b>6</b><span data-i18n="stat_1">Independent Radar Pages</span></div>
            <div class="stat"><b>24/7</b><span data-i18n="stat_2">Continuous Source Tracking</span></div>
            <div class="stat"><b>90D</b><span data-i18n="stat_3">Freshness-first Filtering</span></div>
            <div class="stat"><b>CN/EN</b><span data-i18n="stat_4">Bilingual Delivery</span></div>
          </div>
        </section>

        <section class="section">
          <h3 data-i18n="modules_title">Radar Modules</h3>
          <div class="flow">
            <div class="flow-code">01 / Papers</div>
            <div class="flow-desc" data-i18n="m1">High-value papers, deep-analysis-ready summaries, and personalized subscriptions.</div>
            <a class="flow-go" href="/panel" data-i18n="enter">Enter</a>
          </div>
          <div class="flow">
            <div class="flow-code">02 / AI Frontier</div>
            <div class="flow-desc" data-i18n="m2">Official launches, releases, benchmarks, and platform updates from major labs.</div>
            <a class="flow-go" href="/progress" data-i18n="enter">Enter</a>
          </div>
          <div class="flow">
            <div class="flow-code">03 / AI Finance</div>
            <div class="flow-desc" data-i18n="m3">Earnings, calls, capex, M&A and AI-linked capital market movements.</div>
            <a class="flow-go" href="/finance" data-i18n="enter">Enter</a>
          </div>
          <div class="flow">
            <div class="flow-code">04 / Industry Reports</div>
            <div class="flow-desc" data-i18n="m4">Global institutions and strategic reports distilled into actionable signals.</div>
            <a class="flow-go" href="/reports" data-i18n="enter">Enter</a>
          </div>
          <div class="flow">
            <div class="flow-code">05 / Policy Safety</div>
            <div class="flow-desc" data-i18n="m5">Regulation, incidents, and governance events in one risk-aware timeline.</div>
            <a class="flow-go" href="/policy-safety" data-i18n="enter">Enter</a>
          </div>
          <div class="flow">
            <div class="flow-code">06 / OSS Signals</div>
            <div class="flow-desc" data-i18n="m6">Open-source tools and developer momentum with noise-reduced relevance filtering.</div>
            <a class="flow-go" href="/oss" data-i18n="enter">Enter</a>
          </div>
        </section>

        <section class="section">
          <h3 data-i18n="pipeline_title">Intelligence Pipeline</h3>
          <div class="flow">
            <div class="flow-code">Collect</div>
            <div class="flow-desc" data-i18n="p1">Official sources, market feeds, policy channels, reports, and OSS signals.</div>
            <span></span>
          </div>
          <div class="flow">
            <div class="flow-code">Deduplicate</div>
            <div class="flow-desc" data-i18n="p2">Persistent history index and key-level dedupe to prevent repeat capture.</div>
            <span></span>
          </div>
          <div class="flow">
            <div class="flow-code">Enrich</div>
            <div class="flow-desc" data-i18n="p3">Bilingual normalization, structured tags, and LLM-based insight extraction.</div>
            <span></span>
          </div>
          <div class="flow">
            <div class="flow-code">Deliver</div>
            <div class="flow-desc" data-i18n="p4">Dashboard intelligence + push channels for rapid decision cycles.</div>
            <span></span>
          </div>
        </section>
      </div>
    </div>
  </div>

  <script>
    const I18N = {
      "zh-CN": {
        site_title: "OmniHawk AI",
        site_sub: "像鹰一样，从全域噪声中锁定高价值 AI 信号。",
        tab_home: "首页",
        tab_papers: "论文雷达",
        tab_progress: "AI 前沿雷达",
        tab_finance: "AI 财经信息",
        tab_reports: "AI 产业报告",
        tab_policy_safety: "AI 政策与安全",
        tab_oss: "AI 开源生态与开发者信号",
        hero_kicker: "ALL IN AI 情报平台",
        hero_title: "从弱信号到战略决策，一站完成。",
        hero_sub: "OmniHawk AI 同步扫描论文、模型发布、资本市场、政策风险与开源生态，形成连续的 AI 情报闭环。",
        hero_cta_primary: "开始监测",
        hero_cta_secondary: "进入论文雷达",
        overview_title: "项目介绍",
        overview_desc: "这是一个面向 AI 全产业链的情报操作台，不止追踪模型新闻，而是覆盖“研究-技术-资本-政策-生态”的完整链路。",
        stat_1: "独立雷达页面",
        stat_2: "持续源跟踪",
        stat_3: "时效优先过滤",
        stat_4: "中英双语输出",
        modules_title: "雷达模块",
        enter: "进入",
        m1: "高价值论文、深度分析摘要、订阅推送能力。",
        m2: "大厂与实验室官方发布、版本、评测与关键更新。",
        m3: "财报、电话会、CapEx、融资并购与 AI 相关资本市场动态。",
        m4: "全球机构报告提炼，捕捉行业结构与需求变化。",
        m5: "政策、监管、事故与治理事件的风险时间线。",
        m6: "开源工具与开发者活跃信号，降低版本噪音。",
        pipeline_title: "情报流水线",
        p1: "聚合官方源、资本市场、政策渠道、机构报告和开源生态信号。",
        p2: "基于持久化历史索引进行去重，避免重复抓取。",
        p3: "进行中英富化、结构化标签与 LLM 要点抽取。",
        p4: "通过可视化面板与推送通道支持快速决策。",
      },
      "en-US": {
        site_title: "OmniHawk AI",
        site_sub: "Hawk-level sensing for the full AI ecosystem.",
        tab_home: "Home",
        tab_papers: "Papers",
        tab_progress: "AI Frontier",
        tab_finance: "AI Finance",
        tab_reports: "Industry Reports",
        tab_policy_safety: "Policy & Safety",
        tab_oss: "OSS Signals",
        hero_kicker: "All-in AI Intelligence Platform",
        hero_title: "From weak signals to strategic decisions.",
        hero_sub: "OmniHawk AI scans papers, launches, capital markets, policy risk, and OSS momentum in one continuous loop.",
        hero_cta_primary: "Start Monitoring",
        hero_cta_secondary: "Open Paper Radar",
        overview_title: "Project Overview",
        overview_desc: "A complete AI intelligence workbench across research, frontier tech, finance, policy and open-source ecosystems.",
        stat_1: "Independent Radar Pages",
        stat_2: "Continuous Source Tracking",
        stat_3: "Freshness-first Filtering",
        stat_4: "Bilingual Output",
        modules_title: "Radar Modules",
        enter: "Enter",
        m1: "High-value papers with deep-analysis summaries and subscriptions.",
        m2: "Official launches, releases, benchmarks and key updates.",
        m3: "Earnings, calls, capex, M&A and AI-linked market movement.",
        m4: "Global reports distilled into strategic signals.",
        m5: "Policy, regulation and incident timelines with risk context.",
        m6: "Open-source tool and developer momentum with less noise.",
        pipeline_title: "Intelligence Pipeline",
        p1: "Collect from official sources, markets, policy channels, reports, and OSS signals.",
        p2: "Deduplicate through persistent historical indexes.",
        p3: "Enrich with bilingual normalization, tags and LLM insights.",
        p4: "Deliver through dashboard surfaces and push channels.",
      }
    };

    const state = {
      lang: localStorage.getItem("panel_lang") || "zh-CN",
      theme: localStorage.getItem("panel_theme") || "dark",
    };

    function t(key) {
      const dict = I18N[state.lang] || I18N["zh-CN"];
      return dict[key] || key;
    }

    function applyTheme() {
      document.documentElement.setAttribute("data-theme", state.theme === "light" ? "light" : "dark");
      const themeShort = document.getElementById("themeShort");
      if (themeShort) themeShort.textContent = state.theme === "light" ? "Light" : "Dark";
    }

    function applyI18n() {
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        el.textContent = t(key);
      });
      const langShort = document.getElementById("langShort");
      if (langShort) langShort.textContent = state.lang === "zh-CN" ? "EN" : "ZH";
      document.title = t("site_title");
    }

    function initPageShellMotion() {
      const body = document.body;
      if (!body) return;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => body.classList.add("page-ready"));
      });
      document.querySelectorAll(".tab[href], .cta[href], .flow-go[href]").forEach((link) => {
        link.addEventListener("click", (event) => {
          const href = link.getAttribute("href") || "";
          if (!href) return;
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          body.classList.add("page-leaving");
          window.setTimeout(() => {
            window.location.href = href;
          }, 180);
        });
      });
    }

    document.getElementById("langToggle")?.addEventListener("click", () => {
      state.lang = state.lang === "zh-CN" ? "en-US" : "zh-CN";
      localStorage.setItem("panel_lang", state.lang);
      applyI18n();
    });

    document.getElementById("themeToggle")?.addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      localStorage.setItem("panel_theme", state.theme);
      applyTheme();
    });

    applyTheme();
    applyI18n();
    initPageShellMotion();
  </script>
</body>
</html>
"""


def build_progress_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OmniHawk AI | Frontier Radar</title>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Orbitron:wght@700;800;900&family=Rajdhani:wght@500;600;700&display=swap");
    :root {
      --bg: #121212;
      --bg-grad-1: rgba(255, 255, 255, 0.02);
      --bg-grad-2: rgba(30, 215, 96, 0.16);
      --card: #181818;
      --input-bg: #1f1f1f;
      --text: #ffffff;
      --muted: #b3b3b3;
      --line: #303030;
      --line-strong: #4d4d4d;
      --primary: #1ed760;
      --primary-2: #1db954;
      --danger: #f3727f;
      --badge-bg: rgba(30, 215, 96, 0.16);
      --badge-border: rgba(30, 215, 96, 0.35);
      --badge-text: #bcf9d2;
      --panel-shadow: rgba(0, 0, 0, 0.5) 0 8px 24px;
      --card-shadow: rgba(0, 0, 0, 0.3) 0 8px 8px;
      --title-glow: rgba(30, 215, 96, 0.34);
    }
    :root[data-theme="light"] {
      --bg: #f4f7fb;
      --bg-grad-1: rgba(29, 185, 84, 0.12);
      --bg-grad-2: rgba(21, 128, 61, 0.08);
      --card: #ffffff;
      --input-bg: #eef2f8;
      --text: #0f172a;
      --muted: #475569;
      --line: #d5deea;
      --line-strong: #9fb2cc;
      --primary: #1db954;
      --primary-2: #15803d;
      --danger: #dc2626;
      --badge-bg: rgba(34, 197, 94, 0.12);
      --badge-border: rgba(34, 197, 94, 0.28);
      --badge-text: #15803d;
      --panel-shadow: rgba(15, 23, 42, 0.08) 0 8px 24px;
      --card-shadow: rgba(15, 23, 42, 0.08) 0 8px 12px;
      --title-glow: rgba(21, 128, 61, 0.2);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Circular Std", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(1200px 700px at 5% -10%, var(--bg-grad-1), transparent 55%),
        radial-gradient(1000px 650px at 95% -15%, var(--bg-grad-2), transparent 50%),
        var(--bg);
      color: var(--text);
      min-height: 100vh;
      opacity: 0;
      transform: translateY(16px);
      transition:
        background-color 0.35s ease,
        color 0.2s ease,
        opacity 0.28s ease,
        transform 0.34s cubic-bezier(.22,1,.36,1);
    }
    body.page-ready {
      opacity: 1;
      transform: translateY(0);
    }
    body.page-leaving {
      opacity: 0;
      transform: translateX(28px);
      pointer-events: none;
    }
    .wrap { max-width: 1700px; margin: 0 auto; padding: 18px 16px 24px; }
    .top {
      background: transparent;
      border: none;
      border-radius: 0;
      padding: 0 0 12px;
      position: static;
      top: auto;
      z-index: 5;
      backdrop-filter: none;
      box-shadow: none;
    }
    .top-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 12px;
    }
    .top-left {
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-width: 0;
    }
    .top-right { display: flex; align-items: center; gap: 10px; }
    .title {
      font-size: 34px;
      font-weight: 760;
      margin: 0;
      letter-spacing: 1px;
      text-transform: uppercase;
      line-height: 1.22;
      padding: 4px 0 6px;
      display: block;
      overflow: visible;
      font-family: "Orbitron", "Rajdhani", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background: linear-gradient(120deg, #ffffff 0%, #e8fff0 36%, var(--primary) 78%, #8ef4b6 100%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      text-shadow: 0 0 18px var(--title-glow), 0 8px 24px rgba(0, 0, 0, 0.38);
    }
    :root[data-theme="light"] .title {
      background: none;
      -webkit-background-clip: initial;
      background-clip: initial;
      -webkit-text-fill-color: #0f7a3a;
      color: #0f7a3a;
      text-shadow: 0 1px 0 rgba(15, 23, 42, 0.16), 0 0 4px rgba(21, 128, 61, 0.12);
    }
    .page-tabs {
      display: inline-flex;
      align-items: center;
      gap: 18px;
      flex-wrap: wrap;
    }
    .page-tab {
      display: inline-flex;
      align-items: center;
      border: none;
      border-radius: 0;
      padding: 6px 0;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.2px;
      text-transform: none;
      color: var(--muted);
      text-decoration: none;
      background: transparent;
      transition: border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease;
    }
    .page-tab:hover { border-color: transparent; color: var(--text); text-decoration: none; }
    .page-tab.active {
      border-color: transparent;
      color: var(--text);
      background: transparent;
      border-bottom: 2px solid var(--primary);
    }
    .icon-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-width: 108px;
      justify-content: center;
      padding: 10px 12px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.3px;
      text-transform: none;
      cursor: pointer;
    }
    .icon-btn svg { width: 16px; height: 16px; }
    .row, .toolbar {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .toolbar { margin-top: 12px; }
    .row label, .toolbar label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: var(--muted);
    }
    button, select, input[type="text"], input[type="number"], input[type="date"], input[type="password"] {
      border: none;
      border-radius: 10px;
      padding: 10px 14px;
      background: var(--input-bg);
      color: var(--text);
      font-size: 15px;
      transition: border-color 0.2s ease, background-color 0.2s ease;
    }
    button, select { cursor: pointer; }
    button:disabled {
      cursor: not-allowed;
      opacity: 0.64;
    }
    button.primary {
      border-color: var(--primary);
      background: var(--primary);
      color: #111;
    }
    button.primary:hover { background: var(--primary-2); }
    input[type="text"] { min-width: 320px; }
    .status {
      margin-top: 10px;
      font-size: 14px;
      color: var(--muted);
      white-space: pre-wrap;
    }
    .error { color: var(--danger); }
    .config-toggle-row {
      margin-top: 10px;
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    .panel-box {
      display: none;
      margin-top: 10px;
      padding: 12px;
      background: var(--card);
      border-radius: 10px;
      box-shadow: var(--card-shadow);
    }
    .panel-box.open { display: block; }
    .panel-box h4 {
      margin: 0 0 10px;
      font-size: 16px;
      letter-spacing: 0.2px;
    }
    .cfg-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      align-items: start;
    }
    .cfg-grid label {
      display: grid;
      grid-template-columns: 136px minmax(0, 1fr);
      gap: 8px;
      align-items: center;
      min-width: 0;
    }
    .cfg-grid label > span {
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .cfg-grid label > input,
    .cfg-grid label > select {
      width: 100%;
      min-width: 0;
      box-sizing: border-box;
    }
    .cfg-grid .full { grid-column: 1 / -1; }
    .cfg-actions {
      margin-top: 10px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .sub-list {
      margin-top: 10px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }
    .sub-item {
      background: var(--input-bg);
      border-radius: 10px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .sub-item .line {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 14px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      margin: 14px 0 0;
      align-items: stretch;
    }
    .card {
      background: var(--card);
      border-radius: 12px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s ease, box-shadow 0.24s ease;
      overflow: hidden;
    }
    .card:hover { transform: translateY(-4px); }
    .card-head {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: 8px;
    }
    .card h3 {
      margin: 0;
      font-size: 24px;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .card-title-link {
      color: inherit;
      text-decoration: none;
    }
    .card-title-link:hover {
      text-decoration: none;
      color: #1ed760;
    }
    .meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 4px 8px;
      font-size: 16px;
      color: var(--muted);
      margin-bottom: 8px;
    }
    .meta span {
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .content-scroll {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .tag-block {
      background: rgba(148, 163, 184, 0.04);
      border-radius: 12px;
      padding: 8px;
    }
    .badges {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin: 0;
      align-content: flex-start;
    }
    .badge {
      background: var(--badge-bg);
      color: var(--badge-text);
      border-radius: 8px;
      padding: 3px 10px;
      font-size: 14px;
    }
    .card-body {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .summary-block {
      background: rgba(148, 163, 184, 0.07);
      border-radius: 12px;
      padding: 8px;
    }
    :root[data-theme="dark"] .summary-block {
      background: rgba(148, 163, 184, 0.08);
    }
    .section-label {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 5px;
    }
    .summary {
      line-height: 1.65;
      font-size: 17px;
      white-space: normal;
      word-break: break-word;
      color: var(--text);
    }
    .takeaway {
      border-radius: 12px;
      padding: 8px;
      background: linear-gradient(135deg, rgba(30, 215, 96, 0.16), rgba(30, 215, 96, 0.06));
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
    }
    :root[data-theme="dark"] .takeaway {
      background: linear-gradient(135deg, rgba(30, 215, 96, 0.2), rgba(30, 215, 96, 0.08));
    }
    .takeaway-text {
      font-size: 16px;
      line-height: 1.58;
      font-weight: 600;
      color: var(--text);
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 10px;
      padding-top: 10px;
      box-shadow: inset 0 1px 0 rgba(148, 163, 184, 0.14);
    }
    .btn-sm {
      border-radius: 10px;
      padding: 8px 14px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      font-weight: 700;
    }
    .empty {
      border: none;
      border-radius: 12px;
      padding: 24px;
      text-align: center;
      color: var(--muted);
      background: var(--card);
      grid-column: 1 / -1;
    }
    a { color: #1ed760; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @media (max-width: 1380px) {
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 900px) {
      .wrap { padding: 12px 10px 16px; }
      .top { padding: 0 0 10px; border-radius: 0; }
      .grid { grid-template-columns: minmax(0, 1fr); }
      .title { font-size: 28px; }
      .meta { grid-template-columns: 1fr; }
      input[type="text"] { min-width: 100%; }
      .card h3 { font-size: 23px; }
      .cfg-grid { grid-template-columns: 1fr; }
      .cfg-grid label { grid-template-columns: 1fr; gap: 6px; }
      .cfg-grid label > span { white-space: normal; overflow: visible; text-overflow: clip; }
    }
    @media (max-width: 640px) {
      .grid { grid-template-columns: minmax(0, 1fr); }
      .card { height: auto; }
      .content-scroll { overflow: visible; padding-right: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      body { transition: none; }
      .card { transition: none; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="top-head">
        <div class="top-left">
          <p class="title" id="pageTitle">OmniHawk AI · AI 前沿雷达</p>
          <div class="page-tabs">
            <a class="page-tab" href="/" data-i18n="tab_home">首页</a>
            <a class="page-tab" href="/panel" data-i18n="tab_papers">论文雷达</a>
            <a class="page-tab" href="/progress" data-progress-tab="frontier" data-i18n="tab_progress">AI 前沿雷达</a>
            <a class="page-tab" href="/finance" data-progress-tab="market_finance" data-i18n="tab_finance">AI 财经信息</a>
            <a class="page-tab" href="/reports" data-progress-tab="industry_report" data-i18n="tab_reports">AI 产业报告</a>
            <a class="page-tab" href="/policy-safety" data-progress-tab="policy_safety" data-i18n="tab_policy_safety">AI 政策与安全</a>
            <a class="page-tab" href="/oss" data-progress-tab="oss_signal" data-i18n="tab_oss">AI 开源生态与开发者信号</a>
          </div>
        </div>
        <div class="top-right">
          <button id="langToggle" class="icon-btn" type="button" title="Language">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 5h12M9 3v2M7 5a17 17 0 0 0 5 10M9 5a17 17 0 0 1-5 10"></path>
              <path d="M14 13h7M17.5 10v3M16 21l1.5-3 1.5 3"></path>
            </svg>
            <span id="langShort">ZH</span>
          </button>
          <button id="themeToggle" class="icon-btn" type="button" title="Theme">
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 1 0 9.8 9.8Z"></path>
            </svg>
            <span id="themeShort">Dark</span>
          </button>
        </div>
      </div>
      <div class="row">
        <button id="fetchNow" class="primary" data-i18n="fetch_now">抓取官方源</button>
        <label><span data-i18n="max_per_source">每源抓取</span>
          <select id="maxPerSource">
            <option value="5">5</option>
            <option value="12">12</option>
            <option value="20" selected>20</option>
            <option value="40">40</option>
            <option value="80">80</option>
          </select>
        </label>
        <button id="refreshNow" data-i18n="refresh">刷新</button>
        <label><span data-i18n="push_channel">推送渠道</span>
          <select id="notifyChannel">
            <option value="feishu">Feishu</option>
            <option value="wework">WeCom</option>
            <option value="wechat">WeChat Personal</option>
            <option value="telegram">Telegram</option>
            <option value="dingtalk">DingTalk</option>
            <option value="ntfy">ntfy</option>
            <option value="bark">Bark</option>
            <option value="slack">Slack</option>
            <option value="email">Email</option>
          </select>
        </label>
        <button id="pushNow" data-i18n="push_now">推送当前结果</button>
      </div>
      <div class="toolbar">
        <input id="searchQ" type="text" data-i18n-ph="search_ph" placeholder="关键词（标题/摘要/来源）" />
        <label><span data-i18n="region">区域</span>
          <select id="filterRegion">
            <option value="" data-i18n="region_any">全部</option>
            <option value="global" data-i18n="region_global">全球</option>
            <option value="us" data-i18n="region_us">美国</option>
            <option value="cn" data-i18n="region_cn">中国大陆</option>
            <option value="hk" data-i18n="region_hk">中国香港</option>
            <option value="jp" data-i18n="region_jp">日本</option>
            <option value="kr" data-i18n="region_kr">韩国</option>
            <option value="apac" data-i18n="region_apac">亚太</option>
            <option value="eu" data-i18n="region_eu">欧洲</option>
            <option value="uk" data-i18n="region_uk">英国</option>
            <option value="fr" data-i18n="region_fr">法国</option>
          </select>
        </label>
        <label><span data-i18n="event_type">类型</span>
          <select id="filterEventType">
            <option value="" data-i18n="event_any">全部</option>
            <option value="release" data-i18n="event_release">版本发布</option>
            <option value="report" data-i18n="event_report">技术报告</option>
            <option value="benchmark" data-i18n="event_benchmark">评测基准</option>
            <option value="safety" data-i18n="event_safety">安全治理</option>
            <option value="update" data-i18n="event_update">一般更新</option>
          </select>
        </label>
        <label><span data-i18n="source">来源</span>
          <select id="filterSource">
            <option value="" data-i18n="source_any">全部来源</option>
          </select>
        </label>
        <button id="applyFilters" data-i18n="apply_filters">筛选</button>
        <button id="clearFilters" data-i18n="clear_filters">清空筛选</button>
      </div>
      <div class="config-toggle-row">
        <button id="openProgressSettings" data-i18n="open_page_settings">参数配置</button>
        <button id="openProgressSubscriptions" data-i18n="open_page_subscriptions">订阅配置</button>
      </div>
      <div id="progressSettingsBox" class="panel-box">
        <h4 data-i18n="settings_title">页面参数配置</h4>
        <div class="cfg-grid">
          <label><span data-i18n="max_per_source">每源抓取</span>
            <input id="cfgMaxPerSource" type="number" min="1" max="120" value="20" />
          </label>
          <label><span data-i18n="fetch_workers">抓取并发线程</span>
            <input id="cfgFetchWorkers" type="number" min="1" max="16" value="6" />
          </label>
          <label><span data-i18n="push_channel">推送渠道</span>
            <select id="cfgNotifyChannel">
              <option value="feishu">Feishu</option>
              <option value="wework">WeCom</option>
              <option value="wechat">WeChat Personal</option>
              <option value="telegram">Telegram</option>
              <option value="dingtalk">DingTalk</option>
              <option value="ntfy">ntfy</option>
              <option value="bark">Bark</option>
              <option value="slack">Slack</option>
              <option value="email">Email</option>
            </select>
          </label>
          <label><span data-i18n="push_limit">推送条数</span>
            <input id="cfgNotifyLimit" type="number" min="1" max="30" value="8" />
          </label>
          <label><span data-i18n="output_language">输出语言</span>
            <select id="cfgOutputLanguage">
              <option value="Chinese" data-i18n="lang_chinese">简体中文</option>
              <option value="Traditional Chinese" data-i18n="lang_traditional_chinese">繁体中文</option>
              <option value="English" data-i18n="lang_english">English</option>
              <option value="Japanese" data-i18n="lang_japanese">日本語</option>
              <option value="Korean" data-i18n="lang_korean">한국어</option>
              <option value="French" data-i18n="lang_french">Français</option>
            </select>
          </label>
          <label><span data-i18n="auto_interval">定时抓取(分钟)</span>
            <input id="cfgAutoInterval" type="number" min="5" max="1440" value="60" />
          </label>
          <label><span data-i18n="auto_enabled">启用定时抓取</span>
            <select id="cfgAutoEnabled">
              <option value="0" data-i18n="opt_no">否</option>
              <option value="1" data-i18n="opt_yes">是</option>
            </select>
          </label>
          <label><span data-i18n="auto_push_enabled">抓取后自动推送订阅</span>
            <select id="cfgAutoPushEnabled">
              <option value="0" data-i18n="opt_no">否</option>
              <option value="1" data-i18n="opt_yes">是</option>
            </select>
          </label>
          <label><span data-i18n="settings_filter_q">默认关键词</span>
            <input id="cfgQ" type="text" />
          </label>
          <label><span data-i18n="source">默认来源</span>
            <select id="cfgSource">
              <option value="" data-i18n="source_any">全部来源</option>
            </select>
          </label>
          <label><span data-i18n="region">默认区域</span>
            <select id="cfgRegion">
              <option value="" data-i18n="region_any">全部</option>
              <option value="global" data-i18n="region_global">全球</option>
              <option value="us" data-i18n="region_us">美国</option>
              <option value="cn" data-i18n="region_cn">中国大陆</option>
              <option value="hk" data-i18n="region_hk">中国香港</option>
              <option value="jp" data-i18n="region_jp">日本</option>
              <option value="kr" data-i18n="region_kr">韩国</option>
              <option value="apac" data-i18n="region_apac">亚太</option>
              <option value="eu" data-i18n="region_eu">欧洲</option>
              <option value="uk" data-i18n="region_uk">英国</option>
              <option value="fr" data-i18n="region_fr">法国</option>
            </select>
          </label>
          <label><span data-i18n="event_type">默认类型</span>
            <select id="cfgEventType">
              <option value="" data-i18n="event_any">全部</option>
              <option value="release" data-i18n="event_release">版本发布</option>
              <option value="report" data-i18n="event_report">技术报告</option>
              <option value="benchmark" data-i18n="event_benchmark">评测基准</option>
              <option value="safety" data-i18n="event_safety">安全治理</option>
              <option value="update" data-i18n="event_update">一般更新</option>
            </select>
          </label>
          <label><span data-i18n="cfg_feishu_webhook">Feishu Webhook</span>
            <input id="cfgFeishuWebhook" type="text" placeholder="https://open.feishu.cn/..." />
          </label>
          <label><span data-i18n="cfg_wework_webhook">WeCom Webhook</span>
            <input id="cfgWeworkWebhook" type="text" placeholder="https://qyapi.weixin.qq.com/..." />
          </label>
          <label><span data-i18n="cfg_wework_msg_type">WeCom Message Type</span>
            <select id="cfgWeworkMsgType">
              <option value="markdown" data-i18n="cfg_wework_msg_markdown">Markdown (Group Bot)</option>
              <option value="text" data-i18n="cfg_wework_msg_text">Text (Personal WeChat)</option>
            </select>
          </label>
          <label><span data-i18n="cfg_dingtalk_webhook">DingTalk Webhook</span>
            <input id="cfgDingtalkWebhook" type="text" placeholder="https://oapi.dingtalk.com/robot/send?access_token=..." />
          </label>
          <label><span data-i18n="cfg_telegram_bot_token">Telegram Bot Token</span>
            <input id="cfgTelegramBotToken" type="text" placeholder="123456:ABC..." />
          </label>
          <label><span data-i18n="cfg_telegram_chat_id">Telegram Chat ID</span>
            <input id="cfgTelegramChatId" type="text" placeholder="-1001234567890" />
          </label>
          <label><span data-i18n="cfg_ntfy_server_url">ntfy Server URL</span>
            <input id="cfgNtfyServerUrl" type="text" placeholder="https://ntfy.sh" />
          </label>
          <label><span data-i18n="cfg_ntfy_topic">ntfy Topic</span>
            <input id="cfgNtfyTopic" type="text" placeholder="omnihawk-ai" />
          </label>
          <label><span data-i18n="cfg_ntfy_token">ntfy Token</span>
            <input id="cfgNtfyToken" type="password" placeholder="optional token" />
          </label>
          <label><span data-i18n="cfg_bark_url">Bark URL</span>
            <input id="cfgBarkUrl" type="text" placeholder="https://api.day.app/<device_key>" />
          </label>
          <label><span data-i18n="cfg_slack_webhook">Slack Webhook</span>
            <input id="cfgSlackWebhook" type="text" placeholder="https://hooks.slack.com/services/..." />
          </label>
          <label><span data-i18n="cfg_email_from">邮箱发件人</span>
            <input id="cfgEmailFrom" type="text" placeholder="example@qq.com" />
          </label>
          <label><span data-i18n="cfg_email_password">邮箱授权码</span>
            <input id="cfgEmailPassword" type="password" placeholder="password/token" />
          </label>
          <label><span data-i18n="cfg_email_to">邮箱收件人</span>
            <input id="cfgEmailTo" type="text" placeholder="a@xx.com;b@yy.com" />
          </label>
          <label><span data-i18n="cfg_email_smtp_server">SMTP Server</span>
            <input id="cfgEmailSmtpServer" type="text" placeholder="smtp.qq.com" />
          </label>
          <label><span data-i18n="cfg_email_smtp_port">SMTP Port</span>
            <input id="cfgEmailSmtpPort" type="text" placeholder="465" />
          </label>
        </div>
        <div class="cfg-actions">
          <button id="saveProgressSettings" class="primary" data-i18n="save_settings">保存设置</button>
          <button id="reloadProgressSettings" data-i18n="reload_settings">重载设置</button>
        </div>
      </div>
      <div id="progressSubscriptionsBox" class="panel-box">
        <h4 data-i18n="sub_settings_title">页面订阅配置</h4>
        <div class="cfg-grid">
          <label><span data-i18n="sub_name">订阅名称</span>
            <input id="subName" type="text" />
          </label>
          <label><span data-i18n="push_channel">推送渠道</span>
            <select id="subChannel">
              <option value="feishu">Feishu</option>
              <option value="wework">WeCom</option>
              <option value="wechat">WeChat Personal</option>
              <option value="telegram">Telegram</option>
              <option value="dingtalk">DingTalk</option>
              <option value="ntfy">ntfy</option>
              <option value="bark">Bark</option>
              <option value="slack">Slack</option>
              <option value="email">Email</option>
            </select>
          </label>
          <label><span data-i18n="sub_strategy">推送策略</span>
            <select id="subStrategy">
              <option value="incremental" data-i18n="strategy_incremental">增量监控</option>
              <option value="daily" data-i18n="strategy_daily">当日汇总</option>
              <option value="realtime" data-i18n="strategy_realtime">实时告警</option>
            </select>
          </label>
          <label><span data-i18n="sub_limit">订阅条数</span>
            <input id="subLimit" type="number" min="1" max="200" value="20" />
          </label>
          <label><span data-i18n="sub_enabled">启用</span>
            <select id="subEnabled">
              <option value="1" data-i18n="opt_yes">是</option>
              <option value="0" data-i18n="opt_no">否</option>
            </select>
          </label>
          <label><span data-i18n="settings_filter_q">关键词</span>
            <input id="subQ" type="text" />
          </label>
          <label><span data-i18n="source">来源</span>
            <select id="subSource">
              <option value="" data-i18n="source_any">全部来源</option>
            </select>
          </label>
          <label><span data-i18n="region">区域</span>
            <select id="subRegion">
              <option value="" data-i18n="region_any">全部</option>
              <option value="global" data-i18n="region_global">全球</option>
              <option value="us" data-i18n="region_us">美国</option>
              <option value="cn" data-i18n="region_cn">中国大陆</option>
              <option value="hk" data-i18n="region_hk">中国香港</option>
              <option value="jp" data-i18n="region_jp">日本</option>
              <option value="kr" data-i18n="region_kr">韩国</option>
              <option value="apac" data-i18n="region_apac">亚太</option>
              <option value="eu" data-i18n="region_eu">欧洲</option>
              <option value="uk" data-i18n="region_uk">英国</option>
              <option value="fr" data-i18n="region_fr">法国</option>
            </select>
          </label>
          <label><span data-i18n="event_type">类型</span>
            <select id="subEventType">
              <option value="" data-i18n="event_any">全部</option>
              <option value="release" data-i18n="event_release">版本发布</option>
              <option value="report" data-i18n="event_report">技术报告</option>
              <option value="benchmark" data-i18n="event_benchmark">评测基准</option>
              <option value="safety" data-i18n="event_safety">安全治理</option>
              <option value="update" data-i18n="event_update">一般更新</option>
            </select>
          </label>
        </div>
        <div class="cfg-actions">
          <button id="saveProgressSubscription" class="primary" data-i18n="sub_save">保存订阅</button>
          <button id="runProgressSubscriptions" data-i18n="sub_run_all">运行全部订阅</button>
        </div>
        <div id="progressSubscriptionList" class="sub-list"></div>
      </div>
      <div id="actionMsg" class="status"></div>
      <div id="error" class="status error"></div>
    </div>
    <div id="cards" class="grid"></div>
  </div>
  <script>
    const I18N = {
      "zh-CN": {
        tab_home: "首页",
        tab_papers: "论文雷达",
        tab_progress: "AI 前沿雷达",
        tab_finance: "AI 财经信息",
        tab_reports: "AI 产业报告",
        tab_policy_safety: "AI 政策与安全",
        tab_oss: "AI 开源生态与开发者信号",
        page_title_progress: "OmniHawk AI · AI 前沿雷达",
        page_title_finance: "OmniHawk AI · AI 财经信息",
        page_title_reports: "OmniHawk AI · AI 产业报告",
        page_title_policy_safety: "OmniHawk AI · AI 政策与安全",
        page_title_oss: "OmniHawk AI · AI 开源生态与开发者信号",
        fetch_now: "抓取官方源",
        max_per_source: "每源抓取",
        fetch_workers: "抓取并发线程",
        refresh: "刷新",
        push_now: "推送当前结果",
        push_channel: "推送渠道",
        push_limit: "推送条数",
        output_language: "输出语言",
        lang_chinese: "简体中文",
        lang_traditional_chinese: "繁体中文",
        lang_english: "English",
        lang_japanese: "日本语",
        lang_korean: "韩语",
        lang_french: "法语",
        search_ph: "关键词（标题/摘要/来源）",
        region: "区域",
        region_any: "全部",
        region_global: "全球",
        region_us: "美国",
        region_cn: "中国大陆",
        region_hk: "中国香港",
        region_jp: "日本",
        region_kr: "韩国",
        region_apac: "亚太",
        region_eu: "欧洲",
        region_uk: "英国",
        region_fr: "法国",
        source_group_global: "全球",
        source_group_us: "美国",
        source_group_cn: "中国大陆",
        source_group_hk: "中国香港",
        source_group_jp: "日本",
        source_group_kr: "韩国",
        source_group_apac: "亚太",
        source_group_eu: "欧洲",
        source_group_uk: "英国",
        source_group_fr: "法国",
        source_group_other: "其他区域",
        event_type: "类型",
        event_any: "全部",
        event_release: "版本发布",
        event_report: "技术报告",
        event_benchmark: "评测基准",
        event_safety: "安全治理",
        event_update: "一般更新",
        source: "来源",
        source_any: "全部来源",
        open_page_settings: "参数配置",
        open_page_subscriptions: "订阅配置",
        settings_title: "页面参数配置",
        sub_settings_title: "页面订阅配置",
        save_settings: "保存设置",
        reload_settings: "重载设置",
        settings_filter_q: "默认关键词",
        auto_enabled: "启用定时抓取",
        auto_interval: "定时抓取(分钟)",
        auto_push_enabled: "抓取后自动推送订阅",
        cfg_feishu_webhook: "Feishu Webhook",
        cfg_wework_webhook: "WeCom Webhook",
        cfg_wework_msg_type: "WeCom 消息类型",
        cfg_wework_msg_markdown: "Markdown（群机器人）",
        cfg_wework_msg_text: "Text（个人微信）",
        cfg_dingtalk_webhook: "DingTalk Webhook",
        cfg_telegram_bot_token: "Telegram Bot Token",
        cfg_telegram_chat_id: "Telegram Chat ID",
        cfg_ntfy_server_url: "ntfy Server URL",
        cfg_ntfy_topic: "ntfy Topic",
        cfg_ntfy_token: "ntfy Token",
        cfg_bark_url: "Bark URL",
        cfg_slack_webhook: "Slack Webhook",
        cfg_email_from: "邮箱发件人",
        cfg_email_password: "邮箱授权码",
        cfg_email_to: "邮箱收件人",
        cfg_email_smtp_server: "SMTP Server",
        cfg_email_smtp_port: "SMTP Port",
        opt_yes: "是",
        opt_no: "否",
        sub_name: "订阅名称",
        sub_strategy: "推送策略",
        sub_limit: "订阅条数",
        strategy_incremental: "增量监控 (incremental)",
        strategy_daily: "当日汇总 (daily)",
        strategy_realtime: "实时告警 (real-time)",
        sub_enabled: "启用",
        sub_save: "保存订阅",
        sub_run_all: "运行全部订阅",
        sub_apply: "应用",
        sub_run_once: "运行一次",
        sub_delete: "删除",
        sub_enable: "启用",
        sub_disable: "停用",
        sub_empty: "暂无订阅",
        apply_filters: "筛选",
        clear_filters: "清空筛选",
        msg_fetching: "正在抓取官方源，请稍候...",
        msg_fetched: "抓取完成：新增 {added} 条，更新 {updated} 条，当前总计 {total} 条；已完成 {enriched} 条中文富化。",
        msg_fetch_started: "后台抓取任务已启动，可切换页面继续操作。",
        msg_fetch_running: "抓取进行中（{scope}）...",
        msg_pushed: "推送完成",
        msg_settings_saved: "页面参数已保存",
        msg_sub_saved: "订阅已保存",
        msg_sub_deleted: "订阅已删除",
        msg_filter_applied: "筛选条件已应用",
        msg_filter_cleared: "筛选已清空",
        label_org: "机构",
        label_source: "来源",
        label_region: "区域",
        label_time: "发布时间",
        label_type: "类型",
        section_keywords: "关键词",
        section_summary: "摘要",
        section_takeaway: "要点",
        btn_open: "打开原文",
        empty_title: "暂无可展示的 AI 技术进展",
        empty_hint: "请先点击“抓取官方源”或调整筛选条件。"
      },
      "en-US": {
        tab_home: "Home",
        tab_papers: "Papers",
        tab_progress: "AI Frontier",
        tab_finance: "AI Finance",
        tab_reports: "AI Industry Reports",
        tab_policy_safety: "AI Policy & Safety",
        tab_oss: "AI OSS & Dev Signals",
        page_title_progress: "OmniHawk AI · Frontier Radar",
        page_title_finance: "OmniHawk AI · Finance Intelligence",
        page_title_reports: "OmniHawk AI · Industry Reports",
        page_title_policy_safety: "OmniHawk AI · Policy & Safety",
        page_title_oss: "OmniHawk AI · OSS & Dev Signals",
        fetch_now: "Fetch Official Sources",
        max_per_source: "Items per Source",
        fetch_workers: "Fetch Worker Pool",
        refresh: "Refresh",
        push_now: "Push Current Results",
        push_channel: "Push Channel",
        push_limit: "Push Count",
        output_language: "Output Language",
        lang_chinese: "Simplified Chinese",
        lang_traditional_chinese: "Traditional Chinese",
        lang_english: "English",
        lang_japanese: "Japanese",
        lang_korean: "Korean",
        lang_french: "French",
        search_ph: "Keyword (title/summary/source)",
        region: "Region",
        region_any: "All",
        region_global: "Global",
        region_us: "United States",
        region_cn: "Mainland China",
        region_hk: "Hong Kong, China",
        region_jp: "Japan",
        region_kr: "South Korea",
        region_apac: "APAC",
        region_eu: "Europe",
        region_uk: "United Kingdom",
        region_fr: "France",
        source_group_global: "Global",
        source_group_us: "United States",
        source_group_cn: "Mainland China",
        source_group_hk: "Hong Kong, China",
        source_group_jp: "Japan",
        source_group_kr: "South Korea",
        source_group_apac: "APAC",
        source_group_eu: "Europe",
        source_group_uk: "United Kingdom",
        source_group_fr: "France",
        source_group_other: "Other Regions",
        event_type: "Event Type",
        event_any: "All",
        event_release: "Release",
        event_report: "Technical Report",
        event_benchmark: "Benchmark",
        event_safety: "Safety & Policy",
        event_update: "General Update",
        source: "Source",
        source_any: "All Sources",
        open_page_settings: "Page Settings",
        open_page_subscriptions: "Subscriptions",
        settings_title: "Page Settings",
        sub_settings_title: "Subscription Settings",
        save_settings: "Save Settings",
        reload_settings: "Reload Settings",
        settings_filter_q: "Default Keyword",
        auto_enabled: "Enable Auto Fetch",
        auto_interval: "Auto Fetch Interval (min)",
        auto_push_enabled: "Auto push subscriptions after fetch",
        cfg_feishu_webhook: "Feishu Webhook",
        cfg_wework_webhook: "WeCom Webhook",
        cfg_wework_msg_type: "WeCom Message Type",
        cfg_wework_msg_markdown: "Markdown (Group Bot)",
        cfg_wework_msg_text: "Text (Personal WeChat)",
        cfg_dingtalk_webhook: "DingTalk Webhook",
        cfg_telegram_bot_token: "Telegram Bot Token",
        cfg_telegram_chat_id: "Telegram Chat ID",
        cfg_ntfy_server_url: "ntfy Server URL",
        cfg_ntfy_topic: "ntfy Topic",
        cfg_ntfy_token: "ntfy Token",
        cfg_bark_url: "Bark URL",
        cfg_slack_webhook: "Slack Webhook",
        cfg_email_from: "Email Sender",
        cfg_email_password: "Email Password",
        cfg_email_to: "Email Recipients",
        cfg_email_smtp_server: "SMTP Server",
        cfg_email_smtp_port: "SMTP Port",
        opt_yes: "Yes",
        opt_no: "No",
        sub_name: "Subscription Name",
        sub_strategy: "Strategy",
        sub_limit: "Item Limit",
        strategy_incremental: "Incremental",
        strategy_daily: "Daily",
        strategy_realtime: "Real-time",
        sub_enabled: "Enabled",
        sub_save: "Save Subscription",
        sub_run_all: "Run All Subscriptions",
        sub_apply: "Apply",
        sub_run_once: "Run Once",
        sub_delete: "Delete",
        sub_enable: "Enable",
        sub_disable: "Disable",
        sub_empty: "No subscriptions yet",
        apply_filters: "Apply",
        clear_filters: "Clear",
        msg_fetching: "Fetching official sources...",
        msg_fetched: "Done: +{added} new, {updated} updated, {total} total; {enriched} enriched in Chinese.",
        msg_fetch_started: "Background fetch started. You can switch pages safely.",
        msg_fetch_running: "Fetch in progress ({scope})...",
        msg_pushed: "Push completed",
        msg_settings_saved: "Page settings saved",
        msg_sub_saved: "Subscription saved",
        msg_sub_deleted: "Subscription deleted",
        msg_filter_applied: "Filters applied",
        msg_filter_cleared: "Filters cleared",
        label_org: "Organization",
        label_source: "Source",
        label_region: "Region",
        label_time: "Published",
        label_type: "Type",
        section_keywords: "Keywords",
        section_summary: "Summary",
        section_takeaway: "Key Insight",
        btn_open: "Open",
        empty_title: "No AI progress items found",
        empty_hint: "Click 'Fetch Official Sources' or adjust filters."
      }
    };

    const MODE_CONFIG = {
      frontier: { kind: "official_blog,official_site", tabValue: "frontier", titleKey: "page_title_progress" },
      market_finance: { kind: "market_finance", tabValue: "market_finance", titleKey: "page_title_finance" },
      industry_report: { kind: "industry_report", tabValue: "industry_report", titleKey: "page_title_reports" },
      policy_safety: { kind: "policy_safety", tabValue: "policy_safety", titleKey: "page_title_policy_safety" },
      oss_signal: { kind: "oss_signal", tabValue: "oss_signal", titleKey: "page_title_oss" },
    };

    const ROUTE_MODE_MAP = {
      "/progress": "frontier",
      "/finance": "market_finance",
      "/reports": "industry_report",
      "/policy-safety": "policy_safety",
      "/oss": "oss_signal",
    };

    const state = {
      lang: localStorage.getItem("panel_lang") || "zh-CN",
      theme: localStorage.getItem("panel_theme") || "dark",
      fixedKind: "official_blog,official_site",
      activeTab: "frontier",
      pageTitleKey: "page_title_progress",
      pageSettings: null,
      subscriptions: [],
      items: [],
      sources: [],
      translatingKeys: {},
      fetchPollTimer: null,
      fetchRunning: false,
      finishedJobIds: {},
      query: {
        q: "",
        source_id: "",
        region: "",
        event_type: "",
      },
    };

    function esc(v) {
      return String(v || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function t(key, vars = {}) {
      const dict = I18N[state.lang] || I18N["zh-CN"];
      let text = dict[key] || key;
      Object.keys(vars || {}).forEach((k) => {
        text = text.replace(new RegExp(`\\\\{${k}\\\\}`, "g"), String(vars[k]));
      });
      return text;
    }

    async function fetchJSON(url, options = {}) {
      const res = await fetch(url, options);
      const text = await res.text();
      let data = {};
      try { data = text ? JSON.parse(text) : {}; } catch (_) {}
      if (!res.ok) {
        const msg = data.error || data.message || `${res.status} ${res.statusText}`;
        throw new Error(msg);
      }
      return data;
    }

    function setMessage(msg) {
      const el = document.getElementById("actionMsg");
      if (el) el.textContent = msg || "";
    }

    function setError(msg) {
      const el = document.getElementById("error");
      if (el) el.textContent = msg || "";
    }

    function setFetchButtonRunning(running) {
      state.fetchRunning = !!running;
      const btn = document.getElementById("fetchNow");
      if (!btn) return;
      btn.disabled = state.fetchRunning;
      btn.setAttribute("aria-busy", state.fetchRunning ? "true" : "false");
    }

    function normalizePath(path) {
      const raw = String(path || "").trim() || "/progress";
      if (raw.length > 1 && raw.endsWith("/")) {
        return raw.slice(0, -1);
      }
      return raw;
    }

    function applyProgressMode() {
      const path = normalizePath(window.location.pathname || "/progress");
      const modeName = ROUTE_MODE_MAP[path] || "frontier";
      const mode = MODE_CONFIG[modeName] || MODE_CONFIG.frontier;
      state.fixedKind = String(mode.kind || "");
      state.activeTab = String(mode.tabValue || "frontier");
      state.pageTitleKey = String(mode.titleKey || "page_title_progress");
      document.querySelectorAll("[data-progress-tab]").forEach((tab) => {
        const tabValue = String(tab.getAttribute("data-progress-tab") || "");
        tab.classList.toggle("active", tabValue === state.activeTab);
      });
    }

    function applyTheme() {
      document.documentElement.setAttribute("data-theme", state.theme === "light" ? "light" : "dark");
      const themeShort = document.getElementById("themeShort");
      if (themeShort) themeShort.textContent = state.theme === "light" ? "Light" : "Dark";
    }

    function initPageShellMotion() {
      const body = document.body;
      if (!body) return;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => body.classList.add("page-ready"));
      });
      document.querySelectorAll(".page-tab[href]").forEach((link) => {
        link.addEventListener("click", (event) => {
          const href = link.getAttribute("href") || "";
          if (!href || link.classList.contains("active")) return;
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          body.classList.add("page-leaving");
          window.setTimeout(() => {
            window.location.href = href;
          }, 180);
        });
      });
    }

    function applyI18n() {
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        el.textContent = t(key);
      });
      document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
        const key = el.getAttribute("data-i18n-ph");
        if (!key) return;
        el.setAttribute("placeholder", t(key));
      });
      const titleText = t(state.pageTitleKey || "page_title_progress");
      const pageTitle = document.getElementById("pageTitle");
      if (pageTitle) pageTitle.textContent = titleText;
      document.title = titleText;
      const langShort = document.getElementById("langShort");
      if (langShort) langShort.textContent = state.lang === "zh-CN" ? "EN" : "ZH";
      fillSourceOptions();
      renderCards();
      renderProgressSubscriptions();
      ensureTargetTranslations().catch(() => {});
    }

    function toDateText(iso) {
      const s = String(iso || "").trim();
      if (!s) return "-";
      return s.replace("T", " ").replace("+00:00", " UTC");
    }

    function localRegion(v) {
      const r = String(v || "").toLowerCase();
      if (r === "us") return t("region_us");
      if (r === "cn") return t("region_cn");
      if (r === "hk") return t("region_hk");
      if (r === "jp") return t("region_jp");
      if (r === "kr") return t("region_kr");
      if (r === "apac") return t("region_apac");
      if (r === "eu") return t("region_eu");
      if (r === "uk") return t("region_uk");
      if (r === "fr") return t("region_fr");
      if (r === "global") return t("region_global");
      return v || "-";
    }

    function sourceRegionMeta(regionValue) {
      const region = String(regionValue || "global").trim().toLowerCase() || "global";
      const mapping = {
        global: { code: "GLOBAL", labelKey: "source_group_global" },
        us: { code: "US", labelKey: "source_group_us" },
        cn: { code: "CN", labelKey: "source_group_cn" },
        hk: { code: "HK", labelKey: "source_group_hk" },
        jp: { code: "JP", labelKey: "source_group_jp" },
        kr: { code: "KR", labelKey: "source_group_kr" },
        apac: { code: "APAC", labelKey: "source_group_apac" },
        eu: { code: "EU", labelKey: "source_group_eu" },
        uk: { code: "UK", labelKey: "source_group_uk" },
        fr: { code: "FR", labelKey: "source_group_fr" },
      };
      if (mapping[region]) return { region, ...mapping[region] };
      return { region, code: region.toUpperCase(), labelKey: "source_group_other" };
    }

    function localEventType(v) {
      const e = String(v || "").toLowerCase();
      if (e === "release") return t("event_release");
      if (e === "report") return t("event_report");
      if (e === "benchmark") return t("event_benchmark");
      if (e === "safety") return t("event_safety");
      return t("event_update");
    }

    function fillSourceOptions() {
      const kindScope = String(state.fixedKind || "")
        .split(",")
        .map((x) => String(x || "").trim().toLowerCase())
        .filter(Boolean);
      const scopedSources = kindScope.length
        ? state.sources.filter((s) => kindScope.includes(String(s.kind || "").toLowerCase()))
        : state.sources;
      const options = [`<option value="">${esc(t("source_any"))}</option>`];
      const grouped = {};
      for (const s of scopedSources) {
        const id = String(s.id || "").trim();
        if (!id) continue;
        const name = String(s.name || s.org || id).trim() || id;
        const regionMeta = sourceRegionMeta(s.region);
        const regionKey = regionMeta.region || "global";
        if (!grouped[regionKey]) grouped[regionKey] = [];
        grouped[regionKey].push({ id, name });
      }
      const regionOrder = ["global", "us", "cn", "hk", "jp", "kr", "apac", "eu", "uk", "fr"];
      const extraRegions = Object.keys(grouped)
        .filter((key) => !regionOrder.includes(key))
        .sort();
      const fullOrder = [...regionOrder, ...extraRegions];
      for (const regionKey of fullOrder) {
        const rows = grouped[regionKey];
        if (!rows || !rows.length) continue;
        rows.sort((a, b) => a.name.localeCompare(b.name));
        const meta = sourceRegionMeta(regionKey);
        const groupLabel = `[${meta.code}] ${t(meta.labelKey)}`;
        options.push(`<optgroup label="${esc(groupLabel)}">`);
        for (const row of rows) {
          options.push(`<option value="${esc(row.id)}">${esc(row.name)}</option>`);
        }
        options.push("</optgroup>");
      }
      const html = options.join("");
      const validIds = new Set(scopedSources.map((s) => String(s.id || "")));
      const applySelect = (id, fallback = "") => {
        const sel = document.getElementById(id);
        if (!sel) return;
        const current = sel.value || fallback || "";
        sel.innerHTML = html;
        sel.value = validIds.has(current) ? current : "";
      };
      applySelect("filterSource", state.query.source_id || "");
      applySelect("cfgSource", state.pageSettings?.query?.source_id || "");
      applySelect("subSource", "");
      const filterSel = document.getElementById("filterSource");
      if (filterSel) state.query.source_id = filterSel.value || "";
    }

    function captureQuery() {
      return {
        q: (document.getElementById("searchQ")?.value || "").trim(),
        source_id: (document.getElementById("filterSource")?.value || "").trim(),
        region: (document.getElementById("filterRegion")?.value || "").trim(),
        event_type: (document.getElementById("filterEventType")?.value || "").trim(),
      };
    }

    function applyInputs(q) {
      const query = q || {};
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.value = value || "";
      };
      set("searchQ", query.q || "");
      set("filterSource", query.source_id || "");
      set("filterRegion", query.region || "");
      set("filterEventType", query.event_type || "");
    }

    function buildParams(query) {
      const params = new URLSearchParams();
      if (query.q) params.set("q", query.q);
      if (query.source_id) params.set("source_id", query.source_id);
      if (query.region) params.set("region", query.region);
      if (query.event_type) params.set("event_type", query.event_type);
      params.set("scope", state.activeTab || "frontier");
      if (state.fixedKind) params.set("kind", state.fixedKind);
      params.set("limit", "200");
      return params;
    }

    function syncFromUrl() {
      const p = new URLSearchParams(window.location.search || "");
      state.query = {
        q: p.get("q") || "",
        source_id: p.get("source_id") || "",
        region: p.get("region") || "",
        event_type: p.get("event_type") || "",
      };
      applyInputs(state.query);
    }

    function normalizedOutputLanguage() {
      const configured = String(state.pageSettings?.output_language || "").trim();
      if (configured) return configured;
      return state.lang === "en-US" ? "English" : "Chinese";
    }

    function languageKeyOf(value) {
      const raw = String(value || "").trim().toLowerCase().replace(/_/g, "-");
      if (!raw) return "zh";
      const alias = {
        english: "en",
        chinese: "zh",
        "traditional chinese": "zh-hant",
        korean: "ko",
        japanese: "ja",
        french: "fr",
      };
      return alias[raw] || raw.replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "") || "zh";
    }

    function pickProgressLocalized(it, field) {
      const lang = normalizedOutputLanguage();
      const langKey = languageKeyOf(lang);
      const i18n = (it && typeof it.i18n === "object" && it.i18n) ? it.i18n : {};
      const entry = (i18n && typeof i18n[langKey] === "object") ? i18n[langKey] : {};
      const mapped = String(entry?.[field] || "").trim();
      if (mapped) return mapped;
      if (field === "title") {
        if (langKey === "zh" || langKey.startsWith("zh-")) return String(it.title_zh || it.title || "");
        return String(it.title || it.title_zh || "");
      }
      if (field === "summary") {
        if (langKey === "zh" || langKey.startsWith("zh-")) return String(it.summary_zh || it.summary || "");
        return String(it.summary || it.summary_zh || "");
      }
      if (field === "llm_takeaway") {
        if (langKey === "zh" || langKey.startsWith("zh-")) return String(it.llm_takeaway_zh || it.llm_takeaway || "");
        return String(it.llm_takeaway || it.llm_takeaway_zh || "");
      }
      return "";
    }

    function renderCards() {
      const root = document.getElementById("cards");
      if (!root) return;
      const items = Array.isArray(state.items) ? state.items : [];
      if (!items.length) {
        root.innerHTML = `
          <div class="empty">
            <div>${esc(t("empty_title"))}</div>
            <div style="margin-top:6px">${esc(t("empty_hint"))}</div>
          </div>
        `;
        return;
      }
      root.innerHTML = items.map((it) => {
        const title = String(pickProgressLocalized(it, "title") || "");
        const url = String(it.url || "");
        const sourceName = String(it.source_name || "");
        const org = String(it.org || "-");
        const region = String(it.region || "-");
        const eventType = String(it.event_type || "update");
        const published = toDateText(it.published_at || "");
        const summaryRaw = String(pickProgressLocalized(it, "summary") || "");
        const summary = summaryRaw.trim();
        const takeawayRaw = String(pickProgressLocalized(it, "llm_takeaway") || "");
        const takeaway = takeawayRaw.trim();
        const tags = Array.isArray(it.tags) ? it.tags.filter(Boolean) : [];
        return `
          <article class="card">
            <div class="card-head">
              <h3><a class="card-title-link" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title || "-")}</a></h3>
            </div>
            <div class="meta">
              <span>${esc(t("label_org"))}: ${esc(org)}</span>
              <span>${esc(t("label_source"))}: ${esc(sourceName || "-")}</span>
              <span>${esc(t("label_region"))}: ${esc(localRegion(region))}</span>
              <span>${esc(t("label_type"))}: ${esc(localEventType(eventType))}</span>
              <span>${esc(t("label_time"))}: ${esc(published)}</span>
            </div>
            <div class="card-body">
              ${takeaway ? `
                <div class="takeaway">
                  <div class="section-label">${esc(t("section_takeaway"))}</div>
                  <div class="takeaway-text">${esc(takeaway)}</div>
                </div>
              ` : ""}
              <div class="content-scroll">
                ${tags.length ? `
                  <div class="tag-block">
                    <div class="section-label">${esc(t("section_keywords"))}</div>
                    <div class="badges">
                      ${tags.map((x) => `<span class="badge">${esc(x)}</span>`).join("")}
                    </div>
                  </div>
                ` : ""}
                ${summary ? `
                  <div class="summary-block">
                    <div class="section-label">${esc(t("section_summary"))}</div>
                    <div class="summary">${esc(summary)}</div>
                  </div>
                ` : ""}
              </div>
            </div>
            <div class="actions">
              <a class="btn-sm" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(t("btn_open"))}</a>
            </div>
          </article>
        `;
      }).join("");
    }

    async function ensureTargetTranslations() {
      const outputLanguage = normalizedOutputLanguage();
      const langKey = languageKeyOf(outputLanguage);
      const keys = [];
      for (const it of (state.items || [])) {
        const key = String(it.progress_key || "");
        if (!key) continue;
        const i18n = (it && typeof it.i18n === "object" && it.i18n) ? it.i18n : {};
        const entry = (i18n && typeof i18n[langKey] === "object") ? i18n[langKey] : {};
        const titleReady = langKey === "zh" || langKey.startsWith("zh-")
          ? String(it.title_zh || "").trim()
          : String(entry?.title || "").trim();
        const summaryReady = langKey === "zh" || langKey.startsWith("zh-")
          ? String(it.summary_zh || "").trim()
          : String(entry?.summary || "").trim();
        const takeawayReady = langKey === "zh" || langKey.startsWith("zh-")
          ? String(it.llm_takeaway_zh || "").trim()
          : String(entry?.llm_takeaway || "").trim();
        if (titleReady && summaryReady && takeawayReady) continue;
        if (state.translatingKeys[key]) continue;
        state.translatingKeys[key] = true;
        keys.push(key);
        if (keys.length >= 12) break;
      }
      if (!keys.length) return;
      try {
        const data = await fetchJSON("/api/progress/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ keys, output_language: outputLanguage }),
        });
        if (Number(data.changed || 0) > 0) {
          await refreshItems();
        }
      } catch (_) {
        // Ignore translation failures; keep original language content.
      } finally {
        for (const key of keys) {
          delete state.translatingKeys[key];
        }
      }
    }

    async function loadSources() {
      const data = await fetchJSON(`/api/progress/sources?scope=${encodeURIComponent(state.activeTab)}`);
      state.sources = Array.isArray(data.items) ? data.items : [];
      fillSourceOptions();
    }

    async function refreshItems() {
      const params = buildParams(state.query);
      try { window.history.replaceState(null, "", `?${params.toString()}`); } catch (_) {}
      const data = await fetchJSON(`/api/progress?${params.toString()}`);
      state.items = Array.isArray(data.items) ? data.items : [];
      renderCards();
      ensureTargetTranslations().catch(() => {});
    }

    async function runFetch() {
      if (state.fetchRunning) return;
      setError("");
      setMessage(t("msg_fetching"));
      setFetchButtonRunning(true);
      try {
        const maxPerSource = Number(document.getElementById("maxPerSource")?.value || 20);
        const fetchWorkers = Number(
          document.getElementById("cfgFetchWorkers")?.value || state.pageSettings?.fetch_workers || 6
        );
        const cfgIds = Array.isArray(state.pageSettings?.source_ids) ? state.pageSettings.source_ids : [];
        const data = await fetchJSON("/api/progress/fetch/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scope: state.activeTab,
            max_per_source: maxPerSource,
            fetch_workers: fetchWorkers,
            source_ids: cfgIds,
            async: true,
          })
        });
        if (!data.ok) throw new Error(data.error || "fetch start failed");
        setMessage(t("msg_fetch_started"));
        startFetchPolling();
      } catch (e) {
        setError(e.message || String(e));
        setFetchButtonRunning(false);
      }
    }

    async function pushNow() {
      setError("");
      setMessage("");
      try {
        const channel = String(document.getElementById("notifyChannel")?.value || state.pageSettings?.notify_channel || "feishu");
        const pushLimit = Number(state.pageSettings?.notify_limit || 8);
        const payload = {
          scope: state.activeTab,
          channel,
          limit: pushLimit,
          filters: {
            ...state.query,
            kind: state.fixedKind || "",
          },
        };
        const data = await fetchJSON("/api/progress/push", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        setMessage(`${t("msg_pushed")} (${channel}) · ${data.message || "ok"}`);
      } catch (e) {
        setError(e.message || String(e));
      }
    }

    async function applyFilters() {
      state.query = captureQuery();
      await refreshItems();
      setMessage(t("msg_filter_applied"));
    }

    async function clearFilters() {
      state.query = { q: "", source_id: "", region: "", event_type: "" };
      applyInputs(state.query);
      await refreshItems();
      setMessage(t("msg_filter_cleared"));
    }

    function togglePanelBox(id) {
      const target = document.getElementById(id);
      if (!target) return;
      const boxes = ["progressSettingsBox", "progressSubscriptionsBox"];
      for (const boxId of boxes) {
        const el = document.getElementById(boxId);
        if (!el) continue;
        if (boxId === id) el.classList.toggle("open");
        else el.classList.remove("open");
      }
    }

    function applyProgressSettingsInputs(cfg) {
      const settings = cfg || {};
      state.pageSettings = settings;
      const set = (id, value) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.value = (value ?? "").toString();
      };
      set("cfgMaxPerSource", settings.max_per_source || 20);
      set("cfgFetchWorkers", settings.fetch_workers || 6);
      set("cfgNotifyChannel", settings.notify_channel || "feishu");
      set("cfgNotifyLimit", settings.notify_limit || 8);
      set("cfgOutputLanguage", settings.output_language || (state.lang === "en-US" ? "English" : "Chinese"));
      set("cfgAutoEnabled", settings.auto_enabled ? "1" : "0");
      set("cfgAutoInterval", settings.auto_interval_minutes || 60);
      set("cfgAutoPushEnabled", settings.auto_push_enabled ? "1" : "0");
      const q = settings.query || {};
      set("cfgQ", q.q || "");
      set("cfgSource", q.source_id || "");
      set("cfgRegion", q.region || "");
      set("cfgEventType", q.event_type || "");
      set("cfgFeishuWebhook", settings.feishu_webhook_url || "");
      set("cfgWeworkWebhook", settings.wework_webhook_url || "");
      set("cfgWeworkMsgType", settings.wework_msg_type || "markdown");
      set("cfgDingtalkWebhook", settings.dingtalk_webhook_url || "");
      set("cfgTelegramBotToken", settings.telegram_bot_token || "");
      set("cfgTelegramChatId", settings.telegram_chat_id || "");
      set("cfgNtfyServerUrl", settings.ntfy_server_url || "https://ntfy.sh");
      set("cfgNtfyTopic", settings.ntfy_topic || "");
      set("cfgNtfyToken", settings.ntfy_token || "");
      set("cfgBarkUrl", settings.bark_url || "");
      set("cfgSlackWebhook", settings.slack_webhook_url || "");
      set("cfgEmailFrom", settings.email_from || "");
      set("cfgEmailPassword", settings.email_password || "");
      set("cfgEmailTo", settings.email_to || "");
      set("cfgEmailSmtpServer", settings.email_smtp_server || "smtp.qq.com");
      set("cfgEmailSmtpPort", settings.email_smtp_port || "465");
      set("maxPerSource", settings.max_per_source || 20);
      set("notifyChannel", settings.notify_channel || "feishu");
    }

    function collectProgressSettingsInputs() {
      return {
        scope: state.activeTab,
        max_per_source: Number(document.getElementById("cfgMaxPerSource")?.value || 20),
        fetch_workers: Number(document.getElementById("cfgFetchWorkers")?.value || 6),
        notify_channel: String(document.getElementById("cfgNotifyChannel")?.value || "feishu"),
        notify_limit: Number(document.getElementById("cfgNotifyLimit")?.value || 8),
        output_language: String(document.getElementById("cfgOutputLanguage")?.value || "").trim() || (state.lang === "en-US" ? "English" : "Chinese"),
        auto_enabled: String(document.getElementById("cfgAutoEnabled")?.value || "0") === "1",
        auto_interval_minutes: Number(document.getElementById("cfgAutoInterval")?.value || 60),
        auto_push_enabled: String(document.getElementById("cfgAutoPushEnabled")?.value || "0") === "1",
        feishu_webhook_url: String(document.getElementById("cfgFeishuWebhook")?.value || "").trim(),
        wework_webhook_url: String(document.getElementById("cfgWeworkWebhook")?.value || "").trim(),
        email_from: String(document.getElementById("cfgEmailFrom")?.value || "").trim(),
        email_password: String(document.getElementById("cfgEmailPassword")?.value || "").trim(),
        email_to: String(document.getElementById("cfgEmailTo")?.value || "").trim(),
        email_smtp_server: String(document.getElementById("cfgEmailSmtpServer")?.value || "").trim(),
        email_smtp_port: String(document.getElementById("cfgEmailSmtpPort")?.value || "").trim(),
        query: {
          q: String(document.getElementById("cfgQ")?.value || "").trim(),
          source_id: String(document.getElementById("cfgSource")?.value || "").trim(),
          region: String(document.getElementById("cfgRegion")?.value || "").trim(),
          event_type: String(document.getElementById("cfgEventType")?.value || "").trim(),
        },
        wework_msg_type: String(document.getElementById("cfgWeworkMsgType")?.value || "markdown").trim(),
        dingtalk_webhook_url: String(document.getElementById("cfgDingtalkWebhook")?.value || "").trim(),
        telegram_bot_token: String(document.getElementById("cfgTelegramBotToken")?.value || "").trim(),
        telegram_chat_id: String(document.getElementById("cfgTelegramChatId")?.value || "").trim(),
        ntfy_server_url: String(document.getElementById("cfgNtfyServerUrl")?.value || "").trim(),
        ntfy_topic: String(document.getElementById("cfgNtfyTopic")?.value || "").trim(),
        ntfy_token: String(document.getElementById("cfgNtfyToken")?.value || "").trim(),
        bark_url: String(document.getElementById("cfgBarkUrl")?.value || "").trim(),
        slack_webhook_url: String(document.getElementById("cfgSlackWebhook")?.value || "").trim(),
      };
    }

    async function loadProgressSettings() {
      const data = await fetchJSON(`/api/progress/settings?scope=${encodeURIComponent(state.activeTab)}`);
      applyProgressSettingsInputs(data.settings || {});
      fillSourceOptions();
      const job = data.job || {};
      if (job.running) {
        setFetchButtonRunning(true);
        startFetchPolling();
      } else {
        setFetchButtonRunning(false);
      }
    }

    async function saveProgressSettings() {
      const payload = collectProgressSettingsInputs();
      const data = await fetchJSON("/api/progress/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      applyProgressSettingsInputs(data.settings || {});
      setMessage(t("msg_settings_saved"));
    }

    function renderProgressSubscriptions() {
      const root = document.getElementById("progressSubscriptionList");
      if (!root) return;
      const items = Array.isArray(state.subscriptions) ? state.subscriptions : [];
      if (!items.length) {
        root.innerHTML = `<div class="muted">${esc(t("sub_empty"))}</div>`;
        return;
      }
      root.innerHTML = items.map((item) => {
        const id = esc(item.id || "");
        const filters = item.filters || {};
        const preview = [
          filters.q ? `q:${filters.q}` : "",
          filters.source_id ? `source:${filters.source_id}` : "",
          filters.region ? `region:${filters.region}` : "",
          filters.event_type ? `type:${filters.event_type}` : "",
        ].filter(Boolean).join(" | ") || "-";
        return `
          <div class="sub-item">
            <div class="line">
              <b>${esc(item.name || "-")}</b>
              <span class="badge">${esc(item.channel || "-")}</span>
              <span class="badge">${esc(item.strategy || "incremental")}</span>
              <span class="badge">${item.enabled ? esc(t("sub_enable")) : esc(t("sub_disable"))}</span>
            </div>
            <div class="line">${esc(preview)}</div>
            <div class="line">${esc(item.last_notified_at || "-")} / ${Number(item.last_match_count || 0)}</div>
            <div class="line">
              <button class="btn-sm sub-apply" data-id="${id}">${esc(t("sub_apply"))}</button>
              <button class="btn-sm sub-run" data-id="${id}">${esc(t("sub_run_once"))}</button>
              <button class="btn-sm sub-toggle" data-id="${id}" data-enabled="${item.enabled ? "1" : "0"}">${item.enabled ? esc(t("sub_disable")) : esc(t("sub_enable"))}</button>
              <button class="btn-sm sub-delete" data-id="${id}">${esc(t("sub_delete"))}</button>
            </div>
          </div>
        `;
      }).join("");
    }

    async function loadProgressSubscriptions() {
      const data = await fetchJSON(`/api/progress/subscriptions?scope=${encodeURIComponent(state.activeTab)}`);
      state.subscriptions = Array.isArray(data.items) ? data.items : [];
      renderProgressSubscriptions();
    }

    function collectProgressSubscriptionForm() {
      return {
        scope: state.activeTab,
        name: String(document.getElementById("subName")?.value || "").trim(),
        channel: String(document.getElementById("subChannel")?.value || "feishu"),
        strategy: String(document.getElementById("subStrategy")?.value || "incremental"),
        enabled: String(document.getElementById("subEnabled")?.value || "1") === "1",
        limit: Number(document.getElementById("subLimit")?.value || 20),
        filters: {
          q: String(document.getElementById("subQ")?.value || "").trim(),
          source_id: String(document.getElementById("subSource")?.value || "").trim(),
          region: String(document.getElementById("subRegion")?.value || "").trim(),
          event_type: String(document.getElementById("subEventType")?.value || "").trim(),
        },
      };
    }

    async function saveProgressSubscription(extra = {}) {
      const payload = { ...collectProgressSubscriptionForm(), ...extra };
      const data = await fetchJSON("/api/progress/subscriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      state.subscriptions = Array.isArray(data.items) ? data.items : [];
      renderProgressSubscriptions();
      setMessage(t("msg_sub_saved"));
    }

    async function runProgressSubscriptions(id = "") {
      const data = await fetchJSON("/api/progress/subscriptions/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(id ? { scope: state.activeTab, id } : { scope: state.activeTab }),
      });
      await loadProgressSubscriptions();
      const parts = (data.results || []).map((x) => `${x.name}: ${x.message}`).join(" | ");
      setMessage(parts || `ok: ${data.success_count || 0}/${data.total || 0}`);
    }

    async function deleteProgressSubscription(id) {
      await fetchJSON("/api/progress/subscriptions/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      await loadProgressSubscriptions();
      setMessage(t("msg_sub_deleted"));
    }

    async function toggleProgressSubscription(id, enabledNow) {
      const item = (state.subscriptions || []).find((x) => String(x.id || "") === String(id || ""));
      if (!item) return;
      await saveProgressSubscription({
        id,
        name: item.name || "",
        channel: item.channel || "feishu",
        strategy: item.strategy || "incremental",
        limit: Number(item.limit || 120),
        enabled: !enabledNow,
        filters: item.filters || {},
      });
    }

    function applyProgressSubscription(id) {
      const item = (state.subscriptions || []).find((x) => String(x.id || "") === String(id || ""));
      if (!item) return;
      const filters = item.filters || {};
      state.query = {
        q: String(filters.q || ""),
        source_id: String(filters.source_id || ""),
        region: String(filters.region || ""),
        event_type: String(filters.event_type || ""),
      };
      const strategyEl = document.getElementById("subStrategy");
      if (strategyEl) strategyEl.value = String(item.strategy || "incremental");
      applyInputs(state.query);
      refreshItems().catch((e) => setError(e.message || String(e)));
    }

    function stopFetchPolling() {
      if (state.fetchPollTimer) {
        window.clearInterval(state.fetchPollTimer);
        state.fetchPollTimer = null;
      }
    }

    async function checkFetchStatus() {
      const data = await fetchJSON(`/api/progress/fetch/status?scope=${encodeURIComponent(state.activeTab)}`);
      const job = data.job || {};
      if (job.running) {
        setFetchButtonRunning(true);
        setMessage(t("msg_fetch_running", { scope: state.activeTab }));
        return;
      }
      setFetchButtonRunning(false);
      const jobId = String(job.job_id || "");
      if (!jobId) return;
      if (state.finishedJobIds[state.activeTab] === jobId) return;
      state.finishedJobIds[state.activeTab] = jobId;
      const result = (job.result && typeof job.result === "object") ? job.result : {};
      if (result && result.ok) {
        const enrichment = (result.enrichment && typeof result.enrichment === "object") ? result.enrichment : {};
        setMessage(t("msg_fetched", {
          added: Number(result.added || 0),
          updated: Number(result.updated || 0),
          total: Number(result.total || 0),
          enriched: Number(enrichment.changed || 0),
        }));
        await refreshItems();
      } else if (job.error) {
        setError(String(job.error || ""));
      }
      stopFetchPolling();
    }

    function startFetchPolling() {
      stopFetchPolling();
      state.fetchPollTimer = window.setInterval(() => {
        checkFetchStatus().catch((e) => setError(e.message || String(e)));
      }, 1500);
      checkFetchStatus().catch((e) => setError(e.message || String(e)));
    }

    document.getElementById("fetchNow").addEventListener("click", runFetch);
    document.getElementById("refreshNow").addEventListener("click", async () => {
      setError(""); setMessage("");
      await refreshItems();
    });
    document.getElementById("pushNow").addEventListener("click", pushNow);
    document.getElementById("applyFilters").addEventListener("click", applyFilters);
    document.getElementById("clearFilters").addEventListener("click", clearFilters);
    document.getElementById("openProgressSettings").addEventListener("click", () => togglePanelBox("progressSettingsBox"));
    document.getElementById("openProgressSubscriptions").addEventListener("click", () => togglePanelBox("progressSubscriptionsBox"));
    document.getElementById("saveProgressSettings").addEventListener("click", async () => {
      try { await saveProgressSettings(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("reloadProgressSettings").addEventListener("click", async () => {
      try { await loadProgressSettings(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("saveProgressSubscription").addEventListener("click", async () => {
      try { await saveProgressSubscription(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("runProgressSubscriptions").addEventListener("click", async () => {
      try { await runProgressSubscriptions(); } catch (e) { setError(e.message || String(e)); }
    });
    document.getElementById("progressSubscriptionList").addEventListener("click", async (event) => {
      const target = event.target;
      if (!target || !(target instanceof HTMLElement)) return;
      const btn = target.closest("button");
      if (!btn) return;
      const subId = String(btn.getAttribute("data-id") || "").trim();
      if (!subId) return;
      try {
        if (btn.classList.contains("sub-apply")) {
          applyProgressSubscription(subId);
        } else if (btn.classList.contains("sub-run")) {
          await runProgressSubscriptions(subId);
        } else if (btn.classList.contains("sub-delete")) {
          await deleteProgressSubscription(subId);
        } else if (btn.classList.contains("sub-toggle")) {
          const enabledNow = btn.getAttribute("data-enabled") === "1";
          await toggleProgressSubscription(subId, enabledNow);
        }
      } catch (e) {
        setError(e.message || String(e));
      }
    });
    document.getElementById("searchQ").addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        applyFilters().catch((e) => setError(e.message || String(e)));
      }
    });
    document.getElementById("langToggle").addEventListener("click", () => {
      state.lang = state.lang === "zh-CN" ? "en-US" : "zh-CN";
      localStorage.setItem("panel_lang", state.lang);
      applyI18n();
    });
    document.getElementById("themeToggle").addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      localStorage.setItem("panel_theme", state.theme);
      applyTheme();
      renderCards();
    });

    applyProgressMode();
    initPageShellMotion();

    (async function boot() {
      applyTheme();
      syncFromUrl();
      await loadSources();
      await loadProgressSettings();
      await loadProgressSubscriptions();
      applyI18n();
      await refreshItems();
      await checkFetchStatus().catch(() => {});
    })().catch((e) => setError(e.message || String(e)));
  </script>
</body>
</html>
"""






