#!/usr/bin/env python
"""Offline coverage audit for the EasyGEE skill."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


REQUIRED_REFERENCES = [
    "setup-auth.md",
    "quota-monitoring.md",
    "interaction-router.md",
    "geomaster-integration.md",
    "geomaster-knowledge-index.json",
    "geoai-encyclopedia.md",
    "browser-preview.md",
    "gee-agent-playbook.md",
    "geemap-agent-recipes.md",
    "geemap-api-surface.md",
    "export-patterns.md",
    "data-layer-records.md",
    "dataset-discovery.md",
    "boundary-compute-patterns.md",
    "dataset-qa-patterns.md",
    "cross-sensor-harmonization.md",
    "temporal-compositing.md",
    "sentinel1-sar-methods.md",
    "task-patterns.md",
    "workflow-templates.md",
    "workflows.md",
    "opengeos-patterns.md",
    "evaluation-prompts.md",
    "SOURCES.md",
    "map-console-agent-contract.json",
]

REQUIRED_SCRIPTS = [
    "easygee_project.py",
    "check_gee_geemap.py",
    "ee_auth_workflow.py",
    "geemap_auth_workflow.py",
    "authorize_geemap_once.py",
    "ensure_gcloud_cli.py",
    "show_ee_quotas.py",
    "refresh_map_console_quota.py",
    "route_easygee_interaction.py",
    "route_geospatial_method.py",
    "search_easygee_references.py",
    "serve_map_preview.py",
    "create_map_console.py",
    "map_console_agent.py",
    "resolve_ambiguous_geo_request.py",
    "plan_gee_export.py",
    "scaffold_geemap_workflow.py",
    "search_gee_dataset.py",
    "dataset_catalog_engine.py",
    "scaffold_gee_template.py",
    "plan_gee_task.py",
    "choose_geemap_tool.py",
    "review_ee_code.py",
    "run_evaluation_prompts.py",
    "audit_skill_coverage.py",
]

REQUIRED_GEOAI_FILES = [
    "SKILL.md",
    "patterns.md",
    "glossary.md",
    "cheatsheet.md",
    "chapters/ch03-geospatial-data-essentials.md",
    "chapters/ch06-preparing-training-data.md",
    "chapters/ch08-object-detection.md",
    "chapters/ch09-semantic-segmentation.md",
    "chapters/ch10-instance-segmentation.md",
    "chapters/ch12-change-detection.md",
    "chapters/ch13-pixel-regression.md",
    "chapters/ch14-sam-geospatial.md",
    "chapters/ch15-vision-language-models.md",
    "chapters/ch16-satellite-embeddings.md",
    "references/source-map.md",
]

SOURCE_MARKERS = [
    "developers.google.com/earth-engine/guides/auth",
    "developers.google.com/earth-engine/guides/access",
    "earthengine.google.com/signup",
    "console.cloud.google.com/apis/library/earthengine.googleapis.com",
    "console.cloud.google.com/earth-engine/configuration",
    "docs.cloud.google.com/docs/quotas/view-manage",
    "docs.cloud.google.com/docs/quotas/reference/rest/v1/projects.locations.services.quotaInfos/list",
    "docs.cloud.google.com/docs/quotas/reference/rest/v1/projects.locations.services.quotaInfos",
    "docs.cloud.google.com/sdk/gcloud/reference/beta/quotas/info/list",
    "docs.cloud.google.com/sdk/docs/install-sdk",
    "docs.cloud.google.com/sdk/docs/downloads-versioned-archives",
    "docs.cloud.google.com/monitoring/alerts/using-quota-metrics",
    "developers.google.com/earth-engine/guides/client_server",
    "developers.google.com/earth-engine/guides/classification",
    "developers.google.com/earth-engine/guides/exporting",
    "developers.google.com/earth-engine/guides/ic_composite_mosaic",
    "developers.google.com/earth-engine/apidocs/ee-imagecollection-qualitymosaic",
    "developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
    "developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED",
    "developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD",
    "developers.google.com/earth-engine/guides/sentinel1",
    "developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002",
    "developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002",
    "developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2",
    "developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG",
    "developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater",
    "developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop",
    "developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_POP",
    "developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons",
    "geemap.org/usage",
    "geemap.org/common",
    "book.geemap.org/chapters/07_data_export",
    "geemap.org/notebooks/00_geemap_key_features",
    "geemap.org/notebooks/11_export_image",
    "github.com/sadassimov/geemu-skill",
    "github.com/opengeos/GeoAgent",
    "github.com/opengeos/GeoLibre",
    "mp.weixin.qq.com/s/pEVuV8Q4dH2BWv_zQCDmZQ",
    "book.opengeoai.org",
    "github.com/giswqs/GeoAI-Book",
    "opengeoai.org",
    "samgeo.gishub.org",
    "creativecommons.org/licenses/by/4.0",
]


@dataclass
class Check:
    status: str
    name: str
    detail: str


def run_python(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-B", str(script), *args],
        cwd=str(cwd),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def add(checks: list[Check], ok: bool, name: str, detail: str) -> None:
    checks.append(Check("ok" if ok else "fail", name, detail))


def audit(skill_dir: Path) -> list[Check]:
    checks: list[Check] = []
    skill_md = skill_dir / "SKILL.md"
    sources = skill_dir / "references" / "SOURCES.md"
    skill_text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
    sources_text = sources.read_text(encoding="utf-8") if sources.exists() else ""

    add(checks, skill_md.exists(), "skill-md-exists", str(skill_md))

    for name in REQUIRED_REFERENCES:
        path = skill_dir / "references" / name
        add(checks, path.exists(), f"reference:{name}", "exists" if path.exists() else str(path))
        add(checks, f"references/{name}" in skill_text or name == "SOURCES.md", f"reference-linked:{name}", "mentioned in SKILL.md or attribution file")

    for name in REQUIRED_SCRIPTS:
        path = skill_dir / "scripts" / name
        add(checks, path.exists(), f"script:{name}", "exists" if path.exists() else str(path))
        if name != "audit_skill_coverage.py":
            add(checks, f"scripts/{name}" in skill_text, f"script-linked:{name}", "mentioned in SKILL.md")

    geoai_root = skill_dir / "references" / "geoai-with-python"
    for relative in REQUIRED_GEOAI_FILES:
        path = geoai_root / relative
        add(checks, path.exists(), f"geoai-bundle:{relative}", "exists" if path.exists() else str(path))

    for marker in SOURCE_MARKERS:
        add(checks, marker in sources_text, f"source:{marker}", "recorded in SOURCES.md")

    plan = run_python(skill_dir / "scripts" / "plan_gee_task.py", "surface water time series by watershed", cwd=skill_dir)
    add(checks, plan.returncode == 0, "plan-script-runs", plan.stderr.strip() or "ran")
    plan_output = plan.stdout.lower()
    for expected in ("water-flood", "time-series", "zonal-statistics"):
        add(checks, expected in plan_output, f"plan-detects:{expected}", plan.stdout.strip())

    zh_plan = run_python(skill_dir / "scripts" / "plan_gee_task.py", "洪水淹没范围按流域统计时间序列", cwd=skill_dir)
    add(checks, zh_plan.returncode == 0, "plan-script-runs:zh", zh_plan.stderr.strip() or "ran")
    zh_plan_output = zh_plan.stdout.lower()
    for expected in ("water-flood", "time-series", "zonal-statistics"):
        add(checks, expected in zh_plan_output, f"plan-zh-detects:{expected}", zh_plan.stdout.strip())

    choose = run_python(skill_dir / "scripts" / "choose_geemap_tool.py", "draw an AOI and export a geotiff", cwd=skill_dir)
    add(checks, choose.returncode == 0, "choose-script-runs", choose.stderr.strip() or "ran")
    choose_output = choose.stdout.lower()
    for expected in ("draw-aoi", "export-image"):
        add(checks, expected in choose_output, f"choose-detects:{expected}", choose.stdout.strip())

    zh_choose = run_python(skill_dir / "scripts" / "choose_geemap_tool.py", "绘制研究区并导出影像", cwd=skill_dir)
    add(checks, zh_choose.returncode == 0, "choose-script-runs:zh", zh_choose.stderr.strip() or "ran")
    zh_choose_output = zh_choose.stdout.lower()
    for expected in ("draw-aoi", "export-image"):
        add(checks, expected in zh_choose_output, f"choose-zh-detects:{expected}", zh_choose.stdout.strip())

    export_smoke = run_python(
        skill_dir / "scripts" / "plan_gee_export.py",
        "export current AOI NDVI to Google Drive as a 10 m GeoTIFF",
        "--json",
        cwd=skill_dir,
    )
    add(checks, export_smoke.returncode == 0, "export-planner-runs", export_smoke.stderr.strip() or "ran")
    try:
        export_payload = json.loads(export_smoke.stdout)
    except json.JSONDecodeError:
        export_payload = {}
    add(checks, export_payload.get("data_kind") == "image", "export-planner-image-kind", export_smoke.stdout.strip())
    add(checks, export_payload.get("destination") == "drive", "export-planner-drive-destination", export_smoke.stdout.strip())
    add(checks, export_payload.get("route") == "ee_batch_image_to_drive", "export-planner-image-drive-route", export_smoke.stdout.strip())
    add(checks, export_payload.get("scale_m") == 10, "export-planner-scale", export_smoke.stdout.strip())
    add(
        checks,
        "ee.batch.Export.image.toDrive" in set(export_payload.get("functions", [])),
        "export-planner-image-function",
        export_smoke.stdout.strip(),
    )

    export_table = run_python(
        skill_dir / "scripts" / "plan_gee_export.py",
        "export a monthly NDVI time series CSV for multiple polygons to Drive",
        "--json",
        cwd=skill_dir,
    )
    add(checks, export_table.returncode == 0, "export-planner-table-runs", export_table.stderr.strip() or "ran")
    try:
        table_payload = json.loads(export_table.stdout)
    except json.JSONDecodeError:
        table_payload = {}
    add(checks, table_payload.get("data_kind") == "table", "export-planner-table-kind", export_table.stdout.strip())
    add(checks, table_payload.get("route") == "ee_batch_table_to_drive", "export-planner-table-route", export_table.stdout.strip())

    export_map = run_python(
        skill_dir / "scripts" / "plan_gee_export.py",
        "save the current map as HTML for sharing",
        "--json",
        cwd=skill_dir,
    )
    add(checks, export_map.returncode == 0, "export-planner-map-runs", export_map.stderr.strip() or "ran")
    try:
        map_payload = json.loads(export_map.stdout)
    except json.JSONDecodeError:
        map_payload = {}
    add(checks, map_payload.get("data_kind") == "map", "export-planner-map-kind", export_map.stdout.strip())
    add(checks, map_payload.get("route") == "geemap_map_communication_export", "export-planner-map-route", export_map.stdout.strip())

    data_layer_search = run_python(
        skill_dir / "scripts" / "search_easygee_references.py",
        "data layer record official community band semantics scale offset QA",
        "--json",
        cwd=skill_dir,
    )
    add(checks, data_layer_search.returncode == 0, "local-reference-search-runs:data-layer", data_layer_search.stderr.strip() or "ran")
    try:
        data_layer_hits = json.loads(data_layer_search.stdout)
    except json.JSONDecodeError:
        data_layer_hits = []
    data_layer_paths = {item.get("path") for item in data_layer_hits if isinstance(item, dict)}
    add(checks, "references/data-layer-records.md" in data_layer_paths, "local-reference-search-data-layer", data_layer_search.stdout.strip())

    boundary_search = run_python(
        skill_dir / "scripts" / "search_easygee_references.py",
        "boundary compute tiling tile count exact AOI export region",
        "--json",
        cwd=skill_dir,
    )
    add(checks, boundary_search.returncode == 0, "local-reference-search-runs:boundary", boundary_search.stderr.strip() or "ran")
    try:
        boundary_hits = json.loads(boundary_search.stdout)
    except json.JSONDecodeError:
        boundary_hits = []
    boundary_paths = {item.get("path") for item in boundary_hits if isinstance(item, dict)}
    add(checks, "references/boundary-compute-patterns.md" in boundary_paths, "local-reference-search-boundary-compute", boundary_search.stdout.strip())

    export_ref_search = run_python(
        skill_dir / "scripts" / "search_easygee_references.py",
        "export product destination Drive GeoTIFF task metadata",
        "--json",
        cwd=skill_dir,
    )
    add(checks, export_ref_search.returncode == 0, "local-reference-search-runs:export", export_ref_search.stderr.strip() or "ran")
    try:
        export_ref_hits = json.loads(export_ref_search.stdout)
    except json.JSONDecodeError:
        export_ref_hits = []
    export_ref_paths = {item.get("path") for item in export_ref_hits if isinstance(item, dict)}
    add(checks, "references/export-patterns.md" in export_ref_paths, "local-reference-search-export-patterns", export_ref_search.stdout.strip())

    project_smoke = run_python(skill_dir / "scripts" / "easygee_project.py", "smoke", cwd=skill_dir)
    add(checks, project_smoke.returncode == 0, "project-resolver-smoke", project_smoke.stdout.strip() or project_smoke.stderr.strip())

    ambiguous_smoke = run_python(skill_dir / "scripts" / "resolve_ambiguous_geo_request.py", "--smoke", cwd=skill_dir)
    add(checks, ambiguous_smoke.returncode == 0, "ambiguous-request-smoke", ambiguous_smoke.stdout.strip() or ambiguous_smoke.stderr.strip())

    ambiguous_cases = [
        (
            "ambiguous-water-aoi",
            ("提取这个AOI中的水体", "--has-aoi", "--json"),
            "water",
            "ask_user",
            "water_semantics",
        ),
        (
            "ambiguous-long-term-water",
            ("提取这个AOI里的长期水体", "--has-aoi", "--json"),
            "water",
            "gee_product",
            None,
        ),
        (
            "ambiguous-current-image-rooftop",
            ("提取这个影像里的屋顶", "--has-active-image", "--active-layer", "visible satellite image", "--json"),
            "rooftop",
            "ask_user",
            "building_output",
        ),
    ]
    for name, args, expected_target, expected_route, expected_question in ambiguous_cases:
        planned = run_python(skill_dir / "scripts" / "resolve_ambiguous_geo_request.py", *args, cwd=skill_dir)
        add(checks, planned.returncode == 0, f"{name}:runs", planned.stderr.strip() or "ran")
        try:
            payload = json.loads(planned.stdout)
        except json.JSONDecodeError:
            payload = {}
        question_ids = {item.get("id") for item in payload.get("clarifying_questions", []) if isinstance(item, dict)}
        routes = {item.get("route") for item in payload.get("candidate_routes", []) if isinstance(item, dict)}
        add(checks, payload.get("intent", {}).get("target") == expected_target, f"{name}:target", planned.stdout.strip())
        add(checks, payload.get("recommended_route") == expected_route, f"{name}:route", planned.stdout.strip())
        add(checks, {"gee_product", "gee_remote_sensing", "current_image_vision"}.issubset(routes), f"{name}:routes", planned.stdout.strip())
        if expected_question:
            add(checks, expected_question in question_ids, f"{name}:question", planned.stdout.strip())

    auth_smoke = run_python(skill_dir / "scripts" / "ee_auth_workflow.py", "--smoke", cwd=skill_dir)
    add(checks, auth_smoke.returncode == 0, "auth-workflow-smoke", auth_smoke.stdout.strip() or auth_smoke.stderr.strip())

    auth_plan = run_python(skill_dir / "scripts" / "ee_auth_workflow.py", "--project", "demo-project", "--mode", "localhost", cwd=skill_dir)
    add(checks, auth_plan.returncode == 0, "auth-workflow-runs", auth_plan.stderr.strip() or "ran")
    auth_text = auth_plan.stdout
    for expected in (
        "Project ID",
        "earthengine.google.com/signup",
        "console.cloud.google.com/apis/library/earthengine.googleapis.com",
        "console.cloud.google.com/earth-engine/configuration",
        "authenticate --auth_mode=localhost",
        "set_project demo-project",
        "ee.Initialize(project='demo-project')",
    ):
        add(checks, expected in auth_text, f"auth-workflow-contains:{expected}", auth_text.strip())

    geemap_auth_smoke = run_python(skill_dir / "scripts" / "geemap_auth_workflow.py", "--smoke", cwd=skill_dir)
    add(checks, geemap_auth_smoke.returncode == 0, "geemap-auth-workflow-smoke", geemap_auth_smoke.stdout.strip() or geemap_auth_smoke.stderr.strip())

    geemap_auth_plan = run_python(
        skill_dir / "scripts" / "geemap_auth_workflow.py",
        "--project",
        "demo-project",
        "--mode",
        "localhost",
        cwd=skill_dir,
    )
    add(checks, geemap_auth_plan.returncode == 0, "geemap-auth-workflow-runs", geemap_auth_plan.stderr.strip() or "ran")
    geemap_auth_text = geemap_auth_plan.stdout
    for expected in (
        "geemap authorization workflow",
        "geemap does not keep separate Google credentials",
        "authenticate --auth_mode=localhost",
        "set_project demo-project",
        "import geemap",
        "ee.Initialize(project='demo-project')",
        "geemap maps can render local basemaps before EE auth",
    ):
        add(checks, expected in geemap_auth_text, f"geemap-auth-workflow-contains:{expected}", geemap_auth_text.strip())

    one_sentence_auth_smoke = run_python(skill_dir / "scripts" / "authorize_geemap_once.py", "--smoke", cwd=skill_dir)
    add(
        checks,
        one_sentence_auth_smoke.returncode == 0,
        "one-sentence-auth-smoke",
        one_sentence_auth_smoke.stdout.strip() or one_sentence_auth_smoke.stderr.strip(),
    )

    one_sentence_auth_plan = run_python(
        skill_dir / "scripts" / "authorize_geemap_once.py",
        "--project",
        "demo-project",
        cwd=skill_dir,
    )
    add(checks, one_sentence_auth_plan.returncode == 0, "one-sentence-auth-plan-runs", one_sentence_auth_plan.stderr.strip() or "ran")
    one_sentence_auth_text = one_sentence_auth_plan.stdout
    for expected in (
        "EasyGEE one-sentence geemap authorization",
        "Google requires the account owner to approve OAuth in the browser",
        "Suppress OAuth command output",
        "Google Cloud CLI login",
        "check_gee_geemap.py --project PROJECT_ID --initialize",
        "--run",
        "credential file present",
    ):
        add(checks, expected in one_sentence_auth_text, f"one-sentence-auth-contains:{expected}", one_sentence_auth_text.strip())

    gcloud_smoke = run_python(skill_dir / "scripts" / "ensure_gcloud_cli.py", "--smoke", cwd=skill_dir)
    add(checks, gcloud_smoke.returncode == 0, "gcloud-resource-smoke", gcloud_smoke.stdout.strip() or gcloud_smoke.stderr.strip())

    gcloud_plan = run_python(
        skill_dir / "scripts" / "ensure_gcloud_cli.py",
        "--project",
        "demo-project",
        cwd=skill_dir,
    )
    add(checks, gcloud_plan.returncode == 0, "gcloud-resource-plan-runs", gcloud_plan.stderr.strip() or "ran")
    gcloud_text = gcloud_plan.stdout
    for expected in (
        "EasyGEE Google Cloud CLI fixed resource",
        "fixed root",
        "google-cloud-sdk",
        "Standard one-command setup",
    ):
        add(checks, expected in gcloud_text, f"gcloud-resource-contains:{expected}", gcloud_text.strip())

    quota_smoke = run_python(skill_dir / "scripts" / "show_ee_quotas.py", "--smoke", cwd=skill_dir)
    add(checks, quota_smoke.returncode == 0, "quota-script-smoke", quota_smoke.stdout.strip() or quota_smoke.stderr.strip())

    quota_report = run_python(
        skill_dir / "scripts" / "show_ee_quotas.py",
        "https://console.cloud.google.com/iam-admin/quotas?service=earthengine.googleapis.com&project=example-ee-project-123456",
        "--no-live",
        cwd=skill_dir,
    )
    add(checks, quota_report.returncode == 0, "quota-script-runs", quota_report.stderr.strip() or "ran")
    quota_text = quota_report.stdout
    for expected in (
        "example-ee-project-123456",
        "earthengine.googleapis.com",
        "Official Earth Engine default/fixed quota reference",
        "Max concurrent requests",
        "EECU-time",
        "beta quotas info list",
    ):
        add(checks, expected in quota_text, f"quota-script-contains:{expected}", quota_text.strip())

    router_smoke = run_python(skill_dir / "scripts" / "route_easygee_interaction.py", "--smoke", cwd=skill_dir)
    add(checks, router_smoke.returncode == 0, "interaction-router-smoke", router_smoke.stdout.strip() or router_smoke.stderr.strip())

    router_cases = [
        (
            "interaction-router-compute",
            "统计北京朝阳公园 NDVI 均值并导出 CSV",
            "compute_first",
            "defer_and_offer",
            {"stat", "table"},
        ),
        (
            "interaction-router-map",
            "给我看北京朝阳公园 NDVI，打开地图叠加图层",
            "map_first",
            "open_or_update",
            {"map_layer"},
        ),
        (
            "interaction-router-mixed",
            "先算两个区域 NDVI 差异，如果异常就打开地图标出来",
            "mixed",
            "compute_then_handoff_if_useful",
            {"stat", "map_layer"},
        ),
    ]
    for name, prompt, expected_mode, expected_policy, expected_artifacts in router_cases:
        routed = run_python(skill_dir / "scripts" / "route_easygee_interaction.py", prompt, "--json", cwd=skill_dir)
        add(checks, routed.returncode == 0, f"{name}:runs", routed.stderr.strip() or "ran")
        try:
            payload = json.loads(routed.stdout)
        except json.JSONDecodeError:
            payload = {}
        artifacts = set(payload.get("artifacts", [])) if isinstance(payload, dict) else set()
        add(checks, payload.get("mode") == expected_mode, f"{name}:mode", routed.stdout.strip())
        add(checks, payload.get("browser_policy") == expected_policy, f"{name}:browser-policy", routed.stdout.strip())
        add(checks, expected_artifacts.issubset(artifacts), f"{name}:artifacts", routed.stdout.strip())

    method_router_smoke = run_python(skill_dir / "scripts" / "route_geospatial_method.py", "--smoke", cwd=skill_dir)
    add(checks, method_router_smoke.returncode == 0, "geospatial-method-router-smoke", method_router_smoke.stdout.strip() or method_router_smoke.stderr.strip())

    method_cases = [
        (
            "method-router-gee",
            "用 GEE 算北京朝阳公园 NDVI 并导出表格",
            "gee_first",
            "earth_engine",
            {"gee-agent-playbook.md", "dataset-qa-patterns.md", "task-patterns.md"},
        ),
        (
            "method-router-local",
            "本地 GeoTIFF 计算 NDVI 并保存 COG",
            "local_first",
            "local_python",
            {"geomaster:core-libraries.md", "geomaster:remote-sensing.md", "geomaster:big-data.md"},
        ),
        (
            "method-router-hybrid",
            "GEE 获取 Sentinel-2，导出 COG 后用本地模型分类",
            "hybrid",
            "earth_engine_plus_local",
            {"gee-agent-playbook.md", "geomaster:machine-learning.md", "geomaster:big-data.md"},
        ),
        (
            "method-router-geoai",
            "Use GEE Sentinel-2 for semantic segmentation and train locally",
            "hybrid",
            "earth_engine_plus_local",
            {"geoai-encyclopedia.md", "geoai-with-python/SKILL.md", "geoai-with-python/chapters/ch09-semantic-segmentation.md"},
        ),
        (
            "method-router-catalog",
            "帮我找适合洪水监测的 GEE 数据集",
            "catalog_first",
            "gee_catalog",
            {"search_gee_dataset.py", "dataset-qa-patterns.md", "geomaster:data-sources.md"},
        ),
        (
            "method-router-browser",
            "先画 AOI 再看图层",
            "browser_first",
            "easygee_map_console",
            {"interaction-router.md", "browser-preview.md"},
        ),
    ]
    for name, prompt, expected_method, expected_backend, expected_reads in method_cases:
        routed = run_python(skill_dir / "scripts" / "route_geospatial_method.py", prompt, "--json", cwd=skill_dir)
        add(checks, routed.returncode == 0, f"{name}:runs", routed.stderr.strip() or "ran")
        try:
            payload = json.loads(routed.stdout)
        except json.JSONDecodeError:
            payload = {}
        read_refs = set(payload.get("read", [])) if isinstance(payload, dict) else set()
        add(checks, payload.get("method") == expected_method, f"{name}:method", routed.stdout.strip())
        add(checks, payload.get("primary_backend") == expected_backend, f"{name}:backend", routed.stdout.strip())
        add(checks, expected_reads.issubset(read_refs), f"{name}:read", routed.stdout.strip())

    preview_smoke = run_python(skill_dir / "scripts" / "serve_map_preview.py", "--smoke", cwd=skill_dir)
    add(checks, preview_smoke.returncode == 0, "browser-preview-smoke", preview_smoke.stdout.strip() or preview_smoke.stderr.strip())

    console_smoke = run_python(skill_dir / "scripts" / "create_map_console.py", "--smoke", cwd=skill_dir)
    add(checks, console_smoke.returncode == 0, "map-console-smoke", console_smoke.stdout.strip() or console_smoke.stderr.strip())

    with tempfile.TemporaryDirectory(prefix="easygee-console-") as tmp:
        empty_path = Path(tmp) / "empty.html"
        empty_plan = run_python(
            skill_dir / "scripts" / "create_map_console.py",
            "--project",
            "demo-project",
            "--output",
            str(empty_path),
            "--catalog-mode",
            "curated",
            "--no-live-quota",
            "--allow-default-quota-state",
            cwd=skill_dir,
        )
        add(checks, empty_plan.returncode == 0 and empty_path.exists(), "map-console-empty-runs", empty_plan.stdout.strip() or empty_plan.stderr.strip())
        empty_text = empty_path.read_text(encoding="utf-8") if empty_path.exists() else ""
        add(checks, "Layers: 0" in empty_plan.stdout, "map-console-empty-layer-count", empty_plan.stdout.strip())
        add(checks, '"layers": []' in empty_text, "map-console-empty-no-layers", str(empty_path))
        add(checks, '"bounds": null' in empty_text, "map-console-empty-no-aoi", str(empty_path))
        add(checks, "119.8684" not in empty_text and "120.4522" not in empty_text, "map-console-empty-no-hangzhou-bounds", str(empty_path))
        add(checks, '"sample-dem"' not in empty_text, "map-console-empty-no-sample-layer", str(empty_path))

        console_path = Path(tmp) / "index.html"
        console_plan = run_python(
            skill_dir / "scripts" / "create_map_console.py",
            "--sample",
            "--project",
            "demo-project",
            "--output",
            str(console_path),
            cwd=skill_dir,
        )
        add(checks, console_plan.returncode == 0 and console_path.exists(), "map-console-sample-runs", console_plan.stdout.strip() or console_plan.stderr.strip())
        console_text = console_path.read_text(encoding="utf-8") if console_path.exists() else ""
        for expected in (
            "EasyGEE Map Console",
            "Add Layers",
            "Layers",
            "Inspector",
            "Quota items",
            "quota-stat-grid",
            "dataset-favorite",
            "catalog.favorites",
            "easygee-dataset-favorites",
            "easygee-aoi:",
            "easygee-measurements:",
            "/api/session/state",
            "/api/session/profile",
            "/api/session/actions",
            "window.EasyGEE",
            "restoreProfileFromServer",
            "applySessionProfile",
            "syncState",
            "pollActions",
            "getMeasurementSummary",
            "extractNdvi",
            "AOI_LAYER_ID",
            "VIS_PRESETS",
            "removeLayer",
            "applyLayerPreset",
            "setAoiStyle",
            "updateLayerStyle",
            "stylePreset",
            "visualPreferences",
            "selectedDataset",
            "aoiBounds",
            "hasExplicitAoi",
            "processingAoi",
            "processingBounds",
            "getSelectedDataset",
            "defaultPreviewRecipeForDataset",
            "recipeSummary",
            "detail-recipe",
            "badge.basemapSource",
            "displayBasemapSource",
            "layerBadgeTitle",
            "STATE =",
            "projectSource",
        ):
            add(checks, expected in console_text, f"map-console-contains:{expected}", str(console_path))
        add(checks, "ndvi-btn" not in console_text, "map-console-no-ndvi-toolbar-button", str(console_path))

    preview_plan = run_python(skill_dir / "scripts" / "serve_map_preview.py", "--plan", "--title", "EasyGEE Audit", cwd=skill_dir)
    add(checks, preview_plan.returncode == 0, "browser-preview-plan-runs", preview_plan.stderr.strip() or "ran")
    preview_text = preview_plan.stdout
    for expected in (
        "EasyGEE browser preview",
        "http://127.0.0.1:",
        "Keep this process running",
    ):
        add(checks, expected in preview_text, f"browser-preview-contains:{expected}", preview_text.strip())

    agent_smoke = run_python(skill_dir / "scripts" / "map_console_agent.py", "smoke", cwd=skill_dir)
    add(checks, agent_smoke.returncode == 0, "map-console-agent-smoke", agent_smoke.stdout.strip() or agent_smoke.stderr.strip())

    search_smoke = run_python(skill_dir / "scripts" / "search_gee_dataset.py", "--smoke", cwd=skill_dir)
    add(checks, search_smoke.returncode == 0, "search-dataset-smoke", search_smoke.stdout.strip() or search_smoke.stderr.strip())

    search = run_python(skill_dir / "scripts" / "search_gee_dataset.py", "洪水淹没范围和人口暴露", "--json", "--no-expanded-catalog", cwd=skill_dir)
    add(checks, search.returncode == 0, "search-dataset-runs:zh", search.stderr.strip() or "ran")
    try:
        search_payload = json.loads(search.stdout)
    except json.JSONDecodeError:
        search_payload = {"candidates": []}
    search_ids = {item.get("id") for item in search_payload.get("candidates", []) if isinstance(item, dict)}
    for expected in ("COPERNICUS/S1_GRD", "WorldPop/GP/100m/pop"):
        add(checks, expected in search_ids, f"search-detects:{expected}", ", ".join(sorted(str(item) for item in search_ids)))

    templates = run_python(skill_dir / "scripts" / "scaffold_gee_template.py", "--list-profiles", cwd=skill_dir)
    add(checks, templates.returncode == 0, "template-list-runs", templates.stderr.strip() or "ran")
    for expected in ("s2-ndvi-cloud-score", "s1-flood-area", "landsat-lst", "modis-vi-timeseries", "dynamic-world-area", "jrc-water-change"):
        add(checks, expected in templates.stdout, f"template-profile:{expected}", templates.stdout.strip())

    with tempfile.TemporaryDirectory(prefix="easygee-template-") as tmp:
        template_path = Path(tmp) / "template.py"
        template = run_python(
            skill_dir / "scripts" / "scaffold_gee_template.py",
            str(template_path),
            "--mode",
            "script",
            "--profile",
            "s2-ndvi-cloud-score",
            cwd=skill_dir,
        )
        add(checks, template.returncode == 0 and template_path.exists(), "template-generate-script", template.stdout.strip() or template.stderr.strip())
        compile_result = subprocess.run(
            [sys.executable, "-B", "-m", "py_compile", str(template_path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        add(checks, compile_result.returncode == 0, "template-script-compiles", compile_result.stderr.strip() or "compiled")

    evaluation = run_python(skill_dir / "scripts" / "run_evaluation_prompts.py", cwd=skill_dir)
    add(checks, evaluation.returncode == 0, "evaluation-prompts-run", evaluation.stdout.strip() or evaluation.stderr.strip())

    bad_code = """
