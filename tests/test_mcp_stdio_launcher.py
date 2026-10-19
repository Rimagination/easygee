from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MCP_CONFIG = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["easygee"]
COMMAND = shutil.which(MCP_CONFIG["command"])
TIMEOUT = 30.0


def launcher_cwd() -> Path:
    configured = MCP_CONFIG.get("cwd")
    return (ROOT / str(configured)).resolve() if configured else Path(tempfile.gettempdir())


def run_launcher(payload: bytes, tmp_path: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    if not COMMAND:
        pytest.skip(f"{MCP_CONFIG['command']} is required for the MCP launcher test")
    process_env = os.environ.copy()
    process_env["EASYGEE_USER_CONFIG_DIR"] = str(tmp_path / "config")
    process_env.pop("EASYGEE_WORKSPACE", None)
    if env:
        process_env.update(env)
    return subprocess.run(
        [COMMAND, *MCP_CONFIG["args"]],
        cwd=launcher_cwd(),
        env=process_env,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=TIMEOUT,
        check=False,
    )


INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "easygee-regression", "version": "0"},
    },
}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}
CANCELLED = {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99}}
TOOLS_LIST = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}


def frame(message: dict[str, object]) -> bytes:
    body = json.dumps(message, separators=(",", ":")).encode("utf-8")
    return b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body


def lines(*messages: dict[str, object]) -> bytes:
    return b"".join(json.dumps(message).encode("utf-8") + b"\n" for message in messages)


def parse_framed_messages(data: bytes) -> list[dict[str, object]]:
    messages: list[dict[str, object]] = []
    offset = 0
    while offset < len(data):
        assert data.startswith(b"Content-Length: ", offset), data[:200]
        header_end = data.find(b"\r\n\r\n", offset)
        assert header_end >= 0, data[offset:]
        length = int(data[offset + len(b"Content-Length: ") : header_end].split(b"\r\n", 1)[0])
        body_start = header_end + 4
        body_end = body_start + length
        assert len(data) >= body_end, data[offset:]
        messages.append(json.loads(data[body_start:body_end].decode("utf-8")))
        offset = body_end
    return messages


def parse_line_messages(data: bytes) -> list[dict[str, object]]:
    assert data.startswith(b"{") or not data, data[:200]
    return [json.loads(line.decode("utf-8")) for line in data.splitlines() if line]


@pytest.mark.parametrize("mode", ["framed", "lines"])
def test_mcp_launcher_handles_json_rpc_from_unrelated_session(mode: str, tmp_path: Path) -> None:
    sequence = (INITIALIZE, INITIALIZED, CANCELLED, TOOLS_LIST)
    payload = b"".join(frame(message) for message in sequence) if mode == "framed" else lines(*sequence)

    result = run_launcher(payload, tmp_path)

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    result.stderr.decode("utf-8")
    messages = parse_framed_messages(result.stdout) if mode == "framed" else parse_line_messages(result.stdout)
    assert [message.get("id") for message in messages] == [0, 1], "notifications must not get responses"
    assert messages[0]["result"]["serverInfo"]["name"] == "easygee"
    assert "resources" in messages[0]["result"]["capabilities"]
    tool_names = {tool["name"] for tool in messages[1]["result"]["tools"]}
    assert "easygee_preview_plan" in tool_names


def test_mcp_resources_expose_skill_docs(tmp_path: Path) -> None:
    listed = parse_line_messages(
        run_launcher(lines(INITIALIZE, {"jsonrpc": "2.0", "id": 1, "method": "resources/list"}), tmp_path).stdout
    )
    uris = {item["uri"] for item in listed[1]["result"]["resources"]}
    skill_uri = "easygee://docs/skills/easygee/SKILL.md"
    assert skill_uri in uris
    assert any(uri.startswith("easygee://docs/extras/") for uri in uris)

    requests = lines(
        INITIALIZE,
        {"jsonrpc": "2.0", "id": 1, "method": "resources/read", "params": {"uri": skill_uri}},
        {"jsonrpc": "2.0", "id": 2, "method": "resources/read", "params": {"uri": "easygee://docs/../.mcp.json"}},
    )
    read, escaped = parse_line_messages(run_launcher(requests, tmp_path).stdout)[1:]
    assert read["result"]["contents"][0]["text"].startswith("---")
    assert "error" in escaped


def test_missing_configured_python_is_a_clean_tool_error(tmp_path: Path) -> None:
    missing_python = ROOT / "missing-python-路径.exe"
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "easygee_check_environment", "arguments": {}}}

    result = run_launcher(lines(INITIALIZE, call), tmp_path, env={"EASYGEE_PYTHON": str(missing_python)})

    assert result.returncode == 0
    result.stderr.decode("utf-8")
    response = parse_line_messages(result.stdout)[1]
    assert "missing-python-路径.exe" in response["error"]["message"]
