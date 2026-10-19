#!/usr/bin/env python
"""Probe Earth Engine BigQuery raster-function slot-time usage.

This helper builds a deliberately tiny BigQuery SQL query that calls
ST_REGIONSTATS on a small Earth Engine raster area. By default it only prints
the SQL and the exact run command. Use --run --ack-cost to execute because a
real BigQuery job can consume quota and may incur project charges.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from easygee_project import gcloud_root  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT = "YOUR_EE_PROJECT"
DEFAULT_LOCATION = "US"
DEFAULT_RASTER = "ee://USGS/SRTMGL1_003"
DEFAULT_BAND = "elevation"


def quote_ps(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def find_bq() -> str | None:
    candidates: list[str] = []
    env_bq = os.environ.get("EASYGEE_BQ")
    if env_bq:
        candidates.append(env_bq)
    fixed_bin = gcloud_root() / "bin"
    candidates.extend([str(fixed_bin / "bq.cmd"), str(fixed_bin / "bq")] if os.name == "nt" else [str(fixed_bin / "bq")])
    which = shutil.which("bq")
    if which:
        candidates.append(which)
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def build_sql(args: argparse.Namespace) -> str:
    return f"""-- EasyGEE BigQuery slot-time probe.
-- Tiny AOI; intended only to create a small Earth Engine raster-function usage sample.
WITH probe AS (
  SELECT ST_REGIONSTATS(
    ST_BUFFER(ST_GEOGPOINT({args.lon:.8f}, {args.lat:.8f}), {args.radius_meters:g}),
    '{args.raster}',
    '{args.band}',
    options => JSON '{{"scale": {args.scale:g}}}'
  ) AS stats
)
SELECT
  stats.count AS pixel_count,
  stats.mean AS mean_value,
  stats.min AS min_value,
  stats.max AS max_value
FROM probe;
"""


def run_command(command: list[str], sql: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=sql,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def refresh_quota(project: str, minutes: int) -> None:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "show_ee_quotas.py"),
        "--project",
        project,
        "--include-usage",
        "--minutes",
        str(minutes),
        "--json",
    ]
    result = run_command(command)
    print("Quota refresh result:")
    if result.stdout:
        try:
            payload = json.loads(result.stdout)
            rows = payload.get("usage_rows") or []
            metrics = sorted({row.get("quota_metric") for row in rows})
            print(json.dumps({"usageRows": len(rows), "metrics": metrics}, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def print_plan(args: argparse.Namespace, sql: str, bq: str | None) -> None:
    print("EasyGEE BigQuery slot-time probe")
    print(f"  project: {args.project}")
    print(f"  location: {args.location}")
    print(f"  raster: {args.raster}")
    print(f"  band: {args.band}")
    print(f"  AOI: lon={args.lon}, lat={args.lat}, radius={args.radius_meters} m")
    print(f"  scale: {args.scale} m")
    print(f"  bq CLI: {bq or 'not found'}")
    print()
    print("SQL:")
    print(sql)
    print("Run command:")
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--project",
        args.project,
        "--run",
        "--ack-cost",
    ]
    print("  " + " ".join(quote_ps(part) for part in command))
    print()
    print("Notes:")
    print("  - This is intentionally tiny, but it still creates a BigQuery job when --run is used.")
    print("  - After the job finishes, Cloud Monitoring quota usage can take a few minutes to appear.")
    print("  - If BigQuery or Earth Engine permissions are missing, fix those before expecting quota refresh.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny BigQuery raster-function probe for Earth Engine slot-time usage")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="Google Cloud project id")
    parser.add_argument("--location", default=DEFAULT_LOCATION, help="BigQuery job location, usually US for this probe")
    parser.add_argument("--lon", type=float, default=120.16, help="Probe longitude")
    parser.add_argument("--lat", type=float, default=30.25, help="Probe latitude")
    parser.add_argument("--radius-meters", type=float, default=120.0, help="Small buffer radius in meters")
    parser.add_argument("--scale", type=float, default=90.0, help="Raster sampling scale in meters")
    parser.add_argument("--raster", default=DEFAULT_RASTER, help="Earth Engine raster id")
    parser.add_argument("--band", default=DEFAULT_BAND, help="Raster band")
    parser.add_argument("--run", action="store_true", help="Actually execute the BigQuery job")
    parser.add_argument("--ack-cost", action="store_true", help="Required with --run because BigQuery jobs may consume quota/cost")
    parser.add_argument("--refresh-quota", action="store_true", help="Refresh EasyGEE quota JSON after running")
    parser.add_argument("--wait-seconds", type=int, default=90, help="Wait before quota refresh")
    parser.add_argument("--quota-minutes", type=int, default=180, help="Monitoring lookback window for quota refresh")
    args = parser.parse_args()

    sql = build_sql(args)
    bq = find_bq()
    if not args.run:
        print_plan(args, sql, bq)
        return 0
    if not args.ack_cost:
        parser.error("--run requires --ack-cost")
    if not bq:
        print("bq CLI was not found. Install or initialize Google Cloud CLI first.", file=sys.stderr)
        return 2
    if args.project == DEFAULT_PROJECT:
        print("Pass --project PROJECT_ID before running.", file=sys.stderr)
        return 2

    job_id = "easygee_slot_probe_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    command = [
        bq,
        "query",
        "--use_legacy_sql=false",
        f"--project_id={args.project}",
        f"--location={args.location}",
        f"--job_id={job_id}",
        "--format=json",
        sql,
    ]
    print("Running BigQuery raster-function probe...")
    print(f"  job id: {job_id}")
    result = run_command(command)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        return result.returncode
    if args.refresh_quota:
        print(f"Waiting {args.wait_seconds}s before quota refresh...")
        time.sleep(max(0, args.wait_seconds))
        refresh_quota(args.project, args.quota_minutes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
