from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("easygee_installer", ROOT / "scripts" / "install.py")
installer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(installer)


@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(installer, "ROOT", tmp_path / "plugin checkout")
    monkeypatch.setattr(installer, "CODEX_MARKETPLACE", tmp_path / "marketplace.json")
    monkeypatch.setattr(installer, "CODEX_VALIDATOR", tmp_path / "validator.py")
    monkeypatch.setattr(installer, "DRY_RUN", False)
    monkeypatch.setattr(installer, "codex_source_path", lambda: "./plugins/easygee")
    monkeypatch.setenv("EASYGEE_USER_CONFIG_DIR", str(tmp_path / "config"))
    for key in ("EASYGEE_SETTINGS", "EASYGEE_PYTHON"):
        monkeypatch.delenv(key, raising=False)
    return tmp_path


def old_marketplace() -> bytes:
    return b'{"name":"personal","plugins":[{"name":"other"},{"name":"easygee","source":{"path":"./old"}}],"custom":true}\n'


def claude_state(monkeypatch: pytest.MonkeyPatch, *, installed: bool, source: Path | None = None) -> None:
    marketplaces = [{"name": "easygee", "source": "directory", "path": str(source or installer.ROOT)}]
    plugins = [{"id": "easygee@easygee", "scope": "user", "enabled": False}] if installed else []
    monkeypatch.setattr(installer, "query_json", lambda args: marketplaces if "marketplace" in args else plugins, raising=False)


