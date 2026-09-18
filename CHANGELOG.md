# Changelog

## Unreleased

### Added

- `scripts/install.py`: one cross-platform installer that creates a shared
  Python environment, records it as `pythonPath` in settings.json, and
  registers EasyGEE with Codex, Claude Code, Qoder, or any `--skills-dir`;
  `--print-mcp-config` for other MCP clients, `--uninstall`/`--purge`,
  `--dry-run`. Re-running it refreshes each host's cached copy, including
  when the version number has not changed.
- `.claude-plugin/marketplace.json` so Claude Code can install from a local
  checkout; Claude's manifest declares the MCP server with
  `${CLAUDE_PLUGIN_ROOT}`.
- MCP `resources/list` and `resources/read` expose the skill and reference
  documents to MCP clients without skill support.
- `requirements.txt` and `requirements-vector.txt`.

### Changed

- The MCP server launches with `python` directly (no PowerShell launcher) and
  needs only the standard library; Earth Engine scripts run with
  `EASYGEE_PYTHON` or `pythonPath`, so hosts that filter environment
  variables still find the right interpreter.
- Workspace, cache, and gcloud locations resolve from `EASYGEE_WORKSPACE`,
  `EASYGEE_CACHE_DIR`, `EASYGEE_GCLOUD_ROOT` or settings.json, with defaults
  under the EasyGEE user directory instead of fixed `D:` paths. An existing
  gcloud install at the previous Windows default (`D:\Dev\tools\google-cloud-sdk`)
  is still found.
- `skills/easygee/SKILL.md` is now a short router (33 KB → 7 KB); detailed
  guidance moved verbatim into `references/`.
- GeoMaster and GEE Growth Diary moved to `extras/` and are read on demand by
  the easygee skill instead of being registered as separate skills.
- Map Console HTML, CSS, and JavaScript moved from `create_map_console.py`
  into `skills/easygee/assets/map-console/`; generated pages are unchanged.

### Removed

- Duplicate logo files (about 3 MB), session hooks, the `/easygee` command
  (the skill is invocable directly), `scripts/run-easygee-mcp.ps1`, and the
  per-host `adapters/` notes (replaced by the installer).

### Fixed

- The MCP server no longer answers JSON-RPC notifications.

## 0.4.1 - 2026-09-17

### Added

- Chinese EasyGEE routing aliases: “打开地图”, “地图工作台”, “地图控制台”,
  and “Map Console” now open the persistent Map Console workbench.
- Regression coverage for Windows MCP stdio startup and redirected-AppData
  persistence writes.

### Changed

- Map Console layer ordering, measurement workflows, accessibility/i18n,
  and Sentinel-2 NDVI styling were refined.
- The cloud-mask comparison now uses controlled single-scene conditions,
  valid-source-pixel denominators, toggleable mask layers, consensus output,
  and clearer metric semantics.
- Windows MCP launching now pins the project working directory and emits
  UTF-8 diagnostics.

### Fixed

- Settings, profile, and secret writes now fall back safely when Windows
  redirected AppData rejects an atomic cross-device rename.
- Landsat/Sentinel comparison map attribution handling was corrected.

### Validation

- Added focused persistence and MCP launcher regression tests.

## 0.4.0 - 2026-08-30

### Added

- Configurable XYZ, TMS, ArcGIS, WMS, WMTS, raster PMTiles, and COG basemaps,
  including built-in Tianditu vector, imagery, and terrain presets.
- GeoLibre-inspired high-performance data paths: HTTP Range-backed raster
  PMTiles, lazy MapLibre WebGL COG rendering, in-session caches, and compact
  first-render/readiness diagnostics.
- A GIS-style basemap-to-layer workflow with overlay stacking, opacity and
  visibility controls, source details, default basemaps, and zoom-to-layer.
- Durable per-user Map Console profiles for favorites, custom basemaps, map
  view, recent reproducible layers, and per-project layer state.

### Security

- Tianditu keys stay session-only by default; optional device persistence uses
  Windows DPAPI and excludes plaintext credentials from profiles and agent
  state.
- Custom source URLs reject embedded credentials and credential-shaped query
  parameters, while stale browser protocol state can no longer overwrite a
  newer persisted profile.

### Fixed

- Basemap selection and layer checkboxes now update the rendered map and saved
  state consistently, including SRTM visibility and primary-basemap controls.
- Terrain basemaps reuse the last available native zoom where providers lack
  higher-resolution tiles instead of filling the view with unavailable tiles.

### Validation

- Added focused coverage for PMTiles/COG adapters, custom basemap sanitation,
  secure Tianditu credential persistence, byte-range serving, stale-protocol
  handling, profile restoration, basemap overlays, and zoom-to-layer.

## 0.3.2 - 2026-08-18

### Added

- A generic `multimodal-geo-vector` skill for turning local or GEE imagery
  annotations into CRS-aware GeoPackage/GeoJSON artifacts.
- AOI-local recent-scene selection, polygon-hole preservation, and automatic
  raster/vector QA overlays.
- Routing regression coverage for short photovoltaic, vehicle, tree-crown,
  field-parcel, and vessel prompts.

### Changed

- Short multimodal prompts now treat center coordinates as spatial seeds and
  GeoPackage as a local GIS deliverable without asking redundant questions.
- GEE visual-boundary workflows prefer one traceable clear acquisition over a
  median composite and report valid-pixel coverage.

## 0.3.1 - 2026-08-01

### Changed

- Updated Chinese and English README acknowledgements with the official HLS,
  USGS CFMask, Sentinel-1, and Earth Engine compositing sources used by the
  remote-sensing method layer.
- Collapsed the project-layout tree inside an expandable README section and
  documented the new remote-sensing references and scripts.

## 0.3.0 - 2026-08-01

### Added

- Compact remote-sensing method references for Landsat cloud masking, HLS
  cross-sensor harmonization, temporal compositing, and Sentinel-1 SAR.
- Visual and numeric teaching cases comparing Sentinel-2 cloud masks and
  Landsat/Sentinel-2 observations.
- Task-planner and dataset-catalog routes for HLS, SAR geometry, and temporal
  composite semantics.
- Eleven offline evaluation prompts covering the expanded Earth Engine and
  geemap workflows.

### Changed

- Sentinel-2 minimal examples now apply Cloud Score+ pixel-level masking after
  scene-level filtering.
- Landsat Collection 2 defaults now mask fill, cloud/shadow/snow, and saturated
  pixels with `QA_PIXEL` and `QA_RADSAT`.
- Local reference search now prioritizes curated EasyGEE method cards over
  secondary teaching material.

### Validation

- EasyGEE coverage audit: 363/363 checks passed.
- Evaluation prompts: 11/11 passed.
- Project tests: 5 passed.

## 0.2.0 - 2026-07-19

### Added

- A standard-library, bilingual catalog engine for more than 5,000 official
  Earth Engine and community catalog records.
- Exact-id, name, theme, and task retrieval with inspectable match reasons,
  provenance-aware ranking, deprecation handling, and metadata filters.
- Role-based task recommendations for flood risk, vegetation monitoring, soil
  moisture, and land-cover workflows.
- Dataset comparison, catalog verification, optional live Earth Engine asset
  checks, and catalog coverage statistics.
- MCP tools for search, recommendation, comparison, and verification.
- Offline unit tests for DEM, Chinese soil-moisture search, flood-risk bundles,
  filters/comparison, and no-match behavior.

### Changed

- Removed unrelated generic dataset fallbacks when a query has no evidence.
- Updated the curated Copernicus DEM record to the current 2024_1 product.
- Enabled `community` and `all` catalog modes in the Map Console CLI.
