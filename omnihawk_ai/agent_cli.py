# coding=utf-8
"""OmniHawk AI agent-oriented CLI.

This CLI exposes the same tool capabilities as the MCP server, but through
direct local command invocation. It is designed for:
- terminal automation
- CI/CD scripts
- agent workflows that prefer JSON stdin/stdout over MCP transport
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp_server import server as mcp_server


TOOL_NAMES: List[str] = [
    "get_project_overview",
    "list_pages",
    "list_scopes",
    "get_global_settings",
    "save_global_settings",
    "get_schedule_settings",
    "set_schedule_interval",
    "set_schedule_cron",
    "list_scope_sources",
    "list_scope_items",
    "fetch_scope_items",
    "get_scope_settings",
    "save_scope_settings",
    "list_scope_subscriptions",
    "upsert_scope_subscription",
    "delete_scope_subscription",
    "run_scope_subscriptions",
    "list_papers",
    "get_paper_detail",
    "deep_analyze_paper",
    "set_paper_action",
    "list_paper_subscriptions",
    "upsert_paper_subscription",
    "delete_paper_subscription",
    "run_paper_subscriptions",
]


def _ensure_utf8_io() -> None:
    """Best-effort UTF-8 stdout/stderr on Windows consoles."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _dump(payload: Dict[str, Any], compact: bool = False) -> str:
    if compact:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def _load_json_object(text: str, source: str) -> Dict[str, Any]:
    try:
        obj = json.loads(text or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"{source} must be a JSON object")
    return obj


def _load_call_args(args_json: str, args_file: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if args_file:
        path = Path(args_file).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"args file not found: {path}")
        payload.update(_load_json_object(path.read_text(encoding="utf-8-sig"), f"file:{path}"))
    if args_json.strip():
        payload.update(_load_json_object(args_json, "inline JSON"))
    return payload


def _collect_tools() -> Dict[str, Any]:
    registry: Dict[str, Any] = {}
    for name in TOOL_NAMES:
        tool = getattr(mcp_server, name, None)
        fn = getattr(tool, "fn", None)
        if callable(fn):
            registry[name] = tool
    return registry


def _serializable_default(value: Any) -> Any:
    if value is inspect._empty:
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, dict)):
        return value
    return repr(value)


def _list_tools(registry: Dict[str, Any], compact: bool = False) -> int:
    tools: List[Dict[str, Any]] = []
    for name in TOOL_NAMES:
        tool = registry.get(name)
        if not tool:
            continue
        fn = getattr(tool, "fn")
        sig = inspect.signature(fn)
        params = []
        for p in sig.parameters.values():
            params.append(
                {
                    "name": p.name,
                    "required": p.default is inspect._empty,
                    "default": _serializable_default(p.default),
                    "annotation": str(p.annotation) if p.annotation is not inspect._empty else "",
                    "kind": str(p.kind).replace("Parameter.", ""),
                }
            )
        tools.append(
            {
                "name": name,
                "doc": (str(getattr(tool, "description", "") or "").strip() or (inspect.getdoc(fn) or "").strip()),
                "params": params,
            }
        )
    print(
        _dump(
            {"ok": True, "tool_count": len(tools), "tools": tools},
            compact=compact,
        )
    )
    return 0


async def _invoke_tool(tool: Any, kwargs: Dict[str, Any]) -> Any:
    fn = getattr(tool, "fn", None)
    if not callable(fn):
        raise TypeError("tool has no callable function")
    return await fn(**kwargs)


def _print_result(raw: Any, compact: bool = False) -> None:
    if isinstance(raw, str):
        text = raw.strip()
        if compact:
            try:
                print(_dump(json.loads(text), compact=True))
                return
            except Exception:
                pass
        print(text)
        return
    if isinstance(raw, dict):
        print(_dump(raw, compact=compact))
        return
    print(_dump({"ok": True, "result": raw}, compact=compact))


def main() -> None:
    _ensure_utf8_io()
    parser = argparse.ArgumentParser(
        description="OmniHawk AI Agent CLI (MCP-compatible local tool invoker)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  omnihawk-ai-cli tools\n"
            "  omnihawk-ai-cli call get_project_overview\n"
            "  omnihawk-ai-cli call list_scope_items --args '{\"scope\":\"market_finance\",\"limit\":20}'\n"
            "  omnihawk-ai-cli call upsert_scope_subscription --args-file ./payload.json\n"
            "  omnihawk-ai-cli call set_schedule_interval --args '{\"interval_minutes\":20}'\n"
            "  omnihawk-ai-cli call set_schedule_cron --args '{\"cron_expr\":\"*/15 * * * *\"}'\n"
            "  omnihawk-ai-cli --project-root . --output-dir ./output call list_papers --args '{\"limit\":5}'\n"
        ),
    )
    parser.add_argument("--project-root", default="", help="Override OmniHawk project root path")
    parser.add_argument("--output-dir", default="", help="Override output directory path")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")

    sub = parser.add_subparsers(dest="command", required=True)
    tools_cmd = sub.add_parser("tools", help="List all available CLI tools")
    tools_cmd.add_argument(
        "--compact",
        dest="sub_compact",
        action="store_true",
        help="Emit compact JSON for this command",
    )

    call = sub.add_parser("call", help="Invoke one tool")
    call.add_argument("tool", help="Tool name (same as MCP tool)")
    call.add_argument(
        "--args",
        default="{}",
        help='Inline JSON object for tool args, e.g. \'{"scope":"frontier","limit":20}\'',
    )
    call.add_argument("--args-file", default="", help="Path to JSON file for tool args")
    call.add_argument(
        "--compact",
        dest="sub_compact",
        action="store_true",
        help="Emit compact JSON for this command",
    )

    args = parser.parse_args()
    compact = bool(getattr(args, "compact", False) or getattr(args, "sub_compact", False))
    registry = _collect_tools()
    mcp_server._configure_context_paths(
        project_root=str(args.project_root or "").strip() or None,
        output_dir=str(args.output_dir or "").strip() or None,
    )

    if args.command == "tools":
        raise SystemExit(_list_tools(registry, compact=compact))

    tool_name = str(args.tool or "").strip()
    fn = registry.get(tool_name)
    if fn is None:
        print(
            _dump(
                {
                    "ok": False,
                    "error": f"unknown tool: {tool_name}",
                    "hint": "run `omnihawk-ai-cli tools` to list available tools",
                },
                compact=compact,
            )
        )
        raise SystemExit(2)

    try:
        kwargs = _load_call_args(args.args, args.args_file)
        result = asyncio.run(_invoke_tool(fn, kwargs))
        _print_result(result, compact=compact)
        raise SystemExit(0)
    except TypeError as exc:
        print(
            _dump(
                {
                    "ok": False,
                    "error": f"invalid arguments for {tool_name}: {exc}",
                    "hint": "run `omnihawk-ai-cli tools` and check this tool's params",
                },
                compact=compact,
            )
        )
        raise SystemExit(2)
    except ValueError as exc:
        print(_dump({"ok": False, "error": str(exc)}, compact=compact))
        raise SystemExit(2)
    except Exception as exc:
        print(_dump({"ok": False, "error": f"tool execution failed: {exc}"}, compact=compact))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
