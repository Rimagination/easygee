#!/usr/bin/env python
"""Show Earth Engine quota values for a Google Cloud project.

The script is credential-safe: it never prints access tokens or credential file
contents. It prefers `gcloud beta quotas info list`, falls back to the Cloud
Quotas REST API using a short-lived `gcloud auth print-access-token` result,
and always prints the official Earth Engine default quota table as a fallback.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import easygee_project


DEFAULT_SERVICE = "earthengine.googleapis.com"
CONSOLE_URL = "https://console.cloud.google.com/iam-admin/quotas"
CLOUD_QUOTAS_ENDPOINT = "https://cloudquotas.googleapis.com/v1"
MONITORING_ENDPOINT = "https://monitoring.googleapis.com/v3"
UNLIMITED_QUOTA_INT64 = 9_223_372_036_854_775_807
UNLIMITED_QUOTA_THRESHOLD = 9_000_000_000_000_000_000


@dataclass(frozen=True)
class QuotaRow:
    quota: str
    metric: str
    value: str
    unit: str
    scope: str
    kind: str
    dimensions: str
    source: str


@dataclass(frozen=True)
class UsageRow:
    quota_metric: str
    limit_name: str
    metric_type: str
    value: str
    end_time: str
    labels: str


@dataclass
class QuotaReport:
    project: str | None
    service: str
    console_url: str
    live_source: str | None
    live_quotas: list[QuotaRow]
    usage_source: str | None
    usage_rows: list[UsageRow]
    default_quotas: list[QuotaRow]
    commands: list[str]
    warnings: list[str]


DEFAULT_EE_QUOTAS = [
    QuotaRow(
        "Max concurrent requests (standard endpoint)",
        DEFAULT_SERVICE,
        "40",
        "concurrent requests",
        "per project",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Max concurrent requests (high-volume endpoint)",
        DEFAULT_SERVICE,
        "40",
        "concurrent requests",
        "per project",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Max rate of requests (per project)",
        DEFAULT_SERVICE,
        "100/s; 6000/min",
        "requests",
        "per project",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Max rate of requests (per account)",
        DEFAULT_SERVICE,
        "100/s; 6000/min",
        "requests",
        "per account",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Average concurrent batch tasks",
        DEFAULT_SERVICE,
        "2",
        "tasks on average",
        "per project",
        "adjustable/tier-dependent",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Max asset storage space",
        DEFAULT_SERVICE,
        "250",
        "GB",
        "per owner",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Max number of assets",
        DEFAULT_SERVICE,
        "10000",
        "assets",
        "per owner",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Earth Engine compute time (EECU-time) per day",
        f"{DEFAULT_SERVICE}/daily_eecu_usage_time",
        "Unlimited by default",
        "seconds/day",
        "per project",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "BigQuery raster function slot-time per day",
        f"{DEFAULT_SERVICE}/bigquery_slot_usage_time",
        "1260000",
        "slot-seconds/day (350 slot-hours)",
        "per project",
        "adjustable",
        "-",
        "official Earth Engine default",
    ),
    QuotaRow(
        "Task queue length",
        DEFAULT_SERVICE,
        "3000",
        "READY tasks",
        "per project queue",
        "fixed",
        "-",
        "official Earth Engine fixed limit",
    ),
    QuotaRow(
        "Request payload size",
        DEFAULT_SERVICE,
        "10",
        "MB",
        "per request",
        "fixed",
        "-",
        "official Earth Engine fixed limit",
    ),
    QuotaRow(
        "Large aggregation result size",
        DEFAULT_SERVICE,
        "100",
        "MiB",
        "system-wide",
        "fixed",
        "-",
        "official Earth Engine fixed limit",
    ),
]


def find_gcloud() -> str | None:
    candidates = []
    env_gcloud = os.environ.get("EASYGEE_GCLOUD")
    if env_gcloud:
        candidates.append(env_gcloud)
    fixed_bin = easygee_project.gcloud_root() / "bin"
    candidates.extend([str(fixed_bin / "gcloud.cmd"), str(fixed_bin / "gcloud")] if os.name == "nt" else [str(fixed_bin / "gcloud")])
    which = shutil.which("gcloud")
    if which:
        candidates.append(which)
    local_appdata = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("ProgramFiles")
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    for root in (local_appdata, program_files, program_files_x86):
        if not root:
            continue
        candidates.extend(
            [
                str(Path(root) / "Google" / "Cloud SDK" / "google-cloud-sdk" / "bin" / "gcloud.cmd"),
                str(Path(root) / "Google" / "Cloud SDK" / "google-cloud-sdk" / "bin" / "gcloud"),
            ]
        )
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return which


def subprocess_command(executable: str, args: list[str]) -> list[str]:
    suffix = Path(executable).suffix.lower()
    if os.name == "nt" and suffix in {".cmd", ".bat"}:
        return ["cmd.exe", "/c", executable, *args]
    return [executable, *args]


def gcloud_env() -> dict[str, str]:
    env = os.environ.copy()
    if "CLOUDSDK_PYTHON" not in env and Path(sys.executable).exists():
        env["CLOUDSDK_PYTHON"] = sys.executable
    env.setdefault("CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK", "1")
    env.setdefault("CLOUDSDK_CORE_DISABLE_PROMPTS", "1")
    return env


def gcloud_component_installed(gcloud: str, component: str) -> bool:
    try:
        gcloud_path = Path(gcloud).resolve()
    except OSError:
        return True
    if gcloud_path.parent.name.lower() != "bin":
        return True
    install_dir = gcloud_path.parent.parent / ".install"
    return (install_dir / f"{component}.manifest").exists() or (install_dir / f"{component}.snapshot.json").exists()


def run_gcloud(gcloud: str, args: list[str], timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        subprocess_command(gcloud, args),
        env=gcloud_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )


def project_from_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    project = query.get("project", [None])[0]
    return project.strip() if project else None


def service_from_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    service = query.get("service", [None])[0]
    return service.strip() if service else None


def quota_console_url(project: str | None, service: str) -> str:
    query = {"service": service}
    if project:
        query["project"] = project
    return CONSOLE_URL + "?" + urllib.parse.urlencode(query)


def quote_ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def user_commands(project: str | None, service: str) -> list[str]:
    project_token = project or "YOUR_PROJECT_ID"
    script = str(Path(__file__).resolve())
    gcloud = find_gcloud() or "gcloud"
    gcloud_cmd = quote_ps(gcloud) if gcloud != "gcloud" else "gcloud"
    return [
        f"{gcloud_cmd} auth login",
        f"{gcloud_cmd} config set project {project_token}",
        f"{gcloud_cmd} beta quotas info list --service={service} --project={project_token} --format=json",
        f"python {quote_ps(script)} --project {project_token}",
        f"python {quote_ps(script)} --project {project_token} --include-usage",
    ]


def get_config_project(gcloud: str) -> str | None:
    result = run_gcloud(gcloud, ["config", "get-value", "project", "--quiet"], timeout=20)
    value = result.stdout.strip()
    if result.returncode == 0 and value and value != "(unset)":
        return value
    return None


def get_access_token(gcloud: str) -> tuple[str | None, str | None]:
    result = run_gcloud(gcloud, ["auth", "print-access-token"], timeout=30)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return None, detail or "gcloud auth print-access-token failed"
    token = result.stdout.strip()
    return (token or None), None


def fetch_json(url: str, token: str, timeout: int = 45) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def http_error_message(error: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
    except Exception:
        return f"HTTP {error.code}: {error.reason}"
    message = payload.get("error", {}).get("message")
    return f"HTTP {error.code}: {message or error.reason}"


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def is_unlimited_quota_value(value: Any) -> bool:
    text = normalize_value(value).replace(",", "").strip()
    if not text:
        return False
    lowered = text.lower()
    if "unlimited" in lowered or lowered in {"inf", "infinity", "∞"}:
        return True
    try:
        return int(text) >= UNLIMITED_QUOTA_THRESHOLD
    except ValueError:
        return False


def normalize_quota_value(value: Any) -> str:
    if is_unlimited_quota_value(value):
        return "Unlimited"
    return normalize_value(value)


def dimensions_text(dimensions: Any, locations: Any = None) -> str:
    parts: list[str] = []
    if isinstance(dimensions, dict) and dimensions:
        parts.extend(f"{key}={value}" for key, value in sorted(dimensions.items()))
    elif isinstance(dimensions, list) and dimensions:
        parts.extend(str(value) for value in dimensions)
    if isinstance(locations, list) and locations:
        parts.append("locations=" + ",".join(str(item) for item in locations))
    return "; ".join(parts) if parts else "-"


def normalize_quota_infos(items: list[dict[str, Any]], source: str) -> list[QuotaRow]:
    rows: list[QuotaRow] = []
    for item in items:
        quota = item.get("quotaDisplayName") or item.get("displayName") or item.get("quotaId") or item.get("name") or "quota"
        metric = item.get("metric") or item.get("metricDisplayName") or item.get("name") or ""
        unit = normalize_value(item.get("metricUnit"))
        kind = "fixed" if item.get("isFixed") else "adjustable"
        if item.get("isConcurrent"):
            kind += "/concurrent"
        dims_infos = item.get("dimensionsInfos") or item.get("dimensionsInfo") or []
        if dims_infos:
            for dims_info in dims_infos:
                details = dims_info.get("details") or {}
                value = details.get("value")
                if value is None:
                    value = dims_info.get("value") or dims_info.get("quotaValue")
                rows.append(
                    QuotaRow(
                        str(quota),
                        str(metric),
                        normalize_quota_value(value) or "(no value)",
                        unit or "-",
                        item.get("containerType") or "project",
                        kind,
                        dimensions_text(dims_info.get("dimensions"), dims_info.get("applicableLocations")),
                        source,
                    )
                )
        else:
            value = item.get("value") or item.get("quotaValue") or item.get("effectiveLimit")
            rows.append(
                QuotaRow(
                    str(quota),
                    str(metric),
                    normalize_quota_value(value) or "(no value)",
                    unit or "-",
                    item.get("containerType") or "project",
                    kind,
                    dimensions_text(item.get("dimensions")),
                    source,
                )
            )
    return sorted(rows, key=lambda row: (row.metric.lower(), row.quota.lower(), row.dimensions.lower()))


def gcloud_quota_infos(gcloud: str, project: str, service: str) -> tuple[list[QuotaRow], str | None, str | None]:
    commands = [
        (["beta", "quotas", "info", "list"], "gcloud beta quotas info list", "beta"),
        (["alpha", "quotas", "info", "list"], "gcloud alpha quotas info list", "alpha"),
    ]
    last_error: str | None = None
    skipped: list[str] = []
    for prefix, label, component in commands:
        if not gcloud_component_installed(gcloud, component):
            skipped.append(component)
            continue
        args = [
            *prefix,
            f"--service={service}",
            f"--project={project}",
            "--format=json",
            "--quiet",
        ]
        try:
            result = run_gcloud(gcloud, args)
        except subprocess.TimeoutExpired:
            last_error = f"{label} timed out"
            continue
        if result.returncode != 0:
            last_error = (result.stderr or result.stdout).strip() or f"{label} failed"
            continue
        try:
            payload = json.loads(result.stdout or "[]")
        except json.JSONDecodeError as exc:
            last_error = f"{label} returned non-JSON output: {exc}"
            continue
        items = payload if isinstance(payload, list) else payload.get("quotaInfos", [])
        return normalize_quota_infos(items, label), label, None
    if skipped and not last_error:
        last_error = "Skipping gcloud quota command groups because local components are not installed: " + ", ".join(skipped)
    return [], None, last_error


def cloudquotas_quota_infos(gcloud: str, project: str, service: str) -> tuple[list[QuotaRow], str | None]:
    token, token_error = get_access_token(gcloud)
    if not token:
        return [], token_error
    parent = f"projects/{urllib.parse.quote(project, safe='')}/locations/global/services/{service}"
    base_url = f"{CLOUD_QUOTAS_ENDPOINT}/{parent}/quotaInfos"
    items: list[dict[str, Any]] = []
    page_token: str | None = None
    try:
        while True:
            params = {"pageSize": "200"}
            if page_token:
                params["pageToken"] = page_token
            url = base_url + "?" + urllib.parse.urlencode(params)
            payload = fetch_json(url, token)
            items.extend(payload.get("quotaInfos", []))
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
    except urllib.error.HTTPError as exc:
        return [], http_error_message(exc)
    except Exception as exc:
        return [], f"Cloud Quotas REST request failed: {exc}"
    return normalize_quota_infos(items, "Cloud Quotas REST API"), None


def latest_point_value(point: dict[str, Any]) -> str:
    value = point.get("value") or {}
    for key in ("int64Value", "doubleValue", "stringValue", "boolValue"):
        if key in value:
            return normalize_value(value[key])
    return normalize_value(value)


def monitoring_usage_rows(gcloud: str, project: str, service: str, minutes: int) -> tuple[list[UsageRow], str | None]:
    token, token_error = get_access_token(gcloud)
    if not token:
        return [], token_error
    end = dt.datetime.now(dt.timezone.utc)
    start = end - dt.timedelta(minutes=minutes)
    metric_types = [
        "serviceruntime.googleapis.com/quota/allocation/usage",
        "serviceruntime.googleapis.com/quota/rate/net_usage",
    ]
    rows: list[UsageRow] = []
    for metric_type in metric_types:
        filter_expr = (
            f'metric.type="{metric_type}" '
            f'resource.type="consumer_quota" '
            f'resource.label.service="{service}"'
        )
        params = {
            "filter": filter_expr,
            "interval.startTime": start.isoformat().replace("+00:00", "Z"),
            "interval.endTime": end.isoformat().replace("+00:00", "Z"),
            "pageSize": "200",
        }
        url = f"{MONITORING_ENDPOINT}/projects/{urllib.parse.quote(project, safe='')}/timeSeries?" + urllib.parse.urlencode(params)
        try:
            payload = fetch_json(url, token)
        except urllib.error.HTTPError as exc:
            return rows, http_error_message(exc)
        except Exception as exc:
            return rows, f"Cloud Monitoring request failed: {exc}"
        for series in payload.get("timeSeries", []):
            metric = series.get("metric") or {}
            labels = metric.get("labels") or {}
            points = series.get("points") or []
            if not points:
                continue
            point = points[0]
            interval = point.get("interval") or {}
            rows.append(
                UsageRow(
                    quota_metric=str(labels.get("quota_metric") or ""),
                    limit_name=str(labels.get("limit_name") or ""),
                    metric_type=metric_type.rsplit("/", 1)[-1],
                    value=latest_point_value(point),
                    end_time=str(interval.get("endTime") or ""),
                    labels=", ".join(f"{key}={value}" for key, value in sorted(labels.items()) if key not in {"quota_metric", "limit_name"}),
                )
            )
    return sorted(rows, key=lambda row: (row.quota_metric, row.limit_name, row.metric_type)), None


def build_report(args: argparse.Namespace) -> QuotaReport:
    service = args.service or service_from_url(args.console_url) or DEFAULT_SERVICE
    project = args.project or project_from_url(args.console_url)
    warnings: list[str] = []
    live_quotas: list[QuotaRow] = []
    usage_rows: list[UsageRow] = []
    live_source: str | None = None
    usage_source: str | None = None
    gcloud = find_gcloud()

    if not project:
        resolved = easygee_project.resolve_project(None, remember_discovered=True)
        if easygee_project.is_concrete_project(resolved.project):
            project = resolved.project
            warnings.append(f"Using locally configured project from {resolved.source}.")

    if not project and gcloud:
        project = get_config_project(gcloud)
        if project:
            warnings.append("Using gcloud configured project.")

    if not project:
        warnings.append("No project id was provided. Pass --project PROJECT_ID or a Cloud Console quota URL with project=.")

    if args.no_live:
        warnings.append("Live quota lookup skipped because --no-live was set.")
    elif not gcloud:
        warnings.append("gcloud was not found. Install/init Google Cloud CLI or use the Cloud Console link below.")
    elif project:
        live_quotas, live_source, gcloud_error = gcloud_quota_infos(gcloud, project, service)
        if not live_quotas:
            rest_rows, rest_error = cloudquotas_quota_infos(gcloud, project, service)
            if rest_rows:
                live_quotas = rest_rows
                live_source = "Cloud Quotas REST API"
            elif rest_error:
                if gcloud_error:
                    warnings.append(gcloud_error)
                warnings.append(rest_error)
            elif gcloud_error:
                warnings.append(gcloud_error)
        if args.include_usage:
            usage_rows, usage_error = monitoring_usage_rows(gcloud, project, service, args.minutes)
            if usage_rows:
                usage_source = "Cloud Monitoring API"
            elif usage_error:
                warnings.append(usage_error)

    return QuotaReport(
        project=project,
        service=service,
        console_url=quota_console_url(project, service),
        live_source=live_source,
        live_quotas=live_quotas,
        usage_source=usage_source,
        usage_rows=usage_rows,
        default_quotas=DEFAULT_EE_QUOTAS if service == DEFAULT_SERVICE else [],
        commands=user_commands(project, service),
        warnings=dedupe(warnings),
    )


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def shorten(value: str, width: int) -> str:
    value = value.replace("\n", " ")
    if len(value) <= width:
        return value
    if width <= 3:
        return value[:width]
    return value[: width - 3] + "..."


def print_table(headers: list[str], rows: list[list[str]], max_width: int = 36) -> None:
    if not rows:
        print("  (none)")
        return
    shortened_rows = [[shorten(str(cell), max_width) for cell in row] for row in rows]
    widths = [
        min(max(len(headers[index]), *(len(row[index]) for row in shortened_rows)), max_width)
        for index in range(len(headers))
    ]
    header_line = "  " + " | ".join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    separator = "  " + "-+-".join("-" * width for width in widths)
    print(header_line)
    print(separator)
    for row in shortened_rows:
        print("  " + " | ".join(row[index].ljust(widths[index]) for index in range(len(headers))))


def print_text(report: QuotaReport) -> None:
    print("Earth Engine quota report")
    print(f"  project: {report.project or 'UNKNOWN'}")
    print(f"  service: {report.service}")
    print(f"  console: {report.console_url}")
    print(f"  live quota source: {report.live_source or 'not available'}")
    print(f"  usage source: {report.usage_source or 'not requested/available'}")
    print("")
    if report.live_quotas:
        print("Live quota values")
        print_table(
            ["Quota", "Value", "Unit", "Metric", "Dimensions", "Kind"],
            [[row.quota, row.value, row.unit, row.metric, row.dimensions, row.kind] for row in report.live_quotas],
        )
        print("")
    else:
        print("Live quota values")
        print("  Not available in this session. Use the commands below or open the Console URL.")
        print("")

    if report.usage_rows:
        print("Recent usage from Cloud Monitoring")
        print_table(
            ["Quota metric", "Limit", "Usage metric", "Latest", "End time", "Labels"],
            [[row.quota_metric, row.limit_name, row.metric_type, row.value, row.end_time, row.labels] for row in report.usage_rows],
        )
        print("")
    elif report.usage_source is None:
        print("Recent usage")
        print("  Not requested. Re-run with --include-usage to query Cloud Monitoring quota metrics.")
        print("")

    if report.default_quotas:
        print("Official Earth Engine default/fixed quota reference")
        print_table(
            ["Quota", "Value", "Unit", "Scope", "Kind"],
            [[row.quota, row.value, row.unit, row.scope, row.kind] for row in report.default_quotas],
            max_width=48,
        )
        print("")

    if report.warnings:
        print("Notes")
        for warning in report.warnings:
            print(f"  - {warning}")
        print("")

    print("Credential-safe commands")
    for command in report.commands:
        print(f"  {command}")


def report_to_json(report: QuotaReport) -> dict[str, Any]:
    return {
        "project": report.project,
        "service": report.service,
        "console_url": report.console_url,
        "live_source": report.live_source,
        "live_quotas": [asdict(row) for row in report.live_quotas],
        "usage_source": report.usage_source,
        "usage_rows": [asdict(row) for row in report.usage_rows],
        "default_quotas": [asdict(row) for row in report.default_quotas],
        "commands": report.commands,
        "warnings": report.warnings,
    }


def smoke() -> int:
    url = "https://console.cloud.google.com/iam-admin/quotas?service=earthengine.googleapis.com&project=example-ee-project-123456"
    if project_from_url(url) != "example-ee-project-123456":
        print("FAIL: project URL parsing")
        return 1
    sample = [
        {
            "quotaDisplayName": "Daily EECU time",
            "metric": "earthengine.googleapis.com/daily_eecu_usage_time",
            "metricUnit": "s/d/{project}",
            "containerType": "PROJECT",
            "isFixed": False,
            "dimensionsInfos": [{"dimensions": {}, "details": {"value": "86400"}}],
        }
    ]
    rows = normalize_quota_infos(sample, "sample")
    if not rows or rows[0].value != "86400" or "daily_eecu_usage_time" not in rows[0].metric:
        print("FAIL: quota normalization")
        return 1
    unlimited_sample = [
        {
            "quotaDisplayName": "EECU-seconds per day",
            "metric": "earthengine.googleapis.com/daily_eecu_usage_time",
            "metricUnit": "s{CPU}",
            "dimensionsInfos": [{"dimensions": {}, "details": {"value": str(UNLIMITED_QUOTA_INT64)}}],
        }
    ]
    unlimited_rows = normalize_quota_infos(unlimited_sample, "sample")
    if not unlimited_rows or unlimited_rows[0].value != "Unlimited":
        print("FAIL: unlimited quota normalization")
        return 1
    args = argparse.Namespace(
        project=None,
        console_url=url,
        service=None,
        no_live=True,
        include_usage=False,
        minutes=60,
    )
    report = build_report(args)
    if report.project != "example-ee-project-123456" or not report.default_quotas:
        print("FAIL: report build")
        return 1
    original_find_gcloud = globals()["find_gcloud"]
    original_gcloud_quota_infos = globals()["gcloud_quota_infos"]
    original_cloudquotas_quota_infos = globals()["cloudquotas_quota_infos"]
    try:
        fallback_rows = normalize_quota_infos(sample, "Cloud Quotas REST API")
        globals()["find_gcloud"] = lambda: "gcloud"
        globals()["gcloud_quota_infos"] = lambda gcloud, project, service: (
            [],
            None,
            "Skipping gcloud quota command groups because local components are not installed: beta, alpha",
        )
        globals()["cloudquotas_quota_infos"] = lambda gcloud, project, service: (fallback_rows, None)
        fallback_report = build_report(
            argparse.Namespace(
                project="example-ee-project-123456",
                console_url=None,
                service=None,
                no_live=False,
                include_usage=False,
                minutes=60,
            )
        )
        if fallback_report.live_source != "Cloud Quotas REST API" or any("Skipping gcloud" in item for item in fallback_report.warnings):
            print("FAIL: REST fallback should suppress gcloud component warning")
            return 1
    finally:
        globals()["find_gcloud"] = original_find_gcloud
        globals()["gcloud_quota_infos"] = original_gcloud_quota_infos
        globals()["cloudquotas_quota_infos"] = original_cloudquotas_quota_infos
    print("show_ee_quotas smoke passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("console_url", nargs="?", help="Optional Cloud Console quotas URL containing project= and service=.")
    parser.add_argument("--project", help="Google Cloud project id or number. Overrides project= in the URL.")
    parser.add_argument("--service", default=None, help=f"Quota service name. Defaults to {DEFAULT_SERVICE}.")
    parser.add_argument("--include-usage", action="store_true", help="Also query recent Cloud Monitoring quota usage metrics.")
    parser.add_argument("--minutes", type=int, default=60, help="Lookback window for --include-usage. Default: 60.")
    parser.add_argument("--no-live", action="store_true", help="Skip gcloud/API calls and print console/default guidance only.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--smoke", action="store_true", help="Run offline self-checks.")
    args = parser.parse_args()

    if args.smoke:
        return smoke()

    report = build_report(args)
    if args.json:
        print(json.dumps(report_to_json(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