def test_codex_repeat_install_preserves_other_entries(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    installer.CODEX_MARKETPLACE.write_bytes(old_marketplace())
    calls = []
    monkeypatch.setattr(installer, "run", lambda args, **kwargs: calls.append(args) or 0)
    installer.install_codex()
    installer.install_codex()
    result = json.loads(installer.CODEX_MARKETPLACE.read_bytes())
    assert result["custom"] is True
    assert [item["name"] for item in result["plugins"]] == ["other", "easygee"]
    assert calls == [["codex", "plugin", "add", "easygee@personal"]] * 2


@pytest.mark.parametrize("existing", [True, False])
def test_failed_codex_install_restores_marketplace(isolated: Path, monkeypatch: pytest.MonkeyPatch, existing: bool) -> None:
    if existing:
        installer.CODEX_MARKETPLACE.write_bytes(old_marketplace())
    def fail(args, **kwargs):
        if "add" in args:
            raise SystemExit("install failed")
        return 0
    monkeypatch.setattr(installer, "run", fail)
    with pytest.raises(SystemExit, match="install failed"):
        installer.install_codex()
    if existing:
        assert installer.CODEX_MARKETPLACE.read_bytes() == old_marketplace()
    else:
        assert not installer.CODEX_MARKETPLACE.exists()


def test_validation_precedes_marketplace_changes(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    installer.CODEX_MARKETPLACE.write_bytes(old_marketplace())
    installer.CODEX_VALIDATOR.touch()
    def fail(args, **kwargs):
        raise SystemExit("invalid plugin")
    monkeypatch.setattr(installer, "run", fail)
    with pytest.raises(SystemExit, match="invalid plugin"):
        installer.install_codex()
    assert installer.CODEX_MARKETPLACE.read_bytes() == old_marketplace()


def test_failed_atomic_write_keeps_existing_config(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    installer.CODEX_MARKETPLACE.write_bytes(old_marketplace())
    def fail(*args):
        raise OSError("replacement failed")
    monkeypatch.setattr(installer.os, "replace", fail)
    with pytest.raises(OSError, match="replacement failed"):
        installer.write_json(installer.CODEX_MARKETPLACE, {})
    assert installer.CODEX_MARKETPLACE.read_bytes() == old_marketplace()


def test_failed_codex_removal_keeps_registration(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    installer.CODEX_MARKETPLACE.write_bytes(old_marketplace())
    def fail(args, *, check=True, **kwargs):
        if check:
            raise SystemExit("remove failed")
        return 1
    monkeypatch.setattr(installer, "run", fail)
    with pytest.raises(SystemExit, match="remove failed"):
        installer.uninstall_codex()
    assert installer.CODEX_MARKETPLACE.read_bytes() == old_marketplace()


@pytest.mark.parametrize("installed", [False, True])
def test_claude_uses_install_or_update_without_removal(isolated: Path, monkeypatch: pytest.MonkeyPatch, installed: bool) -> None:
    claude_state(monkeypatch, installed=installed)
    calls = []
    monkeypatch.setattr(installer, "run", lambda args, **kwargs: calls.append(args) or 0)
    installer.install_claude()
    assert calls == [
        ["claude", "plugin", "marketplace", "update", "easygee"],
        ["claude", "plugin", "update" if installed else "install", "easygee@easygee", "--scope", "user"],
    ]


def test_claude_does_not_replace_another_checkout(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    claude_state(monkeypatch, installed=True, source=isolated / "another checkout")
    calls = []
    monkeypatch.setattr(installer, "run", lambda args, **kwargs: calls.append(args) or 0)
    with pytest.raises(SystemExit, match="already"):
        installer.install_claude()
    assert calls == []


def test_failed_claude_update_never_uninstalls(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    claude_state(monkeypatch, installed=True)
    calls = []
    def fail(args, **kwargs):
        calls.append(args)
        if args[2] in ("install", "update"):
            raise SystemExit("update failed")
        return 0
    monkeypatch.setattr(installer, "run", fail)
    with pytest.raises(SystemExit, match="update failed"):
        installer.install_claude()
    assert not any("uninstall" in args or "remove" in args for args in calls)


def test_failed_uninstall_stops_purge(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    claude_state(monkeypatch, installed=True)
    venv = isolated / "config" / "venv"
    venv.mkdir(parents=True)
    marker = venv / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    def fail(args, *, check=True, **kwargs):
        if check:
            raise SystemExit("uninstall failed")
        return 1
    monkeypatch.setattr(installer, "run", fail)
    monkeypatch.setattr(sys, "argv", ["install.py", "--hosts", "claude", "--uninstall", "--purge"])
    with pytest.raises(SystemExit, match="uninstall failed"):
        installer.main()
    assert marker.read_text(encoding="utf-8") == "keep"


def test_claude_preserves_marketplace_used_by_project_scope(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plugins = [
        {"id": "easygee@easygee", "scope": "user"},
        {"id": "easygee@easygee", "scope": "project"},
    ]
    monkeypatch.setattr(installer, "query_json", lambda args: plugins)
    calls = []
    monkeypatch.setattr(installer, "run", lambda args, **kwargs: calls.append(args) or 0)
    installer.uninstall_claude()
    assert calls == [["claude", "plugin", "uninstall", "easygee@easygee", "--scope", "user"]]


def test_purge_keeps_external_python(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    venv = isolated / "config" / "venv"
    venv.mkdir(parents=True)
    external = isolated / "custom python"
    external.touch()
    installer.easygee_project.save_settings({"pythonPath": str(external), "custom": True})
    monkeypatch.setattr(sys, "argv", ["install.py", "--hosts", "none", "--uninstall", "--purge"])
    assert installer.main() == 0
    assert not venv.exists()
    assert external.exists()
    assert installer.easygee_project.load_settings()["pythonPath"] == str(external)


def test_purge_refuses_linked_environment(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    venv = isolated / "config" / "venv"
    monkeypatch.setattr(installer, "is_link", lambda path: path == venv)
    monkeypatch.setattr(sys, "argv", ["install.py", "--hosts", "none", "--uninstall", "--purge"])
    with pytest.raises(SystemExit, match="linked"):
        installer.main()


def test_link_install_repeat_and_uninstall_preserve_sources(isolated: Path) -> None:
    source = installer.ROOT / "skills" / "easygee"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("source", encoding="utf-8")
    target = isolated / "host skills"
    installer.link_skills(target)
    installer.link_skills(target)
    assert (target / "easygee" / "SKILL.md").read_text(encoding="utf-8") == "source"
    installer.unlink_skills(target)
    installer.unlink_skills(target)
    assert not (target / "easygee").exists()
    assert (source / "SKILL.md").read_text(encoding="utf-8") == "source"


def test_dry_run_does_not_execute_hosts_or_write_configs(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected(*args, **kwargs):
        pytest.fail("dry run executed a host CLI")
    monkeypatch.setattr(installer.subprocess, "call", unexpected)
    monkeypatch.setattr(installer.subprocess, "check_output", unexpected)
    monkeypatch.setattr(sys, "argv", ["install.py", "--hosts", "codex,claude", "--skip-env", "--dry-run"])
    assert installer.main() == 0
    assert not installer.CODEX_MARKETPLACE.exists()
    assert not (isolated / "config").exists()


def test_registered_skills_are_top_level_only() -> None:
    skills = ROOT / "skills"
    assert sorted(skills.rglob("SKILL.md")) == sorted(skills.glob("*/SKILL.md"))


def test_windows_wrapper_stops_after_git_failure(tmp_path: Path) -> None:
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        pytest.skip("PowerShell is not available")
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "init", "--initial-branch=main", str(checkout)], check=True, capture_output=True)
    scripts = checkout / "scripts"
    scripts.mkdir()
    (scripts / "install.py").write_text("print('INSTALLER_RAN')", encoding="utf-8")
    result = subprocess.run(
        [shell, "-NoProfile", "-File", str(ROOT / "scripts" / "install-easygee.ps1"), "-PluginDir", str(checkout)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    assert result.returncode != 0
    assert "INSTALLER_RAN" not in result.stdout
