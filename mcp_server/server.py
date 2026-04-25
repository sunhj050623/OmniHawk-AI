"""OmniHawk AI MCP Server.

Expose OmniHawk AI's current 6-page intelligence capabilities through MCP:
- Paper Radar
- Frontier Radar
- AI Finance
- AI Industry Reports
- AI Policy & Safety
- AI OSS & Dev Signals
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from trendradar.web.panel_server import (
    DashboardHandler,
    DeepAnalysisService,
    PanelActionStore,
    PanelSettingsStore,
    PanelSubscriptionStore,
    PaperRepository,
    NOTIFY_CHANNELS,
    NOTIFY_CHANNEL_SET,
    PROGRESS_SCOPE_KIND_MAP,
    PROGRESS_SCOPE_NAME_MAP_ZH,
    PROGRESS_SCOPES,
    ProgressPageSettingsStore,
    ProgressSubscriptionStore,
    normalize_analysis_language,
    normalize_panel_filters,
    normalize_progress_filters,
    normalize_progress_scope,
    parse_bool_text,
    parse_int_value,
)
from trendradar.web.progress_repo import AIProgressRepository

from . import __version__


APP_NAME = "omnihawk-ai"
mcp = FastMCP(APP_NAME)


PAGE_REGISTRY: List[Dict[str, str]] = [
    {"id": "paper", "name_zh": "论文雷达", "name_en": "Paper Radar", "scope": ""},
    {"id": "frontier", "name_zh": "AI 前沿雷达", "name_en": "AI Frontier", "scope": "frontier"},
    {"id": "finance", "name_zh": "AI 财经信息", "name_en": "AI Finance", "scope": "market_finance"},
    {"id": "reports", "name_zh": "AI 产业报告", "name_en": "AI Industry Reports", "scope": "industry_report"},
    {"id": "policy-safety", "name_zh": "AI 政策与安全", "name_en": "AI Policy & Safety", "scope": "policy_safety"},
    {"id": "oss", "name_zh": "AI 开源生态与开发者信号", "name_en": "AI OSS & Dev Signals", "scope": "oss_signal"},
]

SCOPE_ALIASES: Dict[str, str] = {
    "frontier": "frontier",
    "progress": "frontier",
    "finance": "market_finance",
    "market_finance": "market_finance",
    "market-finance": "market_finance",
    "reports": "industry_report",
    "industry_report": "industry_report",
    "industry-report": "industry_report",
    "policy": "policy_safety",
    "policy_safety": "policy_safety",
    "policy-safety": "policy_safety",
    "safety": "policy_safety",
    "oss": "oss_signal",
    "oss_signal": "oss_signal",
    "oss-signal": "oss_signal",
}


@dataclass
class OmniHawkContext:
    project_root: Path
    output_dir: Path
    settings: PanelSettingsStore
    actions: PanelActionStore
    paper_subscriptions: PanelSubscriptionStore
    progress_page_settings: ProgressPageSettingsStore
    progress_subscriptions: ProgressSubscriptionStore
    papers: PaperRepository
    progress: AIProgressRepository
    deep_analyzer: DeepAnalysisService
    helper: DashboardHandler


_context_lock = threading.RLock()
_context: Optional[OmniHawkContext] = None
_root_override: Optional[Path] = None
_output_override: Optional[Path] = None


def _json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def _clean_text_list(values: Optional[List[Any]]) -> List[str]:
    out: List[str] = []
    if not isinstance(values, list):
        return out
    for value in values:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _normalize_scope(value: Any, default: str = "frontier") -> str:
    raw = str(value or "").strip().lower()
    raw = raw.replace("-", "_")
    mapped = SCOPE_ALIASES.get(raw, raw)
    return normalize_progress_scope(mapped, default=default)


def _normalize_channel(value: Any) -> str:
    channel = str(value or "feishu").strip().lower()
    if channel not in NOTIFY_CHANNEL_SET:
        raise ValueError(f"channel must be {'|'.join(NOTIFY_CHANNELS)}")
    return channel


def _resolve_project_root(project_root: Optional[str]) -> Path:
    if project_root:
        return Path(project_root).resolve()
    if _root_override is not None:
        return _root_override.resolve()
    env_root = str(os.getenv("OMNIHAWK_PROJECT_ROOT", "") or "").strip()
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[1]


def _resolve_output_dir(output_dir: Optional[str], project_root: Path) -> Path:
    if output_dir:
        return Path(output_dir).resolve()
    if _output_override is not None:
        return _output_override.resolve()
    env_output = str(
        os.getenv("OMNIHAWK_OUTPUT_DIR", "")
        or os.getenv("TRENDRADAR_OUTPUT_DIR", "")
        or ""
    ).strip()
    if env_output:
        return Path(env_output).resolve()
    return (project_root / "output").resolve()


def _build_helper(
    settings: PanelSettingsStore,
    actions: PanelActionStore,
    paper_subscriptions: PanelSubscriptionStore,
    progress_page_settings: ProgressPageSettingsStore,
    progress_subscriptions: ProgressSubscriptionStore,
    papers: PaperRepository,
    progress: AIProgressRepository,
    deep_analyzer: DeepAnalysisService,
) -> DashboardHandler:
    helper = DashboardHandler.__new__(DashboardHandler)
    helper.settings = settings
    helper.actions = actions
    helper.subscriptions = paper_subscriptions
    helper.progress_page_settings = progress_page_settings
    helper.progress_subscriptions = progress_subscriptions
    helper.papers = papers
    helper.progress = progress
    helper.deep_analyzer = deep_analyzer
    helper.paper_enrich_retry_after = {}
    helper.paper_enrich_retry_lock = threading.RLock()
    return helper


def _build_context(project_root: Optional[str] = None, output_dir: Optional[str] = None) -> OmniHawkContext:
    root = _resolve_project_root(project_root)
    out = _resolve_output_dir(output_dir, root)
    out.mkdir(parents=True, exist_ok=True)

    settings = PanelSettingsStore(out)
    actions = PanelActionStore(out)
    paper_subscriptions = PanelSubscriptionStore(out)
    progress_page_settings = ProgressPageSettingsStore(out)
    progress_subscriptions = ProgressSubscriptionStore(out)
    papers = PaperRepository(out, settings_store=settings, action_store=actions)
    progress = AIProgressRepository(out)
    deep_analyzer = DeepAnalysisService(settings_store=settings, paper_repo=papers)
    helper = _build_helper(
        settings=settings,
        actions=actions,
        paper_subscriptions=paper_subscriptions,
        progress_page_settings=progress_page_settings,
        progress_subscriptions=progress_subscriptions,
        papers=papers,
        progress=progress,
        deep_analyzer=deep_analyzer,
    )

    return OmniHawkContext(
        project_root=root,
        output_dir=out,
        settings=settings,
        actions=actions,
        paper_subscriptions=paper_subscriptions,
        progress_page_settings=progress_page_settings,
        progress_subscriptions=progress_subscriptions,
        papers=papers,
        progress=progress,
        deep_analyzer=deep_analyzer,
        helper=helper,
    )


def _ensure_context(project_root: Optional[str] = None, output_dir: Optional[str] = None) -> OmniHawkContext:
    global _context
    with _context_lock:
        if _context is None:
            _context = _build_context(project_root=project_root, output_dir=output_dir)
            return _context

        root = _resolve_project_root(project_root)
        out = _resolve_output_dir(output_dir, root)
        if _context.project_root == root and _context.output_dir == out:
            return _context

        _context = _build_context(project_root=project_root, output_dir=output_dir)
        return _context


def _configure_context_paths(project_root: Optional[str], output_dir: Optional[str]) -> None:
    global _context, _root_override, _output_override
    with _context_lock:
        _context = None
        _root_override = Path(project_root).resolve() if project_root else None
        _output_override = Path(output_dir).resolve() if output_dir else None


def _scope_allowed_kinds(scope: str) -> List[str]:
    kind_text = str(PROGRESS_SCOPE_KIND_MAP.get(scope, PROGRESS_SCOPE_KIND_MAP["frontier"]))
    return [x.strip().lower() for x in kind_text.split(",") if x.strip()]


def _scope_sources(ctx: OmniHawkContext, scope: str) -> List[Dict[str, Any]]:
    allowed = set(_scope_allowed_kinds(scope))
    rows = []
    for source in ctx.progress.list_sources():
        kind = str(source.get("kind", "") or "").strip().lower()
        if kind in allowed:
            rows.append(dict(source))
    rows.sort(key=lambda r: (str(r.get("region", "")), str(r.get("org", "")), str(r.get("name", ""))))
    return rows


def _group_sources_by_region(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        region = str(row.get("region", "global") or "global").strip().lower() or "global"
        grouped.setdefault(region, []).append(row)
    for region in grouped:
        grouped[region].sort(key=lambda r: (str(r.get("org", "")), str(r.get("name", ""))))
    return grouped


def _progress_query_payload(
    *,
    scope: str,
    limit: int,
    q: str,
    source_id: str,
    region: str,
    event_type: str,
    date_from: str,
    date_to: str,
    sort_by: str,
    sort_order: str,
) -> Dict[str, Any]:
    safe_limit = parse_int_value(limit, 1, 500) or 120
    safe_sort_by = str(sort_by or "time").strip().lower()
    if safe_sort_by not in {"time", "source", "title"}:
        safe_sort_by = "time"
    safe_sort_order = str(sort_order or "desc").strip().lower()
    if safe_sort_order not in {"asc", "desc"}:
        safe_sort_order = "desc"
    return {
        "limit": safe_limit,
        "q": str(q or "").strip(),
        "source_id": str(source_id or "").strip(),
        "region": str(region or "").strip(),
        "kind": str(PROGRESS_SCOPE_KIND_MAP.get(scope, PROGRESS_SCOPE_KIND_MAP["frontier"])),
        "event_type": str(event_type or "").strip(),
        "date_from": str(date_from or "").strip(),
        "date_to": str(date_to or "").strip(),
        "sort_by": safe_sort_by,
        "sort_order": safe_sort_order,
    }


def _paper_filters(filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return normalize_panel_filters(filters if isinstance(filters, dict) else {})


@mcp.tool
async def get_project_overview() -> str:
    """Get OmniHawk AI capability overview and current data status."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_rows = []
        for scope in PROGRESS_SCOPES:
            query = _progress_query_payload(
                scope=scope,
                limit=1,
                q="",
                source_id="",
                region="",
                event_type="",
                date_from="",
                date_to="",
                sort_by="time",
                sort_order="desc",
            )
            listed = ctx.progress.list_items(**query)
            scope_rows.append(
                {
                    "scope": scope,
                    "name_zh": PROGRESS_SCOPE_NAME_MAP_ZH.get(scope, scope),
                    "kind": PROGRESS_SCOPE_KIND_MAP.get(scope, ""),
                    "source_count": len(_scope_sources(ctx, scope)),
                    "item_count": int(listed.get("total_filtered", 0) or 0),
                    "updated_at": listed.get("updated_at", ""),
                }
            )

        papers_preview = ctx.papers.list_papers(
            limit=1,
            mode="all",
            sort_by="time",
            sort_order="desc",
            history="all",
            filters={},
            output_language="Chinese",
            include_internal=False,
        )

        return {
            "ok": True,
            "project": "OmniHawk AI",
            "mcp_server": APP_NAME,
            "version": __version__,
            "project_root": str(ctx.project_root),
            "output_dir": str(ctx.output_dir),
            "pages": PAGE_REGISTRY,
            "paper": {
                "count": int((papers_preview.get("stats") or {}).get("total_candidates", 0) or 0),
                "returned": int((papers_preview.get("stats") or {}).get("returned", 0) or 0),
                "db_path": str(papers_preview.get("db_path", "") or ""),
            },
            "progress": scope_rows,
        }

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_pages() -> str:
    """List all independent pages supported by OmniHawk AI."""

    return _json({"ok": True, "pages": PAGE_REGISTRY, "count": len(PAGE_REGISTRY)})


