<div align="center">
  <img src="./assets/logo.png" alt="EasyGEE" width="96" />
  <h1>EasyGEE</h1>

  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-0F766E?style=flat-square" /></a>
  <a href="./.codex-plugin/plugin.json"><img alt="Plugin" src="https://img.shields.io/badge/plugin-Codex%20%7C%20Claude-2563EB?style=flat-square" /></a>
  <a href="./.mcp.json"><img alt="MCP" src="https://img.shields.io/badge/MCP-stdio-111827?style=flat-square" /></a>

  [中文](./README.md) · **English**

  A Google Earth Engine / geemap workbench plugin for AI agents.

  [Capabilities](#capabilities) · [Layout](#layout) · [Usage](#usage) · [Security](#security) · [Acknowledgements](#acknowledgements)
</div>

## Capabilities

EasyGEE packages Google Earth Engine, geemap, GeoMaster method knowledge, and a local browser map console into one reusable agent plugin. It is not trying to clone the classic GEE Code Editor. It helps agents turn natural-language requests into dataset discovery, auth guidance, quota checks, map previews, and hybrid cloud/local geospatial workflows.

- Search 5,000+ official and community GEE records by dataset id, name, theme, or bilingual task, with provenance, deprecation, and match evidence in the ranking.
- Turn an outcome into role-based data bundles—for example flood event, historical baseline, terrain, rainfall, and population/building exposure—and compare or verify candidates before coding.
- Standardize Earth Engine / geemap authorization without exposing OAuth tokens, verification codes, credential files, or service account keys.
- Query Earth Engine quota limits and usage as agent-readable summaries.
- Generate a persistent EasyGEE Map Console for AOI drawing, layer overlays, configurable basemaps, and visual QA; restore map views, favorites, custom sources, and recent layers per local user and project.
- Connect XYZ, TMS, ArcGIS, WMS, WMTS, raster PMTiles, and COG sources, including Tianditu vector, imagery, and terrain presets; promote basemaps to normal layers for ordering, visibility, and opacity controls.
- Accelerate PMTiles and COG access with HTTP Range requests, session caches, and a lazy MapLibre WebGL engine while keeping imagery bytes and tile logs out of agent context.
- Bundle GeoMaster as a skill for CRS, local GIS, remote sensing, ML, STAC/COG, scientific-domain methods, and troubleshooting.
- Bundle the GeoAI Encyclopedia as EasyGEE's task-method layer for image recognition, object detection, semantic/instance segmentation, change detection, pixel regression, SAM, satellite embeddings, vision-language models, and QGIS GeoAI. The router loads only the relevant chapter and keeps GEE/export orchestration separate from local model execution.
- Bundle GEE Growth Diary as a distilled method skill from 153 GEEer成长日记 articles covering dataset choice, indices, time series, classification, water extraction, charts, and exports.
- Bundle remote-sensing method cards and visual teaching cases for Landsat cloud masking, Sentinel-2 cloud masking, HLS cross-sensor harmonization, temporal compositing, Sentinel-1 SAR, and Landsat/Sentinel-2 comparison.

## Layout

<details>
<summary>Expand the project layout</summary>

```text
easygee/
├── .codex-plugin/       # Codex plugin metadata
├── .claude-plugin/      # Claude Code plugin and marketplace metadata
├── .mcp.json            # MCP server declaration (Codex and other MCP clients)
├── assets/              # EasyGEE logo
├── commands/            # Claude Code shortcut commands
├── scripts/             # MCP server and installer (install.py)
├── skills/
│   ├── easygee/         # GEE / geemap / map-console and remote-sensing workflows
│   │   ├── references/  # method references read on demand
│   │   ├── assets/      # Map Console front-end templates
│   │   └── scripts/     # catalog search, task routing, cases, and offline evaluation
│   └── multimodal-geo-vector/ # imagery annotations to CRS-aware vectors
├── extras/
│   ├── geomaster/       # Local GIS and remote-sensing knowledge (read on demand by easygee)
│   └── gee-growth-diary/ # Distilled GEEer成长日记 playbook (read on demand by easygee)
└── requirements*.txt    # Python dependencies
```

</details>

## Usage

### 1. Quick Install

One-sentence agent install:

```text
Install this plugin for me: [Rimagination/easygee](https://github.com/Rimagination/easygee)
```

The agent should clone the repository to `~/plugins/easygee` and run `python scripts/install.py`.

Manual install (requires Python 3.9+ and git):

```bash
git clone https://github.com/Rimagination/easygee.git ~/plugins/easygee
python ~/plugins/easygee/scripts/install.py
```

On Windows, this one-liner clones or updates the repository and runs the same installer:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command '$p=Join-Path $HOME "plugins\easygee"; if(Test-Path $p){ git -C $p pull --ff-only } else { git clone https://github.com/Rimagination/easygee.git $p }; & (Join-Path $p "scripts\install-easygee.ps1")'
```

The installer does two things:

1. Creates a Python environment in the EasyGEE user directory (with uv when available), installs `requirements.txt`, and records the interpreter in `settings.json`. All agents share this environment.
2. Registers EasyGEE with every detected agent: Codex and Claude Code through their plugin CLIs, Qoder through links in its skills folder.

Common options:

| Option | Effect |
| --- | --- |
| `--hosts codex,claude,qoder` | Agents to register; default `auto` uses what is detected |
| `--skills-dir <dir>` | Link the skills into any agent folder that reads `SKILL.md` |
| `--python <path>` | Use an existing Python environment instead of creating one |
| `--with-vector` | Also install the multimodal vectorization dependencies |
| `--print-mcp-config` | Print an MCP config snippet for other MCP clients |
| `--uninstall` / `--purge` | Unregister; `--purge` also deletes the Python environment |
| `--dry-run` | Show the actions without running them |

EasyGEE user directory: `%LOCALAPPDATA%\EasyGEE` on Windows, `~/.config/easygee` elsewhere. Workspace, cache, and interpreter paths can be changed in `settings.json` or overridden with `EASYGEE_WORKSPACE`, `EASYGEE_CACHE_DIR`, and `EASYGEE_PYTHON`.

### 2. Quick Use

Just tell the agent what you want in plain language. These examples cover common daily workflows:

```text
Authorize geemap for example-ee-project-123456.

Open the EasyGEE map around Beijing Chaoyang Park so I can draw an AOI.

I want summer 2024 NDVI for Beijing Chaoyang Park. Pick a suitable GEE dataset and explain why.

Search 5,000+ records for DEMs, keep current official products, and compare the top three.

I need a mountain flood-risk assessment but have not chosen data. Recommend a bundle by hazard, terrain, rainfall, and exposure roles.

Compare COPERNICUS/DEM/GLO30_2024_1 with USGS/SRTMGL1_003 and verify the final id before writing code.

Add Sentinel-2 true color and NDVI layers to the map so I can inspect clouds and vegetation in the browser.

Show my Earth Engine project quota, usage tier, and remaining capacity.

Export NDVI for the current AOI to Google Drive and check whether the export parameters make sense.

I have a local GeoJSON. Decide whether this should run in GEE or local GIS, then generate a runnable script.
```

## Security

EasyGEE treats the browser and credentials as private user space. Agents may prepare auth plans, launch local tools, and summarize safe checks, but must not ask the user to paste OAuth URLs, verification codes, tokens, credential files, service account keys, or short-lived access tokens into chat, logs, docs, or commits.

GeoMaster is bundled as a skill snapshot rather than a nested git checkout. This keeps the plugin self-contained, lightweight, offline-friendly, and free from dependency folders, repository state, or unknown remote sync behavior.

## Acknowledgements

EasyGEE distills patterns from many open geospatial resources and projects. Special thanks to:

- [Google Earth Engine documentation](https://developers.google.com/earth-engine) for authentication, initialization, quotas, exports, the client/server model, and remote-sensing workflow guidance.
- [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/) and the [Earth Engine STAC Catalog](https://storage.googleapis.com/earthengine-stac/catalog/catalog.json) as the main sources for dataset discovery and dataset detail cards.
- [GEE Community Catalog](https://gee-community-catalog.org/) and [community_datasets.csv](https://github.com/sadassimov/geemu-skill/blob/main/awesome-gee-community-datasets/community_datasets.csv) for community dataset coverage beyond the official catalog.
- The WeChat public account [GEEer成长日记](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzNjMxNDk1NQ==&action=getalbum&album_id=2182256849633247236) for Chinese GEE practice cases and task inspiration that helped EasyGEE better cover Chinese-language remote-sensing workflows.
- The WeChat public account [野火遥感Fire Centre](https://mp.weixin.qq.com/s/pEVuV8Q4dH2BWv_zQCDmZQ) for Chinese wildfire remote-sensing, disaster monitoring, and applied case-study references.
- [GEEMu Skill](https://github.com/sadassimov/geemu-skill) for inspiration around lightweight local knowledge search, data-layer records, boundary/compute gates, and export dry-run patterns.
- [geemap](https://geemap.org/) / [gee-community/geemap](https://github.com/gee-community/geemap) for Python-based GEE maps, notebooks, export helpers, and dataset exploration patterns.
- [Qiusheng Wu's Earth-Engine-Catalog](https://github.com/giswqs/Earth-Engine-Catalog) for a lightweight machine-readable Earth Engine catalog index.
- [OpenGeoAgent / GeoAgent](https://github.com/opengeos/GeoAgent), [GeoLibre](https://github.com/opengeos/GeoLibre), [leafmap](https://leafmap.org/), and [anymap](https://github.com/opengeos/anymap) for map-first, agentic, and local-first GIS workbench ideas.
- [Insight Maps](https://map.insightmaps.app/) for compact map tools, layer catalog interactions, and polished Web GIS UI references.
- [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) for README hero structure, badges, and language-switch layout inspiration.
- [NASA HLS L30](https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002) and [HLS S30](https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002) for official HLS 30 m NBAR, harmonization processing, common bands, and Fmask semantics.
- [USGS CFMask](https://www.usgs.gov/landsat-missions/cfmask-algorithm) and the [Landsat cloud-algorithm validation study](https://www.usgs.gov/publications/cloud-detection-algorithm-comparison-and-validation-operational-landsat-data-products) for Landsat QA_PIXEL, CFMask boundaries, and validation evidence.
- [Sentinel-1 Algorithms](https://developers.google.com/earth-engine/guides/sentinel1) for official SAR GRD preprocessing, polarization/orbit filtering, dB backscatter, and terrain limitations.
- [Earth Engine Compositing and Mosaicking](https://developers.google.com/earth-engine/guides/ic_composite_mosaic) and the [`qualityMosaic()` API](https://developers.google.com/earth-engine/apidocs/ee-imagecollection-qualitymosaic) for temporal composite, mosaic, quality-pixel, and source-pixel semantics.

See [skills/easygee/references/SOURCES.md](./skills/easygee/references/SOURCES.md) for the fuller source and attribution record.
