from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "easygee" / "scripts"
spec = importlib.util.spec_from_file_location("easygee_project", SCRIPTS / "easygee_project.py")
project = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules.setdefault("easygee_project", project)
spec.loader.exec_module(project)


@pytest.fixture
def user_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("EASYGEE_WORKSPACE", "EASYGEE_CACHE_DIR", "EASYGEE_GCLOUD_ROOT", "EASYGEE_PYTHON", "EASYGEE_SETTINGS"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("EASYGEE_USER_CONFIG_DIR", str(tmp_path / "user"))
    monkeypatch.setattr(project, "LEGACY_WINDOWS_GCLOUD_ROOT", tmp_path / "legacy-sdk")
    return tmp_path / "user"


def write_settings(user_dir: Path, **values: str) -> None:
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "settings.json").write_text(json.dumps({"version": 1, **values}), encoding="utf-8")


def test_defaults_live_under_user_dir(user_dir: Path) -> None:
    assert project.workspace_root() == user_dir / "workspace"
    assert project.cache_root() == user_dir / "cache"
    assert project.configured_python() is None
    if os.name == "nt":
        assert project.gcloud_root() == user_dir / "tools" / "google-cloud-sdk"


def test_settings_then_env_override(user_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_settings(user_dir, workspaceDir=str(tmp_path / "ws"), pythonPath="py-from-settings", gcloudRoot=str(tmp_path / "sdk"))
    assert project.workspace_root() == tmp_path / "ws"
    assert project.configured_python() == "py-from-settings"
    assert project.gcloud_root() == tmp_path / "sdk"

    monkeypatch.setenv("EASYGEE_WORKSPACE", str(tmp_path / "ws-env"))
    monkeypatch.setenv("EASYGEE_PYTHON", "py-from-env")
    assert project.workspace_root() == tmp_path / "ws-env"
    assert project.configured_python() == "py-from-env"


@pytest.mark.skipif(os.name != "nt", reason="legacy default only existed on Windows")
def test_existing_legacy_gcloud_install_is_still_found(user_dir: Path, tmp_path: Path) -> None:
    legacy_bin = tmp_path / "legacy-sdk" / "bin"
    legacy_bin.mkdir(parents=True)
    (legacy_bin / "gcloud.cmd").write_text("@echo off\n", encoding="utf-8")
    assert project.gcloud_root() == tmp_path / "legacy-sdk"