@mcp.tool
async def list_scopes() -> str:
    """List progress scopes (frontier/finance/reports/policy-safety/oss)."""

    rows = []
    for scope in PROGRESS_SCOPES:
        rows.append(
            {
                "scope": scope,
                "name_zh": PROGRESS_SCOPE_NAME_MAP_ZH.get(scope, scope),
                "kinds": _scope_allowed_kinds(scope),
            }
        )
    return _json({"ok": True, "items": rows, "count": len(rows)})


@mcp.tool
async def get_global_settings() -> str:
    """Get global settings shared across pages (LLM, notifications, etc.)."""

    payload = await asyncio.to_thread(lambda: _ensure_context().settings.load())
    return _json({"ok": True, "settings": payload})


@mcp.tool
async def save_global_settings(updates: Dict[str, Any]) -> str:
    """Save global settings. Only known fields are persisted."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        patch = updates if isinstance(updates, dict) else {}
        saved = ctx.settings.save(patch)
        return {"ok": True, "settings": saved}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_scope_sources(scope: str = "frontier") -> str:
    """List data sources for a scope, with region grouping."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        items = _scope_sources(ctx, scope_key)
        return {
            "ok": True,
            "scope": scope_key,
            "name_zh": PROGRESS_SCOPE_NAME_MAP_ZH.get(scope_key, scope_key),
            "allowed_kinds": _scope_allowed_kinds(scope_key),
            "items": items,
            "grouped_by_region": _group_sources_by_region(items),
            "count": len(items),
        }

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_scope_items(
    scope: str = "frontier",
    limit: int = 120,
    q: str = "",
    source_id: str = "",
    region: str = "",
    event_type: str = "",
    date_from: str = "",
    date_to: str = "",
    sort_by: str = "time",
    sort_order: str = "desc",
    enrich: bool = False,
    force_enrich: bool = False,
) -> str:
    """List items in one progress scope with optional LLM Chinese enrichment."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        req = _progress_query_payload(
            scope=scope_key,
            limit=limit,
            q=q,
            source_id=source_id,
            region=region,
            event_type=event_type,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        data = ctx.progress.list_items(**req)
        enrichment: Dict[str, Any] = {
            "ok": True,
            "requested": 0,
            "translated": 0,
            "changed": 0,
            "translated_keys": [],
            "failed": [],
            "skipped": 0,
        }
        if bool(parse_bool_text(enrich, False)):
            items = data.get("items") if isinstance(data.get("items"), list) else []
            keys = [str(row.get("progress_key", "") or "").strip() for row in items if isinstance(row, dict)]
            keys = [key for key in keys if key][:200]
            if keys:
                enrichment = ctx.helper._translate_progress_items(
                    keys=keys,
                    force=bool(parse_bool_text(force_enrich, False)),
                    max_workers=2,
                    allow_skip_unconfigured=True,
                )
                if int(enrichment.get("changed", 0) or 0) > 0:
                    data = ctx.progress.list_items(**req)
        data["scope"] = scope_key
        data["name_zh"] = PROGRESS_SCOPE_NAME_MAP_ZH.get(scope_key, scope_key)
        data["kind"] = req["kind"]
        data["enrichment"] = enrichment
        return data

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def fetch_scope_items(
    scope: str = "frontier",
    max_per_source: int = 20,
    source_ids: Optional[List[str]] = None,
    enrich: bool = True,
    force_enrich: bool = False,
) -> str:
    """Fetch latest items for one scope, then optionally enrich Chinese card fields."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        safe_max = parse_int_value(max_per_source, 1, 120) or 20
        requested_ids = _clean_text_list(source_ids)
        allowed_ids = ctx.helper._resolve_progress_source_ids(scope_key, requested_ids)
        result = ctx.progress.fetch(max_per_source=safe_max, source_ids=allowed_ids)

        changed_keys: List[str] = []
        for key in list(result.get("added_keys", []) or []) + list(result.get("updated_keys", []) or []):
            text = str(key or "").strip()
            if text and text not in changed_keys:
                changed_keys.append(text)

        enrichment: Dict[str, Any] = {
            "ok": True,
            "requested": 0,
            "translated": 0,
            "changed": 0,
            "translated_keys": [],
            "failed": [],
            "skipped": 0,
        }
        if bool(parse_bool_text(enrich, True)) and changed_keys:
            enrichment = ctx.helper._translate_progress_items(
                keys=changed_keys,
                force=bool(parse_bool_text(force_enrich, False)),
                max_workers=2,
                allow_skip_unconfigured=True,
            )

        result["scope"] = scope_key
        result["name_zh"] = PROGRESS_SCOPE_NAME_MAP_ZH.get(scope_key, scope_key)
        result["kind"] = str(PROGRESS_SCOPE_KIND_MAP.get(scope_key, PROGRESS_SCOPE_KIND_MAP["frontier"]))
        result["requested_source_ids"] = requested_ids
        result["effective_source_ids"] = allowed_ids
        result["enrichment"] = enrichment
        return result

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def get_scope_settings(scope: str = "frontier") -> str:
    """Get persisted settings for one scope."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        settings = ctx.progress_page_settings.get_scope(scope_key)
        return {"ok": True, "scope": scope_key, "settings": settings}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def save_scope_settings(scope: str = "frontier", updates: Optional[Dict[str, Any]] = None) -> str:
    """Save scope-level settings (independent per page)."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        patch = dict(updates) if isinstance(updates, dict) else {}
        if "query" in patch:
            patch["query"] = normalize_progress_filters(patch.get("query") if isinstance(patch.get("query"), dict) else {})
        if "source_ids" in patch:
            patch["source_ids"] = _clean_text_list(patch.get("source_ids") if isinstance(patch.get("source_ids"), list) else [])
        saved = ctx.progress_page_settings.save_scope(scope_key, patch)
        return {"ok": True, "scope": scope_key, "settings": saved}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_scope_subscriptions(scope: str = "frontier") -> str:
    """List subscriptions for one scope."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        items = ctx.progress_subscriptions.list(scope_key)
        return {"ok": True, "scope": scope_key, "items": items, "count": len(items)}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def upsert_scope_subscription(
    scope: str = "frontier",
    name: str = "",
    channel: str = "feishu",
    filters: Optional[Dict[str, Any]] = None,
    enabled: bool = True,
    limit: int = 120,
    sub_id: str = "",
) -> str:
    """Create or update one scope subscription."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        safe_channel = _normalize_channel(channel)
        safe_filters = normalize_progress_filters(filters if isinstance(filters, dict) else {})
        safe_limit = parse_int_value(limit, 1, 500) or 120
        saved = ctx.progress_subscriptions.upsert(
            scope=scope_key,
            name=str(name or "").strip(),
            channel=safe_channel,
            filters=safe_filters,
            enabled=bool(parse_bool_text(enabled, True)),
            limit=safe_limit,
            sub_id=str(sub_id or "").strip(),
        )
        items = ctx.progress_subscriptions.list(scope_key)
        current = None
        for item in items:
            if str(item.get("id", "") or "") == str(saved.get("id", "") or ""):
                current = item
                break
        return {"ok": True, "scope": scope_key, "item": current, "items": items, "count": len(items)}

    try:
        payload = await asyncio.to_thread(worker)
        return _json(payload)
    except ValueError as exc:
        return _json({"ok": False, "error": str(exc)})


