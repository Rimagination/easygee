#!/usr/bin/env python3
"""Small stdio MCP wrapper around EasyGEE's existing scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "easygee"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
DOC_ROOTS = (PLUGIN_ROOT / "skills", PLUGIN_ROOT / "extras")
RESOURCE_PREFIX = "easygee://docs/"
SERVER_NAME = "easygee"
SERVER_VERSION = "0.2.0"

sys.path.insert(0, str(SCRIPT_ROOT))
import easygee_project  # noqa: E402

# MCP clients read stderr as UTF-8; localized Windows consoles default to e.g. GBK.
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

FRAME_MODE: str | None = None


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: list[dict[str, Any]] = [
    {
        "name": "easygee_check_environment",
        "description": "Check local Earth Engine, geemap, and optional project initialization readiness without printing credentials.",
        "inputSchema": _schema(
            {
                "project": {"type": "string", "description": "Optional Google Cloud / Earth Engine project id."},
                "initialize": {"type": "boolean", "description": "Try ee.Initialize(project=...) without running OAuth."},
            }
        ),
    },
    {
        "name": "easygee_auth_plan",
        "description": "Return a credential-safe Earth Engine/geemap authorization plan. Does not run OAuth.",
        "inputSchema": _schema(
            {
                "project": {"type": "string", "description": "Google Cloud / Earth Engine project id."},
                "mode": {
                    "type": "string",
                    "enum": ["auto", "localhost", "notebook", "gcloud", "colab", "service-account"],
                    "description": "Earth Engine auth mode.",
                },
                "include_auth_snippet": {"type": "boolean", "description": "Include ee.Authenticate(...) setup snippet."},
            }
        ),
    },
    {
        "name": "easygee_search_catalog",
        "description": "Search 5,000+ official/community GEE records by exact id, name, bilingual theme, or task with provenance- and deprecation-aware ranking.",
        "inputSchema": _schema(
            {
                "query": {"type": "string", "description": "Dataset need, task prompt, or analysis goal."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Maximum candidate count."},
                "mode": {"type": "string", "enum": ["auto", "exact", "theme", "task"], "description": "Optional query mode override."},
                "source": {"type": "string", "enum": ["official", "community", "curated"], "description": "Optional provenance filter."},
                "provider": {"type": "string", "description": "Optional provider substring filter."},
                "category": {"type": "string", "description": "Optional category substring filter."},
                "kind": {"type": "string", "description": "Optional image/image_collection/table type filter."},
                "max_resolution_m": {"type": "number", "minimum": 0, "description": "Require a known resolution no coarser than this many meters."},
                "include_deprecated": {"type": "boolean", "description": "Include deprecated products; false by default."},
            },
            ["query"],
        ),
    },
    {
        "name": "easygee_recommend_datasets",
        "description": "Recommend a role-based GEE dataset bundle for a bilingual analysis task, such as flood hazard + terrain + rainfall + exposure.",
        "inputSchema": _schema(
            {
                "task": {"type": "string", "description": "Analysis outcome or task in Chinese or English."},
                "limit_per_role": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Maximum candidates for each task role."},
            },
            ["task"],
        ),
    },
    {
        "name": "easygee_compare_datasets",
        "description": "Compare provenance, type, provider, category, resolution, dates, license, and deprecation metadata for GEE dataset ids.",
        "inputSchema": _schema(
            {
                "ids": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 12, "description": "Dataset ids to compare."},
            },
            ["ids"],
        ),
    },
    {
        "name": "easygee_verify_dataset",
        "description": "Verify a dataset id in the merged catalog and optionally probe the live Earth Engine API without starting OAuth.",
        "inputSchema": _schema(
            {
                "id": {"type": "string", "description": "Earth Engine dataset or asset id."},
                "live": {"type": "boolean", "description": "Also call ee.data.getAsset using existing credentials."},
                "project": {"type": "string", "description": "Optional Earth Engine project for the live check."},
            },
            ["id"],
        ),
    },
    {
        "name": "easygee_quota_summary",
        "description": "Show Earth Engine quota totals and optional recent usage for a Cloud project or quotas Console URL.",
        "inputSchema": _schema(
            {
                "project": {"type": "string", "description": "Google Cloud project id or number."},
                "console_url": {"type": "string", "description": "Optional Cloud Console quotas URL."},
                "include_usage": {"type": "boolean", "description": "Query recent Cloud Monitoring usage metrics."},
                "minutes": {"type": "integer", "minimum": 1, "maximum": 1440, "description": "Lookback window for usage metrics."},
                "no_live": {"type": "boolean", "description": "Skip live Google Cloud API calls and use fallback guidance."},
            }
        ),
    },
    {
        "name": "easygee_create_map_console",
        "description": "Generate the EasyGEE local browser map console HTML. This does not start a long-running server.",
        "inputSchema": _schema(
            {
                "project": {"type": "string", "description": "Optional Earth Engine / Google Cloud project id."},
                "title": {"type": "string", "description": "Map console title."},
                "lat": {"type": "number", "description": "Initial latitude."},
                "lon": {"type": "number", "description": "Initial longitude."},
                "zoom": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Initial zoom."},
                "default_layer": {"type": "string", "description": "Default layer id such as ndvi, s2-rgb, dynamic-world, jrc-water, or srtm."},
                "live": {"type": "boolean", "description": "Pre-populate live Earth Engine demo layers."},
                "sample": {"type": "boolean", "description": "Generate offline sample console without Earth Engine calls."},
                "output": {"type": "string", "description": "Optional output HTML path under the EasyGEE workspace or export directory."},
            }
        ),
    },
    {
        "name": "easygee_preview_plan",
        "description": "Return a local preview server plan for an EasyGEE/geemap HTML artifact without starting the server.",
        "inputSchema": _schema(
            {
                "target": {"type": "string", "description": "Optional HTML file or directory to preview."},
                "title": {"type": "string", "description": "Placeholder title when no target is supplied."},
            }
        ),
    },
]


def _read_message() -> dict[str, Any] | None:
    global FRAME_MODE
    first = sys.stdin.buffer.readline()
    if not first:
        return None
    if first.startswith(b"Content-Length:"):
        FRAME_MODE = FRAME_MODE or "headers"
        length = int(first.decode("ascii").split(":", 1)[1].strip())
        while True:
            line = sys.stdin.buffer.readline()
            if line in (b"\r\n", b"\n", b""):
                break
        payload = sys.stdin.buffer.read(length)
        return json.loads(payload.decode("utf-8"))
    FRAME_MODE = FRAME_MODE or "lines"
    return json.loads(first.decode("utf-8"))


def _write_message(message: dict[str, Any]) -> None:
    payload = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if FRAME_MODE == "headers":
        sys.stdout.buffer.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
        sys.stdout.buffer.write(payload)
    else:
        sys.stdout.buffer.write(payload + b"\n")
    sys.stdout.buffer.flush()


def _response(request_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = result
    _write_message(message)


def _tool_text(text: str, *, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def _safe_output_path(raw: str | None) -> Path:
    workspace = easygee_project.workspace_root()
    if not raw:
        return workspace / "map-console" / "index.html"
    candidate = Path(raw).expanduser().resolve()
    allowed_roots = [root.resolve() for root in (workspace, easygee_project.export_root()) if root]
    if not any(candidate == root or root in candidate.parents for root in allowed_roots):
        raise ValueError(f"output must be under: {', '.join(str(root) for root in allowed_roots)}")
    if candidate.suffix.lower() != ".html":
        raise ValueError("output must be an .html file")
    return candidate


def _script_python() -> str:
    """Interpreter with earthengine-api/geemap; the server itself only needs the stdlib."""
    configured = easygee_project.configured_python()
    if not configured:
        return sys.executable
    if not Path(configured).exists():
        raise ValueError(f"configured EasyGEE Python not found: {configured} (set EASYGEE_PYTHON or pythonPath in settings.json)")
    return configured


def _doc_files() -> list[Path]:
    return sorted(path for root in DOC_ROOTS if root.exists() for path in root.rglob("*.md"))


def _doc_uri(path: Path) -> str:
    return RESOURCE_PREFIX + path.relative_to(PLUGIN_ROOT).as_posix()


def list_resources() -> dict[str, Any]:
    resources = []
    for path in _doc_files():
        name = path.relative_to(PLUGIN_ROOT).as_posix()
        entry: dict[str, Any] = {"uri": _doc_uri(path), "name": name, "mimeType": "text/markdown"}
        if path.name == "SKILL.md":
            entry["description"] = f"Skill entry point: {path.parent.name}"
        resources.append(entry)
    return {"resources": resources}


def read_resource(uri: str) -> dict[str, Any]:
    if not uri.startswith(RESOURCE_PREFIX):
        raise ValueError(f"unknown resource: {uri}")
    path = (PLUGIN_ROOT / uri[len(RESOURCE_PREFIX):]).resolve()
    if path.suffix != ".md" or not any(root.resolve() in path.parents for root in DOC_ROOTS) or not path.is_file():
        raise ValueError(f"unknown resource: {uri}")
    return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": path.read_text(encoding="utf-8")}]}


def _run_script(script: str, args: list[str], timeout: int = 120) -> dict[str, Any]:
    script_path = (SCRIPT_ROOT / script).resolve()
    if SCRIPT_ROOT.resolve() not in script_path.parents or script_path.suffix != ".py":
        raise ValueError(f"script is not allowlisted: {script}")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [_script_python(), str(script_path), *args],
        cwd=str(SKILL_ROOT),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _format_run(label: str, run: dict[str, Any]) -> dict[str, Any]:
    text = run["stdout"] or ""
    if run["stderr"]:
        text = f"{text}\n\nstderr:\n{run['stderr']}".strip()
    if not text:
        text = f"{label} completed with exit code {run['returncode']}."
    return _tool_text(text, is_error=run["returncode"] != 0)


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "easygee_check_environment":
        args = ["--json"]
        if arguments.get("project"):
            args += ["--project", str(arguments["project"])]
        if arguments.get("initialize"):
            args.append("--initialize")
        return _format_run(name, _run_script("check_gee_geemap.py", args))

    if name == "easygee_auth_plan":
        args = ["--json"]
        if arguments.get("project"):
            args += ["--project", str(arguments["project"])]
        args += ["--mode", str(arguments.get("mode") or "auto")]
        if arguments.get("include_auth_snippet"):
            args.append("--include-auth-snippet")
        return _format_run(name, _run_script("ee_auth_workflow.py", args))

    if name == "easygee_search_catalog":
        args = ["search", str(arguments["query"]), "--limit", str(int(arguments.get("limit") or 8))]
        if arguments.get("mode"):
            args += ["--mode", str(arguments["mode"])]
        for key, flag in (("source", "--source"), ("provider", "--provider"), ("category", "--category"), ("kind", "--kind"), ("max_resolution_m", "--max-resolution-m")):
            if arguments.get(key) is not None:
                args += [flag, str(arguments[key])]
        if arguments.get("include_deprecated"):
            args.append("--include-deprecated")
        return _format_run(name, _run_script("dataset_catalog_engine.py", args, timeout=180))

    if name == "easygee_recommend_datasets":
        args = ["recommend", str(arguments["task"]), "--limit-per-role", str(int(arguments.get("limit_per_role") or 2))]
        return _format_run(name, _run_script("dataset_catalog_engine.py", args, timeout=180))

    if name == "easygee_compare_datasets":
        ids = arguments.get("ids") or []
        if not isinstance(ids, list) or len(ids) < 2:
            raise ValueError("ids must contain at least two dataset ids")
        return _format_run(name, _run_script("dataset_catalog_engine.py", ["compare", *[str(value) for value in ids]], timeout=180))

    if name == "easygee_verify_dataset":
        args = ["verify", str(arguments["id"])]
        if arguments.get("live"):
            args.append("--live")
        if arguments.get("project"):
            args += ["--project", str(arguments["project"])]
        return _format_run(name, _run_script("dataset_catalog_engine.py", args, timeout=180))

    if name == "easygee_quota_summary":
        args = ["--json"]
        if arguments.get("console_url"):
            args.append(str(arguments["console_url"]))
        if arguments.get("project"):
            args += ["--project", str(arguments["project"])]
        if arguments.get("include_usage"):
            args.append("--include-usage")
        if arguments.get("minutes"):
            args += ["--minutes", str(int(arguments["minutes"]))]
        if arguments.get("no_live"):
            args.append("--no-live")
        return _format_run(name, _run_script("show_ee_quotas.py", args, timeout=180))

    if name == "easygee_create_map_console":
        output = _safe_output_path(arguments.get("output"))
        output.parent.mkdir(parents=True, exist_ok=True)
        args = ["--output", str(output), "--json"]
        if arguments.get("project"):
            args += ["--project", str(arguments["project"])]
        if arguments.get("title"):
            args += ["--title", str(arguments["title"])]
        for key, flag in (("lat", "--lat"), ("lon", "--lon"), ("zoom", "--zoom")):
            if arguments.get(key) is not None:
                args += [flag, str(arguments[key])]
        if arguments.get("default_layer"):
            args += ["--default-layer", str(arguments["default_layer"])]
        if arguments.get("live"):
            args.append("--live")
        if arguments.get("sample"):
            args.append("--sample")
        return _format_run(name, _run_script("create_map_console.py", args, timeout=240))

    if name == "easygee_preview_plan":
        args = ["--json"]
        if arguments.get("target"):
            args.append(str(arguments["target"]))
        if arguments.get("title"):
            args += ["--title", str(arguments["title"])]
        return _format_run(name, _run_script("serve_map_preview.py", args))

    raise ValueError(f"unknown tool: {name}")


def main() -> int:
    while True:
        request = _read_message()
        if request is None:
            return 0
        method = request.get("method")
        request_id = request.get("id")
        try:
            if method == "initialize":
                params = request.get("params") or {}
                _response(
                    request_id,
                    {
                        "protocolVersion": params.get("protocolVersion") or "2025-06-18",
                        "capabilities": {"tools": {}, "resources": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    },
                )
            elif "id" not in request:
                continue  # notifications never get a response
            elif method == "ping":
                _response(request_id, {})
            elif method == "tools/list":
                _response(request_id, {"tools": TOOLS})
            elif method == "resources/list":
                _response(request_id, list_resources())
            elif method == "resources/read":
                _response(request_id, read_resource(str((request.get("params") or {}).get("uri"))))
            elif method == "tools/call":
                params = request.get("params") or {}
                _response(request_id, call_tool(str(params.get("name")), params.get("arguments") or {}))
            else:
                _response(request_id, error={"code": -32601, "message": f"Method not found: {method}"})
        except Exception as exc:
            _response(request_id, error={"code": -32000, "message": str(exc)})


if __name__ == "__main__":
    raise SystemExit(main())
