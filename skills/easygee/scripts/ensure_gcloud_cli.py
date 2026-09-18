#!/usr/bin/env python
"""Ensure Google Cloud CLI is available as EasyGEE's fixed resource.

The fixed resource lives under the EasyGEE user directory by default
(override with EASYGEE_GCLOUD_ROOT). The script can install the official Google archive there, launch a
credential-safe browser login, set the active project, and verify Earth Engine
quota access. It never prints OAuth URLs, verification codes, access tokens, or
credential file contents.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import easygee_project  # noqa: E402
import show_ee_quotas  # noqa: E402


WINDOWS_ARCHIVE_URL = "https://storage.googleapis.com/cloud-sdk-release/google-cloud-sdk-575.0.0-windows-x86_64-bundled-python.zip"
WINGET_PACKAGE_ID = "Google.CloudSDK"


@dataclass(frozen=True)
class Operation:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class GcloudStatus:
    gcloud_cli: str | None
    source: str | None
    fixed_root: str
    fixed_gcloud: str
    archive_url: str
    winget_cli: str | None
    version: str | None
    active_account_present: bool
    configured_project: str | None
    quota_live_source: str | None
    quota_limit_rows: int | None
    quota_usage_rows: int | None
    warnings: tuple[str, ...]
    next_commands: tuple[str, ...]


def default_fixed_root() -> Path:
    return easygee_project.gcloud_root()


def default_cache_dir() -> Path:
    return easygee_project.cache_root() / "gcloud"


def gcloud_for_root(root: Path) -> Path:
    name = "gcloud.cmd" if os.name == "nt" else "gcloud"
    return root / "bin" / name


def quote_ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def powershell_call(*parts: str) -> str:
    return " ".join(quote_ps(part) if any(ch.isspace() for ch in part) or "\\" in part or "/" in part else part for part in parts)


def discover_gcloud(fixed_root: Path) -> tuple[str | None, str | None]:
    env_gcloud = os.environ.get("EASYGEE_GCLOUD")
    if env_gcloud and Path(env_gcloud).exists():
        return str(Path(env_gcloud)), "EASYGEE_GCLOUD"
    fixed = gcloud_for_root(fixed_root)
    if fixed.exists():
        return str(fixed), "easygee-fixed"
    which = shutil.which("gcloud")
    if which:
        return which, "PATH"
    found = show_ee_quotas.find_gcloud()
    if found:
        return found, "standard-install"
    return None, None


def run_gcloud(gcloud: str, args: list[str], timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        show_ee_quotas.subprocess_command(gcloud, args),
        env=show_ee_quotas.gcloud_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )


def gcloud_version(gcloud: str | None) -> str | None:
    if not gcloud:
        return None
    try:
        result = run_gcloud(gcloud, ["--version"], timeout=20)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    first = result.stdout.splitlines()[0].strip() if result.stdout.splitlines() else ""
    return first or None


def active_account_present(gcloud: str | None) -> bool:
    if not gcloud:
        return False
    try:
        result = run_gcloud(gcloud, ["config", "get-value", "account", "--quiet"], timeout=20)
    except Exception:
        return False
    account = result.stdout.strip()
    if result.returncode != 0 or not account or account == "(unset)":
        return False
    try:
        token_result = run_gcloud(gcloud, ["auth", "print-access-token"], timeout=30)
    except Exception:
        return False
    return token_result.returncode == 0 and bool(token_result.stdout.strip())


def safe_extract_zip(archive: Path, destination_parent: Path) -> None:
    parent = destination_parent.resolve()
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = (parent / member.filename).resolve()
            if target != parent and parent not in target.parents:
                raise RuntimeError(f"Archive member would escape destination: {member.filename}")
        zf.extractall(parent)


def download_archive(url: str, cache_dir: Path, timeout: int) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    name = Path(urllib.parse.urlparse(url).path).name or "google-cloud-cli.zip"
    archive = cache_dir / name
    if archive.exists() and archive.stat().st_size > 1_000_000:
        return archive
    tmp = archive.with_suffix(archive.suffix + ".tmp")
    request = urllib.request.Request(url, headers={"User-Agent": "EasyGEE/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, tmp.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    except Exception as primary_error:
        curl = shutil.which("curl.exe") or shutil.which("curl")
        if not curl:
            raise primary_error
        result = subprocess.run(
            [curl, "-L", "--fail", "--retry", "3", "--output", str(tmp), url],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise primary_error
    tmp.replace(archive)
    return archive


def install_from_archive(fixed_root: Path, cache_dir: Path, archive_url: str, timeout: int, force: bool = False) -> Operation:
    gcloud = gcloud_for_root(fixed_root)
    if gcloud.exists() and not force:
        return Operation("cloud-cli-install", True, f"fixed gcloud already exists at {gcloud}")
    if os.name != "nt":
        return Operation("cloud-cli-install", False, "archive installer is currently configured for Windows fixed resources")
    try:
        fixed_root.parent.mkdir(parents=True, exist_ok=True)
        archive = download_archive(archive_url, cache_dir, timeout=timeout)
        safe_extract_zip(archive, fixed_root.parent)
    except Exception as error:
        return Operation("cloud-cli-install", False, f"archive install failed: {type(error).__name__}: {error}")
    if gcloud.exists():
        return Operation("cloud-cli-install", True, f"installed fixed gcloud at {gcloud}")
    return Operation("cloud-cli-install", False, f"archive extracted but {gcloud} was not found")


def install_with_winget(timeout: int) -> Operation:
    winget = shutil.which("winget")
    if not winget:
        return Operation("cloud-cli-install", False, "winget was not found")
    command = [
        winget,
        "install",
        "--id",
        WINGET_PACKAGE_ID,
        "--exact",
        "--accept-source-agreements",
        "--accept-package-agreements",
    ]
    try:
        result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Operation("cloud-cli-install", False, f"winget install timed out after {timeout} seconds")
    ok = result.returncode == 0
    return Operation("cloud-cli-install", ok, "winget install completed" if ok else f"winget install exited with code {result.returncode}")


def login_gcloud(gcloud: str, timeout: int, force: bool) -> Operation:
    if active_account_present(gcloud) and not force:
        return Operation("cloud-auth", True, "valid gcloud credentials already present")
    try:
        result = subprocess.run(
            show_ee_quotas.subprocess_command(gcloud, ["auth", "login", "--brief", "--quiet"]),
            env=show_ee_quotas.gcloud_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return Operation("cloud-auth", False, f"timed out after {timeout} seconds waiting for gcloud browser login")
    return Operation("cloud-auth", result.returncode == 0, "gcloud login completed" if result.returncode == 0 else f"gcloud login exited with code {result.returncode}")


def set_project(gcloud: str, project: str) -> Operation:
    try:
        result = run_gcloud(gcloud, ["config", "set", "project", project, "--quiet"], timeout=30)
    except subprocess.TimeoutExpired:
        return Operation("cloud-project", False, "gcloud config set project timed out")
    return Operation("cloud-project", result.returncode == 0, f"gcloud project set to {project}" if result.returncode == 0 else f"gcloud config set project exited with code {result.returncode}")


def quota_probe(project: str, include_usage: bool, minutes: int) -> Operation:
    args = argparse.Namespace(project=project, console_url=None, service=None, no_live=False, include_usage=include_usage, minutes=minutes)
    report = show_ee_quotas.build_report(args)
    if report.live_quotas and (report.usage_rows or not include_usage):
        usage = f", {len(report.usage_rows)} usage rows" if include_usage else ""
        return Operation("quota-probe", True, f"live quota totals available via {report.live_source} ({len(report.live_quotas)} limits{usage})")
    if report.live_quotas:
        return Operation("quota-probe", True, f"live quota totals available via {report.live_source}; Cloud Monitoring usage was not available")
    return Operation("quota-probe", False, "live quota totals unavailable; check Cloud Quotas IAM/API access")


def build_status(
    *,
    fixed_root: Path,
    archive_url: str,
    project: str | None,
    verify_quota: bool,
    include_usage: bool,
    minutes: int,
) -> GcloudStatus:
    gcloud, source = discover_gcloud(fixed_root)
    warnings: list[str] = []
    quota_live_source = None
    quota_limit_rows = None
    quota_usage_rows = None
    if verify_quota:
        if not project:
            warnings.append("--project is required to verify quota access")
        elif not gcloud:
            warnings.append("Google Cloud CLI is missing, so live quota access cannot be verified")
        else:
            args = argparse.Namespace(project=project, console_url=None, service=None, no_live=False, include_usage=include_usage, minutes=minutes)
            report = show_ee_quotas.build_report(args)
            quota_live_source = report.live_source
            quota_limit_rows = len(report.live_quotas)
            quota_usage_rows = len(report.usage_rows)
            warnings.extend(report.warnings)
    script = str(Path(__file__).resolve())
    project_token = project or "PROJECT_ID"
    next_commands = (
        powershell_call(sys.executable, script, "--project", project_token, "--run"),
        powershell_call(sys.executable, script, "--install"),
        powershell_call(gcloud or str(gcloud_for_root(fixed_root)), "auth", "login"),
        powershell_call(gcloud or str(gcloud_for_root(fixed_root)), "config", "set", "project", project_token),
    )
    return GcloudStatus(
        gcloud_cli=gcloud,
        source=source,
        fixed_root=str(fixed_root),
        fixed_gcloud=str(gcloud_for_root(fixed_root)),
        archive_url=archive_url,
        winget_cli=shutil.which("winget"),
        version=gcloud_version(gcloud),
        active_account_present=active_account_present(gcloud),
        configured_project=show_ee_quotas.get_config_project(gcloud) if gcloud else None,
        quota_live_source=quota_live_source,
        quota_limit_rows=quota_limit_rows,
        quota_usage_rows=quota_usage_rows,
        warnings=tuple(warnings),
        next_commands=next_commands,
    )


def print_status(status: GcloudStatus, operations: list[Operation]) -> None:
    print("EasyGEE Google Cloud CLI fixed resource")
    print(f"  fixed root: {status.fixed_root}")
    print(f"  fixed gcloud: {status.fixed_gcloud}")
    print(f"  gcloud CLI: {status.gcloud_cli or 'missing'}")
    print(f"  source: {status.source or 'none'}")
    print(f"  version: {status.version or 'unknown'}")
    print(f"  active account: {'yes' if status.active_account_present else 'no'}")
    print(f"  configured project: {status.configured_project or 'none'}")
    if status.quota_limit_rows is not None:
        print(f"  live quota rows: {status.quota_limit_rows}")
        print(f"  usage rows: {status.quota_usage_rows}")
        print(f"  quota source: {status.quota_live_source or 'none'}")
    if operations:
        print("")
        print("Operations:")
        for op in operations:
            print(f"  [{'ok' if op.ok else 'fail'}] {op.name}: {op.detail}")
    if status.warnings:
        print("")
        print("Warnings:")
        for warning in status.warnings:
            print(f"  - {warning}")
    print("")
    print("Standard one-command setup:")
    print(f"  {status.next_commands[0]}")


def smoke() -> int:
    fixed = default_fixed_root()
    status = build_status(fixed_root=fixed, archive_url=WINDOWS_ARCHIVE_URL, project="demo-project", verify_quota=False, include_usage=True, minutes=60)
    if not status.fixed_gcloud.endswith(("gcloud.cmd", "gcloud")):
        print("ensure_gcloud_cli smoke failed")
        return 1
    if "windows-x86_64" not in status.archive_url:
        print("ensure_gcloud_cli smoke failed")
        return 1
    print("ensure_gcloud_cli smoke passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="Google Cloud / Earth Engine project id")
    parser.add_argument("--run", action="store_true", help="Install missing fixed CLI, log in, set project, and verify quotas")
    parser.add_argument("--install", action="store_true", help="Install Google Cloud CLI if it is missing")
    parser.add_argument("--force-install", action="store_true", help="Extract the archive even when fixed gcloud already exists")
    parser.add_argument("--install-method", choices=["archive", "winget"], default="archive", help="Installation method when --install or --run is used")
    parser.add_argument("--login", action="store_true", help="Run gcloud auth login with OAuth output suppressed")
    parser.add_argument("--force-login", action="store_true", help="Run gcloud auth login even if an active account is present")
    parser.add_argument("--set-project", action="store_true", help="Set gcloud's active project to --project")
    parser.add_argument("--verify-quota", action="store_true", help="Verify live Earth Engine Cloud Quotas access")
    parser.add_argument("--no-usage", action="store_true", help="Skip Cloud Monitoring usage rows during quota verification")
    parser.add_argument("--minutes", type=int, default=60, help="Cloud Monitoring usage lookback window")
    parser.add_argument("--fixed-root", default=str(default_fixed_root()), help="Fixed google-cloud-sdk directory")
    parser.add_argument("--cache-dir", default=str(default_cache_dir()), help="Download cache directory")
    parser.add_argument("--archive-url", default=WINDOWS_ARCHIVE_URL, help="Official Google Cloud CLI archive URL")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds to wait for install/download/login")
    parser.add_argument("--json", action="store_true", help="Emit JSON status")
    parser.add_argument("--smoke", action="store_true", help="Offline self-test")
    args = parser.parse_args()

    if args.smoke:
        return smoke()
    if args.run:
        args.install = True
        args.login = True
        args.set_project = True
        args.verify_quota = True
    if (args.set_project or args.verify_quota) and not args.project:
        parser.error("--project is required with --set-project, --verify-quota, or --run")

    fixed_root = Path(args.fixed_root).expanduser()
    cache_dir = Path(args.cache_dir).expanduser()
    operations: list[Operation] = []

    gcloud, _ = discover_gcloud(fixed_root)
    if args.install and not gcloud:
        if args.install_method == "archive":
            operations.append(install_from_archive(fixed_root, cache_dir, args.archive_url, timeout=args.timeout, force=args.force_install))
        else:
            operations.append(install_with_winget(timeout=args.timeout))
        gcloud, _ = discover_gcloud(fixed_root)
    elif args.install and args.force_install and args.install_method == "archive":
        operations.append(install_from_archive(fixed_root, cache_dir, args.archive_url, timeout=args.timeout, force=True))
        gcloud, _ = discover_gcloud(fixed_root)

    if args.login:
        if gcloud:
            operations.append(login_gcloud(gcloud, timeout=args.timeout, force=args.force_login))
        else:
            operations.append(Operation("cloud-auth", False, "Google Cloud CLI is missing"))

    if args.set_project:
        if gcloud and args.project:
            operations.append(set_project(gcloud, args.project))
        else:
            operations.append(Operation("cloud-project", False, "Google Cloud CLI or project is missing"))

    if args.verify_quota:
        if args.project:
            operations.append(quota_probe(args.project, include_usage=not args.no_usage, minutes=args.minutes))
        else:
            operations.append(Operation("quota-probe", False, "--project is required"))

    status = build_status(
        fixed_root=fixed_root,
        archive_url=args.archive_url,
        project=args.project,
        verify_quota=args.verify_quota,
        include_usage=not args.no_usage,
        minutes=args.minutes,
    )
    if args.json:
        print(json.dumps({"status": asdict(status), "operations": [asdict(op) for op in operations]}, ensure_ascii=False, indent=2))
    else:
        print_status(status, operations)
    return 0 if all(op.ok for op in operations) else 2 if operations else 0


if __name__ == "__main__":
    raise SystemExit(main())
