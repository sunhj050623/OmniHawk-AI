# coding=utf-8
"""
Interactive paper dashboard server for omnihawk_ai.

Features:
- Manual trigger for `python -m omnihawk_ai`
- Update crawl interval by rewriting `/tmp/crontab`
- Read arXiv paper metadata + insights from RSS sqlite db
- Render paper cards in a lightweight web UI
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import mimetypes
import os
import re
import shlex
import sqlite3
import smtplib
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.mime.text import MIMEText
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse

from omnihawk_ai.ai.client import AIClient
from omnihawk_ai.web.panel_templates import (
    build_deep_analysis_html,
    build_home_html,
    build_panel_html_v2,
    build_progress_html,
    build_settings_html,
)
from omnihawk_ai.web.progress_repo import AIProgressRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INTERVAL_MINUTES = 30
MAX_LOG_LINES = 300
DEFAULT_PAPER_MAX_PER_RUN = 20
DEFAULT_PRIMARY_CATEGORY = "cs.AI"
PROGRESS_SCOPES: Tuple[str, ...] = (
    "frontier",
    "market_finance",
    "industry_report",
    "policy_safety",
    "oss_signal",
)
PROGRESS_SCOPE_ALIAS_MAP: Dict[str, str] = {
    "progress": "frontier",
    "finance": "market_finance",
    "market-finance": "market_finance",
    "reports": "industry_report",
    "industry-reports": "industry_report",
    "industry_reports": "industry_report",
    "policy": "policy_safety",
    "policy-safety": "policy_safety",
    "policy_safety": "policy_safety",
    "oss": "oss_signal",
    "oss-dev": "oss_signal",
    "oss_signal": "oss_signal",
}
PROGRESS_SCOPE_KIND_MAP: Dict[str, str] = {
    "frontier": "official_blog,official_site",
    "market_finance": "market_finance",
    "industry_report": "industry_report",
    "policy_safety": "policy_safety",
    "oss_signal": "oss_signal",
}
PROGRESS_SCOPE_NAME_MAP_ZH: Dict[str, str] = {
    "frontier": "AI 前沿雷达",
    "market_finance": "AI 财经信息",
    "industry_report": "AI 产业报告",
    "policy_safety": "AI 政策与安全",
    "oss_signal": "AI 开源生态与开发者信号",
}
PROGRESS_AUTO_MIN_INTERVAL = 5
PROGRESS_AUTO_MAX_INTERVAL = 24 * 60
PROGRESS_AUTO_DEFAULT_INTERVAL = 60
PROGRESS_FETCH_STALE_TIMEOUT_SECONDS = 20 * 60
PROGRESS_FETCH_SYNC_ENRICH_LIMIT = 0
PAPER_LIST_SYNC_ENRICH_LIMIT = 0
PAPER_FETCH_STALE_TIMEOUT_SECONDS = 3 * 60 * 60
NOTIFY_CHANNELS: Tuple[str, ...] = (
    "feishu",
    "wework",
    "wechat",
    "telegram",
    "dingtalk",
    "ntfy",
    "bark",
    "slack",
    "email",
)
NOTIFY_CHANNEL_SET = set(NOTIFY_CHANNELS)
NOTIFY_CHANNEL_DEFAULT = "feishu"
DEFAULT_NTFY_SERVER_URL = "https://ntfy.sh"
SUBSCRIPTION_STRATEGIES: Tuple[str, ...] = ("daily", "incremental", "realtime")
SUBSCRIPTION_STRATEGY_SET = set(SUBSCRIPTION_STRATEGIES)
SUBSCRIPTION_STRATEGY_DEFAULT = "incremental"
ARXIV_PRIMARY_CATEGORIES = [
    "cs.AI",
    "cs.CL",
    "cs.CV",
    "cs.LG",
    "cs.RO",
    "cs.IR",
    "cs.NE",
    "cs.SE",
    "cs.CR",
    "cs.DB",
    "cs.DC",
    "cs.HC",
    "cs.PL",
    "cs.CY",
]
ARXIV_PRIMARY_CATEGORY_SET = set(ARXIV_PRIMARY_CATEGORIES)
DEEP_ANALYSIS_TEMPLATE_PATH = PROJECT_ROOT / "templates.md"
DEFAULT_DEEP_ANALYSIS_TEMPLATE = """# 深入分析模板（默认）

请围绕以下角度进行严谨分析：
1. 研究问题与背景：明确论文要解决的问题、应用场景、与已有工作的关键差异。
2. 方法机制：拆解核心模块与信息流，指出关键设计选择及其动机。
3. 理论与公式：若论文涉及理论推导或关键公式，给出 LaTeX 形式的核心表达，并解释变量含义与直觉。
4. 实验设计：数据集、指标、对比基线、消融实验是否充分。
5. 结果与证据：结论是否被数据支撑，是否存在统计显著性或评估偏差风险。
6. 可复现性：代码、数据、训练细节、超参数、算力成本是否可复现。
7. 局限与风险：失败案例、边界条件、潜在偏见与安全风险。
8. 应用价值：落地价值、部署复杂度、适用条件。
9. 后续研究建议：给出可执行的后续实验方向。
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_load_json(text: Optional[str]) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def parse_interval_from_cron(cron_expr: str) -> Optional[int]:
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return None

    minute, hour, day, month, weekday = parts
    if day != "*" or month != "*" or weekday != "*":
        return None

    if minute.startswith("*/") and hour == "*":
        try:
            value = int(minute[2:])
            if 1 <= value < 60:
                return value
        except ValueError:
            return None

    if minute == "0" and hour == "*":
        return 60

    if minute == "0" and hour.startswith("*/"):
        try:
            hours = int(hour[2:])
            if 1 <= hours <= 23:
                return hours * 60
        except ValueError:
            return None

    if minute == "0" and hour == "0":
        return 1440

    return None


def interval_to_cron(interval_minutes: int) -> str:
    if interval_minutes < 1:
        raise ValueError("interval_minutes must be >= 1")

    if interval_minutes < 60:
        return f"*/{interval_minutes} * * * *"

    if interval_minutes == 60:
        return "0 * * * *"

    if interval_minutes == 1440:
        return "0 0 * * *"

    if interval_minutes % 60 == 0 and interval_minutes < 1440:
        return f"0 */{interval_minutes // 60} * * *"

    raise ValueError("interval_minutes must be <60, or divisible by 60")


def extract_arxiv_id(text: str) -> str:
    if not text:
        return ""
    match = re.search(
        r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:)(\d{4}\.\d{4,5}(?:v\d+)?)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return ""


