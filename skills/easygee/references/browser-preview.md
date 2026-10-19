# Browser Preview

Use this reference when the user asks for an interactive map, browser-based
visual inspection, a persistent lightweight visualization page, or an in-app
Browser handoff for GEE/geemap outputs.

If the request mixes analysis and visualization, read
`interaction-router.md` first. This file explains the mechanics of building and
serving the browser surface after the routing decision is made.

## Current Capability

EasyGEE can prepare and serve a local preview page. It does not own the browser
runtime by itself; when the in-app Browser skill is available, load
`browser:control-in-app-browser` and open the local preview URL there. If the
Browser skill is unavailable, provide the localhost URL or local HTML path as a
fallback.

## Standard Flow

1. Choose the preview surface:

```powershell
# Fixed EasyGEE workbench UI
python scripts/create_map_console.py --project YOUR_EE_PROJECT --output map-console/index.html

# One-off geemap/folium HTML artifact
python your_map_script.py
```

Use `create_map_console.py` when the user wants a stable browser interface with
layer list, catalog search, inspector, task/log panels, and project-state
export. The generated shell is viewer-first: the map occupies the full browser
surface, and status/control regions stay compressed as floating drawers until
the user opens them. Its interaction style is inspired by professional
ArcGIS/Calcite-style web GIS apps such as Insight Maps: a compact icon tool
rail, an icon-only 30 px status badge instead of a title bar, semantic
layer-type marks, a quota status icon backed by total/used/remaining quota rows
when Cloud Quotas and Monitoring are available, a simple line scale, a
Chinese/English language toggle, and short-lived mode chips instead of large
always-on status panels. Use direct geemap HTML when the user only needs a
specific map artifact from notebook code.

2. Build or export the map artifact:

```python
m = geemap.Map()
# add Earth Engine layers, vector layers, legends, controls, etc.
m.to_html("map_preview.html")
```

3. Start the local preview server with Python's standard library helper:

```powershell
python scripts/serve_map_preview.py map_preview.html
```

4. Keep that server process running while the user interacts with the map.
5. Open the printed `http://127.0.0.1:PORT/...` URL in the in-app Browser when
   that browser surface is available.
6. Use the browser view to inspect layer loading, pan/zoom behavior, legends,
   popups, and whether tiles/rendered HTML are nonblank.

## EasyGEE Map Console

The Map Console is EasyGEE's fixed local browser shell. It is not the native
GEE Code Editor and it is not a geemap widget; it is a lightweight local UI for
recurring GEE/geemap previews.

Standard regions:

- Top bar: an icon-only status badge for EE readiness. Project/title/AOI
  details belong in a hover/focus tooltip, not in always-visible map space.
  The active-layer badge should also expose the current basemap source, with
  full attribution available in its hover/focus title.
- Tool rail: icon buttons for layers, inspector, measure, basemap, quota
  status, task/state, home, zoom controls, and language switching.
- Left drawer: catalog search and layer stack with opacity controls.
- Map workspace: Leaflet map with Earth Engine tile overlays and a minimal
  custom line scale.
- Right drawer: click inspector, active layer metadata, legend.
- Bottom drawer: task board, session log, project state, and state export.
  The project section includes quota rows with total, used, and remaining
  values. If live usage is unavailable, it must say so directly and use the
  official default/fixed quota reference only as a fallback.
  Do not use `--no-live-quota` for ordinary user-facing workbench pages; it is
  reserved for offline smoke tests or explicit no-network previews. For
  non-sample pages, the generator requires the explicit
  `--allow-default-quota-state` guard before it will write default-only quota
  state.
  When making UI-only changes to an existing generated page, patch the UI and
  run `scripts/refresh_map_console_quota.py <map.html>` if quota state needs a
  refresh. That helper updates only `STATE.quota` and refuses to write
  default-only fallback quota state by default, preserving the current map,
  AOI, measurements, and Earth Engine tile layers.

Generated Earth Engine tile URLs are local preview material. Do not commit the
HTML page or copy tile URLs into chat/logs; regenerate the console when tiles
expire or the analysis changes.

