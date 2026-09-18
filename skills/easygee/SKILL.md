---
name: easygee
description: "Google Earth Engine (GEE) Python and geemap workflows: auth, Cloud project and quota setup, 5,000+ dataset discovery and verification, notebooks and scripts, map preview and Map Console, Drive/GCS/asset exports, Sentinel/Landsat/MODIS/SAR methods, JS-to-Python migration, local GIS handoff, and GeoAI remote-sensing methods (detection, segmentation, change detection, SAM, embeddings)."
---

# EasyGEE

Work with Google Earth Engine (GEE), the `earthengine-api` Python client, and
`geemap` reproducibly and credential-safely. This file is a router: read only
the reference named for the task.

## Hard Safety Rules

- Never print, store, document, or commit Earth Engine credentials, OAuth
  tokens, service account keys, or Cloud project secrets.
- Never ask the user to paste OAuth codes, auth URLs, tokens, service account
  keys, or credential file contents into chat, and never print them (including
  `gcloud auth print-access-token` output) in answers, logs, pages, or
  browser automation.
- Do not run OAuth automatically: no `ee.Authenticate()` in reusable scripts;
  give user-run steps. Use `--run` on auth/gcloud helpers only when the user
  explicitly asks to proceed.
- The Earth Engine project id is user-local configuration: never hard-code it
  into docs, code, tests, committed HTML, or plugin bundles.
- Run cost-bearing probes (BigQuery `--run --ack-cost`) only after the user
  accepts the cost. Do not commit generated Map Console HTML or Earth Engine
  tile URLs.

## How To Run

- Prefer the `easygee_*` MCP tools (environment, auth plan, catalog, quota,
  Map Console, preview) when the host exposes them.
- Otherwise run the scripts below (relative to `skills/easygee/`) with the
  configured Python: `EASYGEE_PYTHON` or settings.json `pythonPath`.
- Runtime locations are configurable: workspace `EASYGEE_WORKSPACE` /
  `workspaceDir` (default `%LOCALAPPDATA%\EasyGEE\workspace` on Windows,
  `~/.config/easygee/workspace` elsewhere); cache `EASYGEE_CACHE_DIR` /
  `cacheDir`; gcloud `EASYGEE_GCLOUD_ROOT` (default
  `%LOCALAPPDATA%\EasyGEE\tools\google-cloud-sdk`).

## First Steps

1. Route interaction intent (`compute_first` / `map_first` / `mixed`) with
   `scripts/route_easygee_interaction.py "<task>" --json` →
   `references/interaction-router.md`. "打开地图", "地图工作台", "地图控制台"
   and "Map Console" all mean the persistent EasyGEE Map Console.
2. When data/method choices, local files, CRS, ML, STAC/COG or GEE-vs-local
   are in play, route the backend with
   `scripts/route_geospatial_method.py "<task>" --json` →
   `references/geomaster-integration.md`.
3. Check the environment with `scripts/check_gee_geemap.py` before installing
   or authenticating → `references/setup-auth.md`.
4. Before reporting done, apply "Validation Before Finishing" in
   `references/gee-agent-playbook.md`.

## Routing Table