def clean_arxiv_abstract(text: str) -> str:
    """Remove arXiv RSS boilerplate prefix from abstract text."""
    if not text:
        return ""
    value = str(text).strip()
    value = re.sub(
        r"^\s*arxiv:\s*\d{4}\.\d{4,5}(?:v\d+)?\s+announce\s+type:\s*\w+\s+abstract:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"^\s*abstract:\s*", "", value, flags=re.IGNORECASE)
    return value.strip()


def looks_like_chinese_text(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def normalize_subtopics_text(value: str) -> str:
    topics = [v.strip() for v in str(value or "").split(",") if v.strip()]
    # Keep input order while removing duplicates.
    unique: List[str] = []
    seen = set()
    for topic in topics:
        key = topic.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(topic)
    return ", ".join(unique)


def normalize_model_name(value: str) -> str:
    model = str(value or "").strip()
    if not model:
        return ""
    lowered = model.lower()
    if "/" in model and not lowered.startswith("http://") and not lowered.startswith("https://"):
        model = model.split("/")[-1].strip()
    return model


def normalize_notify_channel(value: Any, default: str = NOTIFY_CHANNEL_DEFAULT) -> str:
    channel = str(value or default).strip().lower()
    if channel not in NOTIFY_CHANNEL_SET:
        channel = default
    return channel


def normalize_subscription_strategy(
    value: Any,
    default: str = SUBSCRIPTION_STRATEGY_DEFAULT,
) -> str:
    raw = str(value or "").strip().lower()
    alias = {
        "daily": "daily",
        "incremental": "incremental",
        "inc": "incremental",
        "real-time": "realtime",
        "real_time": "realtime",
        "realtime": "realtime",
    }
    normalized = alias.get(raw, raw)
    fallback = str(default or SUBSCRIPTION_STRATEGY_DEFAULT).strip().lower()
    if fallback not in SUBSCRIPTION_STRATEGY_SET:
        fallback = SUBSCRIPTION_STRATEGY_DEFAULT
    if normalized not in SUBSCRIPTION_STRATEGY_SET:
        normalized = fallback
    return normalized


def subscription_strategy_label(strategy: Any) -> str:
    key = normalize_subscription_strategy(strategy, default=SUBSCRIPTION_STRATEGY_DEFAULT)
    labels = {
        "daily": "daily 当日汇总",
        "incremental": "incremental 增量监控",
        "realtime": "real-time 实时告警",
    }
    return labels.get(key, labels[SUBSCRIPTION_STRATEGY_DEFAULT])


def to_runtime_model_name(value: str, api_base: str = "") -> str:
    model = str(value or "").strip()
    if not model:
        return ""
    lowered = model.lower()
    if "/" in model and not lowered.startswith("http://") and not lowered.startswith("https://"):
        return model
    # Most compatible path for custom OpenAI-compatible endpoints (e.g. novaapi).
    return f"openai/{model}"


def normalize_analysis_language(value: Any, default: str = "Chinese") -> str:
    alias: Dict[str, str] = {
        "en": "English",
        "en-us": "English",
        "english": "English",
        "zh": "Chinese",
        "zh-cn": "Chinese",
        "zh-hans": "Chinese",
        "chinese": "Chinese",
        "simplified-chinese": "Chinese",
        "zh-hant": "Traditional Chinese",
        "zh-tw": "Traditional Chinese",
        "zh-hk": "Traditional Chinese",
        "traditional-chinese": "Traditional Chinese",
        "ko": "Korean",
        "korean": "Korean",
        "ja": "Japanese",
        "japanese": "Japanese",
        "fr": "French",
        "french": "French",
    }
    fallback = str(default or "").strip()
    raw = str(value or "").strip()
    candidate = raw or fallback
    if not candidate:
        return ""
    lookup = candidate.lower().replace("_", "-")
    if lookup in alias:
        return alias[lookup]
    if not raw and fallback:
        fallback_mapped = alias.get(fallback.lower().replace("_", "-"), "")
        if fallback_mapped:
            return fallback_mapped
    if candidate == candidate.upper() and len(candidate) <= 8:
        return candidate
    return " ".join(part[:1].upper() + part[1:] for part in candidate.split())


def language_cache_key(value: Any) -> str:
    normalized = normalize_analysis_language(value, default="")
    if not normalized:
        return "zh"
    lookup = normalized.lower().replace("_", "-")
    alias = {
        "english": "en",
        "chinese": "zh",
        "traditional chinese": "zh-hant",
        "korean": "ko",
        "japanese": "ja",
        "french": "fr",
    }
    mapped = alias.get(lookup)
    if mapped:
        return mapped
    safe = re.sub(r"[^a-z0-9\\-]+", "-", lookup).strip("-")
    return safe or "zh"


def is_english_language(value: Any) -> bool:
    return language_cache_key(value) == "en"


def is_chinese_language(value: Any) -> bool:
    key = language_cache_key(value)
    return key == "zh" or key.startswith("zh-")


def split_subtopics(value: str) -> List[str]:
    return [v.lower() for v in [x.strip() for x in str(value or "").split(",")] if v]


def compose_research_topic(primary_category: str, subtopics_text: str, fallback: str = "") -> str:
    category = str(primary_category or "").strip()
    subtopics = normalize_subtopics_text(subtopics_text)
    if category and subtopics:
        return f"{category} / {subtopics}"
    if category:
        return category
    if subtopics:
        return subtopics
    return str(fallback or "").strip()


def parse_bool_text(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def parse_int_value(value: Any, minimum: int, maximum: int) -> Optional[int]:
    try:
        parsed = int(str(value).strip())
    except Exception:
        return None
    return max(minimum, min(maximum, parsed))


def load_deep_analysis_template_text() -> str:
    try:
        raw = DEEP_ANALYSIS_TEMPLATE_PATH.read_text(encoding="utf-8")
    except Exception:
        raw = ""
    text = str(raw or "").strip()
    if text:
        return text
    return DEFAULT_DEEP_ANALYSIS_TEMPLATE


def normalize_panel_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    raw = filters or {}
    normalized: Dict[str, Any] = {}
    normalized["q"] = str(raw.get("q", "") or "").strip()
    normalized["author"] = str(raw.get("author", "") or "").strip()
    normalized["affiliation"] = str(raw.get("affiliation", "") or "").strip()
    normalized["tag"] = str(raw.get("tag", "") or "").strip()
    normalized["category"] = str(raw.get("category", "") or "").strip()
    normalized["source_id"] = str(raw.get("source_id", "") or "").strip()
    normalized["region"] = str(raw.get("region", "") or "").strip().lower()
    normalized["event_type"] = str(raw.get("event_type", "") or "").strip().lower()
    normalized["date_from"] = str(raw.get("date_from", "") or "").strip()
    normalized["date_to"] = str(raw.get("date_to", "") or "").strip()
    normalized["has_doi"] = str(raw.get("has_doi", "any") or "any").strip().lower()
    if normalized["has_doi"] not in {"any", "yes", "no"}:
        normalized["has_doi"] = "any"
    score_min = parse_int_value(raw.get("score_min"), 0, 100)
    score_max = parse_int_value(raw.get("score_max"), 0, 100)
    normalized["score_min"] = score_min
    normalized["score_max"] = score_max
    return normalized


def normalize_progress_scope(value: Any, default: str = "frontier") -> str:
    text = str(value or "").strip().lower()
    text = PROGRESS_SCOPE_ALIAS_MAP.get(text, text)
    return text if text in PROGRESS_SCOPES else default


def normalize_progress_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    raw = filters if isinstance(filters, dict) else {}
    # Keep a superset of filter fields so paper/progress pages share one schema.
    return normalize_panel_filters(raw)


def parse_iso_utc(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def has_any_keyword(text: Any, keywords: List[str]) -> bool:
    content = str(text or "").lower()
    if not content:
        return False
    return any(str(word or "").strip().lower() in content for word in keywords if str(word or "").strip())


def is_realtime_priority_progress_item(item: Dict[str, Any], scope: str) -> bool:
    event_type = str(item.get("event_type", "") or "").strip().lower()
    if event_type in {"release", "benchmark", "safety"}:
        return True
    title = str(item.get("title", "") or "")
    summary = str(item.get("summary", "") or "")
    tags = item.get("tags") if isinstance(item.get("tags"), list) else []
    tag_text = " ".join(str(x or "") for x in tags)
    content = " ".join([title, summary, tag_text]).lower()

    if scope == "market_finance":
        finance_keywords = [
            "earnings",
            "guidance",
            "capex",
            "funding",
            "raised",
            "raises",
            "融资",
            "并购",
            "merger",
            "acquisition",
            "m&a",
            "ipo",
        ]
        return has_any_keyword(content, finance_keywords)

    if scope == "policy_safety":
        policy_keywords = [
            "regulation",
            "policy",
            "law",
            "act",
            "compliance",
            "ban",
            "governance",
            "政策",
            "监管",
            "合规",
            "安全",
        ]
        return has_any_keyword(content, policy_keywords)

    if scope == "industry_report":
        report_keywords = [
            "report",
            "white paper",
            "forecast",
            "outlook",
            "survey",
            "报告",
            "白皮书",
            "展望",
        ]
        return has_any_keyword(content, report_keywords)

    if scope in {"frontier", "oss_signal"}:
        return has_any_keyword(
            content,
            [
                "gpt-",
                "claude",
                "gemini",
                "qwen",
                "deepseek",
                "glm",
                "llama",
                "mistral",
                "open source",
                "开源",
            ],
        )
    return False


def is_realtime_priority_paper(paper: Dict[str, Any]) -> bool:
    score = parse_int_value(paper.get("recommendation_score"), 0, 100) or 0
    title = str(paper.get("title", "") or "")
    abstract = str(paper.get("abstract", "") or "")
    content = f"{title} {abstract}".lower()
    conference_keywords = [
        "neurips",
        "icml",
        "iclr",
        "cvpr",
        "eccv",
        "iccv",
        "acl",
        "emnlp",
        "naacl",
        "kdd",
        "aaai",
    ]
    top_conf = has_any_keyword(content, conference_keywords)
    if top_conf and score >= 60:
        return True
    return score >= 85


class PanelSettingsStore:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "panel_settings.json"
        self._lock = threading.RLock()
        self.defaults: Dict[str, Any] = {
            "research_topic": "cs.AI / agent, llm",
            "paper_primary_category": DEFAULT_PRIMARY_CATEGORY,
            "paper_subtopics": "agent, llm",
            "analysis_language": "Chinese",
            "ai_model": "",
            "ai_api_base": "",
            "ai_api_key": "",
            "paper_max_papers_per_run": DEFAULT_PAPER_MAX_PER_RUN,
            "hide_unanalyzed": True,
            "feishu_webhook_url": "",
            "wework_webhook_url": "",
            "wework_msg_type": "markdown",
            "dingtalk_webhook_url": "",
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "ntfy_server_url": DEFAULT_NTFY_SERVER_URL,
            "ntfy_topic": "",
            "ntfy_token": "",
            "bark_url": "",
            "slack_webhook_url": "",
            "email_from": "",
            "email_password": "",
            "email_to": "",
            "email_smtp_server": "smtp.qq.com",
            "email_smtp_port": "465",
            # Unified page settings union fields (paper page keeps independent values).
            "max_per_source": 20,
            "source_ids": [],
            "notify_channel": NOTIFY_CHANNEL_DEFAULT,
            "notify_limit": 8,
            "query": {
                "q": "",
                "author": "",
                "affiliation": "",
                "tag": "",
                "category": "",
                "source_id": "",
                "region": "",
                "event_type": "",
                "date_from": "",
                "date_to": "",
                "has_doi": "any",
                "score_min": None,
                "score_max": None,
            },
            "auto_enabled": False,
            "auto_interval_minutes": PROGRESS_AUTO_DEFAULT_INTERVAL,
            "auto_push_enabled": False,
        }

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(self.defaults)
        merged.update({k: v for k, v in data.items() if k in self.defaults})

        primary_category = str(merged.get("paper_primary_category", "") or "").strip()
        if primary_category and primary_category not in ARXIV_PRIMARY_CATEGORY_SET:
            primary_category = DEFAULT_PRIMARY_CATEGORY
        merged["paper_primary_category"] = primary_category
        merged["paper_subtopics"] = normalize_subtopics_text(str(merged.get("paper_subtopics", "") or ""))

        merged["research_topic"] = compose_research_topic(
            merged.get("paper_primary_category", ""),
            merged.get("paper_subtopics", ""),
            fallback=str(merged.get("research_topic", "") or ""),
        )
        merged["analysis_language"] = normalize_analysis_language(
            merged.get("analysis_language", "Chinese"),
            default="Chinese",
        )
        merged["ai_model"] = normalize_model_name(str(merged.get("ai_model", "") or "").strip())
        merged["ai_api_base"] = str(merged.get("ai_api_base", "") or "").strip()
        merged["ai_api_key"] = str(merged.get("ai_api_key", "") or "").strip()
        merged["feishu_webhook_url"] = str(merged.get("feishu_webhook_url", "") or "").strip()
        merged["wework_webhook_url"] = str(merged.get("wework_webhook_url", "") or "").strip()
        wework_msg_type = str(merged.get("wework_msg_type", "markdown") or "markdown").strip().lower()
        if wework_msg_type not in {"markdown", "text"}:
            wework_msg_type = "markdown"
        merged["wework_msg_type"] = wework_msg_type
        merged["dingtalk_webhook_url"] = str(merged.get("dingtalk_webhook_url", "") or "").strip()
        merged["telegram_bot_token"] = str(merged.get("telegram_bot_token", "") or "").strip()
        merged["telegram_chat_id"] = str(merged.get("telegram_chat_id", "") or "").strip()
        merged["ntfy_server_url"] = (
            str(merged.get("ntfy_server_url", "") or "").strip() or DEFAULT_NTFY_SERVER_URL
        )
        merged["ntfy_topic"] = str(merged.get("ntfy_topic", "") or "").strip()
        merged["ntfy_token"] = str(merged.get("ntfy_token", "") or "").strip()
        merged["bark_url"] = str(merged.get("bark_url", "") or "").strip()
        merged["slack_webhook_url"] = str(merged.get("slack_webhook_url", "") or "").strip()
        merged["email_from"] = str(merged.get("email_from", "") or "").strip()
        merged["email_password"] = str(merged.get("email_password", "") or "").strip()
        merged["email_to"] = str(merged.get("email_to", "") or "").strip()
        merged["email_smtp_server"] = str(merged.get("email_smtp_server", "") or "").strip() or "smtp.qq.com"
        merged["email_smtp_port"] = str(merged.get("email_smtp_port", "") or "").strip() or "465"
        merged["max_per_source"] = parse_int_value(merged.get("max_per_source"), 1, 120) or 20
        source_ids_raw = merged.get("source_ids")
        source_ids: List[str] = []
        if isinstance(source_ids_raw, list):
            for value in source_ids_raw:
                text = str(value or "").strip()
                if text and text not in source_ids:
                    source_ids.append(text)
        merged["source_ids"] = source_ids
        merged["notify_channel"] = normalize_notify_channel(merged.get("notify_channel"))
        merged["notify_limit"] = parse_int_value(merged.get("notify_limit"), 1, 30) or 8
        merged["query"] = normalize_panel_filters(
            merged.get("query") if isinstance(merged.get("query"), dict) else {}
        )
        merged["auto_enabled"] = bool(parse_bool_text(merged.get("auto_enabled"), False))
        merged["auto_interval_minutes"] = (
            parse_int_value(
                merged.get("auto_interval_minutes"),
                PROGRESS_AUTO_MIN_INTERVAL,
                PROGRESS_AUTO_MAX_INTERVAL,
            )
            or PROGRESS_AUTO_DEFAULT_INTERVAL
        )
        merged["auto_push_enabled"] = bool(parse_bool_text(merged.get("auto_push_enabled"), False))

        try:
            max_run = int(merged.get("paper_max_papers_per_run") or DEFAULT_PAPER_MAX_PER_RUN)
        except Exception:
            max_run = DEFAULT_PAPER_MAX_PER_RUN
        merged["paper_max_papers_per_run"] = max(1, min(max_run, 200))
        merged["hide_unanalyzed"] = bool(merged.get("hide_unanalyzed", True))
        return merged

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return self._normalize(dict(self.defaults))
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return self._normalize(data)
            except Exception:
                pass
            return self._normalize(dict(self.defaults))

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            current = self.load()
            current.update(data or {})
            normalized = self._normalize(current)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return normalized


class PanelActionStore:
    """Persist user actions for paper cards (favorite / ignored / note / tags)."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "panel_actions.json"
        self._lock = threading.RLock()

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        normalized: Dict[str, Any] = {
            "favorite": bool(item.get("favorite", False)),
            "ignored": bool(item.get("ignored", False)),
            "note": str(item.get("note", "") or "").strip(),
            "tags": [],
            "created_at": str(item.get("created_at", "") or "").strip() or now,
            "updated_at": str(item.get("updated_at", "") or "").strip() or now,
            "favorite_at": str(item.get("favorite_at", "") or "").strip(),
            "ignored_at": str(item.get("ignored_at", "") or "").strip(),
        }
        raw_tags = item.get("tags") or []
        if isinstance(raw_tags, list):
            normalized["tags"] = [str(v).strip() for v in raw_tags if str(v).strip()]
        elif isinstance(raw_tags, str):
            normalized["tags"] = [v.strip() for v in raw_tags.split(",") if v.strip()]
        return normalized

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        items: Dict[str, Any] = {}
        raw = data.get("items") if isinstance(data, dict) else {}
        if isinstance(raw, dict):
            for key, item in raw.items():
                if not isinstance(item, dict):
                    continue
                paper_key = str(key or "").strip()
                if not paper_key:
                    continue
                items[paper_key] = self._normalize_item(item)
        return {"items": items}

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return {"items": {}}
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    return self._normalize(raw)
            except Exception:
                pass
            return {"items": {}}

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            normalized = self._normalize(data or {})
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return normalized

    def set_action(
        self,
        paper_key: str,
        favorite: Optional[bool] = None,
        ignored: Optional[bool] = None,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        paper_key = str(paper_key or "").strip()
        if not paper_key:
            raise ValueError("paper_key is required")

        with self._lock:
            data = self.load()
            items = data.setdefault("items", {})
            current = self._normalize_item(items.get(paper_key, {}))
            now = utc_now_iso()

            if favorite is not None:
                current["favorite"] = bool(favorite)
                current["favorite_at"] = now if current["favorite"] else ""
                if current["favorite"]:
                    current["ignored"] = False
                    current["ignored_at"] = ""

            if ignored is not None:
                current["ignored"] = bool(ignored)
                current["ignored_at"] = now if current["ignored"] else ""
                if current["ignored"]:
                    current["favorite"] = False
                    current["favorite_at"] = ""

            if note is not None:
                current["note"] = str(note or "").strip()

            if tags is not None:
                current["tags"] = [str(v).strip() for v in tags if str(v).strip()]

            current["updated_at"] = now
            if not current.get("created_at"):
                current["created_at"] = now

            # Drop completely empty records to keep file clean.
            if (
                not current.get("favorite")
                and not current.get("ignored")
                and not current.get("note")
                and not current.get("tags")
            ):
                items.pop(paper_key, None)
                saved_item: Dict[str, Any] = {
                    "favorite": False,
                    "ignored": False,
                    "note": "",
                    "tags": [],
                    "updated_at": now,
                }
            else:
                items[paper_key] = current
                saved_item = current

            self.save(data)
            return saved_item


class PanelSubscriptionStore:
    """Persist saved filter subscriptions for notification push."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "panel_subscriptions.json"
        self._lock = threading.RLock()

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        filters = normalize_panel_filters(item.get("filters") if isinstance(item, dict) else {})
        normalized: Dict[str, Any] = {
            "id": str(item.get("id", "") or "").strip() if isinstance(item, dict) else "",
            "name": str(item.get("name", "") or "").strip() if isinstance(item, dict) else "",
            "channel": str(item.get("channel", NOTIFY_CHANNEL_DEFAULT) or NOTIFY_CHANNEL_DEFAULT).strip().lower()
            if isinstance(item, dict)
            else NOTIFY_CHANNEL_DEFAULT,
            "enabled": bool(item.get("enabled", True)) if isinstance(item, dict) else True,
            "filters": filters,
            "mode": str(item.get("mode", "all") or "all").strip().lower() if isinstance(item, dict) else "all",
            "strategy": normalize_subscription_strategy(item.get("strategy"), default=SUBSCRIPTION_STRATEGY_DEFAULT)
            if isinstance(item, dict)
            else SUBSCRIPTION_STRATEGY_DEFAULT,
            "sort_by": str(item.get("sort_by", "score") or "score").strip().lower()
            if isinstance(item, dict)
            else "score",
            "sort_order": str(item.get("sort_order", "desc") or "desc").strip().lower()
            if isinstance(item, dict)
            else "desc",
            "history": str(item.get("history", "all") or "all").strip().lower() if isinstance(item, dict) else "all",
            "limit": parse_int_value(item.get("limit"), 1, 500) if isinstance(item, dict) else 120,
            "created_at": str(item.get("created_at", "") or "").strip() if isinstance(item, dict) else "",
            "updated_at": str(item.get("updated_at", "") or "").strip() if isinstance(item, dict) else "",
            "last_notified_at": str(item.get("last_notified_at", "") or "").strip()
            if isinstance(item, dict)
            else "",
            "last_match_count": parse_int_value(item.get("last_match_count"), 0, 1000000)
            if isinstance(item, dict)
            else 0,
            "sent_keys": [],
        }
        if normalized["channel"] not in NOTIFY_CHANNEL_SET:
            normalized["channel"] = NOTIFY_CHANNEL_DEFAULT
        if normalized["mode"] not in {"all", "favorites", "ignored"}:
            normalized["mode"] = "all"
        normalized["strategy"] = normalize_subscription_strategy(
            normalized.get("strategy"),
            default=SUBSCRIPTION_STRATEGY_DEFAULT,
        )
        if normalized["sort_by"] not in {"score", "time", "title"}:
            normalized["sort_by"] = "score"
        if normalized["sort_order"] not in {"asc", "desc"}:
            normalized["sort_order"] = "desc"
        if normalized["history"] not in {"latest", "all"}:
            normalized["history"] = "all"
        if not normalized["limit"]:
            normalized["limit"] = 120
        if not normalized["id"]:
            normalized["id"] = uuid.uuid4().hex[:12]
        if not normalized["name"]:
            base = filters.get("q") or filters.get("category") or "订阅"
            normalized["name"] = f"{base}".strip()[:48] or "订阅"
        raw_sent_keys = item.get("sent_keys") if isinstance(item, dict) else []
        if isinstance(raw_sent_keys, list):
            seen = set()
            out: List[str] = []
            for key in raw_sent_keys:
                text = str(key or "").strip()
                if not text or text in seen:
                    continue
                seen.add(text)
                out.append(text)
                if len(out) >= 2000:
                    break
            normalized["sent_keys"] = out
        if not normalized["created_at"]:
            normalized["created_at"] = now
        if not normalized["updated_at"]:
            normalized["updated_at"] = now
        return normalized

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        raw = data.get("items") if isinstance(data, dict) else []
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                items.append(self._normalize_item(entry))
        by_id: Dict[str, Dict[str, Any]] = {}
        for item in items:
            item_id = str(item.get("id", "") or "").strip()
            if not item_id:
                continue
            existing = by_id.get(item_id)
            if not existing or str(item.get("updated_at", "")) >= str(existing.get("updated_at", "")):
                by_id[item_id] = item
        by_signature: Dict[str, Dict[str, Any]] = {}
        for item in by_id.values():
            signature = self._build_signature(
                channel=str(item.get("channel", NOTIFY_CHANNEL_DEFAULT) or NOTIFY_CHANNEL_DEFAULT),
                filters=item.get("filters") if isinstance(item.get("filters"), dict) else {},
                mode=str(item.get("mode", "all") or "all"),
                strategy=normalize_subscription_strategy(
                    item.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                ),
                sort_by=str(item.get("sort_by", "score") or "score"),
                sort_order=str(item.get("sort_order", "desc") or "desc"),
                history=str(item.get("history", "all") or "all"),
                limit=parse_int_value(item.get("limit"), 1, 500) or 120,
            )
            existing = by_signature.get(signature)
            if not existing or str(item.get("updated_at", "")) >= str(existing.get("updated_at", "")):
                by_signature[signature] = item
        dedup = list(by_signature.values())
        dedup.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)
        return {"items": dedup}

    def _build_signature(
        self,
        *,
        channel: str,
        filters: Dict[str, Any],
        mode: str,
        strategy: str,
        sort_by: str,
        sort_order: str,
        history: str,
        limit: int,
    ) -> str:
        payload = {
            "channel": str(channel or NOTIFY_CHANNEL_DEFAULT).strip().lower(),
            "filters": normalize_panel_filters(filters if isinstance(filters, dict) else {}),
            "mode": str(mode or "all").strip().lower(),
            "strategy": normalize_subscription_strategy(strategy, default=SUBSCRIPTION_STRATEGY_DEFAULT),
            "sort_by": str(sort_by or "score").strip().lower(),
            "sort_order": str(sort_order or "desc").strip().lower(),
            "history": str(history or "all").strip().lower(),
            "limit": parse_int_value(limit, 1, 500) or 120,
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return {"items": []}
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    return self._normalize(raw)
            except Exception:
                pass
            return {"items": []}

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            normalized = self._normalize(data or {})
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return normalized

    def upsert(
        self,
        name: str,
        channel: str,
        filters: Dict[str, Any],
        enabled: bool = True,
        sub_id: str = "",
        mode: str = "all",
        strategy: str = SUBSCRIPTION_STRATEGY_DEFAULT,
        sort_by: str = "score",
        sort_order: str = "desc",
        history: str = "all",
        limit: int = 120,
    ) -> Dict[str, Any]:
        with self._lock:
            data = self.load()
            now = utc_now_iso()
            items = data.setdefault("items", [])
            existing_idx = -1
            target_signature = self._build_signature(
                channel=channel,
                filters=filters,
                mode=mode,
                strategy=strategy,
                sort_by=sort_by,
                sort_order=sort_order,
                history=history,
                limit=limit,
            )
            for i, item in enumerate(items):
                if str(item.get("id", "")) == str(sub_id or ""):
                    existing_idx = i
                    break
            if existing_idx < 0 and not str(sub_id or "").strip():
                for i, item in enumerate(items):
                    item_signature = self._build_signature(
                        channel=str(item.get("channel", NOTIFY_CHANNEL_DEFAULT) or NOTIFY_CHANNEL_DEFAULT),
                        filters=item.get("filters") if isinstance(item.get("filters"), dict) else {},
                        mode=str(item.get("mode", "all") or "all"),
                        strategy=normalize_subscription_strategy(
                            item.get("strategy"),
                            default=SUBSCRIPTION_STRATEGY_DEFAULT,
                        ),
                        sort_by=str(item.get("sort_by", "score") or "score"),
                        sort_order=str(item.get("sort_order", "desc") or "desc"),
                        history=str(item.get("history", "all") or "all"),
                        limit=parse_int_value(item.get("limit"), 1, 500) or 120,
                    )
                    if item_signature == target_signature:
                        existing_idx = i
                        break
            if existing_idx >= 0:
                current = dict(items[existing_idx])
                current.update(
                    {
                        "name": name,
                        "channel": channel,
                        "filters": filters,
                        "enabled": enabled,
                        "mode": mode,
                        "strategy": strategy,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "history": history,
                        "limit": limit,
                        "updated_at": now,
                    }
                )
                normalized_item = self._normalize_item(current)
                items[existing_idx] = normalized_item
            else:
                normalized_item = self._normalize_item(
                    {
                        "id": sub_id or uuid.uuid4().hex[:12],
                        "name": name,
                        "channel": channel,
                        "filters": filters,
                        "enabled": enabled,
                        "mode": mode,
                        "strategy": strategy,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "history": history,
                        "limit": limit,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                items.append(normalized_item)
            self.save(data)
            return normalized_item

    def delete(self, sub_id: str) -> bool:
        sub_id = str(sub_id or "").strip()
        if not sub_id:
            return False
        with self._lock:
            data = self.load()
            items = data.get("items") or []
            if not isinstance(items, list):
                return False
            remain = [item for item in items if str(item.get("id", "")) != sub_id]
            changed = len(remain) != len(items)
            if changed:
                self.save({"items": remain})
            return changed

    def mark_notified(self, sub_id: str, sent_keys: List[str], match_count: int) -> Optional[Dict[str, Any]]:
        sub_id = str(sub_id or "").strip()
        with self._lock:
            data = self.load()
            items = data.get("items") or []
            now = utc_now_iso()
            for idx, item in enumerate(items):
                if str(item.get("id", "")) != sub_id:
                    continue
                current = dict(item)
                current_keys = current.get("sent_keys") or []
                if not isinstance(current_keys, list):
                    current_keys = []
                merged: List[str] = []
                seen = set()
                for key in list(sent_keys) + list(current_keys):
                    text = str(key or "").strip()
                    if not text or text in seen:
                        continue
                    seen.add(text)
                    merged.append(text)
                    if len(merged) >= 2000:
                        break
                current["sent_keys"] = merged
                current["last_notified_at"] = now
                current["last_match_count"] = max(0, int(match_count))
                current["updated_at"] = now
                normalized = self._normalize_item(current)
                items[idx] = normalized
                self.save({"items": items})
                return normalized
        return None


class ProgressPageSettingsStore:
    """Persist per-scope settings for progress pages."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "progress_page_settings.json"
        self._lock = threading.RLock()

    def _default_scope_settings(self, scope: str) -> Dict[str, Any]:
        return {
            "scope": scope,
            "max_per_source": 20,
            "fetch_workers": 6,
            "source_ids": [],
            "notify_channel": NOTIFY_CHANNEL_DEFAULT,
            "notify_limit": 8,
            "output_language": "Chinese",
            "feishu_webhook_url": "",
            "wework_webhook_url": "",
            "wework_msg_type": "markdown",
            "dingtalk_webhook_url": "",
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "ntfy_server_url": DEFAULT_NTFY_SERVER_URL,
            "ntfy_topic": "",
            "ntfy_token": "",
            "bark_url": "",
            "slack_webhook_url": "",
            "email_from": "",
            "email_password": "",
            "email_to": "",
            "email_smtp_server": "smtp.qq.com",
            "email_smtp_port": "465",
            "query": {
                "q": "",
                "source_id": "",
                "region": "",
                "event_type": "",
            },
            "auto_enabled": False,
            "auto_interval_minutes": PROGRESS_AUTO_DEFAULT_INTERVAL,
            "auto_push_enabled": False,
            "auto_last_run_at": "",
            "auto_last_status": "",
            "auto_last_message": "",
            "updated_at": utc_now_iso(),
        }

    def _normalize_scope_settings(self, scope: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        base = self._default_scope_settings(scope)
        incoming = payload if isinstance(payload, dict) else {}
        base["max_per_source"] = parse_int_value(incoming.get("max_per_source"), 1, 120) or 20
        base["fetch_workers"] = parse_int_value(incoming.get("fetch_workers"), 1, 16) or 6
        source_ids_raw = incoming.get("source_ids")
        source_ids: List[str] = []
        if isinstance(source_ids_raw, list):
            for value in source_ids_raw:
                text = str(value or "").strip()
                if text and text not in source_ids:
                    source_ids.append(text)
        base["source_ids"] = source_ids
        base["notify_channel"] = normalize_notify_channel(incoming.get("notify_channel"))
        base["notify_limit"] = parse_int_value(incoming.get("notify_limit"), 1, 30) or 8
        base["output_language"] = normalize_analysis_language(incoming.get("output_language", "Chinese"), default="Chinese")
        base["feishu_webhook_url"] = str(incoming.get("feishu_webhook_url", "") or "").strip()
        base["wework_webhook_url"] = str(incoming.get("wework_webhook_url", "") or "").strip()
        wework_msg_type = str(incoming.get("wework_msg_type", "markdown") or "markdown").strip().lower()
        if wework_msg_type not in {"markdown", "text"}:
            wework_msg_type = "markdown"
        base["wework_msg_type"] = wework_msg_type
        base["dingtalk_webhook_url"] = str(incoming.get("dingtalk_webhook_url", "") or "").strip()
        base["telegram_bot_token"] = str(incoming.get("telegram_bot_token", "") or "").strip()
        base["telegram_chat_id"] = str(incoming.get("telegram_chat_id", "") or "").strip()
        base["ntfy_server_url"] = (
            str(incoming.get("ntfy_server_url", "") or "").strip() or DEFAULT_NTFY_SERVER_URL
        )
        base["ntfy_topic"] = str(incoming.get("ntfy_topic", "") or "").strip()
        base["ntfy_token"] = str(incoming.get("ntfy_token", "") or "").strip()
        base["bark_url"] = str(incoming.get("bark_url", "") or "").strip()
        base["slack_webhook_url"] = str(incoming.get("slack_webhook_url", "") or "").strip()
        base["email_from"] = str(incoming.get("email_from", "") or "").strip()
        base["email_password"] = str(incoming.get("email_password", "") or "").strip()
        base["email_to"] = str(incoming.get("email_to", "") or "").strip()
        base["email_smtp_server"] = str(incoming.get("email_smtp_server", "") or "").strip() or "smtp.qq.com"
        base["email_smtp_port"] = str(incoming.get("email_smtp_port", "") or "").strip() or "465"
        base["query"] = normalize_progress_filters(incoming.get("query") if isinstance(incoming, dict) else {})
        base["auto_enabled"] = bool(parse_bool_text(incoming.get("auto_enabled"), False))
        base["auto_interval_minutes"] = (
            parse_int_value(
                incoming.get("auto_interval_minutes"),
                PROGRESS_AUTO_MIN_INTERVAL,
                PROGRESS_AUTO_MAX_INTERVAL,
            )
            or PROGRESS_AUTO_DEFAULT_INTERVAL
        )
        base["auto_push_enabled"] = bool(parse_bool_text(incoming.get("auto_push_enabled"), False))
        base["auto_last_run_at"] = str(incoming.get("auto_last_run_at", "") or "").strip()
        base["auto_last_status"] = str(incoming.get("auto_last_status", "") or "").strip()
        base["auto_last_message"] = str(incoming.get("auto_last_message", "") or "").strip()
        base["updated_at"] = str(incoming.get("updated_at", "") or "").strip() or utc_now_iso()
        return base

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raw_scopes = data.get("scopes") if isinstance(data, dict) else {}
        if not isinstance(raw_scopes, dict):
            raw_scopes = {}
        scopes: Dict[str, Dict[str, Any]] = {}
        for scope in PROGRESS_SCOPES:
            scopes[scope] = self._normalize_scope_settings(scope, raw_scopes.get(scope) if isinstance(raw_scopes, dict) else {})
        return {"scopes": scopes, "updated_at": utc_now_iso()}

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return self._normalize({})
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return self._normalize(data)
            except Exception:
                pass
            return self._normalize({})

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            normalized = self._normalize(data if isinstance(data, dict) else {})
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
            return normalized

    def get_scope(self, scope: str) -> Dict[str, Any]:
        key = normalize_progress_scope(scope)
        payload = self.load()
        scopes = payload.get("scopes") if isinstance(payload, dict) else {}
        if isinstance(scopes, dict) and isinstance(scopes.get(key), dict):
            return dict(scopes[key])
        return self._default_scope_settings(key)

    def save_scope(self, scope: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        key = normalize_progress_scope(scope)
        with self._lock:
            payload = self.load()
            scopes = payload.get("scopes") if isinstance(payload, dict) else {}
            if not isinstance(scopes, dict):
                scopes = {}
            current = scopes.get(key) if isinstance(scopes.get(key), dict) else {}
            merged = dict(current)
            if isinstance(updates, dict):
                merged.update(updates)
            merged["scope"] = key
            merged["updated_at"] = utc_now_iso()
            scopes[key] = self._normalize_scope_settings(key, merged)
            payload["scopes"] = scopes
            saved = self.save(payload)
            saved_scopes = saved.get("scopes") if isinstance(saved, dict) else {}
            if isinstance(saved_scopes, dict) and isinstance(saved_scopes.get(key), dict):
                return dict(saved_scopes[key])
            return self._default_scope_settings(key)

    def mark_auto_result(self, scope: str, ok: bool, message: str) -> Dict[str, Any]:
        return self.save_scope(
            scope,
            {
                "auto_last_run_at": utc_now_iso(),
                "auto_last_status": "ok" if ok else "error",
                "auto_last_message": str(message or "").strip()[:500],
            },
        )


class ProgressSubscriptionStore:
    """Persist per-scope progress subscriptions for push notifications."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "progress_subscriptions.json"
        self._lock = threading.RLock()

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        scope = normalize_progress_scope(item.get("scope", "frontier"), default="frontier")
        channel = str(item.get("channel", NOTIFY_CHANNEL_DEFAULT) or NOTIFY_CHANNEL_DEFAULT).strip().lower()
        if channel not in NOTIFY_CHANNEL_SET:
            channel = NOTIFY_CHANNEL_DEFAULT
        filters = normalize_progress_filters(item.get("filters") if isinstance(item, dict) else {})
        normalized: Dict[str, Any] = {
            "id": str(item.get("id", "") or "").strip() if isinstance(item, dict) else "",
            "scope": scope,
            "name": str(item.get("name", "") or "").strip() if isinstance(item, dict) else "",
            "channel": channel,
            "enabled": bool(item.get("enabled", True)) if isinstance(item, dict) else True,
            "filters": filters,
            "strategy": normalize_subscription_strategy(item.get("strategy"), default=SUBSCRIPTION_STRATEGY_DEFAULT)
            if isinstance(item, dict)
            else SUBSCRIPTION_STRATEGY_DEFAULT,
            "limit": parse_int_value(item.get("limit"), 1, 500) if isinstance(item, dict) else 120,
            "created_at": str(item.get("created_at", "") or "").strip() if isinstance(item, dict) else "",
            "updated_at": str(item.get("updated_at", "") or "").strip() if isinstance(item, dict) else "",
            "last_notified_at": str(item.get("last_notified_at", "") or "").strip() if isinstance(item, dict) else "",
            "last_match_count": parse_int_value(item.get("last_match_count"), 0, 1000000) if isinstance(item, dict) else 0,
            "sent_keys": [],
        }
        if not normalized["limit"]:
            normalized["limit"] = 120
        normalized["strategy"] = normalize_subscription_strategy(
            normalized.get("strategy"),
            default=SUBSCRIPTION_STRATEGY_DEFAULT,
        )
        if not normalized["id"]:
            normalized["id"] = uuid.uuid4().hex[:12]
        if not normalized["name"]:
            base = filters.get("q") or PROGRESS_SCOPE_NAME_MAP_ZH.get(scope, "AI 订阅")
            normalized["name"] = str(base or "AI 订阅").strip()[:64]
        raw_sent_keys = item.get("sent_keys") if isinstance(item, dict) else []
        if isinstance(raw_sent_keys, list):
            seen = set()
            out: List[str] = []
            for key in raw_sent_keys:
                text = str(key or "").strip()
                if not text or text in seen:
                    continue
                seen.add(text)
                out.append(text)
                if len(out) >= 3000:
                    break
            normalized["sent_keys"] = out
        if not normalized["created_at"]:
            normalized["created_at"] = now
        if not normalized["updated_at"]:
            normalized["updated_at"] = now
        return normalized

    def _build_signature(
        self,
        *,
        scope: str,
        channel: str,
        filters: Dict[str, Any],
        strategy: str,
        limit: int,
    ) -> str:
        payload = {
            "scope": normalize_progress_scope(scope, default="frontier"),
            "channel": str(channel or NOTIFY_CHANNEL_DEFAULT).strip().lower(),
            "filters": normalize_progress_filters(filters if isinstance(filters, dict) else {}),
            "strategy": normalize_subscription_strategy(strategy, default=SUBSCRIPTION_STRATEGY_DEFAULT),
            "limit": parse_int_value(limit, 1, 500) or 120,
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raw = data.get("items") if isinstance(data, dict) else []
        items: List[Dict[str, Any]] = []
        if isinstance(raw, list):
            for row in raw:
                if isinstance(row, dict):
                    items.append(self._normalize_item(row))
        by_id: Dict[str, Dict[str, Any]] = {}
        for item in items:
            item_id = str(item.get("id", "") or "").strip()
            if not item_id:
                continue
            old = by_id.get(item_id)
            if old is None or str(item.get("updated_at", "")) >= str(old.get("updated_at", "")):
                by_id[item_id] = item
        by_signature: Dict[str, Dict[str, Any]] = {}
        for item in by_id.values():
            signature = self._build_signature(
                scope=str(item.get("scope", "frontier") or "frontier"),
                channel=str(item.get("channel", NOTIFY_CHANNEL_DEFAULT) or NOTIFY_CHANNEL_DEFAULT),
                filters=item.get("filters") if isinstance(item.get("filters"), dict) else {},
                strategy=normalize_subscription_strategy(
                    item.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                ),
                limit=parse_int_value(item.get("limit"), 1, 500) or 120,
            )
            old = by_signature.get(signature)
            if old is None or str(item.get("updated_at", "")) >= str(old.get("updated_at", "")):
                by_signature[signature] = item
        dedup = list(by_signature.values())
        dedup.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)
        return {"items": dedup}

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return {"items": []}
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return self._normalize(data)
            except Exception:
                pass
            return {"items": []}

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            normalized = self._normalize(data if isinstance(data, dict) else {})
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
            return normalized

    def list(self, scope: str = "") -> List[Dict[str, Any]]:
        target = normalize_progress_scope(scope, default="frontier") if scope else ""
        payload = self.load()
        items = payload.get("items") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            return []
        out: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if target and normalize_progress_scope(item.get("scope", ""), default="frontier") != target:
                continue
            out.append(dict(item))
        return out

    def upsert(
        self,
        *,
        scope: str,
        name: str,
        channel: str,
        filters: Dict[str, Any],
        enabled: bool = True,
        limit: int = 120,
        strategy: str = SUBSCRIPTION_STRATEGY_DEFAULT,
        sub_id: str = "",
    ) -> Dict[str, Any]:
        with self._lock:
            payload = self.load()
            items = payload.setdefault("items", [])
            if not isinstance(items, list):
                items = []
                payload["items"] = items
            scope_key = normalize_progress_scope(scope, default="frontier")
            now = utc_now_iso()
            idx = -1
            for i, item in enumerate(items):
                if str(item.get("id", "")) == str(sub_id or "") and sub_id:
                    idx = i
                    break
            if idx < 0 and not str(sub_id or "").strip():
                target_sig = self._build_signature(
                    scope=scope_key,
                    channel=channel,
                    filters=filters,
                    strategy=strategy,
                    limit=limit,
                )
                for i, item in enumerate(items):
                    sig = self._build_signature(
                        scope=str(item.get("scope", "frontier") or "frontier"),
                        channel=str(item.get("channel", "feishu") or "feishu"),
                        filters=item.get("filters") if isinstance(item.get("filters"), dict) else {},
                        strategy=normalize_subscription_strategy(
                            item.get("strategy"),
                            default=SUBSCRIPTION_STRATEGY_DEFAULT,
                        ),
                        limit=parse_int_value(item.get("limit"), 1, 500) or 120,
                    )
                    if sig == target_sig:
                        idx = i
                        break
            if idx >= 0:
                current = dict(items[idx]) if isinstance(items[idx], dict) else {}
                current.update(
                    {
                        "scope": scope_key,
                        "name": name,
                        "channel": channel,
                        "filters": filters,
                        "enabled": enabled,
                        "limit": limit,
                        "strategy": strategy,
                        "updated_at": now,
                    }
                )
                normalized = self._normalize_item(current)
                items[idx] = normalized
            else:
                normalized = self._normalize_item(
                    {
                        "id": sub_id or uuid.uuid4().hex[:12],
                        "scope": scope_key,
                        "name": name,
                        "channel": channel,
                        "filters": filters,
                        "enabled": enabled,
                        "limit": limit,
                        "strategy": strategy,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                items.append(normalized)
            self.save(payload)
            return normalized

    def delete(self, sub_id: str) -> bool:
        key = str(sub_id or "").strip()
        if not key:
            return False
        with self._lock:
            payload = self.load()
            items = payload.get("items") if isinstance(payload, dict) else []
            if not isinstance(items, list):
                return False
            remain = [item for item in items if str(item.get("id", "")) != key]
            changed = len(remain) != len(items)
            if changed:
                self.save({"items": remain})
            return changed

    def mark_notified(self, sub_id: str, sent_keys: List[str], match_count: int) -> Optional[Dict[str, Any]]:
        key = str(sub_id or "").strip()
        if not key:
            return None
        with self._lock:
            payload = self.load()
            items = payload.get("items") if isinstance(payload, dict) else []
            if not isinstance(items, list):
                return None
            now = utc_now_iso()
            for idx, row in enumerate(items):
                if str(row.get("id", "")) != key:
                    continue
                current = dict(row)
                previous = current.get("sent_keys") if isinstance(current.get("sent_keys"), list) else []
                merged: List[str] = []
                seen = set()
                for value in list(sent_keys or []) + list(previous):
                    text = str(value or "").strip()
                    if not text or text in seen:
                        continue
                    seen.add(text)
                    merged.append(text)
                    if len(merged) >= 3000:
                        break
                current["sent_keys"] = merged
                current["last_notified_at"] = now
                current["last_match_count"] = max(0, int(match_count or 0))
                current["updated_at"] = now
                normalized = self._normalize_item(current)
                items[idx] = normalized
                self.save({"items": items})
                return normalized
        return None


class ProgressFetchTaskManager:
    """Background per-scope fetch tasks so page navigation does not interrupt crawling."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "progress_fetch_tasks.json"
        self._lock = threading.RLock()
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _default_job(self, scope: str) -> Dict[str, Any]:
        return {
            "scope": normalize_progress_scope(scope, default="frontier"),
            "running": False,
            "job_id": "",
            "requested_at": "",
            "requested_by": "",
            "started_at": "",
            "finished_at": "",
            "max_per_source": 20,
            "fetch_workers": 6,
            "source_ids": [],
            "error": "",
            "result": {},
        }

    def _load(self) -> None:
        with self._lock:
            self._jobs = {scope: self._default_job(scope) for scope in PROGRESS_SCOPES}
            if not self.path.exists():
                return
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return
            items = raw.get("jobs") if isinstance(raw, dict) else {}
            if not isinstance(items, dict):
                return
            for scope in PROGRESS_SCOPES:
                entry = items.get(scope)
                if not isinstance(entry, dict):
                    continue
                normalized = self._default_job(scope)
                normalized.update(entry)
                normalized["scope"] = scope
                normalized["running"] = False
                self._jobs[scope] = normalized

    def _save(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "jobs": self._jobs,
            "updated_at": utc_now_iso(),
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _is_running_stale(self, job: Dict[str, Any]) -> bool:
        if not bool(job.get("running")):
            return False
        started_at = parse_iso_utc(job.get("started_at")) or parse_iso_utc(job.get("requested_at"))
        if started_at is None:
            return False
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        return elapsed >= PROGRESS_FETCH_STALE_TIMEOUT_SECONDS

    def _finalize_stale_job(self, scope: str, job: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(job or {})
        message = (
            f"fetch task timeout after {PROGRESS_FETCH_STALE_TIMEOUT_SECONDS // 60} minutes; "
            "marked as stale and released"
        )
        normalized["scope"] = normalize_progress_scope(scope, default="frontier")
        normalized["running"] = False
        normalized["finished_at"] = utc_now_iso()
        normalized["error"] = message
        result_payload = normalized.get("result") if isinstance(normalized.get("result"), dict) else {}
        if not result_payload:
            result_payload = {"ok": False, "error": message}
        else:
            result_payload = dict(result_payload)
            result_payload.setdefault("ok", False)
            result_payload.setdefault("error", message)
        normalized["result"] = result_payload
        self._jobs[normalized["scope"]] = normalized
        return normalized

    def get(self, scope: str) -> Dict[str, Any]:
        key = normalize_progress_scope(scope, default="frontier")
        with self._lock:
            row = dict(self._jobs.get(key) or self._default_job(key))
            if self._is_running_stale(row):
                row = self._finalize_stale_job(key, row)
                self._save()
            return dict(row)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            changed = False
            result: Dict[str, Dict[str, Any]] = {}
            for scope in PROGRESS_SCOPES:
                row = dict(self._jobs.get(scope) or self._default_job(scope))
                if self._is_running_stale(row):
                    row = self._finalize_stale_job(scope, row)
                    changed = True
                result[scope] = dict(row)
            if changed:
                self._save()
            return result

    def start(
        self,
        *,
        scope: str,
        max_per_source: int,
        fetch_workers: int,
        source_ids: List[str],
        requested_by: str,
        runner: Any,
    ) -> Dict[str, Any]:
        key = normalize_progress_scope(scope, default="frontier")
        with self._lock:
            current = dict(self._jobs.get(key) or self._default_job(key))
            if self._is_running_stale(current):
                current = self._finalize_stale_job(key, current)
            if bool(current.get("running")):
                return {"ok": False, "error": "fetch task is already running", "job": current}
            now = utc_now_iso()
            job_id = uuid.uuid4().hex[:12]
            started = {
                "scope": key,
                "running": True,
                "job_id": job_id,
                "requested_at": now,
                "requested_by": str(requested_by or "manual").strip() or "manual",
                "started_at": now,
                "finished_at": "",
                "max_per_source": max(1, min(int(max_per_source or 20), 120)),
                "fetch_workers": max(1, min(int(fetch_workers or 6), 16)),
                "source_ids": [str(x).strip() for x in (source_ids or []) if str(x).strip()],
                "error": "",
                "result": {},
            }
            self._jobs[key] = started
            self._save()

        def _run() -> None:
            error_text = ""
            result_payload: Dict[str, Any] = {}
            try:
                result = runner()
                if isinstance(result, dict):
                    result_payload = dict(result)
                else:
                    result_payload = {"ok": True, "message": str(result)}
            except Exception as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                result_payload = {"ok": False, "error": error_text}
            finished = utc_now_iso()
            with self._lock:
                row = dict(self._jobs.get(key) or self._default_job(key))
                if str(row.get("job_id", "")) != job_id:
                    return
                row["running"] = False
                row["finished_at"] = finished
                row["error"] = error_text
                row["result"] = result_payload
                self._jobs[key] = row
                self._save()

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        return {"ok": True, "job": dict(started)}


class PaperFetchTaskManager:
    """Background crawl task state for paper radar with persistence."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "paper_fetch_task.json"
        self._lock = threading.RLock()
        self._job: Dict[str, Any] = self._default_job()
        self._load()

    def _default_job(self) -> Dict[str, Any]:
        return {
            "running": False,
            "job_id": "",
            "requested_at": "",
            "requested_by": "",
            "started_at": "",
            "finished_at": "",
            "analysis_language": "Chinese",
            "error": "",
            "result": {},
        }

    def _load(self) -> None:
        with self._lock:
            self._job = self._default_job()
            if not self.path.exists():
                return
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return
            row = raw.get("job") if isinstance(raw, dict) else {}
            if not isinstance(row, dict):
                return
            merged = self._default_job()
            merged.update(row)
            merged["running"] = bool(row.get("running", False))
            self._job = merged

    def _save(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = {"job": self._job, "updated_at": utc_now_iso()}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _is_running_stale(self, row: Dict[str, Any]) -> bool:
        if not bool(row.get("running")):
            return False
        started_at = parse_iso_utc(row.get("started_at")) or parse_iso_utc(row.get("requested_at"))
        if started_at is None:
            return False
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        return elapsed >= PAPER_FETCH_STALE_TIMEOUT_SECONDS

    def _finalize_stale(self, row: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(row or {})
        message = (
            f"paper crawl timeout after {PAPER_FETCH_STALE_TIMEOUT_SECONDS // 60} minutes; "
            "marked as stale and released"
        )
        normalized["running"] = False
        normalized["finished_at"] = utc_now_iso()
        normalized["error"] = message
        result = normalized.get("result") if isinstance(normalized.get("result"), dict) else {}
        if not result:
            result = {"ok": False, "error": message}
        else:
            result = dict(result)
            result.setdefault("ok", False)
            result.setdefault("error", message)
        normalized["result"] = result
        return normalized

    def _sync_with_runtime_locked(self, runtime: Dict[str, Any]) -> Dict[str, Any]:
        row = dict(self._job or self._default_job())
        changed = False
        runtime_running = bool(runtime.get("running"))
        runtime_started = str(runtime.get("started_at", "") or "").strip()
        runtime_finished = str(runtime.get("finished_at", "") or "").strip()
        runtime_error = str(runtime.get("last_error", "") or "").strip()
        runtime_exit = runtime.get("last_exit_code")

        if runtime_running and not bool(row.get("running")):
            now = utc_now_iso()
            row["running"] = True
            row["job_id"] = str(row.get("job_id", "") or "").strip() or uuid.uuid4().hex[:12]
            row["requested_at"] = str(row.get("requested_at", "") or "").strip() or runtime_started or now
            row["requested_by"] = str(row.get("requested_by", "") or "").strip() or "runtime"
            row["started_at"] = runtime_started or str(row.get("started_at", "") or "").strip() or now
            row["finished_at"] = ""
            row["error"] = ""
            changed = True

        if (not runtime_running) and bool(row.get("running")):
            row["running"] = False
            row["finished_at"] = runtime_finished or utc_now_iso()
            if runtime_error:
                row["error"] = runtime_error
            ok = (runtime_exit == 0) and not runtime_error
            row["result"] = {
                "ok": ok,
                "exit_code": runtime_exit,
                "error": runtime_error,
                "started_at": runtime_started or str(row.get("started_at", "") or "").strip(),
                "finished_at": row["finished_at"],
            }
            changed = True

        if self._is_running_stale(row):
            row = self._finalize_stale(row)
            changed = True

        if changed:
            self._job = row
            self._save()
        return dict(row)

    def sync_with_runtime(self, runtime: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            return self._sync_with_runtime_locked(runtime if isinstance(runtime, dict) else {})

    def get(self) -> Dict[str, Any]:
        with self._lock:
            row = dict(self._job or self._default_job())
            if self._is_running_stale(row):
                row = self._finalize_stale(row)
                self._job = row
                self._save()
            return dict(row)

    def start(
        self,
        *,
        analysis_language: str,
        requested_by: str,
        runner: Any,
    ) -> Dict[str, Any]:
        lang = normalize_analysis_language(analysis_language, default="Chinese")
        with self._lock:
            row = dict(self._job or self._default_job())
            if self._is_running_stale(row):
                row = self._finalize_stale(row)
                self._job = row
                self._save()
            if bool(row.get("running")):
                return {"ok": False, "error": "paper crawl is already running", "job": row}

            now = utc_now_iso()
            job_id = uuid.uuid4().hex[:12]
            started = {
                "running": True,
                "job_id": job_id,
                "requested_at": now,
                "requested_by": str(requested_by or "manual").strip() or "manual",
                "started_at": now,
                "finished_at": "",
                "analysis_language": lang,
                "error": "",
                "result": {},
            }
            self._job = started
            self._save()

        def _run() -> None:
            error_text = ""
            result_payload: Dict[str, Any] = {}
            try:
                result = runner()
                if isinstance(result, dict):
                    result_payload = dict(result)
                else:
                    result_payload = {"ok": True, "message": str(result)}
            except Exception as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                result_payload = {"ok": False, "error": error_text}

            with self._lock:
                row = dict(self._job or self._default_job())
                if str(row.get("job_id", "")) != job_id:
                    return
                row["running"] = False
                row["finished_at"] = utc_now_iso()
                if error_text:
                    row["error"] = error_text
                row["result"] = result_payload
                self._job = row
                self._save()

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        return {"ok": True, "job": dict(started)}


class ProgressAutoScheduler:
    """Periodic trigger for per-scope progress fetch and subscription push."""

    def __init__(
        self,
        settings_store: ProgressPageSettingsStore,
        task_manager: ProgressFetchTaskManager,
        trigger_once: Any,
    ):
        self.settings_store = settings_store
        self.task_manager = task_manager
        self.trigger_once = trigger_once
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _is_due(self, cfg: Dict[str, Any]) -> bool:
        interval = parse_int_value(
            cfg.get("auto_interval_minutes"),
            PROGRESS_AUTO_MIN_INTERVAL,
            PROGRESS_AUTO_MAX_INTERVAL,
        ) or PROGRESS_AUTO_DEFAULT_INTERVAL
        last = parse_iso_utc(cfg.get("auto_last_run_at"))
        if last is None:
            return True
        return (datetime.now(timezone.utc) - last).total_seconds() >= interval * 60

    def _loop(self) -> None:
        while not self._stop.wait(20):
            payload = self.settings_store.load()
            scopes = payload.get("scopes") if isinstance(payload, dict) else {}
            if not isinstance(scopes, dict):
                continue
            for scope in PROGRESS_SCOPES:
                cfg = scopes.get(scope) if isinstance(scopes.get(scope), dict) else {}
                if not bool(parse_bool_text(cfg.get("auto_enabled"), False)):
                    continue
                job = self.task_manager.get(scope)
                if bool(job.get("running")):
                    continue
                if not self._is_due(cfg):
                    continue

                max_per_source = parse_int_value(cfg.get("max_per_source"), 1, 120) or 20
                fetch_workers = parse_int_value(cfg.get("fetch_workers"), 1, 16) or 6
                source_ids = cfg.get("source_ids") if isinstance(cfg.get("source_ids"), list) else []
                source_ids = [str(x).strip() for x in source_ids if str(x).strip()]
                auto_push = bool(parse_bool_text(cfg.get("auto_push_enabled"), False))

                started = self.task_manager.start(
                    scope=scope,
                    max_per_source=max_per_source,
                    fetch_workers=fetch_workers,
                    source_ids=source_ids,
                    requested_by="auto",
                    runner=lambda s=scope, m=max_per_source, fw=fetch_workers, ids=list(source_ids), ap=auto_push: self.trigger_once(
                        scope=s,
                        max_per_source=m,
                        fetch_workers=fw,
                        source_ids=ids,
                        auto_push=ap,
                        requested_by="auto",
                    ),
                )
                if not started.get("ok"):
                    continue


class CrawlRunner:
    def __init__(self, workdir: Path, settings_store: Optional[PanelSettingsStore] = None):
        self.workdir = workdir
        self.settings_store = settings_store
        self._lock = threading.Lock()
        self._on_finished_callbacks: List[Any] = []
        self._process: Optional[subprocess.Popen[str]] = None
        self._running = False
        self._started_at = ""
        self._finished_at = ""
        self._last_exit_code: Optional[int] = None
        self._last_error = ""
        self._logs: List[str] = []
        self._progress: Dict[str, Any] = {
            "fetched": 0,
            "stored": 0,
            "analyzed": 0,
            "phase": "idle",
        }

    def _update_progress_from_log(self, line: str) -> None:
        text = str(line or "")
        if "[RSS] 开始抓取" in text:
            self._progress["phase"] = "fetching"
        if "[RSS] 抓取完成" in text:
            matched = re.search(r"共\s*(\d+)\s*条", text)
            if matched:
                self._progress["fetched"] = int(matched.group(1))
            self._progress["phase"] = "fetched"
        if "RSS 处理完成" in text:
            matched = re.search(r"新增\s*(\d+)\s*条，更新\s*(\d+)\s*条", text)
            if matched:
                self._progress["stored"] = int(matched.group(1)) + int(matched.group(2))
            self._progress["phase"] = "stored"
        if "[Paper] analyzed" in text:
            matched = re.search(r"analyzed\s*(\d+)\s*arXiv papers", text)
            if matched:
                self._progress["analyzed"] = int(matched.group(1))
            self._progress["phase"] = "analyzed"

    def _append_log(self, line: str) -> None:
        with self._lock:
            self._logs.append(line)
            self._update_progress_from_log(line)
            if len(self._logs) > MAX_LOG_LINES:
                self._logs = self._logs[-MAX_LOG_LINES:]

    def trigger(self, analysis_language: str = "") -> Tuple[bool, str]:
        with self._lock:
            if self._running:
                return False, "crawl is already running"
            if self._detect_existing_crawl_pid() is not None:
                return False, "another crawl process is already running"

            env = os.environ.copy()
            # Panel crawl focuses on paper ingestion/analysis only.
            # Disable legacy report notification and hotlist crawler explicitly.
            env["ENABLE_NOTIFICATION"] = "false"
            env["NOTIFICATION_ENABLED"] = "false"
            env["ENABLE_CRAWLER"] = "false"
            settings = self.settings_store.load() if self.settings_store else {}
            ai_model = str(settings.get("ai_model", "") or "").strip()
            ai_api_base = str(settings.get("ai_api_base", "") or "").strip()
            ai_api_key = str(settings.get("ai_api_key", "") or "").strip()
            runtime_ai_model = to_runtime_model_name(ai_model, ai_api_base)
            research_topic = str(settings.get("research_topic", "") or "").strip()
            paper_primary_category = str(settings.get("paper_primary_category", "") or "").strip()
            paper_subtopics = str(settings.get("paper_subtopics", "") or "").strip()
            paper_max = settings.get("paper_max_papers_per_run")
            resolved_language = normalize_analysis_language(
                analysis_language,
                default=normalize_analysis_language(settings.get("analysis_language", "Chinese"), default="Chinese"),
            )

            if runtime_ai_model:
                env["AI_MODEL"] = runtime_ai_model
            if ai_api_base:
                env["AI_API_BASE"] = ai_api_base
            if ai_api_key:
                env["AI_API_KEY"] = ai_api_key
            if research_topic:
                env["PAPER_RESEARCH_TOPIC"] = research_topic
            if paper_primary_category:
                env["PAPER_PRIMARY_CATEGORY"] = paper_primary_category
            if paper_subtopics:
                env["PAPER_SUBTOPICS"] = paper_subtopics
            if isinstance(paper_max, int) and paper_max > 0:
                env["PAPER_ANALYSIS_MAX_PAPERS_PER_RUN"] = str(paper_max)
            env["PAPER_ANALYSIS_LANGUAGE"] = resolved_language

            passthrough_keys = {
                "FEISHU_WEBHOOK_URL": "feishu_webhook_url",
                "WEWORK_WEBHOOK_URL": "wework_webhook_url",
                "WEWORK_MSG_TYPE": "wework_msg_type",
                "DINGTALK_WEBHOOK_URL": "dingtalk_webhook_url",
                "TELEGRAM_BOT_TOKEN": "telegram_bot_token",
                "TELEGRAM_CHAT_ID": "telegram_chat_id",
                "NTFY_SERVER_URL": "ntfy_server_url",
                "NTFY_TOPIC": "ntfy_topic",
                "NTFY_TOKEN": "ntfy_token",
                "BARK_URL": "bark_url",
                "SLACK_WEBHOOK_URL": "slack_webhook_url",
                "EMAIL_FROM": "email_from",
                "EMAIL_PASSWORD": "email_password",
                "EMAIL_TO": "email_to",
                "EMAIL_SMTP_SERVER": "email_smtp_server",
                "EMAIL_SMTP_PORT": "email_smtp_port",
            }
            for env_key, setting_key in passthrough_keys.items():
                value = str(settings.get(setting_key, "") or "").strip()
                if value:
                    env[env_key] = value

            try:
                self._process = subprocess.Popen(
                    [sys.executable, "-m", "omnihawk_ai"],
                    cwd=str(self.workdir),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )
            except Exception as exc:
                self._last_error = f"failed to start crawl: {exc}"
                self._last_exit_code = -1
                self._finished_at = utc_now_iso()
                return False, self._last_error

            self._running = True
            self._started_at = utc_now_iso()
            self._finished_at = ""
            self._last_error = ""
            self._last_exit_code = None
            self._progress = {
                "fetched": 0,
                "stored": 0,
                "analyzed": 0,
                "phase": "running",
            }
            self._logs = [f"[{self._started_at}] crawl started"]
            if research_topic:
                self._logs.append(f"[panel] research_topic={research_topic}")
            if ai_model:
                self._logs.append(f"[panel] ai_model={ai_model}")
            if runtime_ai_model and runtime_ai_model != ai_model:
                self._logs.append(f"[panel] runtime_ai_model={runtime_ai_model}")
            if isinstance(paper_max, int) and paper_max > 0:
                self._logs.append(f"[panel] paper_max_papers_per_run={paper_max}")
            self._logs.append(f"[panel] analysis_language={resolved_language}")

            watcher = threading.Thread(target=self._watch_process, daemon=True)
            watcher.start()
            return True, "crawl started"

    def add_on_finished_callback(self, callback: Any) -> None:
        if not callable(callback):
            return
        with self._lock:
            self._on_finished_callbacks.append(callback)

    def _detect_existing_crawl_pid(self) -> Optional[int]:
        """
        Detect external `python -m omnihawk_ai` process to avoid duplicate runs.
        Works in Linux container by scanning `/proc`.
        """
        proc_root = Path("/proc")
        if not proc_root.exists():
            return None

        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue

            pid = int(entry.name)
            if self._process and pid == self._process.pid:
                continue
            if pid == os.getpid():
                continue

            cmdline_file = entry / "cmdline"
            try:
                cmdline = cmdline_file.read_bytes().replace(b"\x00", b" ").decode(
                    "utf-8", errors="ignore"
                )
            except Exception:
                continue

            if "omnihawk_ai.web.panel_server" in cmdline:
                continue
            if "-m omnihawk_ai" in cmdline:
                return pid

        return None

    def _watch_process(self) -> None:
        proc = self._process
        if not proc:
            return

        try:
            if proc.stdout:
                for line in proc.stdout:
                    self._append_log(line.rstrip("\r\n"))
            proc.wait()
            exit_code = proc.returncode
        except Exception as exc:
            exit_code = -1
            self._append_log(f"[error] watcher exception: {exc}")

        callbacks: List[Any] = []
        result_payload: Dict[str, Any] = {}
        with self._lock:
            self._running = False
            self._finished_at = utc_now_iso()
            self._last_exit_code = exit_code
            if exit_code != 0:
                self._last_error = f"crawl exited with code {exit_code}"
            self._logs.append(
                f"[{self._finished_at}] crawl finished (exit_code={self._last_exit_code})"
            )
            self._progress["phase"] = "finished"
            if len(self._logs) > MAX_LOG_LINES:
                self._logs = self._logs[-MAX_LOG_LINES:]
            self._process = None
            callbacks = list(self._on_finished_callbacks)
            result_payload = {
                "ok": exit_code == 0,
                "exit_code": exit_code,
                "started_at": self._started_at,
                "finished_at": self._finished_at,
            }

        for callback in callbacks:
            try:
                callback(dict(result_payload))
            except Exception as exc:
                self._append_log(f"[warning] crawl finished callback failed: {type(exc).__name__}: {exc}")

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "started_at": self._started_at,
                "finished_at": self._finished_at,
                "last_exit_code": self._last_exit_code,
                "last_error": self._last_error,
                "logs": list(self._logs),
                "progress": dict(self._progress),
            }


class ScheduleController:
    def __init__(
        self,
        project_root: Path,
        output_dir: Optional[Path] = None,
        settings_store: Optional[PanelSettingsStore] = None,
    ):
        self.project_root = project_root
        self.output_dir = (output_dir or (project_root / "output")).resolve()
        self.settings_store = settings_store
        self.crontab_path = Path("/tmp/crontab")
        self.schedule_state_path = self.output_dir / "panel_schedule.json"
        self.command = self._build_command_from_settings()
        self._lock = threading.Lock()

    def _build_command_from_settings(self) -> str:
        settings = self.settings_store.load() if self.settings_store else {}
        ai_model_raw = str(settings.get("ai_model", "") or "").strip()
        ai_api_base = str(settings.get("ai_api_base", "") or "").strip()
        # Panel mode only keeps paper subscription notifications.
        # Disable legacy hotlist notification chain and hotlist crawler for scheduled crawls.
        env_parts: List[str] = [
            "ENABLE_NOTIFICATION=false",
            "NOTIFICATION_ENABLED=false",
            "ENABLE_CRAWLER=false",
        ]
        mapping = {
            "AI_MODEL": to_runtime_model_name(ai_model_raw, ai_api_base),
            "AI_API_BASE": ai_api_base,
            "AI_API_KEY": str(settings.get("ai_api_key", "") or "").strip(),
            "PAPER_ANALYSIS_LANGUAGE": normalize_analysis_language(
                settings.get("analysis_language", "Chinese"),
                default="Chinese",
            ),
            "PAPER_RESEARCH_TOPIC": str(settings.get("research_topic", "") or "").strip(),
            "PAPER_PRIMARY_CATEGORY": str(settings.get("paper_primary_category", "") or "").strip(),
            "PAPER_SUBTOPICS": str(settings.get("paper_subtopics", "") or "").strip(),
            "FEISHU_WEBHOOK_URL": str(settings.get("feishu_webhook_url", "") or "").strip(),
            "WEWORK_WEBHOOK_URL": str(settings.get("wework_webhook_url", "") or "").strip(),
            "WEWORK_MSG_TYPE": str(settings.get("wework_msg_type", "") or "").strip(),
            "DINGTALK_WEBHOOK_URL": str(settings.get("dingtalk_webhook_url", "") or "").strip(),
            "TELEGRAM_BOT_TOKEN": str(settings.get("telegram_bot_token", "") or "").strip(),
            "TELEGRAM_CHAT_ID": str(settings.get("telegram_chat_id", "") or "").strip(),
            "NTFY_SERVER_URL": str(settings.get("ntfy_server_url", "") or "").strip(),
            "NTFY_TOPIC": str(settings.get("ntfy_topic", "") or "").strip(),
            "NTFY_TOKEN": str(settings.get("ntfy_token", "") or "").strip(),
            "BARK_URL": str(settings.get("bark_url", "") or "").strip(),
            "SLACK_WEBHOOK_URL": str(settings.get("slack_webhook_url", "") or "").strip(),
            "EMAIL_FROM": str(settings.get("email_from", "") or "").strip(),
            "EMAIL_PASSWORD": str(settings.get("email_password", "") or "").strip(),
            "EMAIL_TO": str(settings.get("email_to", "") or "").strip(),
            "EMAIL_SMTP_SERVER": str(settings.get("email_smtp_server", "") or "").strip(),
            "EMAIL_SMTP_PORT": str(settings.get("email_smtp_port", "") or "").strip(),
        }
        for key, value in mapping.items():
            if value:
                env_parts.append(f"{key}={shlex.quote(value)}")

        paper_max = settings.get("paper_max_papers_per_run")
        if isinstance(paper_max, int) and paper_max > 0:
            env_parts.append(f"PAPER_ANALYSIS_MAX_PAPERS_PER_RUN={paper_max}")

        if env_parts:
            return f"cd /app && {' '.join(env_parts)} python -m omnihawk_ai"
        return "cd /app && python -m omnihawk_ai"

    def _load_saved_cron(self) -> str:
        if not self.schedule_state_path.exists():
            return ""
        try:
            data = json.loads(self.schedule_state_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cron_expr = str(data.get("cron_expr", "") or "").strip()
                if cron_expr and len(cron_expr.split()) == 5:
                    return cron_expr
        except Exception:
            pass
        return ""

    def _save_cron(self, cron_expr: str) -> None:
        cron_expr = str(cron_expr or "").strip()
        if not cron_expr:
            return
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.schedule_state_path.write_text(
                json.dumps({"cron_expr": cron_expr}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _read_cron(self) -> str:
        saved_expr = self._load_saved_cron()
        if saved_expr:
            return saved_expr

        if self.crontab_path.exists():
            try:
                line = self.crontab_path.read_text(encoding="utf-8").strip()
                if line:
                    parts = line.split(maxsplit=5)
                    if len(parts) >= 5:
                        return " ".join(parts[:5])
            except Exception:
                pass

        env_expr = (os.getenv("CRON_SCHEDULE", "") or "").strip()
        if env_expr:
            return env_expr
        return "*/30 * * * *"

    def current(self) -> Dict[str, Any]:
        self.command = self._build_command_from_settings()
        cron_expr = self._read_cron()
        interval = parse_interval_from_cron(cron_expr)
        return {"cron_expr": cron_expr, "interval_minutes": interval}

    def update_interval(self, interval_minutes: int) -> Dict[str, Any]:
        cron_expr = interval_to_cron(interval_minutes)
        with self._lock:
            self.command = self._build_command_from_settings()
            line = f"{cron_expr} {self.command}\n"
            self.crontab_path.write_text(line, encoding="utf-8")
            self._save_cron(cron_expr)
        return {"cron_expr": cron_expr, "interval_minutes": interval_minutes}

    def sync_command(self) -> Dict[str, Any]:
        with self._lock:
            self.command = self._build_command_from_settings()
            cron_expr = self._read_cron()
            line = f"{cron_expr} {self.command}\n"
            self.crontab_path.write_text(line, encoding="utf-8")
            self._save_cron(cron_expr)
        return {"cron_expr": cron_expr, "interval_minutes": parse_interval_from_cron(cron_expr)}


class PaperRepository:
    def __init__(
        self,
        output_dir: Path,
        settings_store: Optional[PanelSettingsStore] = None,
        action_store: Optional[PanelActionStore] = None,
    ):
        self.output_dir = output_dir
        self.settings_store = settings_store
        self.action_store = action_store
        self._aff_cache_path = self.output_dir / "panel_affiliations_cache.json"
        self._aff_cache_loaded = False
        self._aff_cache: Dict[str, List[str]] = {}
        self._aff_lock = threading.Lock()
        self._aff_refresh_attempted: set[str] = set()

    def _clean_affiliations(self, values: List[str]) -> List[str]:
        cleaned: List[str] = []
        for item in values or []:
            text = str(item or "").strip()
            if len(text) < 6:
                continue
            lower = text.lower()
            if lower in {"none", "n/a", "unknown"}:
                continue
            if text not in cleaned:
                cleaned.append(text)
        return cleaned

    def _load_aff_cache(self) -> None:
        if self._aff_cache_loaded:
            return
        self._aff_cache_loaded = True
        if not self._aff_cache_path.exists():
            self._aff_cache = {}
            return
        try:
            raw = json.loads(self._aff_cache_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                normalized: Dict[str, List[str]] = {}
                for k, v in raw.items():
                    if isinstance(v, list):
                        normalized[str(k)] = self._clean_affiliations([str(x).strip() for x in v if str(x).strip()])
                self._aff_cache = normalized
            else:
                self._aff_cache = {}
        except Exception:
            self._aff_cache = {}

    def _save_aff_cache(self) -> None:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._aff_cache_path.write_text(
                json.dumps(self._aff_cache, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _fetch_affiliations_from_arxiv(self, arxiv_id: str) -> List[str]:
        arxiv_id = (arxiv_id or "").strip()
        if not arxiv_id:
            return []
        with self._aff_lock:
            self._load_aff_cache()
            cached = self._aff_cache.get(arxiv_id)
            if cached is not None:
                cached = self._clean_affiliations(cached)
                if cached:
                    return list(cached)
                if arxiv_id in self._aff_refresh_attempted:
                    return []
            self._aff_refresh_attempted.add(arxiv_id)

        result: List[str] = []
        try:
            url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "OmniHawk AI-Panel/1.0"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                xml_text = resp.read().decode("utf-8", errors="ignore")
            root = ET.fromstring(xml_text)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entry = root.find("atom:entry", ns)
            if entry is not None:
                for author in entry.findall("atom:author", ns):
                    aff = author.find("arxiv:affiliation", ns)
                    if aff is not None and aff.text and aff.text.strip():
                        val = aff.text.strip()
                        if val not in result:
                            result.append(val)
        except Exception:
            result = []

        if not result:
            result = self._fetch_affiliations_from_abs_page(arxiv_id)
        if not result:
            result = self._fetch_affiliations_from_semantic_scholar(arxiv_id)
        result = self._clean_affiliations(result)

        with self._aff_lock:
            self._load_aff_cache()
            self._aff_cache[arxiv_id] = result
            self._save_aff_cache()
        return list(result)

    def _fetch_affiliations_from_abs_page(self, arxiv_id: str) -> List[str]:
        """Fallback extraction from arXiv abstract page meta tags."""
        try:
            req = urllib.request.Request(
                f"https://arxiv.org/abs/{arxiv_id}",
                headers={"User-Agent": "OmniHawk AI-Panel/1.0"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                page = resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return []

        values: List[str] = []
        # Most reliable source if present.
        patterns = [
            r'<meta\s+name=["\']citation_author_institution["\']\s+content=["\']([^"\']+)["\']',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']citation_author_institution["\']',
        ]
        for pattern in patterns:
            for matched in re.findall(pattern, page, flags=re.IGNORECASE):
                text = html.unescape(str(matched or "")).strip()
                if text and text not in values:
                    values.append(text)
            if values:
                return values
        return values

    def _fetch_affiliations_from_semantic_scholar(self, arxiv_id: str) -> List[str]:
        """Fallback to Semantic Scholar Graph API for author affiliations."""
        if not arxiv_id:
            return []
        url = (
            "https://api.semanticscholar.org/graph/v1/paper/"
            f"ARXIV:{arxiv_id}?fields=authors.affiliations"
        )
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "OmniHawk AI-Panel/1.0"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception:
            return []

        authors = payload.get("authors") if isinstance(payload, dict) else []
        if not isinstance(authors, list):
            return []

        result: List[str] = []
        for author in authors:
            if not isinstance(author, dict):
                continue
            affs = author.get("affiliations") or []
            if isinstance(affs, str):
                affs = [affs]
            if not isinstance(affs, list):
                continue
            for aff in affs:
                text = str(aff or "").strip()
                if text and text not in result:
                    result.append(text)
        return result

    def _latest_rss_db(self) -> Optional[Path]:
        rss_dir = self.output_dir / "rss"
        if not rss_dir.exists():
            return None
        db_files = sorted(rss_dir.glob("*.db"), key=lambda p: p.name, reverse=True)
        return db_files[0] if db_files else None

    def _rss_db_files(self) -> List[Path]:
        rss_dir = self.output_dir / "rss"
        if not rss_dir.exists():
            return []
        return sorted(rss_dir.glob("*.db"), key=lambda p: p.name, reverse=True)

    def _build_paper_key(self, meta: Dict[str, Any], url: str, title: str) -> Tuple[str, str]:
        arxiv_id = str(meta.get("arxiv_id", "") or "").strip()
        if not arxiv_id:
            arxiv_id = extract_arxiv_id(url or "")
        uniq_key = arxiv_id or str(url or "").strip() or str(title or "").strip()
        return uniq_key, arxiv_id

    def get_paper_record_by_key(self, paper_key: str) -> Optional[Dict[str, Any]]:
        target_key = str(paper_key or "").strip()
        if not target_key:
            return None

        db_files = self._rss_db_files()
        if not db_files:
            return None

        for db_path in db_files:
            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                        rowid,
                        title, author, published_at, summary, url,
                        paper_meta_json, paper_insight_json, updated_at
                    FROM rss_items
                    WHERE
                        (paper_meta_json IS NOT NULL AND paper_meta_json <> '')
                        OR url LIKE '%arxiv.org/%'
                    ORDER BY COALESCE(published_at, updated_at) DESC
                    LIMIT 8000
                    """
                )
                rows = cur.fetchall()
            except Exception:
                rows = []
            finally:
                conn.close()

            for row in rows:
                rowid, title, author, published_at, summary, url, meta_json, insight_json, updated_at = row
                meta = safe_load_json(meta_json)
                insight = safe_load_json(insight_json)
                uniq_key, arxiv_id = self._build_paper_key(meta, str(url or ""), str(title or ""))
                if uniq_key != target_key:
                    continue
                return {
                    "db_path": str(db_path),
                    "rowid": int(rowid),
                    "paper_key": uniq_key,
                    "title": str(title or "").strip(),
                    "author": str(author or "").strip(),
                    "published_at": str(published_at or "").strip(),
                    "summary": str(summary or "").strip(),
                    "url": str(url or "").strip(),
                    "updated_at": str(updated_at or "").strip(),
                    "arxiv_id": arxiv_id,
                    "meta": meta,
                    "insight": insight,
                }
        return None

    def get_paper_records_by_keys(self, paper_keys: List[str]) -> Dict[str, Dict[str, Any]]:
        wanted = {str(x or "").strip() for x in (paper_keys or []) if str(x or "").strip()}
        if not wanted:
            return {}

        out: Dict[str, Dict[str, Any]] = {}
        db_files = self._rss_db_files()
        if not db_files:
            return out

        for db_path in db_files:
            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                        rowid,
                        title, author, published_at, summary, url,
                        paper_meta_json, paper_insight_json, updated_at
                    FROM rss_items
                    WHERE
                        (paper_meta_json IS NOT NULL AND paper_meta_json <> '')
                        OR url LIKE '%arxiv.org/%'
                    ORDER BY COALESCE(published_at, updated_at) DESC
                    LIMIT 8000
                    """
                )
                rows = cur.fetchall()
            except Exception:
                rows = []
            finally:
                conn.close()

            for row in rows:
                rowid, title, author, published_at, summary, url, meta_json, insight_json, updated_at = row
                meta = safe_load_json(meta_json)
                insight = safe_load_json(insight_json)
                uniq_key, arxiv_id = self._build_paper_key(meta, str(url or ""), str(title or ""))
                if uniq_key not in wanted or uniq_key in out:
                    continue
                out[uniq_key] = {
                    "db_path": str(db_path),
                    "rowid": int(rowid),
                    "paper_key": uniq_key,
                    "title": str(title or "").strip(),
                    "author": str(author or "").strip(),
                    "published_at": str(published_at or "").strip(),
                    "summary": str(summary or "").strip(),
                    "url": str(url or "").strip(),
                    "updated_at": str(updated_at or "").strip(),
                    "arxiv_id": arxiv_id,
                    "meta": meta,
                    "insight": insight,
                }
                if len(out) >= len(wanted):
                    break
            if len(out) >= len(wanted):
                break

        return out

    def _normalize_keyword_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return []

    def _paper_i18n_map(self, insight: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        raw = insight.get("i18n") if isinstance(insight.get("i18n"), dict) else {}
        out: Dict[str, Dict[str, Any]] = {}
        for key, value in raw.items():
            lang_key = language_cache_key(str(key or ""))
            if not lang_key or not isinstance(value, dict):
                continue
            out[lang_key] = dict(value)
        return out

    def _paper_i18n_entry(self, insight: Dict[str, Any], output_language: str) -> Dict[str, Any]:
        lang_key = language_cache_key(output_language)
        return self._paper_i18n_map(insight).get(lang_key, {})

    def _paper_deep_i18n_entry(self, insight: Dict[str, Any], output_language: str) -> Dict[str, Any]:
        raw = insight.get("deep_analysis_i18n") if isinstance(insight.get("deep_analysis_i18n"), dict) else {}
        lang_key = language_cache_key(output_language)
        value = raw.get(lang_key) if isinstance(raw.get(lang_key), dict) else {}
        return dict(value) if isinstance(value, dict) else {}

    def _pick_localized_title(self, title: str, insight: Dict[str, Any], output_language: str) -> str:
        lang = normalize_analysis_language(output_language, default="Chinese")
        base = str(title or "").strip()
        mapped = self._paper_i18n_entry(insight, lang)
        mapped_title = str(mapped.get("title", "") or "").strip()
        if mapped_title:
            return mapped_title
        title_zh = str(insight.get("title_zh", "") or "").strip()
        title_en = str(insight.get("title_en", "") or "").strip()
        if is_english_language(lang):
            if title_en:
                return title_en
            if base and not looks_like_chinese_text(base):
                return base
            return base
        if is_chinese_language(lang):
            if title_zh:
                return title_zh
            if base and looks_like_chinese_text(base):
                return base
            return base
        return base

    def _pick_localized_insight_text(self, insight: Dict[str, Any], key: str, output_language: str) -> str:
        lang = normalize_analysis_language(output_language, default="Chinese")
        mapped = self._paper_i18n_entry(insight, lang)
        mapped_text = str(mapped.get(key, "") or "").strip()
        if mapped_text:
            return mapped_text

        base = str(insight.get(key, "") or "").strip()
        zh_val = str(insight.get(f"{key}_zh", "") or "").strip()
        en_val = str(insight.get(f"{key}_en", "") or "").strip()
        if is_english_language(lang):
            if en_val:
                return en_val
            if base and not looks_like_chinese_text(base):
                return base
            return ""
        if is_chinese_language(lang):
            if zh_val:
                return zh_val
            if base and looks_like_chinese_text(base):
                return base
            return ""
        return ""

    def _pick_localized_keywords(self, insight: Dict[str, Any], output_language: str) -> List[str]:
        lang = normalize_analysis_language(output_language, default="Chinese")
        mapped = self._paper_i18n_entry(insight, lang)
        mapped_keywords = self._normalize_keyword_list(mapped.get("keywords"))
        if mapped_keywords:
            return mapped_keywords

        base_vals = self._normalize_keyword_list(insight.get("keywords"))
        zh_vals = self._normalize_keyword_list(insight.get("keywords_zh"))
        en_vals = self._normalize_keyword_list(insight.get("keywords_en"))
        if is_english_language(lang):
            if en_vals:
                return en_vals
            if base_vals and not any(looks_like_chinese_text(x) for x in base_vals):
                return base_vals
            return []
        if is_chinese_language(lang):
            if zh_vals:
                return zh_vals
            if base_vals and any(looks_like_chinese_text(x) for x in base_vals):
                return base_vals
            return []
        return []

    def _select_deep_analysis_by_language(self, insight: Dict[str, Any], output_language: str) -> Dict[str, Any]:
        lang = normalize_analysis_language(output_language, default="Chinese")
        mapped = self._paper_deep_i18n_entry(insight, lang)
        if mapped:
            return mapped

        deep_default = insight.get("deep_analysis") if isinstance(insight.get("deep_analysis"), dict) else {}
        deep_zh = insight.get("deep_analysis_zh") if isinstance(insight.get("deep_analysis_zh"), dict) else {}
        deep_en = insight.get("deep_analysis_en") if isinstance(insight.get("deep_analysis_en"), dict) else {}
        if is_english_language(lang):
            if deep_en:
                return deep_en
            if isinstance(deep_default, dict) and deep_default:
                deep_lang = normalize_analysis_language(deep_default.get("language", ""), default="")
                if is_english_language(deep_lang):
                    return deep_default
            return {}
        if is_chinese_language(lang):
            if deep_zh:
                return deep_zh
            if isinstance(deep_default, dict) and deep_default:
                deep_lang = normalize_analysis_language(deep_default.get("language", ""), default="")
                if is_chinese_language(deep_lang):
                    return deep_default
            return {}
        if isinstance(deep_default, dict) and deep_default:
            deep_lang = normalize_analysis_language(deep_default.get("language", ""), default="")
            if language_cache_key(deep_lang) == language_cache_key(lang):
                return deep_default
        return {}

    def get_paper_detail_by_key(self, paper_key: str, output_language: str = "Chinese") -> Optional[Dict[str, Any]]:
        record = self.get_paper_record_by_key(paper_key)
        if not record:
            return None

        meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
        insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}

        arxiv_id = str(record.get("arxiv_id", "") or "").strip()
        raw_title = str(record.get("title", "") or "").strip()
        title = self._pick_localized_title(raw_title, insight, output_language)
        author_text = str(record.get("author", "") or "").strip()
        published_at = str(record.get("published_at", "") or "").strip()
        updated_at = str(record.get("updated_at", "") or "").strip()
        summary = str(record.get("summary", "") or "").strip()
        url = str(record.get("url", "") or "").strip()

        authors_list = self._normalize_authors(meta, author_text)
        affiliations = self._normalize_affiliations(meta)
        if not affiliations and arxiv_id:
            affiliations = self._fetch_affiliations_from_arxiv(arxiv_id)

        primary_category = str(meta.get("primary_category", "") or "").strip()
        tags = self._normalize_tags(meta)
        if not primary_category and tags:
            primary_category = tags[0]

        abstract = clean_arxiv_abstract(str(meta.get("abstract", "") or "").strip() or summary)
        doi = str(meta.get("doi", "") or "").strip()
        pdf_url = str(meta.get("pdf_url", "") or "").strip()
        if not pdf_url and url and "/abs/" in url:
            pdf_url = url.replace("/abs/", "/pdf/")
            if not pdf_url.endswith(".pdf"):
                pdf_url += ".pdf"

        llm_summary = self._pick_localized_insight_text(insight, "one_sentence_summary", output_language)
        if not llm_summary:
            llm_summary = self._pick_localized_insight_text(insight, "summary", output_language)
        method_text = self._pick_localized_insight_text(insight, "method", output_language)
        conclusion = self._pick_localized_insight_text(insight, "conclusion", output_language)
        if not conclusion:
            conclusion = self._pick_localized_insight_text(insight, "findings", output_language)
        innovation = self._pick_localized_insight_text(insight, "innovation", output_language)
        if not innovation:
            innovation = self._pick_localized_insight_text(insight, "novelty", output_language)
        keywords = self._pick_localized_keywords(insight, output_language)

        raw_llm_summary = str(insight.get("one_sentence_summary") or insight.get("summary") or "").strip()
        raw_method = str(insight.get("method", "") or "").strip()
        raw_conclusion = str(insight.get("conclusion") or insight.get("findings") or "").strip()
        raw_innovation = str(insight.get("innovation") or insight.get("novelty") or "").strip()
        raw_keywords = self._normalize_keyword_list(insight.get("keywords"))

        settings = self.settings_store.load() if self.settings_store else {}
        selected_category = str(settings.get("paper_primary_category", "") or "").strip()
        selected_subtopics = split_subtopics(str(settings.get("paper_subtopics", "") or ""))
        recommendation_score = self._calc_recommendation_score(
            selected_category=selected_category,
            selected_subtopics=selected_subtopics,
            primary_category=primary_category,
            tags=tags,
            title=title,
            abstract=abstract,
            published_at=published_at,
            doi=doi,
            insight=insight,
        )
        confidence_score, confidence_label = self._calc_confidence(
            {
                "one_sentence_summary": raw_llm_summary,
                "method": raw_method,
                "conclusion": raw_conclusion,
                "innovation": raw_innovation,
                "keywords": raw_keywords,
                "confidence": insight.get("confidence", ""),
            }
        )

        action: Dict[str, Any] = {}
        if self.action_store:
            action_items = self.action_store.load().get("items", {})
            if isinstance(action_items, dict):
                maybe = action_items.get(str(record.get("paper_key", "") or ""))
                if isinstance(maybe, dict):
                    action = {
                        "favorite": bool(maybe.get("favorite")),
                        "ignored": bool(maybe.get("ignored")),
                        "note": str(maybe.get("note", "") or ""),
                        "tags": maybe.get("tags", []) if isinstance(maybe.get("tags"), list) else [],
                        "favorite_at": str(maybe.get("favorite_at", "") or ""),
                        "updated_at": str(maybe.get("updated_at", "") or ""),
                    }
        if not action:
            action = {
                "favorite": False,
                "ignored": False,
                "note": "",
                "tags": [],
                "favorite_at": "",
                "updated_at": "",
            }

        deep = self._select_deep_analysis_by_language(insight, output_language)
        deep_history = (
            insight.get("deep_analysis_history")
            if isinstance(insight.get("deep_analysis_history"), list)
            else []
        )

        return {
            "paper_key": str(record.get("paper_key", "") or ""),
            "title": title,
            "authors": authors_list,
            "affiliations": affiliations,
            "published_at": published_at,
            "updated_at": updated_at,
            "primary_category": primary_category,
            "tags": tags,
            "arxiv_id": arxiv_id,
            "abstract": abstract,
            "pdf_url": pdf_url,
            "doi": doi,
            "url": url,
            "recommendation_score": recommendation_score,
            "action": action,
            "insight": {
                "one_sentence_summary": llm_summary,
                "keywords": keywords,
                "method": method_text,
                "conclusion": conclusion,
                "innovation": innovation,
                "analysis_basis": str(insight.get("analysis_basis", "") or "").strip(),
                "confidence_label": confidence_label,
                "confidence_score": confidence_score,
                "analyzed_at": str(insight.get("analyzed_at", "") or "").strip(),
                "analysis_run_id": str(insight.get("analysis_run_id", "") or "").strip(),
                "deep_analysis": deep,
                "deep_analysis_history": [x for x in deep_history if isinstance(x, dict)],
            },
        }

    def save_paper_insight(self, db_path: str, rowid: int, insight: Dict[str, Any]) -> bool:
        try:
            rowid_int = int(rowid)
        except Exception:
            return False
        if rowid_int <= 0:
            return False
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE rss_items
                SET paper_insight_json = ?, updated_at = ?
                WHERE rowid = ?
                """,
                (
                    json.dumps(insight or {}, ensure_ascii=False),
                    utc_now_iso(),
                    rowid_int,
                ),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception:
            return False
        finally:
            conn.close()

    def _normalize_tags(self, meta: Dict[str, Any]) -> List[str]:
        tags = meta.get("categories") or []
        if isinstance(tags, list):
            vals = [str(v).strip() for v in tags if str(v).strip()]
        elif isinstance(tags, str):
            vals = [v.strip() for v in tags.split(",") if v.strip()]
        else:
            vals = []
        return vals

    def _normalize_authors(self, meta: Dict[str, Any], author: str) -> List[str]:
        authors = meta.get("authors") or []
        if isinstance(authors, list):
            authors_list = [str(v).strip() for v in authors if str(v).strip()]
        elif isinstance(authors, str):
            authors_list = [v.strip() for v in authors.split(",") if v.strip()]
        else:
            authors_list = []
        if not authors_list and author:
            authors_list = [v.strip() for v in str(author).split(",") if v.strip()]
        # Some arXiv RSS entries provide a single comma-joined author string.
        if len(authors_list) == 1 and "," in authors_list[0]:
            expanded = [v.strip() for v in authors_list[0].split(",") if v.strip()]
            if expanded:
                authors_list = expanded
        return authors_list

    def _normalize_affiliations(self, meta: Dict[str, Any]) -> List[str]:
        raw = meta.get("author_affiliations") or meta.get("affiliations") or []
        if isinstance(raw, list):
            return self._clean_affiliations([str(v).strip() for v in raw if str(v).strip()])
        if isinstance(raw, str):
            return self._clean_affiliations([v.strip() for v in raw.split(";") if v.strip()])
        return []

    def _matches_subtopics(
        self,
        subtopics: List[str],
        title: str,
        abstract: str,
        tags: List[str],
        insight: Dict[str, Any],
    ) -> bool:
        if not subtopics:
            return True
        keywords = insight.get("keywords") or []
        if isinstance(keywords, list):
            keywords_text = ", ".join(str(v) for v in keywords)
        else:
            keywords_text = str(keywords or "")
        haystack = " ".join(
            [
                str(title or ""),
                str(abstract or ""),
                " ".join(tags or []),
                str(keywords_text),
                str(insight.get("one_sentence_summary", "") or ""),
                str(insight.get("method", "") or ""),
            ]
        ).lower()
        return any(topic in haystack for topic in subtopics)

    def _build_haystack(
        self,
        title: str,
        abstract: str,
        tags: List[str],
        insight: Dict[str, Any],
    ) -> str:
        keywords = insight.get("keywords") or []
        if isinstance(keywords, list):
            keywords_text = ", ".join(str(v) for v in keywords)
        else:
            keywords_text = str(keywords or "")
        return " ".join(
            [
                str(title or ""),
                str(abstract or ""),
                " ".join(tags or []),
                keywords_text,
                str(insight.get("one_sentence_summary", "") or ""),
                str(insight.get("method", "") or ""),
                str(insight.get("conclusion", "") or ""),
                str(insight.get("innovation", "") or ""),
            ]
        ).lower()

    def _to_datetime(self, value: str) -> Optional[datetime]:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            pass
        try:
            return datetime.strptime(text[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def _to_timestamp(self, value: str) -> float:
        dt = self._to_datetime(value)
        if not dt:
            return 0.0
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()

    def _extract_score(self, insight: Dict[str, Any], key: str) -> Optional[int]:
        raw = insight.get(key)
        if raw is None:
            return None
        if isinstance(raw, (int, float)):
            return max(0, min(100, int(raw)))
        text = str(raw).strip()
        matched = re.search(r"(\d{1,3})", text)
        if not matched:
            return None
        try:
            return max(0, min(100, int(matched.group(1))))
        except Exception:
            return None

    def _calc_pre_recommendation_score(
        self,
        selected_category: str,
        selected_subtopics: List[str],
        primary_category: str,
        tags: List[str],
        title: str,
        abstract: str,
        published_at: str,
        doi: str,
    ) -> int:
        score = 30

        if selected_category:
            if selected_category == primary_category or selected_category in (tags or []):
                score += 20
            elif primary_category and selected_category.split(".")[0] == primary_category.split(".")[0]:
                score += 8
            else:
                score -= 6

        haystack = " ".join(
            [
                str(title or ""),
                str(abstract or ""),
                " ".join(tags or []),
            ]
        ).lower()

        if selected_subtopics:
            hit_count = sum(1 for topic in selected_subtopics if topic in haystack)
            score += min(30, hit_count * 7)

        title_lower = str(title or "").lower()
        title_signals = [
            "agent",
            "llm",
            "reason",
            "reasoning",
            "alignment",
            "multi-agent",
            "retrieval",
            "rag",
            "benchmark",
            "evaluation",
            "survey",
            "sota",
            "efficient",
            "multimodal",
        ]
        signal_hits = sum(1 for token in title_signals if token in title_lower)
        score += min(15, signal_hits * 3)

        dt = self._to_datetime(published_at)
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_days = max(0, int((datetime.now(timezone.utc) - dt).total_seconds() // 86400))
            if age_days <= 2:
                score += 18
            elif age_days <= 7:
                score += 14
            elif age_days <= 14:
                score += 10
            elif age_days <= 30:
                score += 6
            else:
                score += 2

        if str(doi or "").strip():
            score += 2
        return max(0, min(100, int(score)))

    def _calc_confidence(self, insight: Dict[str, Any]) -> Tuple[int, str]:
        raw = str(insight.get("confidence", "") or "").strip()
        raw_num: Optional[int] = None
        if raw:
            matched = re.search(r"(\d{1,3})", raw)
            if matched:
                try:
                    raw_num = max(0, min(int(matched.group(1)), 100))
                except Exception:
                    raw_num = None

        if raw_num is None:
            parts = [
                bool(str(insight.get("one_sentence_summary", "") or "").strip()),
                bool(str(insight.get("method", "") or "").strip()),
                bool(str(insight.get("conclusion", "") or "").strip()),
                bool(str(insight.get("innovation", "") or "").strip()),
                bool(insight.get("keywords")),
            ]
            raw_num = int((sum(1 for x in parts if x) / max(1, len(parts))) * 100)

        if raw_num >= 80:
            return raw_num, "高"
        if raw_num >= 60:
            return raw_num, "中"
        return raw_num, "低"

    def _calc_recommendation_score(
        self,
        selected_category: str,
        selected_subtopics: List[str],
        primary_category: str,
        tags: List[str],
        title: str,
        abstract: str,
        published_at: str,
        doi: str,
        insight: Dict[str, Any],
    ) -> int:
        stored_final = self._extract_score(insight, "recommendation_score")
        if stored_final is not None:
            return stored_final

        stored_pre = self._extract_score(insight, "pre_score")
        base_score = (
            stored_pre
            if stored_pre is not None
            else self._calc_pre_recommendation_score(
                selected_category=selected_category,
                selected_subtopics=selected_subtopics,
                primary_category=primary_category,
                tags=tags,
                title=title,
                abstract=abstract,
                published_at=published_at,
                doi=doi,
            )
        )

        llm_bonus = 0
        if str(insight.get("one_sentence_summary", "") or "").strip():
            llm_bonus += 10
        if str(insight.get("method", "") or "").strip():
            llm_bonus += 8
        if str(insight.get("conclusion", "") or "").strip():
            llm_bonus += 8
        if str(insight.get("innovation", "") or "").strip():
            llm_bonus += 8
        keywords = insight.get("keywords") or []
        if isinstance(keywords, list):
            llm_bonus += min(8, len([x for x in keywords if str(x).strip()]) * 2)

        confidence_score = self._extract_score(insight, "confidence")
        confidence_bonus = int((confidence_score or 0) * 0.12)
        score = int(round(base_score * 0.72 + llm_bonus + confidence_bonus))
        return max(0, min(100, score))

    def _matches_text(self, keyword: str, *values: Any) -> bool:
        text = str(keyword or "").strip().lower()
        if not text:
            return True
        haystack = " ".join(str(v or "") for v in values).lower()
        return text in haystack

    def list_papers(
        self,
        limit: int = 80,
        mode: str = "all",
        sort_by: str = "score",
        sort_order: str = "desc",
        history: str = "all",
        filters: Optional[Dict[str, Any]] = None,
        output_language: str = "Chinese",
        include_internal: bool = False,
    ) -> Dict[str, Any]:
        settings = self.settings_store.load() if self.settings_store else {}
        selected_category = str(settings.get("paper_primary_category", "") or "").strip()
        selected_subtopics = split_subtopics(str(settings.get("paper_subtopics", "") or ""))
        extra_filters = normalize_panel_filters(filters or {})
        search_q = str(extra_filters.get("q", "") or "").lower()
        search_author = str(extra_filters.get("author", "") or "").lower()
        search_affiliation = str(extra_filters.get("affiliation", "") or "").lower()
        search_tag = str(extra_filters.get("tag", "") or "").lower()
        filter_category = str(extra_filters.get("category", "") or "").strip()
        filter_has_doi = str(extra_filters.get("has_doi", "any") or "any").lower()
        filter_date_from = str(extra_filters.get("date_from", "") or "").strip()
        filter_date_to = str(extra_filters.get("date_to", "") or "").strip()
        score_min = extra_filters.get("score_min")
        score_max = extra_filters.get("score_max")

        view_mode = str(mode or "all").strip().lower()
        if view_mode not in {"all", "favorites", "ignored"}:
            view_mode = "all"
        sort_mode = str(sort_by or "score").strip().lower()
        if sort_mode not in {"score", "time", "title"}:
            sort_mode = "score"
        sort_order_mode = str(sort_order or "desc").strip().lower()
        if sort_order_mode not in {"asc", "desc"}:
            sort_order_mode = "desc"
        history_mode = str(history or "all").strip().lower()
        if history_mode not in {"latest", "all"}:
            history_mode = "all"
        output_lang = normalize_analysis_language(output_language, default="Chinese")

        action_items: Dict[str, Any] = {}
        if self.action_store:
            action_items = self.action_store.load().get("items", {})

        db_files = self._rss_db_files()
        if not db_files:
            return {
                "db_path": "",
                "papers": [],
                "stats": {
                    "mode": view_mode,
                    "sort_by": sort_mode,
                    "sort_order": sort_order_mode,
                    "history_mode": history_mode,
                    "filters": extra_filters,
                    "selected_category": selected_category,
                    "selected_subtopics": selected_subtopics,
                    "total_scanned": 0,
                    "total_candidates": 0,
                    "filtered_unanalyzed": 0,
                    "filtered_category": 0,
                    "filtered_subtopics": 0,
                    "filtered_ignored": 0,
                    "filtered_favorites_mode": 0,
                    "filtered_ignored_mode": 0,
                    "returned": 0,
                    "favorite_records": sum(
                        1 for x in action_items.values() if isinstance(x, dict) and x.get("favorite")
                    ),
                },
            }

        target_db_files = db_files[:1] if history_mode == "latest" else db_files
        latest_db_path = target_db_files[0] if target_db_files else db_files[0]
        scan_limit_per_db = max(200, min(max(1, limit) * 10, 5000))
        max_total_scan = 20000
        rows: List[Tuple[Any, ...]] = []
        for source_db in target_db_files:
            if len(rows) >= max_total_scan:
                break
            remaining = max_total_scan - len(rows)
            per_db_limit = min(scan_limit_per_db, remaining)
            conn = sqlite3.connect(str(source_db))
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                        title, author, published_at, summary, url,
                        paper_meta_json, paper_insight_json, updated_at
                    FROM rss_items
                    WHERE
                        (paper_meta_json IS NOT NULL AND paper_meta_json <> '')
                        OR url LIKE '%arxiv.org/%'
                    ORDER BY COALESCE(published_at, updated_at) DESC
                    LIMIT ?
                    """,
                    (per_db_limit,),
                )
                fetched = cur.fetchall()
                for item in fetched:
                    rows.append((str(source_db),) + tuple(item))
            except Exception:
                pass
            finally:
                conn.close()

        papers: List[Dict[str, Any]] = []
        seen_keys = set()
        aff_lookup_budget = 2
        stats = {
            "mode": view_mode,
            "sort_by": sort_mode,
            "sort_order": sort_order_mode,
            "history_mode": history_mode,
            "filters": extra_filters,
            "selected_category": selected_category,
            "selected_subtopics": selected_subtopics,
            "total_scanned": len(rows),
            "total_candidates": 0,
            "filtered_unanalyzed": 0,
            "filtered_category": 0,
            "filtered_subtopics": 0,
            "filtered_search": 0,
            "filtered_author": 0,
            "filtered_affiliation": 0,
            "filtered_tag": 0,
            "filtered_filter_category": 0,
            "filtered_date": 0,
            "filtered_score": 0,
            "filtered_doi": 0,
            "filtered_ignored": 0,
            "filtered_favorites_mode": 0,
            "filtered_ignored_mode": 0,
            "returned": 0,
            "favorite_records": sum(
                1 for x in action_items.values() if isinstance(x, dict) and x.get("favorite")
            ),
        }
        for row in rows:
            source_db_path, title, author, published_at, summary, url, meta_json, insight_json, updated_at = row
            meta = safe_load_json(meta_json)
            insight = safe_load_json(insight_json)

            arxiv_id = str(meta.get("arxiv_id", "") or "").strip()
            uniq_key, arxiv_id = self._build_paper_key(meta, str(url or ""), str(title or ""))
            if uniq_key in seen_keys:
                continue
            seen_keys.add(uniq_key)
            stats["total_candidates"] += 1

            state = action_items.get(uniq_key, {}) if isinstance(action_items, dict) else {}
            is_favorite = bool(state.get("favorite")) if isinstance(state, dict) else False
            is_ignored = bool(state.get("ignored")) if isinstance(state, dict) else False
            if view_mode == "ignored":
                if not is_ignored:
                    stats["filtered_ignored_mode"] += 1
                    continue
            else:
                if is_ignored:
                    stats["filtered_ignored"] += 1
                    continue
            if view_mode == "favorites" and not is_favorite:
                stats["filtered_favorites_mode"] += 1
                continue

            raw_title = str(title or "").strip()
            localized_title = self._pick_localized_title(raw_title, insight, output_lang)

            authors_list = self._normalize_authors(meta, author)
            affiliations = self._normalize_affiliations(meta)
            if not affiliations and arxiv_id and aff_lookup_budget > 0:
                aff_lookup_budget -= 1
                affiliations = self._fetch_affiliations_from_arxiv(arxiv_id)

            primary_category = str(meta.get("primary_category", "") or "").strip()
            tags = self._normalize_tags(meta)
            if not primary_category and tags:
                primary_category = tags[0]

            pdf_url = str(meta.get("pdf_url", "") or "").strip()
            if not pdf_url and url and "/abs/" in url:
                pdf_url = url.replace("/abs/", "/pdf/")
                if not pdf_url.endswith(".pdf"):
                    pdf_url += ".pdf"

            doi = str(meta.get("doi", "") or "").strip()
            abstract = clean_arxiv_abstract(
                str(meta.get("abstract", "") or "").strip() or str(summary or "").strip()
            )

            raw_llm_summary = str(
                insight.get("one_sentence_summary")
                or insight.get("summary")
                or ""
            ).strip()
            raw_conclusion = str(
                insight.get("conclusion")
                or insight.get("findings")
                or ""
            ).strip()
            raw_innovation = str(
                insight.get("innovation")
                or insight.get("novelty")
                or ""
            ).strip()
            raw_keywords = self._normalize_keyword_list(insight.get("keywords"))
            raw_method_text = str(insight.get("method", "") or "").strip()
            llm_summary = self._pick_localized_insight_text(insight, "one_sentence_summary", output_lang)
            if not llm_summary:
                llm_summary = self._pick_localized_insight_text(insight, "summary", output_lang)
            method_text = self._pick_localized_insight_text(insight, "method", output_lang)
            conclusion = self._pick_localized_insight_text(insight, "conclusion", output_lang)
            if not conclusion:
                conclusion = self._pick_localized_insight_text(insight, "findings", output_lang)
            innovation = self._pick_localized_insight_text(insight, "innovation", output_lang)
            if not innovation:
                innovation = self._pick_localized_insight_text(insight, "novelty", output_lang)
            keywords = self._pick_localized_keywords(insight, output_lang)
            deep_analysis = self._select_deep_analysis_by_language(insight, output_lang)
            analyzed = bool(
                raw_llm_summary
                or raw_method_text
                or raw_conclusion
                or raw_innovation
                or raw_keywords
                or llm_summary
                or method_text
                or conclusion
                or innovation
                or keywords
            )
            if not analyzed:
                stats["filtered_unanalyzed"] += 1
                continue
            if view_mode == "all" and selected_category and selected_category not in set([primary_category] + tags):
                stats["filtered_category"] += 1
                continue
            if view_mode == "all" and not self._matches_subtopics(
                selected_subtopics,
                raw_title,
                abstract,
                tags,
                insight,
            ):
                stats["filtered_subtopics"] += 1
                continue

            recommendation_score = self._calc_recommendation_score(
                selected_category=selected_category,
                selected_subtopics=selected_subtopics,
                primary_category=primary_category,
                tags=tags,
                title=raw_title,
                abstract=abstract,
                published_at=str(published_at or "").strip(),
                doi=doi,
                insight=insight,
            )
            published_text = str(published_at or "").strip()
            tags_text = " ".join(tags or [])
            if search_q and not self._matches_text(
                search_q,
                raw_title,
                localized_title,
                abstract,
                arxiv_id,
                doi,
                pdf_url,
                tags_text,
                " ".join(authors_list),
                " ".join(affiliations),
                raw_llm_summary,
                raw_method_text,
                raw_conclusion,
                raw_innovation,
                llm_summary,
                method_text,
                conclusion,
                innovation,
            ):
                stats["filtered_search"] += 1
                continue
            if search_author and not self._matches_text(search_author, " ".join(authors_list)):
                stats["filtered_author"] += 1
                continue
            if search_affiliation and not self._matches_text(search_affiliation, " ".join(affiliations)):
                stats["filtered_affiliation"] += 1
                continue
            if search_tag and not self._matches_text(search_tag, tags_text):
                stats["filtered_tag"] += 1
                continue
            if filter_category and filter_category not in set([primary_category] + tags):
                stats["filtered_filter_category"] += 1
                continue
            if filter_has_doi == "yes" and not doi:
                stats["filtered_doi"] += 1
                continue
            if filter_has_doi == "no" and doi:
                stats["filtered_doi"] += 1
                continue
            if filter_date_from or filter_date_to:
                published_date = published_text[:10]
                if filter_date_from and (not published_date or published_date < filter_date_from):
                    stats["filtered_date"] += 1
                    continue
                if filter_date_to and (not published_date or published_date > filter_date_to):
                    stats["filtered_date"] += 1
                    continue
            if score_min is not None and recommendation_score < int(score_min):
                stats["filtered_score"] += 1
                continue
            if score_max is not None and recommendation_score > int(score_max):
                stats["filtered_score"] += 1
                continue

            confidence_score, confidence_label = self._calc_confidence(
                {
                    "one_sentence_summary": raw_llm_summary or llm_summary,
                    "method": raw_method_text or method_text,
                    "conclusion": raw_conclusion or conclusion,
                    "innovation": raw_innovation or innovation,
                    "keywords": raw_keywords or keywords,
                    "confidence": insight.get("confidence", ""),
                }
            )

            papers.append(
                {
                    "paper_key": uniq_key,
                    "title": localized_title or raw_title,
                    "authors": authors_list,
                    "affiliations": affiliations,
                    "published_at": published_text,
                    "primary_category": primary_category,
                    "tags": tags,
                    "arxiv_id": arxiv_id,
                    "abstract": abstract,
                    "pdf_url": pdf_url,
                    "doi": doi,
                    "url": str(url or "").strip(),
                    "updated_at": str(updated_at or "").strip(),
                    "recommendation_score": recommendation_score,
                    "action": {
                        "favorite": is_favorite,
                        "ignored": is_ignored,
                        "note": str(state.get("note", "") or "") if isinstance(state, dict) else "",
                        "tags": state.get("tags", []) if isinstance(state, dict) else [],
                        "favorite_at": str(state.get("favorite_at", "") or "") if isinstance(state, dict) else "",
                        "updated_at": str(state.get("updated_at", "") or "") if isinstance(state, dict) else "",
                    },
                    "insight": {
                        "one_sentence_summary": llm_summary,
                        "keywords": keywords,
                        "method": method_text,
                        "conclusion": conclusion,
                        "innovation": innovation,
                        "analysis_basis": str(
                            insight.get("analysis_basis")
                            or "标题、作者、分类、摘要（非全文）"
                        ),
                        "confidence_label": confidence_label,
                        "confidence_score": confidence_score,
                        "analyzed_at": str(insight.get("analyzed_at", "") or "").strip(),
                        "analysis_run_id": str(insight.get("analysis_run_id", "") or "").strip(),
                        "pre_score": self._extract_score(insight, "pre_score"),
                        "deep_analysis": deep_analysis,
                    },
                    "_published_ts": self._to_timestamp(str(published_at or "")),
                    "_analyzed_ts": self._to_timestamp(str(insight.get("analyzed_at", "") or "")),
                    "_history_key": str(insight.get("analysis_run_id", "") or "").strip()
                    or str(insight.get("analyzed_at", "") or "").strip()[:10],
                    "_db_path": str(source_db_path or ""),
                }
            )
        if history_mode == "latest" and papers:
            latest_key = ""
            latest_ts = -1.0
            for paper in papers:
                key = str(paper.get("_history_key", "") or "").strip()
                ts = float(paper.get("_analyzed_ts", 0.0) or 0.0)
                if key and (ts > latest_ts or (ts == latest_ts and key > latest_key)):
                    latest_key = key
                    latest_ts = ts
            if latest_key:
                papers = [paper for paper in papers if str(paper.get("_history_key", "")) == latest_key]
                stats["latest_history_key"] = latest_key

        reverse_sort = sort_order_mode != "asc"
        if sort_mode == "time":
            key_fn = lambda p: (
                float(p.get("_published_ts", 0.0)),
                int(p.get("recommendation_score", 0)),
            )
        elif sort_mode == "title":
            key_fn = lambda p: (
                str(p.get("title", "")).lower(),
                int(p.get("recommendation_score", 0)),
            )
        else:
            key_fn = lambda p: (
                int(p.get("recommendation_score", 0)),
                float(p.get("_published_ts", 0.0)),
            )
        papers.sort(key=key_fn, reverse=reverse_sort)

        papers = papers[: max(1, min(limit, 500))]
        for paper in papers:
            paper.pop("_published_ts", None)
            paper.pop("_analyzed_ts", None)
            paper.pop("_history_key", None)
            if not include_internal:
                paper.pop("_db_path", None)
        stats["returned"] = len(papers)
        return {"db_path": str(latest_db_path), "papers": papers, "stats": stats}


class DeepAnalysisService:
    """Manual deep analysis for one selected paper card."""

    def __init__(self, settings_store: PanelSettingsStore, paper_repo: PaperRepository):
        self.settings_store = settings_store
        self.paper_repo = paper_repo
        self._context_cache: Dict[str, Dict[str, str]] = {}
        self._context_lock = threading.RLock()
        self._markitdown = None

    def _extract_json(self, text: str) -> str:
        if not text:
            return ""
        fenced = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if fenced:
            return fenced.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1].strip()
        return ""

    def _normalize_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in re.split(r"[;\n,]", value) if v.strip()]
        return []

    def _pick_text(self, parsed: Dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = parsed.get(key)
            if value is None:
                continue
            text = str(value or "").strip()
            if text:
                return text
        return ""

    def _pick_list(self, parsed: Dict[str, Any], *keys: str) -> List[str]:
        for key in keys:
            value = parsed.get(key)
            values = self._normalize_list(value)
            if values:
                return values
        return []

    def _has_meaningful_deep_content(self, deep: Any) -> bool:
        if not isinstance(deep, dict):
            return False
        for value in deep.values():
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, list):
                if any(str(item).strip() for item in value):
                    return True
            if isinstance(value, dict) and value:
                return True
        return False

    def _download_url_text(self, url: str, timeout: int = 10) -> str:
        target = str(url or "").strip()
        if not target:
            return ""
        try:
            req = urllib.request.Request(
                target,
                headers={
                    "User-Agent": "OmniHawk AI-Panel/1.0 (+https://arxiv.org)",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content_type = str(resp.headers.get("Content-Type", "") or "").lower()
                data = resp.read()
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
                return data.decode(charset or "utf-8", errors="ignore")
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def _download_url_bytes(self, url: str, timeout: int = 20) -> bytes:
        target = str(url or "").strip()
        if not target:
            return b""
        try:
            req = urllib.request.Request(
                target,
                headers={
                    "User-Agent": "OmniHawk AI-Panel/1.0 (+https://arxiv.org)",
                    "Accept": "application/pdf,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception:
            return b""

    def _get_markitdown(self) -> Any:
        if self._markitdown is False:
            return None
        if self._markitdown is not None:
            return self._markitdown
        try:
            from markitdown import MarkItDown

            self._markitdown = MarkItDown()
            return self._markitdown
        except Exception:
            self._markitdown = False
            return None

    def _strip_markdown_references(self, markdown_text: str) -> str:
        text = str(markdown_text or "").strip()
        if not text:
            return ""
        lines = text.splitlines()
        total = len(lines)
        if total < 24:
            return text
        threshold = max(20, int(total * 0.45))
        heading_patterns = [
            re.compile(r"^\s{0,3}#{1,6}\s*(references|reference|bibliography|works cited|citations)\s*$", re.I),
            re.compile(r"^\s*(references|reference|bibliography|works cited|citations)\s*$", re.I),
            re.compile(r"^\s{0,3}#{1,6}\s*(参考文献|参考资料)\s*$", re.I),
            re.compile(r"^\s*(参考文献|参考资料)\s*$", re.I),
        ]
        cut_idx = -1
        for i, line in enumerate(lines):
            if i < threshold:
                continue
            candidate = str(line or "").strip()
            if not candidate:
                continue
            if any(pat.match(candidate) for pat in heading_patterns):
                cut_idx = i
                break
        if cut_idx > 0:
            return "\n".join(lines[:cut_idx]).strip()
        return text

    def _extract_pdf_context_by_markitdown(
        self,
        pdf_url: str,
        arxiv_id: str = "",
    ) -> Dict[str, str]:
        source_url = str(pdf_url or "").strip()
        if not source_url:
            return {"source": "", "text": ""}

        converter = self._get_markitdown()
        if converter is None:
            return {"source": "markitdown_unavailable", "text": ""}

        markdown_text = ""
        try:
            result = converter.convert(source_url)
            markdown_text = str(getattr(result, "markdown", "") or "").strip()
        except Exception:
            markdown_text = ""

        if not markdown_text:
            raw_pdf = self._download_url_bytes(source_url, timeout=24)
            if raw_pdf:
                tmp_path = ""
                try:
                    suffix = f"_{re.sub(r'[^0-9A-Za-z._-]+', '_', arxiv_id)}.pdf" if arxiv_id else ".pdf"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".pdf") as tmp:
                        tmp.write(raw_pdf)
                        tmp_path = tmp.name
                    result = converter.convert(tmp_path)
                    markdown_text = str(getattr(result, "markdown", "") or "").strip()
                except Exception:
                    markdown_text = ""
                finally:
                    if tmp_path:
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass

        markdown_text = self._strip_markdown_references(markdown_text)
        if not markdown_text:
            return {"source": "", "text": ""}
        return {
            "source": "markitdown_pdf_markdown",
            "text": markdown_text[:48000],
        }

    def _html_to_text(self, raw_html: str) -> str:
        text = str(raw_html or "")
        if not text:
            return ""
        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<(br|/p|/li|/h1|/h2|/h3|/h4|/h5|/h6)\b[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<li\b[^>]*>", "\n- ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_fulltext_context(self, arxiv_id: str, url: str, abstract: str, pdf_url: str = "") -> Dict[str, str]:
        key = str(arxiv_id or "").strip() or str(url or "").strip() or str(pdf_url or "").strip()
        with self._context_lock:
            cached = self._context_cache.get(key)
            if isinstance(cached, dict):
                return dict(cached)

        context_source = "none"
        context_text = ""
        arxiv_clean = str(arxiv_id or "").strip()
        html_url = f"https://arxiv.org/html/{arxiv_clean}" if arxiv_clean else ""
        abs_url = f"https://arxiv.org/abs/{arxiv_clean}" if arxiv_clean else ""
        pdf_url_candidate = str(pdf_url or "").strip()
        if not pdf_url_candidate and abs_url:
            pdf_url_candidate = abs_url.replace("/abs/", "/pdf/")
            if not pdf_url_candidate.endswith(".pdf"):
                pdf_url_candidate += ".pdf"
        if not pdf_url_candidate and arxiv_clean:
            pdf_url_candidate = f"https://arxiv.org/pdf/{arxiv_clean}.pdf"

        # Priority 1: PDF -> MarkItDown markdown (strip references section).
        if pdf_url_candidate:
            pdf_payload = self._extract_pdf_context_by_markitdown(
                pdf_url=pdf_url_candidate,
                arxiv_id=arxiv_clean,
            )
            maybe_source = str(pdf_payload.get("source", "") or "").strip()
            maybe_text = str(pdf_payload.get("text", "") or "").strip()
            if maybe_text:
                context_source = maybe_source
                context_text = maybe_text

        # Priority 2: arXiv HTML full text (contains sections/captions for many papers).
        if not context_text and html_url:
            raw_html = self._download_url_text(html_url, timeout=12)
            if raw_html and "arxiv" in raw_html.lower():
                plain = self._html_to_text(raw_html)
                if plain:
                    context_source = "arxiv_html_fulltext"
                    context_text = plain[:24000]

        # Priority 3: abstract page text (metadata + abstract + comments).
        if not context_text and abs_url:
            raw_abs = self._download_url_text(abs_url, timeout=10)
            if raw_abs:
                plain_abs = self._html_to_text(raw_abs)
                if plain_abs:
                    context_source = "arxiv_abs_page"
                    context_text = plain_abs[:14000]

        # Priority 4: fallback to abstract only.
        if not context_text:
            context_source = "metadata_abstract_only"
            context_text = str(abstract or "").strip()[:8000]

        payload = {"source": context_source, "text": context_text}
        with self._context_lock:
            self._context_cache[key] = dict(payload)
            if len(self._context_cache) > 200:
                # Keep memory bounded.
                oldest_key = next(iter(self._context_cache.keys()))
                self._context_cache.pop(oldest_key, None)
        return payload

    def analyze_selected_paper(
        self,
        paper_key: str,
        focus: str = "",
        question: str = "",
        output_language: str = "",
        force: bool = False,
    ) -> Dict[str, Any]:
        record = self.paper_repo.get_paper_record_by_key(paper_key)
        if not record:
            return {"ok": False, "error": "paper not found"}

        settings = self.settings_store.load()
        model = str(settings.get("ai_model", "") or "").strip()
        api_key = str(settings.get("ai_api_key", "") or "").strip()
        api_base = str(settings.get("ai_api_base", "") or "").strip()
        runtime_model = to_runtime_model_name(model, api_base)
        analysis_language = normalize_analysis_language(
            output_language,
            default=normalize_analysis_language(settings.get("analysis_language", "Chinese"), default="Chinese"),
        )
        is_english = is_english_language(analysis_language)
        output_language_text = analysis_language or "Chinese"
        if not runtime_model:
            return {"ok": False, "error": "LLM 模型未配置"}
        if not api_key:
            return {"ok": False, "error": "LLM API Key 未配置"}

        existing_insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
        existing_deep = existing_insight.get("deep_analysis")
        if not force and self._has_meaningful_deep_content(existing_deep):
            return {
                "ok": True,
                "cached": True,
                "paper_key": paper_key,
                "deep_analysis": existing_deep,
                "message": "已存在深入分析结果（可传 force=true 覆盖）",
            }

        meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
        title = str(record.get("title", "") or "")
        abstract = clean_arxiv_abstract(
            str(meta.get("abstract", "") or "").strip() or str(record.get("summary", "") or "").strip()
        )
        categories = meta.get("categories") or []
        if isinstance(categories, list):
            categories_text = ", ".join(str(v).strip() for v in categories if str(v).strip())
        else:
            categories_text = str(categories or "")
        authors = meta.get("authors") or []
        if isinstance(authors, list):
            authors_text = ", ".join(str(v).strip() for v in authors if str(v).strip())
        else:
            authors_text = str(authors or "")
        primary_category = str(meta.get("primary_category", "") or "").strip()
        arxiv_id = str(record.get("arxiv_id", "") or "").strip()
        url = str(record.get("url", "") or "").strip()
        pdf_url = str(meta.get("pdf_url", "") or "").strip()
        if not pdf_url and url and "/abs/" in url:
            pdf_url = url.replace("/abs/", "/pdf/")
            if not pdf_url.endswith(".pdf"):
                pdf_url += ".pdf"
        full_context = self._extract_fulltext_context(
            arxiv_id=arxiv_id,
            url=url,
            abstract=abstract,
            pdf_url=pdf_url,
        )
        context_source = str(full_context.get("source", "") or "").strip()
        context_text = str(full_context.get("text", "") or "").strip()
        focus_text = str(focus or "").strip()
        question_text = str(question or "").strip()
        if not focus_text:
            auto_focus_parts = []
            research_topic = str(settings.get("research_topic", "") or "").strip()
            if research_topic:
                if is_english:
                    auto_focus_parts.append(f"Research-fit alignment: {research_topic}")
                else:
                    auto_focus_parts.append(f"研究方向契合度: {research_topic}")
            if primary_category:
                if is_english:
                    auto_focus_parts.append(f"Primary category fit: {primary_category}")
                else:
                    auto_focus_parts.append(f"主分类定位: {primary_category}")
            if is_english:
                auto_focus_parts.append(
                    "Focus checks: problem framing, method mechanism, experiment design, reproducibility, practical value, potential risks"
                )
                focus_text = "; ".join(auto_focus_parts)
            else:
                auto_focus_parts.append("重点检查: 问题定义、方法机制、实验设计、可复现性、应用价值、潜在风险")
                focus_text = "；".join(auto_focus_parts)
        if not question_text:
            question_text = (
                "Please additionally provide the 3 most worthwhile follow-up experiment questions."
                if is_english
                else "请额外给出最值得跟进的 3 个后续实验问题。"
            )
        template_text = load_deep_analysis_template_text()
        if len(template_text) > 20000:
            template_text = template_text[:20000]
        language_rule_line = (
            f"4.1) 所有文本字段必须使用 {output_language_text}，不得混入其它语言句子。\n"
        )

        user_prompt = (
            "你是严谨的论文研究助手。请对下述论文做“深入分析”，输出 JSON。\n"
            "要求：\n"
            "1) 基于给定元数据与正文材料，禁止臆造不存在的实验细节。\n"
            "2) 若信息不足，明确写出“信息不足”，不要硬编。\n"
            "3) 所有字段都要返回，缺失时返回空字符串或空数组。\n"
            f"4) 输出语言：{output_language_text}。\n"
            f"{language_rule_line}"
            "5) 若涉及公式，请使用 LaTeX（行内 $...$ 或块级 $$...$$）。\n"
            "6) 禁止输出 JSON 之外的解释文本。\n"
            "7) 模板仅作为思考框架，禁止照抄模板标题或句式，禁止机械罗列。\n"
            "8) 核心叙事字段使用“段落化分析”，建议 2-4 段、每段 2-4 句，不要一句话带过。\n"
            "9) 优先给“结构化叙事”，减少重复字段堆叠。\n"
            "10) 若正文材料出现 Figure/Table 编号，可引用“图1/表2”等；若无则明确“未提供图表信息”。\n\n"
            "参考模板（仅用于维度校验，不可复述原文）：\n"
            f"{template_text}\n\n"
            "请按统一框架输出，逻辑顺序必须清晰：\n"
            "- executive_summary: 结论先行的执行摘要（3-6句）。\n"
            "- problem_landscape: 问题背景、动机、约束、运行例子（可整合）。\n"
            "- method_and_mechanism: 核心方法、关键机制、为何这样设计。\n"
            "- evidence_and_trustworthiness: 实验设计、证据强度、可复现性与可信边界。\n"
            "- impact_and_roadmap: 应用价值、局限风险、后续研究路线。\n\n"
            "列表字段按论文实际内容给出，不要凑数量：\n"
            "- technical_challenges: 解释为什么 naive 方法不行。\n"
            "- contribution_claims: 论文真实贡献点。\n"
            "- key_formulae: 能提取则给公式 + 变量说明，不能提取就空数组。\n"
            "- recommended_followups / reading_questions: 给可执行后续建议。\n\n"
            "JSON 字段：\n"
            "{\n"
            '  "executive_summary": "执行摘要（3-6句）",\n'
            '  "problem_landscape": "问题背景、动机、约束、运行例子（可整合）",\n'
            '  "method_and_mechanism": "方法与关键机制（含设计动机）",\n'
            '  "evidence_and_trustworthiness": "实验证据、可信度与复现边界",\n'
            '  "impact_and_roadmap": "应用价值、局限风险、后续路线",\n'
            '  "technical_challenges": ["挑战A", "挑战B", "..."],\n'
            '  "contribution_claims": ["贡献A", "贡献B", "..."],\n'
            '  "key_formulae": ["关键公式1(LaTeX)+解释", "关键公式2(LaTeX)+解释"],\n'
            '  "recommended_followups": ["后续实验建议1", "后续实验建议2"],\n'
            '  "reading_questions": ["建议进一步阅读的问题1", "问题2"],\n'
            '  "open_problems": "仍待解决的问题",\n'
            '  "confidence_rationale": "说明结论可信度依据（证据充分/不足点）"\n'
            "}\n\n"
            f"论文标题: {title}\n"
            f"arXiv ID: {arxiv_id}\n"
            f"主分类: {primary_category}\n"
            f"分类标签: {categories_text}\n"
            f"作者: {authors_text}\n"
            f"发布时间: {record.get('published_at', '')}\n"
            f"论文链接: {url}\n"
            f"摘要: {abstract}\n"
            f"正文来源: {context_source}\n"
            "正文材料（可能截断）：\n"
            f"{context_text}\n"
        )
        if focus_text:
            user_prompt += f"\n深入关注点: {focus_text}\n"
        if question_text:
            user_prompt += f"用户追问: {question_text}\n"

        client = AIClient(
            {
                "MODEL": runtime_model,
                "API_KEY": api_key,
                "API_BASE": api_base,
                "TEMPERATURE": 0.2,
                "MAX_TOKENS": 10000,
                "TIMEOUT": 180,
            }
        )

        try:
            response = client.chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a rigorous and practical deep paper analysis assistant."
                            if is_english
                            else "你是严谨、务实的论文深度分析助手。"
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ]
            )
        except Exception as exc:
            return {"ok": False, "error": f"LLM 调用失败: {type(exc).__name__}: {exc}"}

        payload = self._extract_json(response)
        parsed: Dict[str, Any] = {}
        if payload:
            try:
                raw = json.loads(payload)
                if isinstance(raw, dict):
                    parsed = raw
            except Exception:
                parsed = {}

        now = utc_now_iso()
        executive_summary = self._pick_text(
            parsed,
            "executive_summary",
            "one_line_verdict",
            "verdict",
            "summary_judgement",
            "summary",
        )
        problem_landscape = self._pick_text(
            parsed,
            "problem_landscape",
            "problem_and_context",
            "background_and_field_context",
            "problem_definition_and_constraints",
        )
        method_and_mechanism = self._pick_text(
            parsed,
            "method_and_mechanism",
            "method_deep_dive",
            "method_details",
            "method_overview",
            "core_idea",
        )
        evidence_and_trustworthiness = self._pick_text(
            parsed,
            "evidence_and_trustworthiness",
            "results_and_evidence",
            "experimental_design",
            "main_results_expectation",
            "reproducibility",
        )
        impact_and_roadmap = self._pick_text(
            parsed,
            "impact_and_roadmap",
            "so_what_summary",
            "practical_value",
            "open_problems",
        )
        confidence_rationale = self._pick_text(
            parsed,
            "confidence_rationale",
            "confidence_note",
            "insight_hypotheses",
            "reproducibility",
        )

        deep = {
            "executive_summary": executive_summary,
            "problem_landscape": problem_landscape,
            "method_and_mechanism": method_and_mechanism,
            "evidence_and_trustworthiness": evidence_and_trustworthiness,
            "impact_and_roadmap": impact_and_roadmap,
            "confidence_rationale": confidence_rationale,
            "one_line_verdict": self._pick_text(
                parsed, "one_line_verdict", "verdict", "summary_judgement", "executive_summary"
            )
            or executive_summary,
            "background_and_field_context": self._pick_text(
                parsed, "background_and_field_context", "background", "field_context", "problem_landscape"
            )
            or problem_landscape,
            "motivation_and_why_now": self._pick_text(
                parsed, "motivation_and_why_now", "why_now", "motivation", "problem_landscape"
            )
            or problem_landscape,
            "problem_definition_and_constraints": self._pick_text(
                parsed,
                "problem_definition_and_constraints",
                "problem_definition",
                "problem_constraints",
                "problem_landscape",
            )
            or problem_landscape,
            "running_example": self._pick_text(parsed, "running_example", "case_example", "running_case"),
            "problem_and_context": self._pick_text(
                parsed,
                "problem_and_context",
                "background_and_field_context",
                "problem_definition_and_constraints",
                "problem_landscape",
            )
            or problem_landscape,
            "technical_challenges": self._pick_list(parsed, "technical_challenges", "challenges"),
            "core_idea": self._pick_text(
                parsed, "core_idea", "key_idea", "core_method_idea", "method_and_mechanism"
            )
            or method_and_mechanism,
            "method_overview": self._pick_text(
                parsed, "method_overview", "approach_overview", "method_and_mechanism"
            )
            or method_and_mechanism,
            "method_details": self._pick_text(parsed, "method_details", "approach_details", "method_and_mechanism")
            or method_and_mechanism,
            "method_deep_dive": self._pick_text(
                parsed, "method_deep_dive", "method_details", "core_idea", "method_and_mechanism"
            )
            or method_and_mechanism,
            "key_formulae": self._pick_list(parsed, "key_formulae", "formulas", "key_equations"),
            "contribution_claims": self._pick_list(parsed, "contribution_claims", "contributions"),
            "experimental_design": self._pick_text(
                parsed, "experimental_design", "experiment_design", "evidence_and_trustworthiness"
            )
            or evidence_and_trustworthiness,
            "results_and_evidence": self._pick_text(
                parsed, "results_and_evidence", "results_analysis", "evidence_and_trustworthiness"
            )
            or evidence_and_trustworthiness,
            "main_results_expectation": self._pick_text(
                parsed, "main_results_expectation", "main_results", "benchmark_expectation"
            ),
            "ablation_plan": self._pick_text(parsed, "ablation_plan", "ablation_study"),
            "in_depth_analysis_plan": self._pick_text(
                parsed, "in_depth_analysis_plan", "in_depth_analysis", "case_study_plan"
            ),
            "insight_hypotheses": self._pick_text(
                parsed, "insight_hypotheses", "insights", "why_it_works", "confidence_rationale"
            )
            or confidence_rationale,
            "strengths": self._pick_text(parsed, "strengths", "advantages"),
            "weaknesses": self._pick_text(parsed, "weaknesses", "risks"),
            "limitations_and_failure_cases": self._pick_text(
                parsed, "limitations_and_failure_cases", "limitations", "failure_cases"
            ),
            "reproducibility": self._pick_text(
                parsed, "reproducibility", "reproducibility_assessment", "confidence_rationale"
            )
            or confidence_rationale,
            "practical_value": self._pick_text(parsed, "practical_value", "application_value", "impact_and_roadmap")
            or impact_and_roadmap,
            "recommended_followups": self._pick_list(parsed, "recommended_followups", "followups"),
            "reading_questions": self._pick_list(parsed, "reading_questions", "future_reading_questions"),
            "open_problems": self._pick_text(parsed, "open_problems", "open_questions"),
            "so_what_summary": self._pick_text(parsed, "so_what_summary", "impact_summary", "impact_and_roadmap")
            or impact_and_roadmap,
            "analysis_framework_version": "v2_integrated",
            "input_context_source": context_source,
            "input_context_chars": len(context_text),
            "focus": focus_text,
            "question": question_text,
            "workflow_mode": "one_click_default",
            "model": runtime_model,
            "model_display": model,
            "language": analysis_language,
            "analyzed_at": now,
        }
        if not any(
            [
                deep.get("one_line_verdict"),
                deep.get("background_and_field_context"),
                deep.get("motivation_and_why_now"),
                deep.get("problem_definition_and_constraints"),
                deep.get("running_example"),
                deep.get("problem_and_context"),
                deep.get("technical_challenges"),
                deep.get("core_idea"),
                deep.get("method_overview"),
                deep.get("method_details"),
                deep.get("method_deep_dive"),
                deep.get("key_formulae"),
                deep.get("contribution_claims"),
                deep.get("experimental_design"),
                deep.get("results_and_evidence"),
                deep.get("main_results_expectation"),
                deep.get("ablation_plan"),
                deep.get("in_depth_analysis_plan"),
                deep.get("insight_hypotheses"),
                deep.get("strengths"),
                deep.get("weaknesses"),
                deep.get("limitations_and_failure_cases"),
                deep.get("reproducibility"),
                deep.get("practical_value"),
                deep.get("recommended_followups"),
                deep.get("reading_questions"),
                deep.get("open_problems"),
                deep.get("so_what_summary"),
            ]
        ):
            raw_fallback = str(response or "").strip()
            if raw_fallback:
                # Fallback for models that do not return strict JSON.
                deep["executive_summary"] = raw_fallback[:3000]
                deep["one_line_verdict"] = raw_fallback[:1200]
                deep["raw_response"] = raw_fallback[:8000]

        insight_to_save = dict(existing_insight)
        insight_to_save["deep_analysis"] = deep
        history = insight_to_save.get("deep_analysis_history") if isinstance(insight_to_save.get("deep_analysis_history"), list) else []
        history = [deep] + [x for x in history if isinstance(x, dict)]
        insight_to_save["deep_analysis_history"] = history[:5]

        saved = self.paper_repo.save_paper_insight(
            db_path=str(record.get("db_path", "") or ""),
            rowid=int(record.get("rowid", 0) or 0),
            insight=insight_to_save,
        )
        if not saved:
            return {"ok": False, "error": "深入分析结果写回数据库失败"}
        return {
            "ok": True,
            "paper_key": paper_key,
            "deep_analysis": deep,
            "message": "深入分析完成",
        }


class DashboardHandler(BaseHTTPRequestHandler):
    runner: CrawlRunner = None  # type: ignore
    schedule: ScheduleController = None  # type: ignore
    papers: PaperRepository = None  # type: ignore
    progress: AIProgressRepository = None  # type: ignore
    deep_analyzer: DeepAnalysisService = None  # type: ignore
    settings: PanelSettingsStore = None  # type: ignore
    actions: PanelActionStore = None  # type: ignore
    subscriptions: PanelSubscriptionStore = None  # type: ignore
    progress_page_settings: ProgressPageSettingsStore = None  # type: ignore
    progress_subscriptions: ProgressSubscriptionStore = None  # type: ignore
    progress_tasks: ProgressFetchTaskManager = None  # type: ignore
    paper_tasks: PaperFetchTaskManager = None  # type: ignore
    progress_auto_scheduler: ProgressAutoScheduler = None  # type: ignore
    paper_enrich_retry_after: Dict[str, float] = {}
    paper_enrich_retry_lock = threading.RLock()
    output_dir: Path = Path("output")
    home_html: str = build_home_html()
    panel_html: str = build_panel_html_v2()
    progress_html: str = build_progress_html()
    settings_html: str = build_settings_html()
    deep_html: str = build_deep_analysis_html()

    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write(f"[panel] {self.address_string()} - {format % args}\n")

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def _send_bytes(
        self,
        body: bytes,
        content_type: str,
        status: int = 200,
        filename: str = "",
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _extract_paper_request(self, params: Dict[str, List[str]]) -> Dict[str, Any]:
        def pick(name: str, default: str = "") -> str:
            return str((params.get(name) or [default])[0] or default).strip()

        limit = parse_int_value(pick("limit", "100"), 1, 500) or 100
        mode = pick("mode", "all")
        sort_by = pick("sort_by", "") or pick("sort", "score")
        sort_order = pick("sort_order", "desc")
        history = pick("history", "all")
        filters = normalize_panel_filters(
            {
                "q": pick("q"),
                "author": pick("author"),
                "affiliation": pick("affiliation") or pick("aff"),
                "tag": pick("tag"),
                "category": pick("category"),
                "source_id": pick("source_id"),
                "region": pick("region"),
                "event_type": pick("event_type"),
                "date_from": pick("date_from"),
                "date_to": pick("date_to"),
                "has_doi": pick("has_doi", "any"),
                "score_min": pick("score_min"),
                "score_max": pick("score_max"),
            }
        )
        requested_lang = pick("output_language", "")
        output_language = normalize_analysis_language(requested_lang, default="Chinese")
        return {
            "limit": limit,
            "mode": mode,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "history": history,
            "filters": filters,
            "output_language": output_language,
        }

    def _extract_progress_request(self, params: Dict[str, List[str]]) -> Dict[str, Any]:
        def pick(name: str, default: str = "") -> str:
            return str((params.get(name) or [default])[0] or default).strip()

        limit = parse_int_value(pick("limit", "200"), 1, 500) or 200
        sort_by = pick("sort_by", "time")
        sort_order = pick("sort_order", "desc")
        return {
            "limit": limit,
            "q": pick("q"),
            "source_id": pick("source_id"),
            "region": pick("region"),
            "kind": pick("kind"),
            "event_type": pick("event_type"),
            "date_from": pick("date_from"),
            "date_to": pick("date_to"),
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

    def _progress_kind_for_scope(self, scope: str) -> str:
        key = normalize_progress_scope(scope, default="frontier")
        return str(PROGRESS_SCOPE_KIND_MAP.get(key, PROGRESS_SCOPE_KIND_MAP["frontier"]))

    def _resolve_progress_source_ids(self, scope: str, requested_ids: List[str]) -> List[str]:
        kind_text = self._progress_kind_for_scope(scope)
        allowed_kinds = {x.strip().lower() for x in kind_text.split(",") if x.strip()}
        sources = self.progress.list_sources()
        allowed_source_ids = [
            str(row.get("id", "") or "").strip()
            for row in sources
            if str(row.get("id", "") or "").strip()
            and str(row.get("kind", "") or "").strip().lower() in allowed_kinds
        ]
        if not requested_ids:
            return allowed_source_ids
        requested = [str(x).strip() for x in requested_ids if str(x).strip()]
        allowed_set = set(allowed_source_ids)
        return [x for x in requested if x in allowed_set]

    def _scope_progress_settings(self, scope: str) -> Dict[str, Any]:
        return self.progress_page_settings.get_scope(scope)

    def _progress_notify_settings(self, scope: str) -> Dict[str, Any]:
        scope_key = normalize_progress_scope(scope, default="frontier")
        global_settings = self.settings.load()
        scope_settings = self.progress_page_settings.get_scope(scope_key)
        merged = dict(global_settings)
        notify_keys = [
            "feishu_webhook_url",
            "wework_webhook_url",
            "wework_msg_type",
            "dingtalk_webhook_url",
            "telegram_bot_token",
            "telegram_chat_id",
            "ntfy_server_url",
            "ntfy_topic",
            "ntfy_token",
            "bark_url",
            "slack_webhook_url",
            "email_from",
            "email_password",
            "email_to",
            "email_smtp_server",
            "email_smtp_port",
        ]
        for key in notify_keys:
            value = str(scope_settings.get(key, "") or "").strip()
            if value:
                merged[key] = value
        return merged

    def _run_progress_subscription(
        self,
        sub: Dict[str, Any],
        *,
        trigger_mode: str = "manual",
        changed_key_set: Optional[set[str]] = None,
    ) -> Dict[str, Any]:
        sub_id = str(sub.get("id", "") or "").strip()
        scope = normalize_progress_scope(sub.get("scope", "frontier"), default="frontier")
        strategy = normalize_subscription_strategy(
            sub.get("strategy"),
            default=SUBSCRIPTION_STRATEGY_DEFAULT,
        )
        filters = normalize_progress_filters(sub.get("filters") if isinstance(sub, dict) else {})
        limit = parse_int_value(sub.get("limit"), 1, 500) or 120
        kind = self._progress_kind_for_scope(scope)
        list_data = self.progress.list_items(
            limit=limit,
            q=str(filters.get("q", "") or "").strip(),
            source_id=str(filters.get("source_id", "") or "").strip(),
            region=str(filters.get("region", "") or "").strip(),
            kind=kind,
            event_type=str(filters.get("event_type", "") or "").strip(),
            date_from=str(filters.get("date_from", "") or "").strip(),
            date_to=str(filters.get("date_to", "") or "").strip(),
            sort_by="time",
            sort_order="desc",
        )
        items = list_data.get("items") if isinstance(list_data.get("items"), list) else []
        sent_keys = sub.get("sent_keys") if isinstance(sub.get("sent_keys"), list) else []
        sent_set = {str(v).strip() for v in sent_keys if str(v).strip()}

        fresh_items: List[Dict[str, Any]] = []
        fresh_keys: List[str] = []
        for row in items:
            if not isinstance(row, dict):
                continue
            key = str(row.get("progress_key", "") or "").strip()
            if not key or key in sent_set:
                continue
            fresh_items.append(row)
            fresh_keys.append(key)

        selected_items: List[Dict[str, Any]] = []
        selected_keys: List[str] = []
        if strategy == "daily":
            for row in items:
                if not isinstance(row, dict):
                    continue
                selected_items.append(row)
                key = str(row.get("progress_key", "") or "").strip()
                if key:
                    selected_keys.append(key)
        elif strategy == "realtime":
            for row in fresh_items:
                if not isinstance(row, dict):
                    continue
                key = str(row.get("progress_key", "") or "").strip()
                if not key:
                    continue
                if changed_key_set and key not in changed_key_set:
                    continue
                if not is_realtime_priority_progress_item(row, scope):
                    continue
                selected_items.append(row)
                selected_keys.append(key)
        else:
            selected_items = list(fresh_items)
            selected_keys = list(fresh_keys)

        scope_settings = self.progress_page_settings.get_scope(scope)
        output_language = normalize_analysis_language(
            scope_settings.get("output_language", "Chinese"),
            default="Chinese",
        )
        result: Dict[str, Any] = {
            "id": sub_id,
            "scope": scope,
            "name": str(sub.get("name", "") or "").strip(),
            "channel": str(sub.get("channel", "") or "").strip(),
            "strategy": strategy,
            "output_language": output_language,
            "trigger_mode": str(trigger_mode or "manual").strip().lower() or "manual",
            "match_count": len(items),
            "new_count": len(fresh_items),
            "push_count": len(selected_items),
            "ok": True,
            "message": "",
        }
        if not selected_items:
            if strategy == "daily":
                result["message"] = "当日汇总无命中，跳过推送"
            elif strategy == "realtime":
                result["message"] = "无高优先级实时告警，跳过推送"
            else:
                result["message"] = "无新增命中，无需推送"
            return result

        settings = self._progress_notify_settings(scope)
        msg_text = self._build_progress_payload_text(
            selected_items,
            strategy=strategy,
            output_language=output_language,
        )
        msg_text = self._translate_notification_text_with_llm(
            msg_text,
            target_language=output_language,
            settings=settings,
        )
        ok, msg = self._send_subscription_notification(
            str(sub.get("channel", "") or "").strip(),
            settings,
            msg_text,
            subject=f"[OmniHawk AI] {PROGRESS_SCOPE_NAME_MAP_ZH.get(scope, 'AI资讯')} {subscription_strategy_label(strategy)} 通知",
        )
        result["ok"] = ok
        result["message"] = msg
        if ok:
            mark_keys = selected_keys if strategy in {"incremental", "realtime"} else []
            self.progress_subscriptions.mark_notified(sub_id, mark_keys, len(items))
        return result

    def _run_progress_subscriptions(
        self,
        scope: str,
        sub_id: str = "",
        *,
        trigger_mode: str = "manual",
        changed_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        scope_key = normalize_progress_scope(scope, default="frontier")
        items = self.progress_subscriptions.list(scope_key)
        targets: List[Dict[str, Any]]
        if sub_id:
            targets = [row for row in items if str(row.get("id", "") or "") == str(sub_id or "").strip()]
        else:
            targets = [row for row in items if bool(row.get("enabled", True))]
        mode = str(trigger_mode or "manual").strip().lower() or "manual"
        if mode == "realtime":
            targets = [
                row
                for row in targets
                if normalize_subscription_strategy(
                    row.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                )
                == "realtime"
            ]
        elif mode == "scheduled":
            targets = [
                row
                for row in targets
                if normalize_subscription_strategy(
                    row.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                )
                != "realtime"
            ]
        if not targets:
            empty_ok = mode in {"scheduled", "realtime"}
            return {
                "ok": empty_ok,
                "error": "no subscription to run",
                "scope": scope_key,
                "trigger_mode": mode,
                "results": [],
                "success_count": 0,
                "total": 0,
            }
        changed_key_set = {str(v).strip() for v in (changed_keys or []) if str(v).strip()}
        results = [
            self._run_progress_subscription(
                row,
                trigger_mode=mode,
                changed_key_set=changed_key_set if changed_key_set else None,
            )
            for row in targets
        ]
        success = sum(1 for row in results if row.get("ok"))
        return {
            "ok": success == len(results),
            "scope": scope_key,
            "trigger_mode": mode,
            "results": results,
            "success_count": success,
            "total": len(results),
        }

    def _run_progress_fetch_task(
        self,
        *,
        scope: str,
        max_per_source: int,
        fetch_workers: int,
        source_ids: List[str],
        auto_push: bool = False,
        requested_by: str = "manual",
    ) -> Dict[str, Any]:
        scope_key = normalize_progress_scope(scope, default="frontier")
        effective_source_ids = self._resolve_progress_source_ids(scope_key, source_ids)
        result = self.progress.fetch(
            max_per_source=max_per_source,
            source_ids=effective_source_ids,
            worker_count=fetch_workers,
        )
        changed_keys: List[str] = []
        for key in result.get("added_keys", []) + result.get("updated_keys", []):
            text = str(key or "").strip()
            if text and text not in changed_keys:
                changed_keys.append(text)
        scope_settings = self.progress_page_settings.get_scope(scope_key)
        output_language = normalize_analysis_language(
            scope_settings.get("output_language", "Chinese"),
            default="Chinese",
        )
        if changed_keys:
            sync_limit = max(0, int(PROGRESS_FETCH_SYNC_ENRICH_LIMIT or 0))
            sync_keys = changed_keys[:sync_limit] if sync_limit > 0 else []
            if sync_keys:
                result["enrichment"] = self._translate_progress_items(
                    keys=sync_keys,
                    output_language=output_language,
                    force=False,
                    max_workers=4,
                    allow_skip_unconfigured=True,
                )
            else:
                result["enrichment"] = {
                    "ok": True,
                    "requested": 0,
                    "translated": 0,
                    "changed": 0,
                    "translated_keys": [],
                    "failed": [],
                    "skipped": True,
                    "reason": "sync enrichment disabled for faster fetch",
                    "output_language": output_language,
                }
            if len(changed_keys) > len(sync_keys):
                result["enrichment_deferred"] = {
                    "deferred_count": len(changed_keys) - len(sync_keys),
                    "sync_limit": sync_limit,
                    "message": "remaining items will be lazily enriched by page-side on-demand translation",
                }
            result["realtime_push"] = self._run_progress_subscriptions(
                scope_key,
                trigger_mode="realtime",
                changed_keys=changed_keys,
            )
        if auto_push:
            result["auto_push"] = self._run_progress_subscriptions(scope_key, trigger_mode="scheduled")
        result["scope"] = scope_key
        result["kind"] = self._progress_kind_for_scope(scope_key)
        result["fetch_workers"] = max(1, min(int(fetch_workers or 1), 16))
        requested = str(requested_by or "manual").strip() or "manual"
        result["requested_by"] = requested
        ok = bool(result.get("ok", True))
        msg = "抓取完成" if ok else str(result.get("error", "抓取失败") or "抓取失败")
        if requested == "auto":
            self.progress_page_settings.mark_auto_result(scope_key, ok=ok, message=msg)
        return result

    def _pick_progress_localized_text(self, item: Dict[str, Any], field: str, output_language: str) -> str:
        lang = normalize_analysis_language(output_language, default="Chinese")
        lang_key = language_cache_key(lang)
        i18n_map = item.get("i18n") if isinstance(item.get("i18n"), dict) else {}
        i18n_entry = i18n_map.get(lang_key) if isinstance(i18n_map.get(lang_key), dict) else {}
        mapped = str(i18n_entry.get(field, "") or "").strip() if isinstance(i18n_entry, dict) else ""
        if mapped:
            return mapped
        if field == "title":
            if is_chinese_language(lang):
                return str(item.get("title_zh", "") or item.get("title", "") or "").strip()
            return str(item.get("title", "") or item.get("title_zh", "") or "").strip()
        if field == "summary":
            if is_chinese_language(lang):
                return str(item.get("summary_zh", "") or item.get("summary", "") or "").strip()
            return str(item.get("summary", "") or item.get("summary_zh", "") or "").strip()
        if field == "llm_takeaway":
            if is_chinese_language(lang):
                return str(item.get("llm_takeaway_zh", "") or item.get("llm_takeaway", "") or "").strip()
            return str(item.get("llm_takeaway", "") or item.get("llm_takeaway_zh", "") or "").strip()
        return ""

    def _build_progress_payload_text(
        self,
        items: List[Dict[str, Any]],
        strategy: str = SUBSCRIPTION_STRATEGY_DEFAULT,
        output_language: str = "Chinese",
    ) -> str:
        def clip_text(text: Any, limit: int) -> str:
            value = re.sub(r"\s+", " ", str(text or "").strip())
            if len(value) <= limit:
                return value
            return value[: max(0, limit - 3)].rstrip() + "..."

        event_map = {
            "release": "版本发布",
            "report": "技术报告",
            "benchmark": "评测基准",
            "safety": "安全治理",
            "update": "一般更新",
        }

        lines: List[str] = []
        total = len(items)
        strategy_key = normalize_subscription_strategy(strategy, default=SUBSCRIPTION_STRATEGY_DEFAULT)
        lines.append(f"AI 技术进展 · {subscription_strategy_label(strategy_key)} · 命中 {total} 条")
        lines.append("")

        max_items = 8
        shown = items[:max_items]
        for idx, item in enumerate(shown, start=1):
            title = clip_text(self._pick_progress_localized_text(item, "title", output_language), 180)
            org = str(item.get("org", "") or "").strip()
            source_name = str(item.get("source_name", "") or "").strip()
            published = str(item.get("published_at", "") or "").strip()
            published_short = published[:19] if published else ""
            event_type_raw = str(item.get("event_type", "") or "").strip().lower()
            event_type = event_map.get(event_type_raw, event_type_raw)
            summary = clip_text(self._pick_progress_localized_text(item, "summary", output_language), 260)
            takeaway = clip_text(self._pick_progress_localized_text(item, "llm_takeaway", output_language), 90)
            url = str(item.get("url", "") or "").strip()
            tags = item.get("tags") if isinstance(item.get("tags"), list) else []
            tags = [str(x).strip() for x in tags if str(x).strip()]

            lines.append(f"{idx}. {title}")
            meta_parts = []
            if org:
                meta_parts.append(f"机构: {org}")
            if source_name:
                meta_parts.append(f"来源: {source_name}")
            if event_type:
                meta_parts.append(f"类型: {event_type}")
            if published_short:
                meta_parts.append(f"发布时间: {published_short}")
            if meta_parts:
                lines.append("   " + " | ".join(meta_parts))
            if takeaway:
                lines.append(f"   要点: {takeaway}")
            if summary:
                lines.append(f"   摘要: {summary}")
            if tags:
                lines.append(f"   标签: {', '.join(tags[:6])}")
            if url:
                lines.append(f"   原文: {url}")
            lines.append("")

        if total > max_items:
            lines.append(f"其余 {total - max_items} 条请在 AI 技术进展面板查看。")
        lines.append(f"推送时间: {utc_now_iso()}")
        return "\n".join(lines).strip() + "\n"

    def _extract_json_object_text(self, text: str) -> str:
        value = str(text or "").strip()
        if not value:
            return ""
        if value.startswith("{") and value.endswith("}"):
            return value
        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", value, re.IGNORECASE)
        if fenced:
            return fenced.group(1).strip()
        idx1 = value.find("{")
        idx2 = value.rfind("}")
        if idx1 >= 0 and idx2 > idx1:
            return value[idx1 : idx2 + 1].strip()
        return ""

    def _normalize_keyword_values(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            parts = re.split(r"[,\n;/|]", value)
            return [str(v).strip() for v in parts if str(v).strip()]
        return []

    def _paper_i18n_map(self, insight: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        if self.papers and hasattr(self.papers, "_paper_i18n_map"):
            try:
                mapped = self.papers._paper_i18n_map(insight)  # type: ignore[attr-defined]
            except Exception:
                mapped = {}
            if isinstance(mapped, dict):
                return mapped
        return {}

    def _paper_deep_i18n_entry(self, insight: Dict[str, Any], output_language: str) -> Dict[str, Any]:
        if self.papers and hasattr(self.papers, "_paper_deep_i18n_entry"):
            try:
                entry = self.papers._paper_deep_i18n_entry(insight, output_language)  # type: ignore[attr-defined]
            except Exception:
                entry = {}
            if isinstance(entry, dict):
                return entry
        return {}

    def _build_paper_llm_client_config(self, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ai_model = str(settings.get("ai_model", "") or "").strip()
        ai_api_base = str(settings.get("ai_api_base", "") or "").strip()
        ai_api_key = str(settings.get("ai_api_key", "") or "").strip()
        runtime_model = to_runtime_model_name(ai_model, ai_api_base)
        if not (runtime_model and ai_api_key):
            return None
        return {
            "MODEL": runtime_model,
            "API_KEY": ai_api_key,
            "API_BASE": ai_api_base,
            "TEMPERATURE": 0.1,
            "MAX_TOKENS": 1200,
            "TIMEOUT": 30,
            "NUM_RETRIES": 0,
        }

    def _paper_item_needs_language(
        self,
        insight: Dict[str, Any],
        record: Optional[Dict[str, Any]],
        target_language: str,
        include_deep: bool = False,
        force: bool = False,
    ) -> bool:
        if force:
            return True
        lang = normalize_analysis_language(target_language, default="Chinese")
        lang_key = language_cache_key(lang)
        raw_title = str((record or {}).get("title", "") or "").strip()
        raw_one_line = str(insight.get("one_sentence_summary") or insight.get("summary") or "").strip()
        raw_method = str(insight.get("method", "") or "").strip()
        raw_conclusion = str(insight.get("conclusion") or insight.get("findings") or "").strip()
        raw_innovation = str(insight.get("innovation") or insight.get("novelty") or "").strip()
        raw_keywords = self._normalize_keyword_values(insight.get("keywords"))

        localized_title = ""
        localized_one_line = ""
        localized_method = ""
        localized_conclusion = ""
        localized_innovation = ""
        localized_keywords: List[str] = []
        if is_english_language(lang):
            localized_title = str(insight.get("title_en", "") or "").strip()
            localized_one_line = str(insight.get("one_sentence_summary_en", "") or "").strip()
            localized_method = str(insight.get("method_en", "") or "").strip()
            localized_conclusion = str(insight.get("conclusion_en", "") or "").strip()
            localized_innovation = str(insight.get("innovation_en", "") or "").strip()
            localized_keywords = self._normalize_keyword_values(insight.get("keywords_en"))
        elif is_chinese_language(lang):
            localized_title = str(insight.get("title_zh", "") or "").strip()
            localized_one_line = str(insight.get("one_sentence_summary_zh", "") or "").strip()
            localized_method = str(insight.get("method_zh", "") or "").strip()
            localized_conclusion = str(insight.get("conclusion_zh", "") or "").strip()
            localized_innovation = str(insight.get("innovation_zh", "") or "").strip()
            localized_keywords = self._normalize_keyword_values(insight.get("keywords_zh"))
        else:
            mapped = self._paper_i18n_map(insight).get(lang_key, {})
            localized_title = str(mapped.get("title", "") or "").strip()
            localized_one_line = str(mapped.get("one_sentence_summary", "") or "").strip()
            localized_method = str(mapped.get("method", "") or "").strip()
            localized_conclusion = str(mapped.get("conclusion", "") or "").strip()
            localized_innovation = str(mapped.get("innovation", "") or "").strip()
            localized_keywords = self._normalize_keyword_values(mapped.get("keywords"))

        if is_english_language(lang):
            title_ready = bool(localized_title) or bool(raw_title and not looks_like_chinese_text(raw_title))
            one_line_ready = bool(localized_one_line) or bool(raw_one_line and not looks_like_chinese_text(raw_one_line))
            method_ready = bool(localized_method) or bool(raw_method and not looks_like_chinese_text(raw_method))
            conclusion_ready = bool(localized_conclusion) or bool(
                raw_conclusion and not looks_like_chinese_text(raw_conclusion)
            )
            innovation_ready = bool(localized_innovation) or bool(
                raw_innovation and not looks_like_chinese_text(raw_innovation)
            )
            keywords_ready = bool(localized_keywords) or bool(
                raw_keywords and not any(looks_like_chinese_text(val) for val in raw_keywords)
            )
        elif is_chinese_language(lang):
            title_ready = bool(localized_title) or bool(raw_title and looks_like_chinese_text(raw_title))
            one_line_ready = bool(localized_one_line) or bool(raw_one_line and looks_like_chinese_text(raw_one_line))
            method_ready = bool(localized_method) or bool(raw_method and looks_like_chinese_text(raw_method))
            conclusion_ready = bool(localized_conclusion) or bool(
                raw_conclusion and looks_like_chinese_text(raw_conclusion)
            )
            innovation_ready = bool(localized_innovation) or bool(
                raw_innovation and looks_like_chinese_text(raw_innovation)
            )
            keywords_ready = bool(localized_keywords) or bool(
                raw_keywords and any(looks_like_chinese_text(val) for val in raw_keywords)
            )
        else:
            title_ready = bool(localized_title)
            one_line_ready = bool(localized_one_line)
            method_ready = bool(localized_method)
            conclusion_ready = bool(localized_conclusion)
            innovation_ready = bool(localized_innovation)
            keywords_ready = bool(localized_keywords)

        has_text_fields = bool(title_ready and one_line_ready and method_ready and conclusion_ready and innovation_ready)
        has_keywords = bool(keywords_ready)
        if not include_deep:
            return not (has_text_fields and has_keywords)
        deep_ready = False
        if is_english_language(lang):
            deep_ready = isinstance(insight.get("deep_analysis_en"), dict) and bool(insight.get("deep_analysis_en"))
        elif is_chinese_language(lang):
            deep_ready = isinstance(insight.get("deep_analysis_zh"), dict) and bool(insight.get("deep_analysis_zh"))
        else:
            deep_ready = bool(self._paper_deep_i18n_entry(insight, lang))
        return not (has_text_fields and has_keywords and deep_ready)

    def _pick_paper_deep_source(
        self,
        insight: Dict[str, Any],
        target_language: str,
    ) -> Tuple[Dict[str, Any], bool]:
        lang = normalize_analysis_language(target_language, default="Chinese")
        lang_key = language_cache_key(lang)
        existing_i18n = self._paper_deep_i18n_entry(insight, lang)
        if existing_i18n:
            return {}, False

        if is_english_language(lang):
            existing_target = insight.get("deep_analysis_en") if isinstance(insight.get("deep_analysis_en"), dict) else {}
            if existing_target:
                return {}, False
        elif is_chinese_language(lang):
            existing_target = insight.get("deep_analysis_zh") if isinstance(insight.get("deep_analysis_zh"), dict) else {}
            if existing_target:
                return {}, False

        deep_default = insight.get("deep_analysis") if isinstance(insight.get("deep_analysis"), dict) else {}
        if deep_default:
            deep_lang = normalize_analysis_language(deep_default.get("language", ""), default="")
            if language_cache_key(deep_lang) == lang_key:
                copied = dict(deep_default)
                copied["language"] = lang
                return copied, False
            return deep_default, True

        if is_english_language(lang):
            opposite_deep = insight.get("deep_analysis_zh") if isinstance(insight.get("deep_analysis_zh"), dict) else {}
            if opposite_deep:
                return opposite_deep, True
        elif is_chinese_language(lang):
            opposite_deep = insight.get("deep_analysis_en") if isinstance(insight.get("deep_analysis_en"), dict) else {}
            if opposite_deep:
                return opposite_deep, True
        else:
            raw = insight.get("deep_analysis_i18n") if isinstance(insight.get("deep_analysis_i18n"), dict) else {}
            for key, value in raw.items():
                if not isinstance(value, dict):
                    continue
                if language_cache_key(key) == lang_key:
                    continue
                return value, True
        return {}, False

    def _enrich_paper_shallow_with_llm(
        self,
        record: Dict[str, Any],
        target_language: str,
        client_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        lang = normalize_analysis_language(target_language, default="Chinese")
        suffix = "en" if is_english_language(lang) else ("zh" if is_chinese_language(lang) else "")
        lang_key = language_cache_key(lang)
        insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
        meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
        raw_title = str(record.get("title", "") or "").strip()
        abstract = clean_arxiv_abstract(
            str(meta.get("abstract", "") or "").strip() or str(record.get("summary", "") or "").strip()
        )
        if not raw_title and not abstract:
            raise ValueError("empty paper context")

        one_sentence = str(insight.get("one_sentence_summary") or insight.get("summary") or "").strip()
        method = str(insight.get("method", "") or "").strip()
        conclusion = str(insight.get("conclusion") or insight.get("findings") or "").strip()
        innovation = str(insight.get("innovation") or insight.get("novelty") or "").strip()
        keywords = self._normalize_keyword_values(insight.get("keywords"))
        keywords_text = ", ".join(keywords[:12])

        target_label = lang
        tone_hint = f"All generated fields must be concise and natural in {target_label}."
        prompt = (
            f"Generate localized card fields in {target_label} from the paper context.\n"
            "Rules:\n"
            "1) Return JSON only. No markdown.\n"
            "2) Fields must be: title, one_sentence_summary, keywords, method, conclusion, innovation.\n"
            "3) keywords must be an array with 4-8 items.\n"
            "4) Keep model names / products / versions / paper terms unchanged.\n"
            "5) Keep one_sentence_summary compact and card-friendly.\n"
            f"6) {tone_hint}\n\n"
            f"title: {raw_title}\n"
            f"abstract: {abstract}\n"
            f"existing_one_sentence_summary: {one_sentence}\n"
            f"existing_keywords: {keywords_text}\n"
            f"existing_method: {method}\n"
            f"existing_conclusion: {conclusion}\n"
            f"existing_innovation: {innovation}\n\n"
            'Output JSON: {"title":"...","one_sentence_summary":"...","keywords":["..."],"method":"...","conclusion":"...","innovation":"..."}'
        )
        system_prompt = "You are an expert AI research editor. Return strict JSON only."
        client = AIClient(client_config)
        response = client.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )
        payload = self._extract_json_object_text(response)
        if not payload:
            raise ValueError("empty shallow enrichment payload")
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise ValueError("shallow enrichment payload is not object")

        title_val = str(parsed.get("title", "") or "").strip()
        if not title_val:
            if is_english_language(lang) and raw_title and not looks_like_chinese_text(raw_title):
                title_val = raw_title
            elif is_chinese_language(lang) and raw_title and looks_like_chinese_text(raw_title):
                title_val = raw_title
            elif raw_title:
                title_val = raw_title
        one_line_val = str(parsed.get("one_sentence_summary", "") or "").strip()
        method_val = str(parsed.get("method", "") or "").strip()
        conclusion_val = str(parsed.get("conclusion", "") or "").strip()
        innovation_val = str(parsed.get("innovation", "") or "").strip()
        keywords_val = self._normalize_keyword_values(parsed.get("keywords"))
        if not keywords_val:
            keywords_val = self._normalize_keyword_values(parsed.get("keyword"))
        if not keywords_val:
            keywords_val = self._normalize_keyword_values(parsed.get("tags"))

        if not any([title_val, one_line_val, method_val, conclusion_val, innovation_val, keywords_val]):
            raise ValueError("empty shallow enrichment fields")

        updates: Dict[str, Any] = {}
        if suffix:
            if title_val:
                updates[f"title_{suffix}"] = title_val
            if one_line_val:
                updates[f"one_sentence_summary_{suffix}"] = one_line_val
            if method_val:
                updates[f"method_{suffix}"] = method_val
            if conclusion_val:
                updates[f"conclusion_{suffix}"] = conclusion_val
            if innovation_val:
                updates[f"innovation_{suffix}"] = innovation_val
            if keywords_val:
                updates[f"keywords_{suffix}"] = keywords_val
            return updates

        i18n_payload: Dict[str, Any] = {}
        if title_val:
            i18n_payload["title"] = title_val
        if one_line_val:
            i18n_payload["one_sentence_summary"] = one_line_val
        if method_val:
            i18n_payload["method"] = method_val
        if conclusion_val:
            i18n_payload["conclusion"] = conclusion_val
        if innovation_val:
            i18n_payload["innovation"] = innovation_val
        if keywords_val:
            i18n_payload["keywords"] = keywords_val
        if i18n_payload:
            updates["i18n"] = {lang_key: i18n_payload}
        return updates

    def _batch_translate_paper_shallow_with_llm(
        self,
        pending: List[Tuple[str, Dict[str, Any]]],
        target_language: str,
        client_config: Dict[str, Any],
    ) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, str]]]:
        lang = normalize_analysis_language(target_language, default="Chinese")
        lang_key = language_cache_key(lang)
        if not pending:
            return {}, []

        max_batch = 6
        translated: Dict[str, Dict[str, Any]] = {}
        failed: List[Dict[str, str]] = []
        client = AIClient(client_config)

        for offset in range(0, len(pending), max_batch):
            chunk = pending[offset : offset + max_batch]
            payload_items: List[Dict[str, Any]] = []
            for key, record in chunk:
                insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
                payload_items.append(
                    {
                        "paper_key": key,
                        "title": str(record.get("title", "") or "").strip(),
                        "one_sentence_summary": str(
                            insight.get("one_sentence_summary") or insight.get("summary") or ""
                        ).strip(),
                        "method": str(insight.get("method", "") or "").strip(),
                        "conclusion": str(insight.get("conclusion") or insight.get("findings") or "").strip(),
                        "innovation": str(insight.get("innovation") or insight.get("novelty") or "").strip(),
                        "keywords": self._normalize_keyword_values(insight.get("keywords")),
                    }
                )

            prompt = (
                f"Translate each paper card field into {lang}.\n"
                "Return strict JSON only with shape:\n"
                '{"items":[{"paper_key":"...","title":"...","one_sentence_summary":"...","method":"...","conclusion":"...","innovation":"...","keywords":["..."]}]}\n\n'
                "Rules:\n"
                "1) Keep paper_key unchanged.\n"
                "2) Keep model names / product names / versions / formulas unchanged.\n"
                "3) keywords must be an array.\n"
                "4) If a source field is empty, return empty string (or [] for keywords).\n\n"
                f"Input JSON:\n{json.dumps(payload_items, ensure_ascii=False)}"
            )
            try:
                response = client.chat(
                    [
                        {"role": "system", "content": "You are a strict multilingual paper field translator. JSON only."},
                        {"role": "user", "content": prompt},
                    ]
                )
                payload_text = self._extract_json_object_text(str(response or ""))
                if not payload_text:
                    raise ValueError("empty batch payload")
                parsed = json.loads(payload_text)
                if not isinstance(parsed, dict):
                    raise ValueError("batch payload is not object")
                items = parsed.get("items") if isinstance(parsed.get("items"), list) else []
                mapped: Dict[str, Dict[str, Any]] = {}
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    paper_key = str(item.get("paper_key", "") or "").strip()
                    if not paper_key:
                        continue
                    mapped[paper_key] = {
                        "title": str(item.get("title", "") or "").strip(),
                        "one_sentence_summary": str(item.get("one_sentence_summary", "") or "").strip(),
                        "method": str(item.get("method", "") or "").strip(),
                        "conclusion": str(item.get("conclusion", "") or "").strip(),
                        "innovation": str(item.get("innovation", "") or "").strip(),
                        "keywords": self._normalize_keyword_values(item.get("keywords")),
                    }

                for key, _record in chunk:
                    localized = mapped.get(key, {})
                    title_val = str(localized.get("title", "") or "").strip()
                    one_line_val = str(localized.get("one_sentence_summary", "") or "").strip()
                    method_val = str(localized.get("method", "") or "").strip()
                    conclusion_val = str(localized.get("conclusion", "") or "").strip()
                    innovation_val = str(localized.get("innovation", "") or "").strip()
                    keywords_val = self._normalize_keyword_values(localized.get("keywords"))
                    if not any([title_val, one_line_val, method_val, conclusion_val, innovation_val, keywords_val]):
                        failed.append({"key": key, "error": "empty batch translation fields"})
                        continue

                    if is_english_language(lang):
                        patch: Dict[str, Any] = {
                            "title_en": title_val,
                            "one_sentence_summary_en": one_line_val,
                            "method_en": method_val,
                            "conclusion_en": conclusion_val,
                            "innovation_en": innovation_val,
                            "keywords_en": keywords_val,
                        }
                    elif is_chinese_language(lang):
                        patch = {
                            "title_zh": title_val,
                            "one_sentence_summary_zh": one_line_val,
                            "method_zh": method_val,
                            "conclusion_zh": conclusion_val,
                            "innovation_zh": innovation_val,
                            "keywords_zh": keywords_val,
                        }
                    else:
                        patch = {
                            "i18n": {
                                lang_key: {
                                    "title": title_val,
                                    "one_sentence_summary": one_line_val,
                                    "method": method_val,
                                    "conclusion": conclusion_val,
                                    "innovation": innovation_val,
                                    "keywords": keywords_val,
                                }
                            }
                        }
                    translated[key] = patch
            except Exception as exc:
                for key, _record in chunk:
                    failed.append({"key": key, "error": f"batch translate failed: {type(exc).__name__}: {exc}"})

        return translated, failed

    def _translate_deep_analysis_with_llm(
        self,
        source_deep: Dict[str, Any],
        target_language: str,
        client_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not source_deep:
            return {}
        lang = normalize_analysis_language(target_language, default="Chinese")
        target_label = lang
        source_text = json.dumps(source_deep, ensure_ascii=False)
        prompt = (
            f"Translate the JSON object values into {target_label}.\n"
            "Rules:\n"
            "1) Keep JSON keys unchanged.\n"
            "2) Preserve equations/LaTeX/URLs/model names exactly.\n"
            "3) For list values, translate each text item.\n"
            "4) Return JSON object only, no extra text.\n\n"
            f"Input JSON:\n{source_text}"
        )
        client = AIClient(client_config)
        response = client.chat(
            [
                {"role": "system", "content": "You are a strict JSON translator."},
                {"role": "user", "content": prompt},
            ]
        )
        payload = self._extract_json_object_text(response)
        if not payload:
            raise ValueError("empty deep translation payload")
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise ValueError("deep translation payload is not object")
        parsed["language"] = lang
        if not str(parsed.get("analyzed_at", "") or "").strip():
            parsed["analyzed_at"] = str(source_deep.get("analyzed_at", "") or utc_now_iso())
        return parsed

    def _translate_single_paper_record(
        self,
        record: Dict[str, Any],
        target_language: str,
        client_config: Dict[str, Any],
        include_deep: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
        updates: Dict[str, Any] = {}
        needs_shallow = self._paper_item_needs_language(
            insight=insight,
            record=record,
            target_language=target_language,
            include_deep=False,
            force=force,
        )
        if needs_shallow:
            updates.update(self._enrich_paper_shallow_with_llm(record, target_language, client_config))

        if include_deep:
            lang = normalize_analysis_language(target_language, default="Chinese")
            lang_key = language_cache_key(lang)
            if is_english_language(lang):
                target_key = "deep_analysis_en"
                existing_target_deep = (
                    insight.get(target_key) if isinstance(insight.get(target_key), dict) else {}
                )
            elif is_chinese_language(lang):
                target_key = "deep_analysis_zh"
                existing_target_deep = (
                    insight.get(target_key) if isinstance(insight.get(target_key), dict) else {}
                )
            else:
                target_key = ""
                existing_target_deep = self._paper_deep_i18n_entry(insight, lang)
            if force or not existing_target_deep:
                source_deep, needs_translate = self._pick_paper_deep_source(insight, target_language)
                if source_deep:
                    translated_deep = (
                        self._translate_deep_analysis_with_llm(source_deep, target_language, client_config)
                        if needs_translate
                        else dict(source_deep)
                    )
                    if translated_deep:
                        translated_deep["language"] = lang
                        if target_key:
                            updates[target_key] = translated_deep
                        else:
                            updates["deep_analysis_i18n"] = {lang_key: translated_deep}
        return updates

    def _translate_paper_items(
        self,
        keys: List[str],
        output_language: str = "Chinese",
        force: bool = False,
        include_deep: bool = False,
        max_workers: int = 2,
        allow_skip_unconfigured: bool = False,
    ) -> Dict[str, Any]:
        cleaned_keys = [str(x).strip() for x in keys if str(x).strip()]
        if not cleaned_keys:
            return {"ok": False, "error": "keys is required"}
        unique_keys: List[str] = []
        seen = set()
        for key in cleaned_keys:
            if key in seen:
                continue
            seen.add(key)
            unique_keys.append(key)
        unique_keys = unique_keys[:200]

        target_language = normalize_analysis_language(output_language, default="Chinese")
        enrich_scope = "deep" if include_deep else "shallow"

        def retry_key_of(paper_key: str) -> str:
            return f"{target_language}:{enrich_scope}:{paper_key}"

        settings = self.settings.load()
        client_config = self._build_paper_llm_client_config(settings)
        if not client_config:
            if allow_skip_unconfigured:
                return {
                    "ok": True,
                    "requested": len(unique_keys),
                    "translated": 0,
                    "changed": 0,
                    "translated_keys": [],
                    "failed": [],
                    "skipped": True,
                    "reason": "LLM 未配置，跳过论文多语言富化",
                }
            return {"ok": False, "error": "LLM 未配置，无法执行论文多语言富化"}

        records = self.papers.get_paper_records_by_keys(unique_keys)
        pending: List[Tuple[str, Dict[str, Any]]] = []
        failed: List[Dict[str, str]] = []
        skipped = 0
        for key in unique_keys:
            record = records.get(key)
            if not isinstance(record, dict):
                failed.append({"key": key, "error": "paper not found"})
                continue
            insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
            if not self._paper_item_needs_language(
                insight,
                record=record,
                target_language=target_language,
                include_deep=include_deep,
                force=force,
            ):
                with self.paper_enrich_retry_lock:
                    self.paper_enrich_retry_after.pop(retry_key_of(key), None)
                skipped += 1
                continue
            if not force:
                with self.paper_enrich_retry_lock:
                    retry_after = float(self.paper_enrich_retry_after.get(retry_key_of(key), 0.0) or 0.0)
                if retry_after > time.time():
                    skipped += 1
                    continue
            pending.append((key, record))

        translated_patches: Dict[str, Dict[str, Any]] = {}
        worker_count = max(1, min(int(max_workers or 2), 2))
        if pending:
            if (not include_deep) and (not is_english_language(target_language)) and (not is_chinese_language(target_language)):
                batch_patches, batch_failed = self._batch_translate_paper_shallow_with_llm(
                    pending=pending,
                    target_language=target_language,
                    client_config=client_config,
                )
                translated_patches.update(batch_patches)
                failed.extend(batch_failed)
                failed_key_set = {str(x.get("key", "") or "").strip() for x in batch_failed if isinstance(x, dict)}
                for key, _record in pending:
                    if key in translated_patches or key in failed_key_set:
                        continue
                    skipped += 1
            else:
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    future_map = {
                        executor.submit(
                            self._translate_single_paper_record,
                            record,
                            target_language,
                            client_config,
                            include_deep,
                            force,
                        ): key
                        for key, record in pending
                    }
                    for future in as_completed(future_map):
                        key = future_map[future]
                        try:
                            patch = future.result()
                            if patch:
                                translated_patches[key] = patch
                            else:
                                skipped += 1
                        except json.JSONDecodeError:
                            error_msg = "invalid paper enrichment json"
                            failed.append({"key": key, "error": error_msg})
                            with self.paper_enrich_retry_lock:
                                self.paper_enrich_retry_after[retry_key_of(key)] = time.time() + 300
                        except Exception as exc:
                            error_msg = f"LLM 调用失败: {type(exc).__name__}: {exc}"
                            failed.append({"key": key, "error": error_msg})
                            cooldown = 900 if "timeout" in error_msg.lower() else 300
                            with self.paper_enrich_retry_lock:
                                self.paper_enrich_retry_after[retry_key_of(key)] = time.time() + cooldown

        changed = 0
        translated_keys: List[str] = []
        for key, patch in translated_patches.items():
            record = records.get(key)
            if not isinstance(record, dict):
                failed.append({"key": key, "error": "paper missing when save"})
                continue
            db_path = str(record.get("db_path", "") or "").strip()
            rowid = int(record.get("rowid", 0) or 0)
            old_insight = record.get("insight") if isinstance(record.get("insight"), dict) else {}
            new_insight = dict(old_insight)
            for patch_key, patch_value in patch.items():
                if patch_key in {"i18n", "deep_analysis_i18n"} and isinstance(patch_value, dict):
                    existed = new_insight.get(patch_key) if isinstance(new_insight.get(patch_key), dict) else {}
                    merged = dict(existed)
                    for lang_key, localized_value in patch_value.items():
                        safe_lang = language_cache_key(lang_key)
                        if not safe_lang:
                            continue
                        if isinstance(localized_value, dict):
                            current_localized = (
                                merged.get(safe_lang) if isinstance(merged.get(safe_lang), dict) else {}
                            )
                            combined_localized = dict(current_localized)
                            combined_localized.update(localized_value)
                            merged[safe_lang] = combined_localized
                    new_insight[patch_key] = merged
                    continue
                new_insight[patch_key] = patch_value
            if new_insight == old_insight:
                skipped += 1
                with self.paper_enrich_retry_lock:
                    self.paper_enrich_retry_after.pop(retry_key_of(key), None)
                continue
            if not self.papers.save_paper_insight(db_path=db_path, rowid=rowid, insight=new_insight):
                failed.append({"key": key, "error": "save paper insight failed"})
                with self.paper_enrich_retry_lock:
                    self.paper_enrich_retry_after[retry_key_of(key)] = time.time() + 120
                continue
            changed += 1
            translated_keys.append(key)
            with self.paper_enrich_retry_lock:
                self.paper_enrich_retry_after.pop(retry_key_of(key), None)

        return {
            "ok": True,
            "requested": len(unique_keys),
            "translated": len(translated_patches),
            "changed": changed,
            "translated_keys": translated_keys,
            "failed": failed,
            "skipped": skipped,
            "worker_count": worker_count,
            "output_language": target_language,
            "include_deep": bool(include_deep),
        }

    def _build_progress_llm_client_config(self, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ai_model = str(settings.get("ai_model", "") or "").strip()
        ai_api_base = str(settings.get("ai_api_base", "") or "").strip()
        ai_api_key = str(settings.get("ai_api_key", "") or "").strip()
        runtime_model = to_runtime_model_name(ai_model, ai_api_base)
        if not (runtime_model and ai_api_key):
            return None
        return {
            "MODEL": runtime_model,
            "API_KEY": ai_api_key,
            "API_BASE": ai_api_base,
            "TEMPERATURE": 0.1,
            "MAX_TOKENS": 1400,
            "TIMEOUT": 35,
        }

    def _progress_i18n_entry(self, row: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        raw = row.get("i18n") if isinstance(row.get("i18n"), dict) else {}
        lang_key = language_cache_key(target_language)
        entry = raw.get(lang_key) if isinstance(raw.get(lang_key), dict) else {}
        return dict(entry) if isinstance(entry, dict) else {}

    def _progress_item_needs_enrichment(
        self,
        row: Dict[str, Any],
        target_language: str,
        force: bool = False,
    ) -> bool:
        if force:
            return True
        lang = normalize_analysis_language(target_language, default="Chinese")
        if is_chinese_language(lang):
            return not (
                str(row.get("title_zh", "") or "").strip()
                and str(row.get("summary_zh", "") or "").strip()
                and str(row.get("llm_takeaway_zh", "") or "").strip()
            )
        mapped = self._progress_i18n_entry(row, lang)
        if mapped:
            return not (
                str(mapped.get("title", "") or "").strip()
                and str(mapped.get("summary", "") or "").strip()
                and str(mapped.get("llm_takeaway", "") or "").strip()
            )
        if is_english_language(lang):
            return not (
                str(row.get("title", "") or "").strip()
                and str(row.get("summary", "") or "").strip()
                and str(row.get("llm_takeaway", "") or "").strip()
            )
        return True

    def _enrich_progress_items_batch_with_llm(
        self,
        pending_rows: List[Tuple[str, Dict[str, Any]]],
        target_language: str,
        client_config: Dict[str, Any],
    ) -> Tuple[Dict[str, Dict[str, str]], List[Dict[str, str]]]:
        lang = normalize_analysis_language(target_language, default="Chinese")
        lang_key = language_cache_key(lang)
        if not pending_rows:
            return {}, []

        max_batch = 8
        translated: Dict[str, Dict[str, str]] = {}
        failed: List[Dict[str, str]] = []
        client = AIClient(client_config)

        for offset in range(0, len(pending_rows), max_batch):
            chunk = pending_rows[offset : offset + max_batch]
            payload_items: List[Dict[str, Any]] = []
            for key, row in chunk:
                payload_items.append(
                    {
                        "id": key,
                        "source_name": str(row.get("source_name", "") or "").strip(),
                        "org": str(row.get("org", "") or "").strip(),
                        "event_type": str(row.get("event_type", "") or "").strip(),
                        "published_at": str(row.get("published_at", "") or "").strip(),
                        "title": str(row.get("title", "") or "").strip(),
                        "summary": str(row.get("summary", "") or "").strip(),
                        "llm_takeaway": str(row.get("llm_takeaway", "") or "").strip(),
                    }
                )

            prompt = (
                f"Translate and normalize each item into {lang}.\n"
                "Return strict JSON only with this shape:\n"
                '{"items":[{"id":"...","title":"...","summary":"...","llm_takeaway":"..."}]}\n\n'
                "Rules:\n"
                "1) Keep IDs exactly the same.\n"
                "2) Preserve model names / product names / versions / URLs.\n"
                "3) summary should be concise and readable.\n"
                "4) llm_takeaway should be one short sentence highlighting the key point.\n"
                "5) If a field is empty in input, return empty string for that field.\n\n"
                f"Input items JSON:\n{json.dumps(payload_items, ensure_ascii=False)}"
            )
            try:
                response = client.chat(
                    [
                        {"role": "system", "content": "You are a strict multilingual technical editor. Return JSON only."},
                        {"role": "user", "content": prompt},
                    ]
                )
                text = str(response or "").strip()
                payload_text = self._extract_json_object_text(text)
                if not payload_text:
                    raise ValueError("empty enrichment payload")
                parsed = json.loads(payload_text)
                if not isinstance(parsed, dict):
                    raise ValueError("enrichment payload is not object")
                parsed_items = parsed.get("items") if isinstance(parsed.get("items"), list) else []
                mapped: Dict[str, Dict[str, str]] = {}
                for item in parsed_items:
                    if not isinstance(item, dict):
                        continue
                    key = str(item.get("id", "") or "").strip()
                    if not key:
                        continue
                    mapped[key] = {
                        "title": str(item.get("title", "") or "").strip(),
                        "summary": str(item.get("summary", "") or "").strip(),
                        "llm_takeaway": str(item.get("llm_takeaway", "") or "").strip(),
                    }

                for key, row in chunk:
                    obj = mapped.get(key, {})
                    title_val = str(obj.get("title", "") or "").strip()
                    summary_val = str(obj.get("summary", "") or "").strip()
                    takeaway_val = str(obj.get("llm_takeaway", "") or "").strip()
                    if not (title_val or summary_val or takeaway_val):
                        failed.append({"key": key, "error": "empty enrichment fields"})
                        continue
                    patch: Dict[str, str] = {
                        "language": lang,
                        "output_language": lang,
                        "title": title_val,
                        "summary": summary_val,
                        "llm_takeaway": takeaway_val,
                    }
                    if is_chinese_language(lang):
                        patch["title_zh"] = title_val
                        patch["summary_zh"] = summary_val
                        patch["llm_takeaway_zh"] = takeaway_val
                    patch["lang"] = lang_key
                    translated[key] = patch
            except Exception as exc:
                for key, _row in chunk:
                    failed.append({"key": key, "error": f"LLM 调用失败: {type(exc).__name__}: {exc}"})

        return translated, failed

    def _translate_progress_items(
        self,
        keys: List[str],
        output_language: str = "Chinese",
        force: bool = False,
        max_workers: int = 2,
        allow_skip_unconfigured: bool = False,
    ) -> Dict[str, Any]:
        cleaned_keys = [str(x).strip() for x in keys if str(x).strip()]
        if not cleaned_keys:
            return {"ok": False, "error": "keys is required"}
        cleaned_keys = cleaned_keys[:200]
        target_language = normalize_analysis_language(output_language, default="Chinese")

        settings = self.settings.load()
        client_config = self._build_progress_llm_client_config(settings)
        if not client_config:
            if allow_skip_unconfigured:
                return {
                    "ok": True,
                    "requested": len(cleaned_keys),
                    "translated": 0,
                    "changed": 0,
                    "translated_keys": [],
                    "failed": [],
                    "skipped": True,
                    "reason": "LLM 未配置，跳过前沿进展富化",
                    "output_language": target_language,
                }
            return {"ok": False, "error": "LLM 未配置，无法执行多语言翻译"}

        loaded = self.progress.load()
        rows = loaded.get("items") if isinstance(loaded, dict) else []
        if not isinstance(rows, list):
            rows = []
        by_key: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = str(row.get("progress_key", "") or "").strip()
            if key:
                by_key[key] = row

        translations: Dict[str, Dict[str, str]] = {}
        failed: List[Dict[str, str]] = []
        pending_rows: List[Tuple[str, Dict[str, Any]]] = []
        skipped = 0

        for key in cleaned_keys:
            row = by_key.get(key)
            if not isinstance(row, dict):
                failed.append({"key": key, "error": "item not found"})
                continue
            if not self._progress_item_needs_enrichment(row, target_language=target_language, force=force):
                skipped += 1
                continue
            if not str(row.get("title", "") or "").strip():
                failed.append({"key": key, "error": "empty title"})
                continue
            pending_rows.append((key, row))

        worker_count = max(1, min(int(max_workers or 2), 4))
        if pending_rows:
            translations, batch_failed = self._enrich_progress_items_batch_with_llm(
                pending_rows=pending_rows,
                target_language=target_language,
                client_config=client_config,
            )
            failed.extend(batch_failed)

        apply_result = (
            self.progress.apply_translations(translations)
            if translations
            else {"ok": True, "changed": 0, "translated_keys": []}
        )
        translated_keys = apply_result.get("translated_keys", [])
        return {
            "ok": True,
            "requested": len(cleaned_keys),
            "translated": len(translations),
            "changed": int(apply_result.get("changed", 0) or 0),
            "translated_keys": translated_keys if isinstance(translated_keys, list) else [],
            "failed": failed,
            "skipped": skipped,
            "worker_count": worker_count,
            "output_language": target_language,
        }

    def _build_subscription_payload_text(
        self,
        sub: Dict[str, Any],
        papers: List[Dict[str, Any]],
        strategy: str = SUBSCRIPTION_STRATEGY_DEFAULT,
    ) -> str:
        name = str(sub.get("name", "") or "").strip()

        def clip_text(text: Any, limit: int) -> str:
            value = re.sub(r"\s+", " ", str(text or "").strip())
            if len(value) <= limit:
                return value
            return value[: max(0, limit - 3)].rstrip() + "..."

        lines: List[str] = []
        total = len(papers)
        strategy_key = normalize_subscription_strategy(strategy, default=SUBSCRIPTION_STRATEGY_DEFAULT)
        strategy_title = subscription_strategy_label(strategy_key)
        if name and name != "订阅":
            lines.append(f"{name} · {strategy_title} · 命中论文 {total} 篇")
        else:
            lines.append(f"{strategy_title} · 命中论文 {total} 篇")
        lines.append("")

        max_items = 5
        shown = papers[:max_items]
        for idx, paper in enumerate(shown, start=1):
            title = clip_text(paper.get("title", ""), 180)
            score = int(paper.get("recommendation_score", 0) or 0)
            published = str(paper.get("published_at", "") or "").strip()
            published_short = published[:10] if published else ""
            category = str(paper.get("primary_category", "") or "").strip()
            arxiv_id = str(paper.get("arxiv_id", "") or "").strip()
            doi = str(paper.get("doi", "") or "").strip()
            abs_url = str(paper.get("url", "") or "").strip()
            pdf_url = str(paper.get("pdf_url", "") or "").strip()
            authors = paper.get("authors") if isinstance(paper.get("authors"), list) else []
            authors = [str(x).strip() for x in authors if str(x).strip()]
            authors_text = ", ".join(authors[:4])
            if len(authors) > 4:
                authors_text += f" 等{len(authors)}位"

            insight = paper.get("insight") if isinstance(paper.get("insight"), dict) else {}
            one_sentence = clip_text(insight.get("one_sentence_summary", ""), 220)
            method = clip_text(insight.get("method", ""), 200)
            keywords = insight.get("keywords") if isinstance(insight.get("keywords"), list) else []
            keywords = [str(x).strip() for x in keywords if str(x).strip()]

            lines.append(f"{idx}. {title}")
            meta_parts = [f"推荐分: {score}"]
            if published_short:
                meta_parts.insert(0, f"发布时间: {published_short}")
            if category:
                meta_parts.append(f"分类: {category}")
            lines.append("   " + " | ".join(meta_parts))
            if authors_text:
                lines.append(f"   作者: {authors_text}")
            if one_sentence:
                lines.append(f"   摘要: {one_sentence}")
            else:
                abstract = clip_text(paper.get("abstract", ""), 220)
                if abstract:
                    lines.append(f"   摘要: {abstract}")
            if method:
                lines.append(f"   方法: {method}")
            if keywords:
                lines.append(f"   关键词: {', '.join(keywords[:6])}")
            if arxiv_id:
                lines.append(f"   arXiv: {arxiv_id}")
            if doi:
                lines.append(f"   DOI: {doi}")
            if abs_url:
                lines.append(f"   原文: {abs_url}")
            if pdf_url:
                lines.append(f"   PDF: {pdf_url}")
            lines.append("")

        if total > max_items:
            lines.append(f"其余 {total - max_items} 篇请在面板查看。")
        lines.append(f"推送时间: {utc_now_iso()}")
        return "\n".join(lines).strip() + "\n"

    def _translate_notification_text_with_llm(
        self,
        message: str,
        target_language: str,
        settings: Dict[str, Any],
    ) -> str:
        source = str(message or "").strip()
        if not source:
            return ""
        lang = normalize_analysis_language(target_language, default="Chinese")
        if is_chinese_language(lang):
            return source
        client_config = self._build_paper_llm_client_config(settings)
        if not client_config:
            client_config = self._build_progress_llm_client_config(settings)
        if not client_config:
            return source
        prompt = (
            f"Translate the following notification text into {lang}.\n"
            "Rules:\n"
            "1) Keep URLs unchanged.\n"
            "2) Keep model names / company names / version numbers unchanged.\n"
            "3) Keep list numbers and overall structure.\n"
            "4) Return translated text only.\n\n"
            f"{source}"
        )
        try:
            client = AIClient(client_config)
            translated = str(
                client.chat(
                    [
                        {"role": "system", "content": "You are a concise multilingual technical translator."},
                        {"role": "user", "content": prompt},
                    ]
                )
                or ""
            ).strip()
            return translated or source
        except Exception:
            return source

    def _send_subscription_notification(
        self,
        channel: str,
        settings: Dict[str, Any],
        message: str,
        subject: str = "[OmniHawk AI] 论文订阅命中通知",
    ) -> Tuple[bool, str]:
        channel = normalize_notify_channel(channel)
        if channel == "feishu":
            webhook = str(settings.get("feishu_webhook_url", "") or "").strip()
            return self._send_test_webhook("feishu", webhook, message=message)
        if channel in {"wework", "wechat"}:
            webhook = str(settings.get("wework_webhook_url", "") or "").strip()
            msg_type = str(settings.get("wework_msg_type", "markdown") or "markdown").strip().lower()
            if channel == "wechat":
                msg_type = "text"
            if msg_type not in {"markdown", "text"}:
                msg_type = "markdown"
            return self._send_test_webhook("wework", webhook, message=message, msg_type=msg_type)
        if channel == "dingtalk":
            webhook = str(settings.get("dingtalk_webhook_url", "") or "").strip()
            return self._send_test_dingtalk(webhook, message=message)
        if channel == "telegram":
            bot_token = str(settings.get("telegram_bot_token", "") or "").strip()
            chat_id = str(settings.get("telegram_chat_id", "") or "").strip()
            return self._send_test_telegram(bot_token, chat_id, message=message)
        if channel == "ntfy":
            server_url = str(settings.get("ntfy_server_url", "") or "").strip() or DEFAULT_NTFY_SERVER_URL
            topic = str(settings.get("ntfy_topic", "") or "").strip()
            token = str(settings.get("ntfy_token", "") or "").strip()
            return self._send_test_ntfy(server_url, topic, token, message=message)
        if channel == "bark":
            bark_url = str(settings.get("bark_url", "") or "").strip()
            return self._send_test_bark(bark_url, message=message)
        if channel == "slack":
            webhook = str(settings.get("slack_webhook_url", "") or "").strip()
            return self._send_test_slack(webhook, message=message)
        if channel == "email":
            return self._send_test_email(
                settings,
                subject=subject,
                body=message,
            )
        return False, "unsupported channel"

    def _run_subscription(self, sub: Dict[str, Any]) -> Dict[str, Any]:
        sub_id = str(sub.get("id", "") or "").strip()
        settings = self.settings.load()
        output_language = normalize_analysis_language(
            settings.get("analysis_language", "Chinese"),
            default="Chinese",
        )
        filters = normalize_panel_filters(sub.get("filters") if isinstance(sub, dict) else {})
        strategy = normalize_subscription_strategy(
            sub.get("strategy"),
            default=SUBSCRIPTION_STRATEGY_DEFAULT,
        )
        mode = str(sub.get("mode", "all") or "all")
        sort_by = str(sub.get("sort_by", "score") or "score")
        sort_order = str(sub.get("sort_order", "desc") or "desc")
        history = str(sub.get("history", "all") or "all")
        limit = parse_int_value(sub.get("limit"), 1, 500) or 120

        data = self.papers.list_papers(
            limit=limit,
            mode=mode,
            sort_by=sort_by,
            sort_order=sort_order,
            history=history,
            filters=filters,
            output_language=output_language,
        )
        papers = data.get("papers") if isinstance(data, dict) else []
        if not isinstance(papers, list):
            papers = []

        sent_keys = sub.get("sent_keys") if isinstance(sub, dict) else []
        if not isinstance(sent_keys, list):
            sent_keys = []
        sent_set = {str(v).strip() for v in sent_keys if str(v).strip()}

        fresh_papers = []
        fresh_keys = []
        for paper in papers:
            key = str(paper.get("paper_key", "") or "").strip()
            if not key or key in sent_set:
                continue
            fresh_papers.append(paper)
            fresh_keys.append(key)

        selected_papers: List[Dict[str, Any]] = []
        selected_keys: List[str] = []
        if strategy == "daily":
            for paper in papers:
                if not isinstance(paper, dict):
                    continue
                selected_papers.append(paper)
                key = str(paper.get("paper_key", "") or "").strip()
                if key:
                    selected_keys.append(key)
        elif strategy == "realtime":
            for paper in fresh_papers:
                if not isinstance(paper, dict):
                    continue
                if not is_realtime_priority_paper(paper):
                    continue
                selected_papers.append(paper)
                key = str(paper.get("paper_key", "") or "").strip()
                if key:
                    selected_keys.append(key)
        else:
            selected_papers = list(fresh_papers)
            selected_keys = list(fresh_keys)

        result: Dict[str, Any] = {
            "id": sub_id,
            "name": str(sub.get("name", "") or "").strip(),
            "channel": str(sub.get("channel", "") or "").strip(),
            "strategy": strategy,
            "output_language": output_language,
            "match_count": len(papers),
            "new_count": len(fresh_papers),
            "push_count": len(selected_papers),
            "ok": True,
            "message": "",
        }
        if not selected_papers:
            if strategy == "daily":
                result["message"] = "当日汇总无命中，跳过推送"
            elif strategy == "realtime":
                result["message"] = "无高优先级实时告警，跳过推送"
            else:
                result["message"] = "无新增命中，无需推送"
            return result

        msg_text = self._build_subscription_payload_text(sub, selected_papers, strategy=strategy)
        msg_text = self._translate_notification_text_with_llm(
            msg_text,
            target_language=output_language,
            settings=settings,
        )
        ok, msg = self._send_subscription_notification(
            str(sub.get("channel", "") or "").strip(),
            settings,
            msg_text,
            subject=f"[OmniHawk AI] 论文订阅 {subscription_strategy_label(strategy)} 通知",
        )
        result["ok"] = ok
        result["message"] = msg
        if ok:
            mark_keys = selected_keys if strategy in {"incremental", "realtime"} else []
            self.subscriptions.mark_notified(sub_id, mark_keys, len(papers))
        return result

    def _run_paper_subscriptions(
        self,
        sub_id: str = "",
        *,
        trigger_mode: str = "manual",
    ) -> Dict[str, Any]:
        payload = self.subscriptions.load()
        items = payload.get("items") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []
        target_id = str(sub_id or "").strip()
        if target_id:
            targets = [item for item in items if str(item.get("id", "")) == target_id]
        else:
            targets = [item for item in items if bool(item.get("enabled", True))]

        mode = str(trigger_mode or "manual").strip().lower() or "manual"
        if mode == "realtime":
            targets = [
                item
                for item in targets
                if normalize_subscription_strategy(
                    item.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                )
                == "realtime"
            ]
        elif mode == "scheduled":
            targets = [
                item
                for item in targets
                if normalize_subscription_strategy(
                    item.get("strategy"),
                    default=SUBSCRIPTION_STRATEGY_DEFAULT,
                )
                != "realtime"
            ]
        if not targets:
            empty_ok = mode in {"scheduled", "realtime"}
            return {
                "ok": empty_ok,
                "error": "no subscription to run",
                "trigger_mode": mode,
                "results": [],
                "success_count": 0,
                "total": 0,
            }
        results = [self._run_subscription(item) for item in targets]
        success_count = sum(1 for x in results if x.get("ok"))
        return {
            "ok": success_count == len(results),
            "trigger_mode": mode,
            "results": results,
            "success_count": success_count,
            "total": len(results),
        }

    def _run_paper_fetch_task(
        self,
        *,
        analysis_language: str,
        requested_by: str = "manual",
    ) -> Dict[str, Any]:
        lang = normalize_analysis_language(analysis_language, default="Chinese")
        ok, message = self.runner.trigger(analysis_language=lang)
        if not ok:
            return {
                "ok": False,
                "error": str(message or "failed to start crawl"),
                "analysis_language": lang,
                "requested_by": str(requested_by or "manual").strip() or "manual",
            }

        # Wait for crawl process completion so persisted task state can reflect final result.
        while True:
            status = self.runner.status()
            if not bool(status.get("running")):
                break
            time.sleep(1.0)

        status = self.runner.status()
        exit_code = status.get("last_exit_code")
        error_text = str(status.get("last_error", "") or "").strip()
        task_ok = (exit_code == 0) and not error_text
        return {
            "ok": task_ok,
            "analysis_language": lang,
            "requested_by": str(requested_by or "manual").strip() or "manual",
            "started_at": str(status.get("started_at", "") or "").strip(),
            "finished_at": str(status.get("finished_at", "") or "").strip(),
            "exit_code": exit_code,
            "error": error_text,
            "message": "crawl finished" if task_ok else (error_text or f"crawl exited with code {exit_code}"),
        }

    def _send_test_webhook(
        self,
        channel: str,
        webhook_url: str,
        message: str = "",
        msg_type: str = "markdown",
    ) -> Tuple[bool, str]:
        webhook_url = str(webhook_url or "").strip()
        if not webhook_url:
            return False, f"{channel} webhook 未配置"

        now = utc_now_iso()
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {now}\n渠道: {channel}"
        if channel == "feishu":
            payload = {
                "msg_type": "text",
                "content": {"text": text_message},
            }
        elif channel == "wework":
            normalized_type = str(msg_type or "markdown").strip().lower()
            if normalized_type == "text":
                payload = {
                    "msgtype": "text",
                    "text": {"content": text_message},
                }
            else:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"content": text_message},
                }
        else:
            return False, f"unsupported channel: {channel}"

        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"

        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_dingtalk(self, webhook_url: str, message: str = "") -> Tuple[bool, str]:
        webhook_url = str(webhook_url or "").strip()
        if not webhook_url:
            return False, "dingtalk webhook 未配置"
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n渠道: dingtalk"
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "OmniHawk AI 通知",
                "text": text_message,
            },
        }
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_telegram(self, bot_token: str, chat_id: str, message: str = "") -> Tuple[bool, str]:
        bot_token = str(bot_token or "").strip()
        chat_id = str(chat_id or "").strip()
        if not bot_token or not chat_id:
            return False, "telegram 配置不完整（bot token/chat id）"
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n渠道: telegram"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text_message}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_ntfy(
        self,
        server_url: str,
        topic: str,
        token: str = "",
        message: str = "",
    ) -> Tuple[bool, str]:
        server_url = str(server_url or "").strip() or DEFAULT_NTFY_SERVER_URL
        topic = str(topic or "").strip()
        token = str(token or "").strip()
        if not topic:
            return False, "ntfy topic 未配置"
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n渠道: ntfy"
        url = f"{server_url.rstrip('/')}/{topic}"
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Title": "OmniHawk AI",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            req = urllib.request.Request(
                url,
                data=text_message.encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_bark(self, bark_url: str, message: str = "") -> Tuple[bool, str]:
        bark_url = str(bark_url or "").strip()
        if not bark_url:
            return False, "bark url 未配置"
        parsed = urlparse(bark_url)
        if not parsed.scheme or not parsed.netloc:
            return False, "bark url 格式无效"
        parts = [x for x in parsed.path.strip("/").split("/") if x]
        device_key = ""
        for part in parts:
            if part.lower() != "push":
                device_key = part
                break
        if not device_key:
            return False, "bark url 缺少 device key"
        api_url = f"{parsed.scheme}://{parsed.netloc}/push"
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n渠道: bark"
        payload = {
            "title": "OmniHawk AI",
            "body": text_message,
            "device_key": device_key,
            "group": "OmniHawk AI",
        }
        try:
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_slack(self, webhook_url: str, message: str = "") -> Tuple[bool, str]:
        webhook_url = str(webhook_url or "").strip()
        if not webhook_url:
            return False, "slack webhook 未配置"
        text_message = str(message or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n渠道: slack"
        payload = {"text": text_message}
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = getattr(resp, "status", 200)
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        if status >= 400:
            return False, f"发送失败: HTTP {status}"
        return True, f"发送成功: HTTP {status}, 响应: {body[:200]}"

    def _send_test_email(
        self,
        settings: Dict[str, Any],
        subject: str = "",
        body: str = "",
    ) -> Tuple[bool, str]:
        email_from = str(settings.get("email_from", "") or "").strip()
        email_password = str(settings.get("email_password", "") or "").strip()
        email_to = str(settings.get("email_to", "") or "").strip()
        smtp_server = str(settings.get("email_smtp_server", "") or "").strip()
        smtp_port_text = str(settings.get("email_smtp_port", "") or "").strip()
        if not (email_from and email_password and email_to):
            return False, "邮箱配置不完整（发件人/密码/收件人）"

        if not smtp_server:
            domain = email_from.split("@")[-1].lower() if "@" in email_from else ""
            defaults = {
                "qq.com": ("smtp.qq.com", 465),
                "163.com": ("smtp.163.com", 465),
                "126.com": ("smtp.126.com", 465),
                "gmail.com": ("smtp.gmail.com", 587),
                "outlook.com": ("smtp-mail.outlook.com", 587),
            }
            smtp_server, default_port = defaults.get(domain, ("smtp.qq.com", 465))
            if not smtp_port_text:
                smtp_port_text = str(default_port)

        try:
            smtp_port = int(smtp_port_text or "465")
        except Exception:
            smtp_port = 465

        recipients = [x.strip() for x in re.split(r"[;,]", email_to) if x.strip()]
        if not recipients:
            return False, "邮箱收件人为空"

        msg = MIMEText(
            str(body or "").strip() or f"OmniHawk AI 面板测试通知\n时间: {utc_now_iso()}\n",
            _subtype="plain",
            _charset="utf-8",
        )
        msg["Subject"] = str(subject or "").strip() or "OmniHawk AI 测试通知"
        msg["From"] = email_from
        msg["To"] = ", ".join(recipients)

        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as smtp:
                    smtp.login(email_from, email_password)
                    smtp.sendmail(email_from, recipients, msg.as_string())
            else:
                with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as smtp:
                    smtp.starttls()
                    smtp.login(email_from, email_password)
                    smtp.sendmail(email_from, recipients, msg.as_string())
        except Exception as exc:
            return False, f"发送失败: {type(exc).__name__}: {exc}"
        return True, f"发送成功: {len(recipients)} 个收件人"

    def _serve_file_from_output(self, rel_path: str) -> bool:
        rel_path = rel_path.lstrip("/")
        target = (self.output_dir / rel_path).resolve()
        try:
            output_real = self.output_dir.resolve()
            if output_real not in target.parents and target != output_real:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                return True
        except Exception:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return True

        if target.is_dir():
            target = target / "index.html"

        if not target.exists() or not target.is_file():
            return False

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        return True

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/":
            self._send_text(self.home_html, "text/html; charset=utf-8")
            return

        if path == "/panel":
            self._send_text(self.panel_html, "text/html; charset=utf-8")
            return

        if path in (
            "/progress",
            "/finance",
            "/reports",
            "/policy-safety",
            "/oss",
        ):
            self._send_text(self.progress_html, "text/html; charset=utf-8")
            return

        if path in ("/settings", "/panel/settings"):
            self._send_text(self.panel_html, "text/html; charset=utf-8")
            return

        if path in ("/deep-analysis", "/panel/deep-analysis"):
            self._send_text(self.deep_html, "text/html; charset=utf-8")
            return

        if path == "/api/status":
            runtime = self.runner.status()
            paper_job = (
                self.paper_tasks.sync_with_runtime(runtime)
                if self.paper_tasks
                else {}
            )
            schedule = self.schedule.current()
            settings = self.settings.load()
            payload = {
                **runtime,
                **schedule,
                "research_topic": settings.get("research_topic", ""),
                "paper_primary_category": settings.get("paper_primary_category", ""),
                "paper_subtopics": settings.get("paper_subtopics", ""),
                "paper_max_papers_per_run": settings.get("paper_max_papers_per_run"),
                "ai_model": settings.get("ai_model", ""),
                "paper_job": paper_job,
                "server_time": utc_now_iso(),
            }
            if bool((paper_job or {}).get("running")):
                payload["running"] = True
            self._send_json(payload)
            return

        if path == "/api/settings":
            self._send_json(self.settings.load())
            return

        if path == "/api/paper-actions":
            self._send_json(self.actions.load())
            return

        if path == "/api/favorites":
            data = self.actions.load()
            records = []
            for key, item in (data.get("items") or {}).items():
                if not isinstance(item, dict):
                    continue
                if not item.get("favorite"):
                    continue
                records.append({"paper_key": key, **item})
            records.sort(key=lambda x: str(x.get("favorite_at", "") or ""), reverse=True)
            self._send_json({"items": records, "count": len(records)})
            return

        if path == "/api/subscriptions":
            data = self.subscriptions.load()
            self._send_json(
                {
                    "items": data.get("items", []),
                    "count": len(data.get("items", [])),
                }
            )
            return

        if path == "/api/progress/sources":
            params = parse_qs(parsed.query)
            scope_raw = str((params.get("scope") or [""])[0] or "").strip()
            scope = normalize_progress_scope(scope_raw, default="")
            all_sources = self.progress.list_sources()
            if scope:
                allowed_kinds = {
                    x.strip().lower()
                    for x in self._progress_kind_for_scope(scope).split(",")
                    if x.strip()
                }
                items = [
                    row
                    for row in all_sources
                    if str(row.get("kind", "") or "").strip().lower() in allowed_kinds
                ]
            else:
                items = all_sources
            self._send_json({"items": items, "count": len(items), "scope": scope or "all"})
            return

        if path == "/api/progress/fetch/status":
            params = parse_qs(parsed.query)
            scope = normalize_progress_scope(str((params.get("scope") or ["frontier"])[0] or "frontier"), default="frontier")
            job = self.progress_tasks.get(scope)
            self._send_json({"ok": True, "scope": scope, "job": job})
            return

        if path == "/api/progress/settings":
            params = parse_qs(parsed.query)
            scope = normalize_progress_scope(str((params.get("scope") or ["frontier"])[0] or "frontier"), default="frontier")
            settings = self.progress_page_settings.get_scope(scope)
            all_sources = self.progress.list_sources()
            allowed_kinds = {x.strip().lower() for x in self._progress_kind_for_scope(scope).split(",") if x.strip()}
            scoped_sources = [
                row
                for row in all_sources
                if str(row.get("kind", "") or "").strip().lower() in allowed_kinds
            ]
            self._send_json(
                {
                    "ok": True,
                    "scope": scope,
                    "settings": settings,
                    "job": self.progress_tasks.get(scope),
                    "sources": scoped_sources,
                }
            )
            return

        if path == "/api/progress/subscriptions":
            params = parse_qs(parsed.query)
            scope = normalize_progress_scope(str((params.get("scope") or ["frontier"])[0] or "frontier"), default="frontier")
            items = self.progress_subscriptions.list(scope)
            self._send_json({"ok": True, "scope": scope, "items": items, "count": len(items)})
            return

        if path == "/api/progress":
            params = parse_qs(parsed.query)
            req = self._extract_progress_request(params)
            scope = normalize_progress_scope(str((params.get("scope") or ["frontier"])[0] or "frontier"), default="frontier")
            if not req.get("kind"):
                req["kind"] = self._progress_kind_for_scope(scope)
            data = self.progress.list_items(**req)
            self._send_json(data)
            return

        if path == "/api/papers":
            params = parse_qs(parsed.query)
            req = self._extract_paper_request(params)
            list_req = dict(req)
            list_req["include_internal"] = True
            data = self.papers.list_papers(**list_req)
            papers = data.get("papers") if isinstance(data, dict) else []
            if not isinstance(papers, list):
                papers = []
            paper_keys = [str(row.get("paper_key", "") or "").strip() for row in papers if isinstance(row, dict)]
            paper_keys = [key for key in paper_keys if key]
            sync_limit = max(0, int(PAPER_LIST_SYNC_ENRICH_LIMIT or 0))
            enrich_keys = paper_keys[:sync_limit] if sync_limit > 0 else []
            enrichment: Dict[str, Any] = {
                "ok": True,
                "requested": len(enrich_keys),
                "translated": 0,
                "changed": 0,
                "translated_keys": [],
                "failed": [],
                "skipped": True,
                "reason": "sync paper enrichment disabled for faster list loading",
            }
            if enrich_keys:
                try:
                    enrichment = self._translate_paper_items(
                        keys=enrich_keys,
                        output_language=str(req.get("output_language", "Chinese") or "Chinese"),
                        force=False,
                        include_deep=False,
                        max_workers=1,
                        allow_skip_unconfigured=True,
                    )
                except Exception as exc:
                    enrichment = {"ok": False, "error": f"paper enrichment failed: {type(exc).__name__}: {exc}"}
            if int(enrichment.get("changed", 0) or 0) > 0:
                data = self.papers.list_papers(**list_req)
                papers = data.get("papers") if isinstance(data, dict) else []
                if not isinstance(papers, list):
                    papers = []
            for row in papers:
                if isinstance(row, dict):
                    row.pop("_db_path", None)
            if isinstance(data, dict):
                data["enrichment"] = enrichment
                if len(paper_keys) > len(enrich_keys):
                    data["enrichment_deferred"] = {
                        "deferred_count": len(paper_keys) - len(enrich_keys),
                        "sync_limit": sync_limit,
                        "message": "remaining items will be lazily enriched by page-side translation",
                    }
            self._send_json(data)
            return

        if path == "/api/paper-detail":
            params = parse_qs(parsed.query)
            paper_key = str((params.get("paper_key") or [""])[0] or "").strip()
            if not paper_key:
                self._send_json({"ok": False, "error": "paper_key is required"}, status=400)
                return
            output_language_raw = str((params.get("output_language") or [""])[0] or "").strip()
            output_language = normalize_analysis_language(output_language_raw, default="Chinese")
            enrichment: Dict[str, Any] = {
                "ok": True,
                "requested": 1,
                "translated": 0,
                "changed": 0,
                "translated_keys": [],
                "failed": [],
                "skipped": 0,
            }
            try:
                enrichment = self._translate_paper_items(
                    keys=[paper_key],
                    output_language=output_language,
                    force=False,
                    include_deep=True,
                    max_workers=1,
                    allow_skip_unconfigured=True,
                )
            except Exception as exc:
                enrichment = {"ok": False, "error": f"paper detail enrichment failed: {type(exc).__name__}: {exc}"}
            paper = self.papers.get_paper_detail_by_key(paper_key, output_language=output_language)
            if not paper:
                self._send_json({"ok": False, "error": "paper not found"}, status=404)
                return
            self._send_json({"ok": True, "paper": paper, "enrichment": enrichment})
            return

        if path == "/api/export":
            params = parse_qs(parsed.query)
            req = self._extract_paper_request(params)
            fmt = str((params.get("format") or ["json"])[0] or "json").strip().lower()
            if fmt not in {"json", "csv", "md"}:
                fmt = "json"
            data = self.papers.list_papers(**req)
            papers = data.get("papers") if isinstance(data, dict) else []
            if not isinstance(papers, list):
                papers = []

            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            if fmt == "csv":
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(
                    [
                        "title",
                        "authors",
                        "affiliations",
                        "published_at",
                        "primary_category",
                        "tags",
                        "arxiv_id",
                        "doi",
                        "recommendation_score",
                        "url",
                        "pdf_url",
                        "one_sentence_summary",
                        "method",
                        "conclusion",
                        "innovation",
                    ]
                )
                for paper in papers:
                    insight = paper.get("insight") if isinstance(paper, dict) else {}
                    if not isinstance(insight, dict):
                        insight = {}
                    writer.writerow(
                        [
                            str(paper.get("title", "") or ""),
                            ", ".join(paper.get("authors") or []),
                            "; ".join(paper.get("affiliations") or []),
                            str(paper.get("published_at", "") or ""),
                            str(paper.get("primary_category", "") or ""),
                            ", ".join(paper.get("tags") or []),
                            str(paper.get("arxiv_id", "") or ""),
                            str(paper.get("doi", "") or ""),
                            int(paper.get("recommendation_score", 0) or 0),
                            str(paper.get("url", "") or ""),
                            str(paper.get("pdf_url", "") or ""),
                            str(insight.get("one_sentence_summary", "") or ""),
                            str(insight.get("method", "") or ""),
                            str(insight.get("conclusion", "") or ""),
                            str(insight.get("innovation", "") or ""),
                        ]
                    )
                body = buf.getvalue().encode("utf-8-sig")
                self._send_bytes(body, "text/csv; charset=utf-8", filename=f"papers-{stamp}.csv")
                return

            if fmt == "md":
                lines = [
                    "# OmniHawk AI 导出",
                    "",
                    f"- 导出时间: {utc_now_iso()}",
                    f"- 论文数量: {len(papers)}",
                    "",
                ]
                for idx, paper in enumerate(papers, start=1):
                    insight = paper.get("insight") if isinstance(paper, dict) else {}
                    if not isinstance(insight, dict):
                        insight = {}
                    lines.append(f"## {idx}. {paper.get('title', '')}")
                    lines.append(f"- 推荐分: {paper.get('recommendation_score', 0)}")
                    lines.append(f"- 发布时间: {paper.get('published_at', '-')}")
                    lines.append(f"- 主分类: {paper.get('primary_category', '-')}")
                    lines.append(f"- 作者: {', '.join(paper.get('authors') or [])}")
                    lines.append(f"- arXiv ID: {paper.get('arxiv_id', '-')}")
                    lines.append(f"- DOI: {paper.get('doi', '-') or '-'}")
                    if paper.get("url"):
                        lines.append(f"- 原文: {paper.get('url')}")
                    if paper.get("pdf_url"):
                        lines.append(f"- PDF: {paper.get('pdf_url')}")
                    lines.append(f"- 摘要: {paper.get('abstract', '-')}")
                    lines.append(f"- 一句话摘要: {insight.get('one_sentence_summary', '-')}")
                    lines.append(f"- 方法: {insight.get('method', '-')}")
                    lines.append(f"- 结论: {insight.get('conclusion', '-')}")
                    lines.append(f"- 创新点: {insight.get('innovation', '-')}")
                    lines.append("")
                body = "\n".join(lines).encode("utf-8")
                self._send_bytes(body, "text/markdown; charset=utf-8", filename=f"papers-{stamp}.md")
                return

            body = json.dumps(
                {
                    "exported_at": utc_now_iso(),
                    "count": len(papers),
                    "stats": data.get("stats", {}),
                    "papers": papers,
                },
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")
            self._send_bytes(body, "application/json; charset=utf-8", filename=f"papers-{stamp}.json")
            return

        if path.startswith("/reports/"):
            rel = path[len("/reports/") :]
            if self._serve_file_from_output(rel):
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        # compatibility: /index.html points to old report index
        if path == "/index.html":
            if self._serve_file_from_output("index.html"):
                return

        if self._serve_file_from_output(path):
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/run-now":
            data = self._read_json()
            requested_lang_raw = str(data.get("analysis_language", "") or "").strip()
            requested_lang = (
                normalize_analysis_language(requested_lang_raw, default="Chinese")
                if requested_lang_raw
                else ""
            )
            default_lang = normalize_analysis_language(
                self.settings.load().get("analysis_language", "Chinese"),
                default="Chinese",
            )
            effective_lang = requested_lang or default_lang
            runtime = self.runner.status()
            paper_job = (
                self.paper_tasks.sync_with_runtime(runtime)
                if self.paper_tasks
                else {}
            )
            if bool(runtime.get("running")) or bool((paper_job or {}).get("running")):
                self._send_json(
                    {
                        "ok": False,
                        "error": "crawl is already running",
                        "job": paper_job,
                    },
                    status=409,
                )
                return

            if self.paper_tasks:
                started = self.paper_tasks.start(
                    analysis_language=effective_lang,
                    requested_by="manual",
                    runner=lambda lang=effective_lang: self._run_paper_fetch_task(
                        analysis_language=lang,
                        requested_by="manual",
                    ),
                )
                if started.get("ok"):
                    self._send_json(
                        {
                            "ok": True,
                            "message": "crawl started",
                            "started": True,
                            "job": started.get("job", {}),
                        }
                    )
                else:
                    self._send_json(started, status=409)
                return

            ok, message = self.runner.trigger(analysis_language=effective_lang)
            if ok:
                self._send_json({"ok": True, "message": message})
            else:
                self._send_json({"ok": False, "error": message}, status=409)
            return

        if path == "/api/schedule":
            data = self._read_json()
            interval = data.get("interval_minutes")
            try:
                interval_int = int(interval)
            except Exception:
                self._send_json({"ok": False, "error": "invalid interval_minutes"}, status=400)
                return

            try:
                info = self.schedule.update_interval(interval_int)
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
                return
            except Exception as exc:
                self._send_json({"ok": False, "error": f"failed to update schedule: {exc}"}, status=500)
                return

            self._send_json({"ok": True, **info})
            return

        if path == "/api/settings":
            data = self._read_json()
            saved = self.settings.save(data)
            schedule_info = self.schedule.sync_command()
            self._send_json({"ok": True, "settings": saved, **schedule_info})
            return

        if path == "/api/paper-actions":
            data = self._read_json()
            paper_key = str(data.get("paper_key", "") or "").strip()
            if not paper_key:
                self._send_json({"ok": False, "error": "paper_key is required"}, status=400)
                return
            favorite = data.get("favorite")
            ignored = data.get("ignored")
            note = data.get("note")
            tags = data.get("tags")
            try:
                saved_item = self.actions.set_action(
                    paper_key=paper_key,
                    favorite=None if favorite is None else bool(favorite),
                    ignored=None if ignored is None else bool(ignored),
                    note=None if note is None else str(note),
                    tags=tags if isinstance(tags, list) else None,
                )
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
                return
            self._send_json({"ok": True, "paper_key": paper_key, "action": saved_item})
            return

        if path == "/api/papers/deep-analyze":
            data = self._read_json()
            paper_key = str(data.get("paper_key", "") or "").strip()
            focus = str(data.get("focus", "") or "").strip()
            question = str(data.get("question", "") or "").strip()
            output_language_raw = str(data.get("output_language", "") or "").strip()
            output_language = (
                normalize_analysis_language(output_language_raw, default="Chinese")
                if output_language_raw
                else ""
            )
            force = bool(parse_bool_text(data.get("force"), False))
            if not paper_key:
                self._send_json({"ok": False, "error": "paper_key is required"}, status=400)
                return
            result = self.deep_analyzer.analyze_selected_paper(
                paper_key=paper_key,
                focus=focus,
                question=question,
                output_language=output_language,
                force=force,
            )
            if result.get("ok"):
                self._send_json(result)
            else:
                self._send_json(result, status=400)
            return

        if path == "/api/papers/translate":
            data = self._read_json()
            keys_raw = data.get("keys")
            if isinstance(keys_raw, list):
                keys = [str(x or "").strip() for x in keys_raw if str(x or "").strip()]
            else:
                key_text = str(data.get("paper_key", "") or "").strip()
                keys = [key_text] if key_text else []
            if not keys:
                self._send_json({"ok": False, "error": "keys is required"}, status=400)
                return
            output_language_raw = str(data.get("output_language", "") or "").strip()
            output_language = normalize_analysis_language(output_language_raw, default="Chinese")
            force = bool(parse_bool_text(data.get("force"), False))
            max_workers = parse_int_value(data.get("max_workers"), 1, 4) or 2
            result = self._translate_paper_items(
                keys=keys,
                output_language=output_language,
                force=force,
                include_deep=False,
                max_workers=max_workers,
                allow_skip_unconfigured=True,
            )
            if result.get("ok"):
                self._send_json(result)
            else:
                self._send_json(result, status=400)
            return

        if path == "/api/progress/settings":
            data = self._read_json()
            scope = normalize_progress_scope(data.get("scope", "frontier"), default="frontier")
            updates: Dict[str, Any] = {}
            if "max_per_source" in data:
                updates["max_per_source"] = parse_int_value(data.get("max_per_source"), 1, 120)
            if "fetch_workers" in data:
                updates["fetch_workers"] = parse_int_value(data.get("fetch_workers"), 1, 16)
            if "source_ids" in data:
                updates["source_ids"] = data.get("source_ids") if isinstance(data.get("source_ids"), list) else []
            if "notify_channel" in data:
                updates["notify_channel"] = str(data.get("notify_channel", "") or "").strip().lower()
            if "notify_limit" in data:
                updates["notify_limit"] = parse_int_value(data.get("notify_limit"), 1, 30)
            if "output_language" in data:
                updates["output_language"] = normalize_analysis_language(
                    data.get("output_language"),
                    default="Chinese",
                )
            if "feishu_webhook_url" in data:
                updates["feishu_webhook_url"] = str(data.get("feishu_webhook_url", "") or "").strip()
            if "wework_webhook_url" in data:
                updates["wework_webhook_url"] = str(data.get("wework_webhook_url", "") or "").strip()
            if "wework_msg_type" in data:
                updates["wework_msg_type"] = str(data.get("wework_msg_type", "") or "").strip().lower()
            if "dingtalk_webhook_url" in data:
                updates["dingtalk_webhook_url"] = str(data.get("dingtalk_webhook_url", "") or "").strip()
            if "telegram_bot_token" in data:
                updates["telegram_bot_token"] = str(data.get("telegram_bot_token", "") or "").strip()
            if "telegram_chat_id" in data:
                updates["telegram_chat_id"] = str(data.get("telegram_chat_id", "") or "").strip()
            if "ntfy_server_url" in data:
                updates["ntfy_server_url"] = str(data.get("ntfy_server_url", "") or "").strip()
            if "ntfy_topic" in data:
                updates["ntfy_topic"] = str(data.get("ntfy_topic", "") or "").strip()
            if "ntfy_token" in data:
                updates["ntfy_token"] = str(data.get("ntfy_token", "") or "").strip()
            if "bark_url" in data:
                updates["bark_url"] = str(data.get("bark_url", "") or "").strip()
            if "slack_webhook_url" in data:
                updates["slack_webhook_url"] = str(data.get("slack_webhook_url", "") or "").strip()
            if "email_from" in data:
                updates["email_from"] = str(data.get("email_from", "") or "").strip()
            if "email_password" in data:
                updates["email_password"] = str(data.get("email_password", "") or "").strip()
            if "email_to" in data:
                updates["email_to"] = str(data.get("email_to", "") or "").strip()
            if "email_smtp_server" in data:
                updates["email_smtp_server"] = str(data.get("email_smtp_server", "") or "").strip()
            if "email_smtp_port" in data:
                updates["email_smtp_port"] = str(data.get("email_smtp_port", "") or "").strip()
            if "query" in data:
                updates["query"] = normalize_progress_filters(data.get("query") if isinstance(data.get("query"), dict) else {})
            if "auto_enabled" in data:
                updates["auto_enabled"] = bool(parse_bool_text(data.get("auto_enabled"), False))
            if "auto_interval_minutes" in data:
                updates["auto_interval_minutes"] = parse_int_value(
                    data.get("auto_interval_minutes"),
                    PROGRESS_AUTO_MIN_INTERVAL,
                    PROGRESS_AUTO_MAX_INTERVAL,
                )
            if "auto_push_enabled" in data:
                updates["auto_push_enabled"] = bool(parse_bool_text(data.get("auto_push_enabled"), False))
            saved = self.progress_page_settings.save_scope(scope, updates)
            self._send_json({"ok": True, "scope": scope, "settings": saved})
            return

        if path in {"/api/progress/fetch", "/api/progress/fetch/start"}:
            data = self._read_json()
            scope = normalize_progress_scope(data.get("scope", "frontier"), default="frontier")
            scope_cfg = self.progress_page_settings.get_scope(scope)
            max_per_source = (
                parse_int_value(data.get("max_per_source"), 1, 120)
                or parse_int_value(scope_cfg.get("max_per_source"), 1, 120)
                or 20
            )
            fetch_workers = (
                parse_int_value(data.get("fetch_workers"), 1, 16)
                or parse_int_value(scope_cfg.get("fetch_workers"), 1, 16)
                or 6
            )
            source_ids_raw = data.get("source_ids")
            if isinstance(source_ids_raw, list):
                source_ids = [str(x).strip() for x in source_ids_raw if str(x).strip()]
            else:
                cfg_ids = scope_cfg.get("source_ids") if isinstance(scope_cfg.get("source_ids"), list) else []
                source_ids = [str(x).strip() for x in cfg_ids if str(x).strip()]
            auto_push = bool(parse_bool_text(data.get("auto_push"), False))
            async_mode = bool(parse_bool_text(data.get("async"), True))

            if path == "/api/progress/fetch" and not async_mode:
                result = self._run_progress_fetch_task(
                    scope=scope,
                    max_per_source=max_per_source,
                    fetch_workers=fetch_workers,
                    source_ids=source_ids,
                    auto_push=auto_push,
                    requested_by="manual",
                )
                self._send_json(result)
                return

            started = self.progress_tasks.start(
                scope=scope,
                max_per_source=max_per_source,
                fetch_workers=fetch_workers,
                source_ids=source_ids,
                requested_by="manual",
                runner=lambda s=scope, m=max_per_source, fw=fetch_workers, ids=list(source_ids), ap=auto_push: self._run_progress_fetch_task(
                    scope=s,
                    max_per_source=m,
                    fetch_workers=fw,
                    source_ids=ids,
                    auto_push=ap,
                    requested_by="manual",
                ),
            )
            if not started.get("ok"):
                self._send_json(started, status=409)
                return
            self._send_json({"ok": True, "scope": scope, "started": True, "job": started.get("job", {})})
            return

        if path == "/api/progress/push":
            data = self._read_json()
            scope = normalize_progress_scope(data.get("scope", "frontier"), default="frontier")
            raw_channel = str(data.get("channel", "") or "").strip().lower()
            channel = normalize_notify_channel(raw_channel)
            if raw_channel and raw_channel not in NOTIFY_CHANNEL_SET:
                allowed = "|".join(NOTIFY_CHANNELS)
                self._send_json({"ok": False, "error": f"channel must be {allowed}"}, status=400)
                return
            limit = parse_int_value(data.get("limit"), 1, 30) or 8
            filters = data.get("filters") if isinstance(data.get("filters"), dict) else {}
            kind_text = str(filters.get("kind", "") or "").strip()
            if not kind_text:
                kind_text = self._progress_kind_for_scope(scope)
            def query_progress_items() -> Dict[str, Any]:
                return self.progress.list_items(
                    limit=limit,
                    q=str(filters.get("q", "") or "").strip(),
                    source_id=str(filters.get("source_id", "") or "").strip(),
                    region=str(filters.get("region", "") or "").strip(),
                    kind=kind_text,
                    event_type=str(filters.get("event_type", "") or "").strip(),
                    date_from=str(filters.get("date_from", "") or "").strip(),
                    date_to=str(filters.get("date_to", "") or "").strip(),
                )

            list_data = query_progress_items()
            items = list_data.get("items") if isinstance(list_data.get("items"), list) else []
            if not items:
                self._send_json({"ok": False, "error": "no matched progress item to push"}, status=400)
                return

            # Try to enrich localized fields before push; if LLM is not configured, skip silently.
            keys = []
            for row in items:
                if not isinstance(row, dict):
                    continue
                key = str(row.get("progress_key", "") or "").strip()
                if key and key not in keys:
                    keys.append(key)
            scope_settings = self.progress_page_settings.get_scope(scope)
            output_language = normalize_analysis_language(
                scope_settings.get("output_language", "Chinese"),
                default="Chinese",
            )
            enrichment = None
            if keys:
                enrichment = self._translate_progress_items(
                    keys=keys,
                    output_language=output_language,
                    force=False,
                    max_workers=2,
                    allow_skip_unconfigured=True,
                )

            # Reload once so payload prefers latest *_zh fields after enrichment.
            list_data = query_progress_items()
            items = list_data.get("items") if isinstance(list_data.get("items"), list) else []
            if not items:
                self._send_json({"ok": False, "error": "no matched progress item to push"}, status=400)
                return

            settings = self._progress_notify_settings(scope)
            msg_text = self._build_progress_payload_text(
                items,
                strategy="daily",
                output_language=output_language,
            )
            msg_text = self._translate_notification_text_with_llm(
                msg_text,
                target_language=output_language,
                settings=settings,
            )
            ok, msg = self._send_subscription_notification(channel, settings, msg_text)
            if ok:
                payload = {"ok": True, "channel": channel, "count": len(items), "message": msg}
                if isinstance(enrichment, dict):
                    payload["enrichment"] = enrichment
                self._send_json(payload)
            else:
                self._send_json({"ok": False, "channel": channel, "error": msg}, status=400)
            return

        if path == "/api/progress/subscriptions":
            data = self._read_json()
            scope = normalize_progress_scope(data.get("scope", "frontier"), default="frontier")
            name = str(data.get("name", "") or "").strip()
            raw_channel = str(data.get("channel", "") or "").strip().lower()
            channel = normalize_notify_channel(raw_channel)
            strategy = normalize_subscription_strategy(
                data.get("strategy"),
                default=SUBSCRIPTION_STRATEGY_DEFAULT,
            )
            enabled = bool(parse_bool_text(data.get("enabled"), True))
            limit = parse_int_value(data.get("limit"), 1, 500) or 120
            sub_id = str(data.get("id", "") or "").strip()
            filters = normalize_progress_filters(data.get("filters") if isinstance(data.get("filters"), dict) else {})
            if raw_channel and raw_channel not in NOTIFY_CHANNEL_SET:
                allowed = "|".join(NOTIFY_CHANNELS)
                self._send_json({"ok": False, "error": f"channel must be {allowed}"}, status=400)
                return
            saved = self.progress_subscriptions.upsert(
                scope=scope,
                name=name,
                channel=channel,
                filters=filters,
                enabled=enabled,
                limit=limit,
                strategy=strategy,
                sub_id=sub_id,
            )
            items = self.progress_subscriptions.list(scope)
            current = None
            for row in items:
                if str(row.get("id", "")) == str(saved.get("id", "")):
                    current = row
                    break
            self._send_json({"ok": True, "scope": scope, "item": current, "items": items})
            return

        if path == "/api/progress/subscriptions/delete":
            data = self._read_json()
            sub_id = str(data.get("id", "") or "").strip()
            if not sub_id:
                self._send_json({"ok": False, "error": "id is required"}, status=400)
                return
            deleted = self.progress_subscriptions.delete(sub_id)
            self._send_json({"ok": bool(deleted), "deleted": bool(deleted), "id": sub_id})
            return

        if path == "/api/progress/subscriptions/run":
            data = self._read_json()
            scope = normalize_progress_scope(data.get("scope", "frontier"), default="frontier")
            sub_id = str(data.get("id", "") or "").strip()
            result = self._run_progress_subscriptions(scope, sub_id=sub_id)
            if result.get("ok"):
                self._send_json(result)
            else:
                self._send_json(result, status=400)
            return

        if path == "/api/progress/translate":
            data = self._read_json()
            keys_raw = data.get("keys")
            keys: List[str] = []
            if isinstance(keys_raw, list):
                keys = [str(x).strip() for x in keys_raw if str(x).strip()]
            output_language = normalize_analysis_language(
                str(data.get("output_language", "") or "").strip(),
                default="Chinese",
            )
            force = bool(parse_bool_text(data.get("force"), False))
            result = self._translate_progress_items(
                keys=keys,
                output_language=output_language,
                force=force,
            )
            if result.get("ok"):
                self._send_json(result)
            else:
                self._send_json(result, status=400)
            return

        if path == "/api/subscriptions":
            data = self._read_json()
            name = str(data.get("name", "") or "").strip()
            raw_channel = str(data.get("channel", "") or "").strip().lower()
            channel = normalize_notify_channel(raw_channel)
            strategy = normalize_subscription_strategy(
                data.get("strategy"),
                default=SUBSCRIPTION_STRATEGY_DEFAULT,
            )
            enabled = parse_bool_text(data.get("enabled"), True)
            sub_id = str(data.get("id", "") or "").strip()
            filters = normalize_panel_filters(data.get("filters") if isinstance(data.get("filters"), dict) else {})
            mode = str(data.get("mode", "all") or "all").strip().lower()
            sort_by = str(data.get("sort_by", "score") or "score").strip().lower()
            sort_order = str(data.get("sort_order", "desc") or "desc").strip().lower()
            history = str(data.get("history", "all") or "all").strip().lower()
            limit = parse_int_value(data.get("limit"), 1, 500) or 120
            if raw_channel and raw_channel not in NOTIFY_CHANNEL_SET:
                allowed = "|".join(NOTIFY_CHANNELS)
                self._send_json({"ok": False, "error": f"channel must be {allowed}"}, status=400)
                return
            if mode not in {"all", "favorites", "ignored"}:
                mode = "all"
            if sort_by not in {"score", "time", "title"}:
                sort_by = "score"
            if sort_order not in {"asc", "desc"}:
                sort_order = "desc"
            if history not in {"all", "latest"}:
                history = "all"
            merged_filters = dict(filters)
            saved_item = self.subscriptions.upsert(
                name=name,
                channel=channel,
                filters=merged_filters,
                enabled=bool(enabled),
                sub_id=sub_id,
                mode=mode,
                strategy=strategy,
                sort_by=sort_by,
                sort_order=sort_order,
                history=history,
                limit=limit,
            )
            saved_payload = self.subscriptions.load()
            saved_items = saved_payload.get("items", []) if isinstance(saved_payload, dict) else []
            current_item = None
            for item in saved_items:
                if str(item.get("id", "")) == str(saved_item.get("id", "")):
                    current_item = item
                    break
            self._send_json({"ok": True, "item": current_item, "items": saved_items})
            return

        if path == "/api/subscriptions/delete":
            data = self._read_json()
            sub_id = str(data.get("id", "") or "").strip()
            if not sub_id:
                self._send_json({"ok": False, "error": "id is required"}, status=400)
                return
            deleted = self.subscriptions.delete(sub_id)
            self._send_json({"ok": bool(deleted), "deleted": bool(deleted), "id": sub_id})
            return

        if path == "/api/subscriptions/run":
            data = self._read_json()
            sub_id = str(data.get("id", "") or "").strip()
            result = self._run_paper_subscriptions(sub_id=sub_id, trigger_mode="manual")
            if result.get("ok"):
                self._send_json(result)
            else:
                self._send_json(result, status=400)
            return

        if path == "/api/notify-test":
            data = self._read_json()
            raw_channel = str(data.get("channel", "") or "").strip().lower()
            channel = normalize_notify_channel(raw_channel)
            if raw_channel and raw_channel not in NOTIFY_CHANNEL_SET:
                allowed = "|".join(NOTIFY_CHANNELS)
                self._send_json({"ok": False, "error": f"channel must be {allowed}"}, status=400)
                return
            settings = self.settings.load()
            if channel == "feishu":
                ok, msg = self._send_test_webhook("feishu", settings.get("feishu_webhook_url", ""))
            elif channel in {"wework", "wechat"}:
                msg_type = "text" if channel == "wechat" else str(settings.get("wework_msg_type", "markdown") or "markdown")
                ok, msg = self._send_test_webhook(
                    "wework",
                    settings.get("wework_webhook_url", ""),
                    msg_type=msg_type,
                )
            elif channel == "dingtalk":
                ok, msg = self._send_test_dingtalk(str(settings.get("dingtalk_webhook_url", "") or "").strip())
            elif channel == "telegram":
                ok, msg = self._send_test_telegram(
                    str(settings.get("telegram_bot_token", "") or "").strip(),
                    str(settings.get("telegram_chat_id", "") or "").strip(),
                )
            elif channel == "ntfy":
                ok, msg = self._send_test_ntfy(
                    str(settings.get("ntfy_server_url", "") or "").strip() or DEFAULT_NTFY_SERVER_URL,
                    str(settings.get("ntfy_topic", "") or "").strip(),
                    str(settings.get("ntfy_token", "") or "").strip(),
                )
            elif channel == "bark":
                ok, msg = self._send_test_bark(str(settings.get("bark_url", "") or "").strip())
            elif channel == "slack":
                ok, msg = self._send_test_slack(str(settings.get("slack_webhook_url", "") or "").strip())
            elif channel == "email":
                ok, msg = self._send_test_email(settings)
            else:
                self._send_json({"ok": False, "error": "unsupported channel"}, status=400)
                return
            if ok:
                self._send_json({"ok": True, "channel": channel, "message": msg})
            else:
                self._send_json({"ok": False, "channel": channel, "error": msg}, status=400)
            return

        self._send_json({"ok": False, "error": "not found"}, status=404)


def run_server(port: int, output_dir: Path) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    settings_store = PanelSettingsStore(output_dir)
    action_store = PanelActionStore(output_dir)
    subscription_store = PanelSubscriptionStore(output_dir)
    progress_page_settings = ProgressPageSettingsStore(output_dir)
    progress_subscription_store = ProgressSubscriptionStore(output_dir)
    progress_repo = AIProgressRepository(output_dir)
    progress_task_manager = ProgressFetchTaskManager(output_dir)
    paper_task_manager = PaperFetchTaskManager(output_dir)
    DashboardHandler.settings = settings_store
    DashboardHandler.actions = action_store
    DashboardHandler.subscriptions = subscription_store
    DashboardHandler.progress_page_settings = progress_page_settings
    DashboardHandler.progress_subscriptions = progress_subscription_store
    DashboardHandler.progress_tasks = progress_task_manager
    DashboardHandler.paper_tasks = paper_task_manager
    DashboardHandler.progress = progress_repo
    DashboardHandler.runner = CrawlRunner(PROJECT_ROOT, settings_store=settings_store)
    DashboardHandler.schedule = ScheduleController(
        PROJECT_ROOT,
        output_dir=output_dir,
        settings_store=settings_store,
    )
    DashboardHandler.papers = PaperRepository(
        output_dir,
        settings_store=settings_store,
        action_store=action_store,
    )
    DashboardHandler.deep_analyzer = DeepAnalysisService(
        settings_store=settings_store,
        paper_repo=DashboardHandler.papers,
    )
    DashboardHandler.output_dir = output_dir
    DashboardHandler.home_html = build_home_html()
    DashboardHandler.panel_html = build_panel_html_v2()
    DashboardHandler.progress_html = build_progress_html()
    DashboardHandler.settings_html = build_settings_html()
    DashboardHandler.deep_html = build_deep_analysis_html()
    paper_worker = DashboardHandler.__new__(DashboardHandler)
    progress_worker = DashboardHandler.__new__(DashboardHandler)

    def _on_paper_crawl_finished(result: Dict[str, Any]) -> None:
        if not isinstance(result, dict) or not bool(result.get("ok", False)):
            return
        try:
            realtime_result = paper_worker._run_paper_subscriptions(trigger_mode="realtime")
            total = int(realtime_result.get("total", 0) or 0)
            success = int(realtime_result.get("success_count", 0) or 0)
            if total > 0:
                print(
                    "[panel] paper realtime subscriptions triggered: "
                    f"{success}/{total} success"
                )
        except Exception as exc:
            print(f"[panel] warning: paper realtime trigger failed: {type(exc).__name__}: {exc}")

    DashboardHandler.runner.add_on_finished_callback(_on_paper_crawl_finished)
    DashboardHandler.progress_auto_scheduler = ProgressAutoScheduler(
        settings_store=progress_page_settings,
        task_manager=progress_task_manager,
        trigger_once=lambda **kwargs: progress_worker._run_progress_fetch_task(**kwargs),
    )
    DashboardHandler.progress_auto_scheduler.start()
    try:
        DashboardHandler.schedule.sync_command()
    except Exception as exc:
        print(f"[panel] warning: failed to sync schedule command: {exc}")

    httpd = ThreadingHTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"[panel] server started on 0.0.0.0:{port}")
    print(f"[panel] output directory: {output_dir}")
    print(f"[panel] dashboard: http://localhost:{port}/")
    print(f"[panel] reports:   http://localhost:{port}/reports/index.html")
    httpd.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="OmniHawk AI paper dashboard server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--output-dir", type=str, default="output")
    args = parser.parse_args()
    run_server(port=args.port, output_dir=Path(args.output_dir))


if __name__ == "__main__":
    main()