AOI and measurement state are part of the workbench, not disposable page
scratch. Use `window.EasyGEE.getAoi()` for follow-up analysis after the user
draws an AOI, `window.EasyGEE.getMeasurements()` /
`getMeasurementSummary()` after repeated distance measurements, and
`window.EasyGEE.extractNdvi()` for Sentinel-2 NDVI extraction. These actions
must sync results back into the existing layer stack; do not add task-specific
toolbar buttons or generate a separate one-off HTML page for the same map
session.

AOI is represented as a system layer in the layer stack. Users and agents can
hide it, style its color/opacity, or clear it. Earth Engine data layers also
carry visualization state such as `visParams`, `styleProfile`, and
`stylePreset`; changing a palette should use the workbench protocol to
regenerate the tile URL with new visualization parameters, not edit generated
HTML. Regular loaded layers should be removable from the same layer stack.
For ImageCollection datasets, Add Layers is a quick preview, not a complete
analysis choice: the resulting layer must carry a `recipe` explaining the
default reducer, band/index, date range, scale factor, and AOI. Analytical
requests such as "MODIS 2024 May-Sep NDVImax" should use an explicit
ImageCollection recipe, then sync the result as a normal layer.
Clearing the AOI only removes the explicit AOI system layer. The console should
still expose `processingAoi` and `processingBounds` from the current map
viewport so users can continue loading remote-sensing preview layers without
redrawing an AOI.

For agent automation, prefer `scripts/map_console_agent.py` and the compact
contract in `map-console-agent-contract.json` over reading generated HTML. The
Map Console syncs its current state to `/api/session/state` and polls
`/api/session/actions`; agents can read AOI/measurements as small JSON and
enqueue layer updates after background analysis. The synced state includes
`selectedDataset` and per-layer `recipe` metadata so agents can resolve phrases
like "this MODIS dataset" or "this layer" without scraping the DOM or asking
the user to copy an ID.

For vague extraction requests made while a Map Console is open, run
`scripts/map_console_agent.py plan --url <localhost-url> "<prompt>" --pretty`
before computing. The planner uses current AOI and layer state to decide whether
to use a catalog product, a reproducible remote-sensing workflow, current-image
visual recognition, or a one-question clarification. Results still return to
the existing layer stack or task log; the workbench should not grow
task-specific buttons such as "NDVI", "Water", or "Rooftop".

Dataset favorites, AOI, and measurement history should survive browser reloads,
preview server restarts, and localhost port changes. The preview server stores a
small profile JSON in local app data by default and exposes it through
`/api/session/profile`. Browser `localStorage` remains a per-origin cache only;
do not treat it as the durable source of workbench state.

## When To Use This

- Interactive geemap map previews.
- Visual QA before exporting screenshots or static maps.
- Lightweight "always open" map page during iterative analysis.
- Local HTML, Leaflet/Folium/geemap exports, simple dashboards, or map reports.

## When Not To Use This

- Headless batch exports that do not need visual inspection.
- Confidential credential flows. Authentication remains a separate setup step.
- Proof of analysis correctness. A browser map is a diagnostic view, not a
  substitute for reducer/export validation.

## Notes

- `scripts/serve_map_preview.py` uses only Python's standard library.
- The preview page may still need network access if the exported HTML loads
  online basemap tiles, CDNs, or Earth Engine tile URLs.
- Do not paste OAuth URLs, tokens, credential files, or service account keys
  into the page or browser automation logs.
- If the map depends on Earth Engine tiles, initialize/authenticate in the
  Python workflow before exporting the geemap HTML.
- Prefer `127.0.0.1` binding for local previews unless the user explicitly asks
  to expose the page on the network.

## Scripts

- Use `scripts/serve_map_preview.py <map.html>` to serve geemap-exported HTML
  or local map artifacts on `127.0.0.1` without extra software. If the
  `browser:control-in-app-browser` skill is available, load it and open the
  printed localhost URL there.
