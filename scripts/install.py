#!/usr/bin/env python3
"""Install EasyGEE once and register it with every detected agent host.

Steps (each can be skipped):
  1. Python runtime: create a venv under the EasyGEE user directory (uv when
     available, else `python -m venv`), install requirements, and record it as
     `pythonPath` in settings.json so every host finds the same interpreter.
  2. Hosts: Codex and Claude Code through their plugin CLIs; skill-folder hosts
     (Qoder, or any `--skills-dir`) through directory links. Other MCP clients
     get a ready-to-paste config from `--print-mcp-config`.

Run `python scripts/install.py --uninstall` to reverse step 2 (and `--purge`
to also delete the venv). Only the standard library is required.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "easygee_mcp_server.py"
sys.path.insert(0, str(ROOT / "skills" / "easygee" / "scripts"))
import easygee_project  # noqa: E402

PLUGIN = "easygee"
CODEX_MARKETPLACE = Path.home() / ".agents" / "plugins" / "marketplace.json"
CODEX_VALIDATOR = Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
QODER_SKILLS = Path.home() / ".qoder" / "skills"
HOSTS = ("codex", "claude", "qoder")
DRY_RUN = False


def step(message: str) -> None:
    print(f"==> {message}", flush=True)


def run(command: list[str]) -> int:
    print("    $ " + subprocess.list2cmdline(command), flush=True)
    if DRY_RUN:
        return 0
    # npm-installed CLIs are .cmd shims on Windows; resolve them explicitly.
    code = subprocess.call([shutil.which(command[0]) or command[0], *command[1:]])
    if code != 0:
        raise SystemExit(f"command failed with exit code {code}: {command[0]}")
    return code


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(data)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def write_json(path: Path, payload: object) -> None:
    if DRY_RUN:
        print(f"    (dry run) would write {path}")
        return
    write_bytes_atomic(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def query_json(command: list[str]) -> list[dict]:
    if DRY_RUN:
        return []
    try:
        output = subprocess.check_output(
            [shutil.which(command[0]) or command[0], *command[1:]], text=True, encoding="utf-8",
        )
        payload = json.loads(output)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise SystemExit(f"cannot inspect host registration: {exc}") from exc
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise SystemExit(f"expected a JSON list from: {subprocess.list2cmdline(command)}")
    return payload


# --- Python runtime -------------------------------------------------------

def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def ensure_runtime(python: str | None, with_vector: bool) -> str:
    uv = shutil.which("uv")
    if python:
        target = Path(python).expanduser().resolve()
        if not target.exists():
            raise SystemExit(f"--python not found: {target}")
    else:
        venv = easygee_project.local_app_data_root() / "venv"
        target = venv_python(venv)
        if target.exists():
            step(f"Reusing Python environment {venv}")
        else:
            step(f"Creating Python environment {venv}")
            run([uv, "venv", "--python", "3.12", str(venv)] if uv else [sys.executable, "-m", "venv", str(venv)])
    requirements = ROOT / ("requirements-vector.txt" if with_vector else "requirements.txt")
    step(f"Installing {requirements.name}")
    if uv:
        run([uv, "pip", "install", "--python", str(target), "-r", str(requirements)])
    else:
        run([str(target), "-m", "pip", "install", "-r", str(requirements)])
    run([str(target), "-c", "import ee, geemap"])
    settings = easygee_project.load_settings()
    settings["pythonPath"] = str(target)
    step(f"Recording pythonPath in {easygee_project.settings_path()}")
    if not DRY_RUN:
        easygee_project.save_settings(settings)
    return str(target)


# --- Hosts ----------------------------------------------------------------

def detect_hosts() -> list[str]:
    found = [name for name in ("codex", "claude") if shutil.which(name)]
    if QODER_SKILLS.parent.exists():
        found.append("qoder")
    return found


def codex_source_path() -> str:
    try:
        relative = ROOT.relative_to(Path.home())
    except ValueError:
        raise SystemExit(f"Codex local marketplaces resolve plugins under {Path.home()}; clone EasyGEE there (default: ~/plugins/easygee).")
    return "./" + relative.as_posix()


def codex_marketplace() -> dict:
    if CODEX_MARKETPLACE.exists():
        payload = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8-sig"))
    else:
        payload = {}
    if not isinstance(payload, dict):
        raise SystemExit(f"expected a JSON object in {CODEX_MARKETPLACE}")
    payload.setdefault("name", "local-plugins")
    payload.setdefault("interface", {"displayName": "Local Plugins"})
    payload.setdefault("plugins", [])
    if not isinstance(payload["plugins"], list) or any(not isinstance(item, dict) for item in payload["plugins"]):
        raise SystemExit(f"expected a plugins list in {CODEX_MARKETPLACE}")
    return payload


def install_codex() -> None:
    step("Registering with Codex")
    marketplace = codex_marketplace()
    entry = {
        "name": PLUGIN,
        "source": {"source": "local", "path": codex_source_path()},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Science",
    }
    marketplace["plugins"] = [item for item in marketplace["plugins"] if item.get("name") != PLUGIN] + [entry]
    if CODEX_VALIDATOR.exists():
        run([sys.executable, str(CODEX_VALIDATOR), str(ROOT)])
    previous = CODEX_MARKETPLACE.read_bytes() if CODEX_MARKETPLACE.exists() else None
    write_json(CODEX_MARKETPLACE, marketplace)
    try:
        # Let the host replace its cached copy without uninstalling the old plugin.
        run(["codex", "plugin", "add", f"{PLUGIN}@{marketplace['name']}"])
    except (OSError, SystemExit, KeyboardInterrupt):
        if not DRY_RUN:
            if previous is None:
                CODEX_MARKETPLACE.unlink(missing_ok=True)
            else:
                write_bytes_atomic(CODEX_MARKETPLACE, previous)
        raise


def uninstall_codex() -> None:
    step("Removing from Codex")
    if not CODEX_MARKETPLACE.exists():
        return
    marketplace = codex_marketplace()
    if not any(item.get("name") == PLUGIN for item in marketplace["plugins"]):
        return
    run(["codex", "plugin", "remove", f"{PLUGIN}@{marketplace['name']}"])
    marketplace["plugins"] = [item for item in marketplace["plugins"] if item.get("name") != PLUGIN]
    write_json(CODEX_MARKETPLACE, marketplace)


def install_claude() -> None:
    step("Registering with Claude Code")
    marketplaces = query_json(["claude", "plugin", "marketplace", "list", "--json"])
    existing = next((item for item in marketplaces if item.get("name") == PLUGIN), None)
    if existing:
        source = existing.get("path")
        if existing.get("source") != "directory" or not source or Path(source).resolve() != ROOT.resolve():
            raise SystemExit(f"Claude marketplace '{PLUGIN}' already uses another source; use that checkout or remove it explicitly before switching.")
    installed = query_json(["claude", "plugin", "list", "--json"])
    action = "update" if any(item.get("id") == f"{PLUGIN}@{PLUGIN}" and item.get("scope") == "user" for item in installed) else "install"
    if existing:
        run(["claude", "plugin", "marketplace", "update", PLUGIN])
    else:
        run(["claude", "plugin", "marketplace", "add", str(ROOT)])
    run(["claude", "plugin", action, f"{PLUGIN}@{PLUGIN}", "--scope", "user"])


def uninstall_claude() -> None:
    step("Removing from Claude Code")
    installed = query_json(["claude", "plugin", "list", "--json"])
    ours = [item for item in installed if item.get("id") == f"{PLUGIN}@{PLUGIN}" and item.get("scope") == "user"]
    if ours:
        run(["claude", "plugin", "uninstall", f"{PLUGIN}@{PLUGIN}", "--scope", "user"])
    # Keep a marketplace still used by plugins in other scopes.
    if any(str(item.get("id", "")).endswith(f"@{PLUGIN}") and item not in ours for item in installed):
        return
    for item in query_json(["claude", "plugin", "marketplace", "list", "--json"]):
        if item.get("name") == PLUGIN and item.get("source") == "directory" and item.get("path") and Path(item["path"]).resolve() == ROOT.resolve():
            run(["claude", "plugin", "marketplace", "remove", PLUGIN])


def skill_dirs() -> list[Path]:
    return sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))


def is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)  # Python 3.12+
    return path.is_symlink() or bool(is_junction and is_junction()) or os.path.realpath(path) != os.path.abspath(path)


def link_skills(target_root: Path) -> None:
    step(f"Linking skills into {target_root}")
    for source in skill_dirs():
        link = target_root / source.name
        if link.exists() or link.is_symlink():
            if not is_link(link):
                print(f"    skip {link}: a real directory already exists")
                continue
            if Path(os.path.realpath(link)) == source.resolve():
                continue
            unlink_dir(link)
        print(f"    {link} -> {source}")
        if DRY_RUN:
            continue
        target_root.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            subprocess.check_call(["cmd", "/c", "mklink", "/J", str(link), str(source)], stdout=subprocess.DEVNULL)
        else:
            link.symlink_to(source, target_is_directory=True)


def unlink_dir(link: Path) -> None:
    # Remove only the link itself; never recurse into the linked plugin tree.
    if DRY_RUN:
        print(f"    (dry run) would unlink {link}")
    elif link.is_symlink() and os.name != "nt":
        link.unlink()
    else:
        os.rmdir(link)


def unlink_skills(target_root: Path) -> None:
    step(f"Unlinking skills from {target_root}")
    for source in skill_dirs():
        link = target_root / source.name
        if (link.exists() or link.is_symlink()) and is_link(link) and Path(os.path.realpath(link)) == source.resolve():
            print(f"    remove {link}")
            unlink_dir(link)


def mcp_config(python: str | None) -> dict:
    command = python or easygee_project.configured_python() or sys.executable
    return {"mcpServers": {PLUGIN: {"command": command, "args": [str(SERVER)]}}}


# --- CLI ------------------------------------------------------------------

def parse_hosts(value: str) -> list[str]:
    if value == "auto":
        return detect_hosts()
    if value == "none":
        return []
    names = list(HOSTS) if value == "all" else [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(names) - set(HOSTS))
    if unknown:
        raise SystemExit(f"unknown host(s): {', '.join(unknown)}; choose from {', '.join(HOSTS)}")
    return names


def main() -> int:
    global DRY_RUN
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--hosts", default="auto", help="auto (default), all, none, or a comma list of: " + ", ".join(HOSTS))
    parser.add_argument("--skills-dir", action="append", default=[], type=Path, help="extra folder to link skills into (repeatable)")
    parser.add_argument("--python", help="use this interpreter instead of creating the EasyGEE venv")
    parser.add_argument("--skip-env", action="store_true", help="do not create/update the Python environment")
    parser.add_argument("--with-vector", action="store_true", help="also install the multimodal-geo-vector dependencies")
    parser.add_argument("--print-mcp-config", action="store_true", help="print an MCP config snippet for other clients and exit")
    parser.add_argument("--uninstall", action="store_true", help="unregister from hosts and remove skill links")
    parser.add_argument("--purge", action="store_true", help="with --uninstall: also delete the EasyGEE venv")
    parser.add_argument("--dry-run", action="store_true", help="print actions without changing anything")
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    if args.print_mcp_config:
        print(json.dumps(mcp_config(args.python), ensure_ascii=False, indent=2))
        return 0

    hosts = parse_hosts(args.hosts)
    if args.uninstall:
        for host in hosts:
            {"codex": uninstall_codex, "claude": uninstall_claude, "qoder": lambda: unlink_skills(QODER_SKILLS)}[host]()
        for folder in args.skills_dir:
            unlink_skills(folder.expanduser())
        if args.purge:
            venv = easygee_project.local_app_data_root().resolve() / "venv"
            if is_link(venv):
                raise SystemExit(f"refusing to purge a linked Python environment: {venv}")
            step(f"Deleting {venv}")
            if venv.exists() and not DRY_RUN:
                shutil.rmtree(venv)
            settings = easygee_project.load_settings()
            if Path(str(settings.get("pythonPath", ""))).is_relative_to(venv) and not DRY_RUN:
                settings.pop("pythonPath")
                easygee_project.save_settings(settings)
        step("EasyGEE uninstalled")
        return 0

    python = None if args.skip_env else ensure_runtime(args.python, args.with_vector)
    for host in hosts:
        {"codex": install_codex, "claude": install_claude, "qoder": lambda: link_skills(QODER_SKILLS)}[host]()
    for folder in args.skills_dir:
        link_skills(folder.expanduser())

    step("EasyGEE installed")
    print(f"    plugin:  {ROOT}")
    print(f"    python:  {python or easygee_project.configured_python() or '(not configured)'}")
    print(f"    hosts:   {', '.join(hosts + [str(p) for p in args.skills_dir]) or '(none)'}")
    print("    Other MCP clients: python scripts/install.py --print-mcp-config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