| Task | Read | Scripts |
| --- | --- | --- |
| Install, auth, project id, geemap auth, one-sentence auth, gcloud CLI | `references/setup-auth.md` | `scripts/check_gee_geemap.py`, `scripts/easygee_project.py`, `scripts/ee_auth_workflow.py`, `scripts/geemap_auth_workflow.py`, `scripts/authorize_geemap_once.py`, `scripts/ensure_gcloud_cli.py` |
| Quota values, usage, Console quota URL, BigQuery slot quota | `references/quota-monitoring.md` | `scripts/show_ee_quotas.py`, `scripts/refresh_map_console_quota.py`, `scripts/probe_bigquery_slot_usage.py` |
| Browser preview, Map Console, AOI/layer state | `references/browser-preview.md`, `references/map-console-agent-contract.json` | `scripts/serve_map_preview.py`, `scripts/create_map_console.py`, `scripts/map_console_agent.py` |
| Headless vs map routing | `references/interaction-router.md` | `scripts/route_easygee_interaction.py` |
| GEE vs local GIS, CRS, COG/STAC, ML | `references/geomaster-integration.md`, `references/geomaster-knowledge-index.json` | `scripts/route_geospatial_method.py` |
| Remote-sensing AI (detection, segmentation, change, regression, SAM, embeddings, VLM) | `references/geoai-encyclopedia.md`, then one chapter in `references/geoai-with-python/` | |
| Non-trivial EE code, reducers, client/server, debugging, final checks | `references/gee-agent-playbook.md` | `scripts/review_ee_code.py` |
| Notebooks, JS-to-Python, local data bridge, geemap ML | `references/geemap-agent-recipes.md`, `references/geemap-api-surface.md` | `scripts/scaffold_geemap_workflow.py`, `scripts/choose_geemap_tool.py` |
| Notebook/script patterns, target mode, minimal examples | `references/workflows.md` | |
| Export/download requests | `references/export-patterns.md` | `scripts/plan_gee_export.py` |
| Dataset search, recommend, compare, verify | `references/dataset-discovery.md` | `scripts/dataset_catalog_engine.py`, `scripts/search_gee_dataset.py`, `scripts/search_easygee_references.py` |
| Provenance, bands, scale factors, QA, output records | `references/data-layer-records.md`, `references/dataset-qa-patterns.md` | |
| AOI complexity, scale, tiling, task-count risk | `references/boundary-compute-patterns.md` | |
| Outcome tasks (NDVI, water/flood, classification, change, zonal stats) and vague extraction | `references/task-patterns.md` | `scripts/plan_gee_task.py`, `scripts/resolve_ambiguous_geo_request.py` |
| Starter templates | `references/workflow-templates.md` | `scripts/scaffold_gee_template.py` |
| Cloud masks, Landsat/S2 comparison, HLS, compositing, Sentinel-1 SAR | `references/landsat-cloud-mask-methods.md`, `references/cloud-mask-comparison-case.md`, `references/landsat-sentinel-comparison-case.md`, `references/cross-sensor-harmonization.md`, `references/temporal-compositing.md`, `references/sentinel1-sar-methods.md` | |
| OpenGeo/opengeos, GeoAgent, GeoLibre, QGIS AI assistants, catalog browsers, map agents, Qiusheng Wu's workflow style | `references/opengeos-patterns.md` | |
| Testing or editing this skill | `references/evaluation-prompts.md` | `scripts/run_evaluation_prompts.py`, `scripts/audit_skill_coverage.py` |
| Attribution, upstream links, licensing | `references/SOURCES.md` | |

## Companion Material

- **GeoMaster** (bundled snapshot, not a registered skill): for remote-sensing
  or GIS methods beyond GEE/geemap plumbing (cloud masks, indices,
  classification, CRS, raster/vector, local files), read
  `extras/geomaster/SKILL.md` from the plugin root
  (`../../extras/geomaster/` from here), loading only the
  files named by the method route. `geomaster:<file>.md` means
  `extras/geomaster/references/<file>.md`.
- **GEEer成长日记** (bundled snapshot): when the user mentions GEEer成长日记, a
  Chinese GEE tutorial/article corpus, or asks what that collection suggests,
  read `extras/gee-growth-diary/SKILL.md` (`../../extras/gee-growth-diary/`)
  as a secondary source index. EasyGEE references and official Earth Engine
  docs remain the authority for dataset ids, scale factors, QA masks, exports,
  and current API behavior.
- **multimodal-geo-vector** (sibling skill): when a multimodal model must
  detect, count, outline, or segment visible targets in local or GEE imagery
  and export CRS-aware vectors. EasyGEE keeps GEE discovery, project/auth,
  preprocessing, and export; that skill handles annotation JSON, tiling,
  pixel-to-map conversion, deduplication, and GeoPackage/GeoJSON handoff.
