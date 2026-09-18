# Export Patterns

Use this reference when a user describes an Earth Engine/geemap export in
natural language. Export requests often hide several separate decisions:
product type, destination, format, AOI, scale/projection, ImageCollection
materialization, and task lifecycle.

## First Step

Run:

```bash
python scripts/plan_gee_export.py "<natural language export request>" --json
```

Use the result to decide whether to proceed with safe defaults or ask one
clarifying question. Do not infer irreversible or expensive export settings
silently.

## Product Types

- **Image/raster**: NDVI/LST/DEM/classification/mask/image layer/GeoTIFF/COG.
  Export a single `ee.Image`, not a raw `ImageCollection`.
- **Table/CSV**: zonal statistics, time series, summaries, chart-ready rows,
  feature properties, area by class. Export a `FeatureCollection`.
- **Vector**: polygons, points, boundaries, building footprints, GeoJSON/SHP/KML.
  In Earth Engine this still uses table exports.
- **Map communication artifact**: HTML/PNG/JPG map output. This is a visual
  product, not an analytical export.
- **Video/GIF**: animation or timelapse from an image collection.

## Backend Decision

| User intent | Preferred backend | Typical functions |
|---|---|---|
| Large raster to Drive | EE batch task | `ee.batch.Export.image.toDrive` |
| Large raster to Cloud Storage | EE batch task | `ee.batch.Export.image.toCloudStorage` |
| Persist reusable EE result | EE asset export | `ee.batch.Export.image.toAsset`, `ee.batch.Export.table.toAsset` |
| Zonal stats/time series CSV | EE batch table export | `ee.batch.Export.table.toDrive` |
| Small notebook raster download | geemap local helper | `geemap.ee_export_image`, `geemap.download_ee_image` |
| Small vector/table download | geemap local helper | `geemap.ee_export_vector`, `geemap.ee_to_csv`, `geemap.ee_to_gdf` |
| Shareable map page/screenshot | geemap map export | `Map.to_html`, `Map.to_image` |

For EasyGEE workbench actions, prefer direct `ee.batch.Export.*` task creation
when the result should be tracked in the task panel. geemap helpers are useful
in notebooks and local exploration, but some helpers start tasks immediately
and can hide task metadata unless the agent records it.

## ImageCollection Rule

An Earth Engine `ImageCollection` is not an export product by itself for raster
exports. It must first be reduced or composited into an `ee.Image`, for example:

- seasonal/monthly median or mean composite,
- `max()` for NDVImax or water occurrence style products,
- `qualityMosaic()` when a quality band should select best pixels,
- `mosaic()` when draw order is the intended behavior,
- map images to features when the desired result is a time-series table.

If the user's wording says "MODIS 2024 May-Sep NDVImax", the agent should read
that as: filter MODIS by AOI/date/months, apply QA/scale factor, select or
derive NDVI, reduce with `max()`, then export the resulting image.

## Parameters To Surface

Always surface these before or immediately after creating an export task:

- product type and source recipe,
- destination and naming: Drive folder/file prefix, Cloud Storage bucket/path,
  Earth Engine asset id, BigQuery table, or local path,
- AOI/region and whether it came from current AOI, map viewport, drawn geometry,
  selected layer, or explicit coordinates,
- scale, CRS, and `crsTransform` when alignment matters,
- format and options: GeoTIFF, COG, CSV, SHP, GeoJSON, KML/KMZ, TFRecord,
- masked/nodata behavior for rasters,
- `maxPixels`, file tiling/sharding options when relevant,
- task status: prepared, started, running, completed, failed, or cancelled.

## Clarification Triggers

Ask one short question when the request leaves a decision that changes the
scientific result or the user's workflow:

- destination is missing and both local download and Drive task are plausible,
- scale/resolution is missing and cannot be inferred from a selected dataset,
- ImageCollection reducer is missing (`max`, `median`, `mean`, `mosaic`, etc.),
- table vs raster is ambiguous, for example "导出 NDVI 结果" after a zonal
  statistics conversation,
- output format is unclear and downstream software matters,
- AOI is missing and using the current viewport would surprise the user.

If a safe project convention exists, proceed with it but state the default in
the task summary.

## EasyGEE Workbench Behavior

- Do not add task-specific toolbar buttons for exports.
- Create or start exports in the background, then sync task metadata into the
  Map Console task panel.
- Keep Drive/GCS/Asset shortcuts separate from task records; the task panel is
  the source of truth.
- For Drive exports, the exact final file URL may not be known at creation
  time. Store folder, prefix, task id, and a Drive search/open shortcut.
- Deleting or hiding an AOI layer must not delete remote-sensing result layers
  or task records.

## Reporting Template

When answering the user after an export action, report:

- `task`: description/name and task id if available,
- `destination`: folder/bucket/asset/table/local path,
- `product`: data kind, dataset/recipe, date range, bands/statistic,
- `region`: AOI source and approximate extent,
- `scale/projection`: scale, CRS/transform assumption,
- `status`: prepared or started, plus how to monitor/open the result.

## Scripts

- Use `scripts/plan_gee_export.py "<export request>" --json` before handling
  natural-language export/download requests. It classifies product type,
  destination, backend (`ee.batch.Export.*`, geemap local helper, or map
  export), format, AOI source, scale, ImageCollection materialization, missing
  parameters, and the task lifecycle policy.

## Operating Rules

- Treat export requests as a structured contract. Parse product kind
  (raster/table/vector/map/video), destination, format, AOI, scale/CRS,
  ImageCollection reducer, naming, and start policy before creating tasks. For
  durable workbench exports, prefer direct `ee.batch.Export.*` calls so EasyGEE
  can persist task id, status, destination, and parameters; use geemap local
  download helpers mainly for notebook-scale local outputs.