@mcp.tool
async def delete_scope_subscription(sub_id: str) -> str:
    """Delete one scope subscription by id."""

    def worker() -> Dict[str, Any]:
        key = str(sub_id or "").strip()
        if not key:
            return {"ok": False, "error": "id is required"}
        deleted = _ensure_context().progress_subscriptions.delete(key)
        return {"ok": bool(deleted), "deleted": bool(deleted), "id": key}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def run_scope_subscriptions(scope: str = "frontier", sub_id: str = "") -> str:
    """Run scope subscriptions immediately and push matched items."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        scope_key = _normalize_scope(scope)
        return ctx.helper._run_progress_subscriptions(scope_key, sub_id=str(sub_id or "").strip())

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_papers(
    limit: int = 100,
    mode: str = "all",
    sort_by: str = "score",
    sort_order: str = "desc",
    history: str = "all",
    filters: Optional[Dict[str, Any]] = None,
    output_language: str = "Chinese",
    enrich: bool = True,
    force_enrich: bool = False,
    include_internal: bool = False,
) -> str:
    """List papers from Paper Radar, with optional bilingual enrichment."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        safe_limit = parse_int_value(limit, 1, 500) or 100
        safe_mode = str(mode or "all").strip().lower()
        if safe_mode not in {"all", "favorites", "ignored"}:
            safe_mode = "all"
        safe_sort_by = str(sort_by or "score").strip().lower()
        if safe_sort_by not in {"score", "time", "title"}:
            safe_sort_by = "score"
        safe_sort_order = str(sort_order or "desc").strip().lower()
        if safe_sort_order not in {"asc", "desc"}:
            safe_sort_order = "desc"
        safe_history = str(history or "all").strip().lower()
        if safe_history not in {"all", "latest"}:
            safe_history = "all"
        lang = normalize_analysis_language(output_language, default="Chinese")

        list_req = {
            "limit": safe_limit,
            "mode": safe_mode,
            "sort_by": safe_sort_by,
            "sort_order": safe_sort_order,
            "history": safe_history,
            "filters": _paper_filters(filters),
            "output_language": lang,
            "include_internal": bool(parse_bool_text(include_internal, False)),
        }
        data = ctx.papers.list_papers(**list_req)

        papers = data.get("papers") if isinstance(data.get("papers"), list) else []
        keys = [str(row.get("paper_key", "") or "").strip() for row in papers if isinstance(row, dict)]
        keys = [key for key in keys if key][:20]

        enrichment: Dict[str, Any] = {
            "ok": True,
            "requested": len(keys),
            "translated": 0,
            "changed": 0,
            "translated_keys": [],
            "failed": [],
            "skipped": 0,
        }
        if bool(parse_bool_text(enrich, True)) and keys:
            enrichment = ctx.helper._translate_paper_items(
                keys=keys,
                output_language=lang,
                force=bool(parse_bool_text(force_enrich, False)),
                include_deep=False,
                max_workers=1,
                allow_skip_unconfigured=True,
            )
            if int(enrichment.get("changed", 0) or 0) > 0:
                data = ctx.papers.list_papers(**list_req)
                papers = data.get("papers") if isinstance(data.get("papers"), list) else []

        if not bool(parse_bool_text(include_internal, False)):
            for row in papers:
                if isinstance(row, dict):
                    row.pop("_db_path", None)

        data["enrichment"] = enrichment
        data["output_language"] = lang
        return data

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def get_paper_detail(
    paper_key: str,
    output_language: str = "Chinese",
    enrich: bool = True,
    force_enrich: bool = False,
) -> str:
    """Get one paper detail card by paper_key."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        key = str(paper_key or "").strip()
        if not key:
            return {"ok": False, "error": "paper_key is required"}

        lang = normalize_analysis_language(output_language, default="Chinese")
        enrichment: Dict[str, Any] = {
            "ok": True,
            "requested": 1,
            "translated": 0,
            "changed": 0,
            "translated_keys": [],
            "failed": [],
            "skipped": 0,
        }
        if bool(parse_bool_text(enrich, True)):
            enrichment = ctx.helper._translate_paper_items(
                keys=[key],
                output_language=lang,
                force=bool(parse_bool_text(force_enrich, False)),
                include_deep=True,
                max_workers=1,
                allow_skip_unconfigured=True,
            )

        paper = ctx.papers.get_paper_detail_by_key(key, output_language=lang)
        if not paper:
            return {"ok": False, "error": "paper not found", "paper_key": key}
        return {"ok": True, "paper_key": key, "paper": paper, "enrichment": enrichment}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def deep_analyze_paper(
    paper_key: str,
    focus: str = "",
    question: str = "",
    output_language: str = "",
    force: bool = False,
) -> str:
    """Run deep analysis for one paper and persist result."""

    def worker() -> Dict[str, Any]:
        key = str(paper_key or "").strip()
        if not key:
            return {"ok": False, "error": "paper_key is required"}
        lang = (
            normalize_analysis_language(output_language, default="Chinese")
            if str(output_language or "").strip()
            else ""
        )
        return _ensure_context().deep_analyzer.analyze_selected_paper(
            paper_key=key,
            focus=str(focus or "").strip(),
            question=str(question or "").strip(),
            output_language=lang,
            force=bool(parse_bool_text(force, False)),
        )

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def set_paper_action(
    paper_key: str,
    favorite: Optional[bool] = None,
    ignored: Optional[bool] = None,
    note: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Set user action on a paper card (favorite/ignored/note/tags)."""

    def worker() -> Dict[str, Any]:
        key = str(paper_key or "").strip()
        if not key:
            return {"ok": False, "error": "paper_key is required"}

        def opt_bool(value: Optional[bool]) -> Optional[bool]:
            if value is None:
                return None
            return bool(parse_bool_text(value, False))

        cleaned_tags = _clean_text_list(tags if isinstance(tags, list) else []) if tags is not None else None
        try:
            action = _ensure_context().actions.set_action(
                paper_key=key,
                favorite=opt_bool(favorite),
                ignored=opt_bool(ignored),
                note=None if note is None else str(note),
                tags=cleaned_tags,
            )
            return {"ok": True, "paper_key": key, "action": action}
        except ValueError as exc:
            return {"ok": False, "error": str(exc), "paper_key": key}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def list_paper_subscriptions() -> str:
    """List all saved paper subscriptions."""

    def worker() -> Dict[str, Any]:
        payload = _ensure_context().paper_subscriptions.load()
        items = payload.get("items") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []
        return {"ok": True, "items": items, "count": len(items)}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def upsert_paper_subscription(
    name: str = "",
    channel: str = "feishu",
    filters: Optional[Dict[str, Any]] = None,
    enabled: bool = True,
    sub_id: str = "",
    mode: str = "all",
    sort_by: str = "score",
    sort_order: str = "desc",
    history: str = "all",
    limit: int = 120,
) -> str:
    """Create or update one paper subscription."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        safe_channel = _normalize_channel(channel)
        safe_mode = str(mode or "all").strip().lower()
        if safe_mode not in {"all", "favorites", "ignored"}:
            safe_mode = "all"
        safe_sort_by = str(sort_by or "score").strip().lower()
        if safe_sort_by not in {"score", "time", "title"}:
            safe_sort_by = "score"
        safe_sort_order = str(sort_order or "desc").strip().lower()
        if safe_sort_order not in {"asc", "desc"}:
            safe_sort_order = "desc"
        safe_history = str(history or "all").strip().lower()
        if safe_history not in {"all", "latest"}:
            safe_history = "all"
        safe_limit = parse_int_value(limit, 1, 500) or 120

        saved = ctx.paper_subscriptions.upsert(
            name=str(name or "").strip(),
            channel=safe_channel,
            filters=_paper_filters(filters),
            enabled=bool(parse_bool_text(enabled, True)),
            sub_id=str(sub_id or "").strip(),
            mode=safe_mode,
            sort_by=safe_sort_by,
            sort_order=safe_sort_order,
            history=safe_history,
            limit=safe_limit,
        )

        payload = ctx.paper_subscriptions.load()
        items = payload.get("items") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []
        current = None
        for item in items:
            if str(item.get("id", "") or "") == str(saved.get("id", "") or ""):
                current = item
                break
        return {"ok": True, "item": current, "items": items, "count": len(items)}

    try:
        payload = await asyncio.to_thread(worker)
        return _json(payload)
    except ValueError as exc:
        return _json({"ok": False, "error": str(exc)})


@mcp.tool
async def delete_paper_subscription(sub_id: str) -> str:
    """Delete one paper subscription by id."""

    def worker() -> Dict[str, Any]:
        key = str(sub_id or "").strip()
        if not key:
            return {"ok": False, "error": "id is required"}
        deleted = _ensure_context().paper_subscriptions.delete(key)
        return {"ok": bool(deleted), "deleted": bool(deleted), "id": key}

    payload = await asyncio.to_thread(worker)
    return _json(payload)


@mcp.tool
async def run_paper_subscriptions(sub_id: str = "") -> str:
    """Run paper subscriptions immediately and push matched results."""

    def worker() -> Dict[str, Any]:
        ctx = _ensure_context()
        payload = ctx.paper_subscriptions.load()
        items = payload.get("items") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []
        target_id = str(sub_id or "").strip()
        if target_id:
            targets = [row for row in items if str(row.get("id", "") or "") == target_id]
        else:
            targets = [row for row in items if bool(row.get("enabled", True))]
        if not targets:
            return {"ok": False, "error": "no subscription to run", "results": []}
        results = [ctx.helper._run_subscription(row) for row in targets]
        success_count = sum(1 for row in results if row.get("ok"))
        return {
            "ok": success_count == len(results),
            "results": results,
            "success_count": success_count,
            "total": len(results),
        }

    payload = await asyncio.to_thread(worker)
    return _json(payload)


def run_server(
    project_root: Optional[str] = None,
    transport: str = "stdio",
    host: str = "0.0.0.0",
    port: int = 3333,
    output_dir: Optional[str] = None,
) -> None:
    """Start OmniHawk MCP server.

    Args:
        project_root: repo root path, optional.
        transport: stdio or http.
        host: http host.
        port: http port.
        output_dir: output directory, optional.
    """

    _configure_context_paths(project_root=project_root, output_dir=output_dir)
    ctx = _ensure_context()

    print()
    print("=" * 68)
    print("  OmniHawk AI MCP Server")
    print("=" * 68)
    print(f"  Version: {__version__}")
    print(f"  Transport: {transport}")
    print(f"  Project root: {ctx.project_root}")
    print(f"  Output dir: {ctx.output_dir}")
    if transport == "http":
        print(f"  Endpoint: http://{host}:{port}/mcp")
    print()
    print("  Tool groups:")
    print("    - Project introspection: get_project_overview, list_pages, list_scopes")
    print("    - Settings: get_global_settings, save_global_settings, get_scope_settings, save_scope_settings")
    print("    - Progress scope data: list_scope_sources, list_scope_items, fetch_scope_items")
    print("    - Progress subscriptions: list_scope_subscriptions, upsert_scope_subscription, delete_scope_subscription, run_scope_subscriptions")
    print("    - Paper radar: list_papers, get_paper_detail, deep_analyze_paper, set_paper_action")
    print("    - Paper subscriptions: list_paper_subscriptions, upsert_paper_subscription, delete_paper_subscription, run_paper_subscriptions")
    print("=" * 68)
    print()

    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    if transport == "http":
        mcp.run(transport="http", host=host, port=port, path="/mcp")
        return
    raise ValueError(f"unsupported transport: {transport}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OmniHawk AI MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m mcp_server.server --transport stdio\n"
            "  python -m mcp_server.server --transport http --host 0.0.0.0 --port 3333\n"
        ),
    )
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=3333)
    parser.add_argument("--project-root", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    run_server(
        project_root=str(args.project_root or "").strip() or None,
        transport=args.transport,
        host=args.host,
        port=int(args.port),
        output_dir=str(args.output_dir or "").strip() or None,
    )


if __name__ == "__main__":
    main()