import ee
ee.Initialize()
roi = ee.Geometry.Point([120, 30]).buffer(1000)
s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(roi).median()
stats = s2.normalizedDifference(["B8", "B4"]).reduceRegion(reducer=ee.Reducer.mean())
print(stats.getInfo())
"""
    with tempfile.TemporaryDirectory(prefix="easygee-audit-") as tmp:
        bad_path = Path(tmp) / "bad_gee.py"
        bad_path.write_text(bad_code, encoding="utf-8")
        review = run_python(skill_dir / "scripts" / "review_ee_code.py", str(bad_path), "--json", cwd=skill_dir)
    add(checks, review.returncode == 0, "review-script-runs", review.stderr.strip() or "ran")
    try:
        findings = json.loads(review.stdout)
    except json.JSONDecodeError:
        findings = []
    finding_codes = {item.get("code") for item in findings if isinstance(item, dict)}
    for expected in ("initialize-missing-project", "s2-no-pixel-mask", "reduceRegion-missing-geometry", "reduceRegion-missing-scale", "getinfo"):
        add(checks, expected in finding_codes, f"review-detects:{expected}", ", ".join(sorted(str(code) for code in finding_codes)))

    return checks


def print_text(checks: list[Check]) -> None:
    for check in checks:
        prefix = "OK" if check.status == "ok" else "FAIL"
        print(f"[{prefix}] {check.name}: {check.detail}")
    total = len(checks)
    failed = sum(1 for check in checks if check.status != "ok")
    print(f"Summary: {total - failed}/{total} checks passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks = audit(args.skill_dir.resolve())
    if args.json:
        print(json.dumps([asdict(check) for check in checks], ensure_ascii=False, indent=2))
    else:
        print_text(checks)
    return 1 if any(check.status != "ok" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