- Use `scripts/create_map_console.py --project <project> --output <index.html>`
  when the user wants a fixed browser UI rather than a one-off map page. This
  creates the viewer-first EasyGEE 地图工作台 (Map Console): the map fills the browser by
  default, while layer/catalog, inspector, measure, basemap, task/log, and
  project/quota controls stay compressed behind a small Calcite-inspired icon
  tool rail and floating drawers. Its Add Layers catalog defaults to official
  Earth Engine STAC entries plus GEE Community Catalog CSV entries, with source
  labels so community datasets are not mistaken for official catalog assets.
  Serve the generated HTML with `serve_map_preview.py`.
- Use `scripts/map_console_agent.py` for agent-facing Map Console work. Prefer
  its `capabilities`, `state --compact`, `aoi`, `measurement-summary`,
  `quick-layer`, `render-recipe`, and `extract-ndvi` commands over reading
  generated HTML or browser DOM. The script talks to the local preview server's
  compact `/api/session/*` protocol and can enqueue browser-visible layer
  actions.

## Map Console Operating Rules

- In the EasyGEE Chinese context, “打开地图”, “地图工作台”, “地图控制台”, and
  “Map Console” all refer to the same persistent EasyGEE 地图工作台. Route these
  requests to the existing Map Console and reuse its browser session when possible.
- For persistent exploratory sessions, prefer the EasyGEE Map Console generated
  by `create_map_console.py` over ad hoc Leaflet/geemap HTML. Treat it as a
  local diagnostic workbench inspired by GEE Code Editor and GeoLibre patterns,
  not as proof that the underlying analysis is statistically correct.
- Keep the Map Console tool rail stable. Do not add task-specific toolbar
  buttons for analyses such as NDVI; run those actions in the background and
  sync the result back as normal layers in the existing layer stack.
- Treat AOI as a system layer inside the Map Console layer stack. Users can
  hide it, change its color/opacity, or clear it through the layer workflow.
  Do not leave drawn AOI state as an unmanageable overlay.
- Treat explicit AOI and processing extent as separate state. After AOI is
  cleared, `aoi` should be null but `processingAoi` / `processingBounds` should
  fall back to the current map viewport so remote-sensing preview layers can
  still be loaded.
- Treat Earth Engine visualization parameters as editable layer state. When a
  user asks to change JRC water to blue, adjust an NDVI palette, remove a
  loaded layer, or restore a default color ramp, enqueue a Map Console action
  such as `updateLayerStyle`, `setAoiStyle`, or `removeLayer` through
  `scripts/map_console_agent.py`; do not regenerate a one-off HTML page.
- Treat ImageCollection layers as reproducible recipes, not just rendered
  tiles. The Map Console state exposes `selectedDataset` and layer `recipe`
  metadata; use explicit recipes for requests like "MODIS May-Sep NDVImax"
  with dataset id, band/index, temporal reducer, date/month window, scale
  factor, AOI, and visualization parameters instead of relying on the Add
  Layers quick-preview default.
- Treat AOI and measurement data as first-class console state. The console
  exposes `window.EasyGEE.getAoi()`, `setAoi()`, `getMeasurements()`,
  `getMeasurementSummary()`, and `extractNdvi()` for follow-up automation.
  Default AOI drawing is rectangular; polygon AOI is supported through the same
  AOI tool state/API without expanding the fixed toolbar.
- Treat the Map Console profile as the durable source for dataset favorites,
  AOI, and measurements. The preview server persists profile JSON in local app
  data by default, with `serve_map_preview.py --profile <path>` available for
  tests or explicit workspaces. Browser `localStorage` is only a cache and may
  be isolated by localhost port.
- For token-efficient follow-up work, read `references/map-console-agent-contract.json`
  or run `map_console_agent.py capabilities` once, then use
  `map_console_agent.py state --compact` for routine map context. Do not reread
  the generated Map Console HTML/CSS or `create_map_console.py` merely to
  discover stable UI capabilities. For existing layer state changes, enqueue
  `show-layer`, `hide-layer`, `select-layer`, or `set-opacity` instead of
  interacting with the browser DOM.
- For common NDVI display requests, try `map_console_agent.py quick-layer`
  before dataset search or custom recipes. It covers deterministic fast paths
  such as Sentinel-2 10 m NDVI and MODIS NDVI max/median seasonal composites,
  using the current AOI or viewport from Map Console state.
