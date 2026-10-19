# Evaluation Prompts

Use this reference to forward-test whether `easygee` helps an agent solve
realistic GEE/geemap tasks better than a broad geospatial skill alone.

These prompts are intentionally phrased like user requests. A validating agent
should use the skill, produce a plan or artifact, and then run available
scripts such as `plan_gee_task.py`, `choose_geemap_tool.py`, and
`review_ee_code.py`. Do not give the validating agent the expected answer.

## Evaluation Rubric

Score each response from 0-2 for each criterion:

- Task framing: AOI, time range, unit, dataset, validation, and persistence are
  explicit or responsibly deferred.
- GEE semantics: lazy server-side objects, scale/projection, reducers, exports,
  and `getInfo()` are handled correctly.
- geemap usage: backend, map layers, drawing tools, exports, local-data bridges,
  and communication maps are chosen appropriately.
- Dataset QA: cloud/shadow masks, scale factors, QA bands, categorical/continuous
  semantics, and official catalog caveats are used.
- Safety and reproducibility: no secrets, no hidden clicked/drawn state, no
  accidental export start, and provenance/limitations are included.
- Review loop: generated code is checked with `review_ee_code.py` or equivalent
  reasoning before handoff.

A strong answer scores at least 9/12 and has no unacknowledged critical failure
such as missing auth/project setup, absent cloud masking for optical imagery, or
large `getInfo()` downloads.

## Prompt Set

### 1. S2 NDVI Notebook

> Build a geemap notebook to map 2024 Sentinel-2 NDVI for an AOI I will draw,
> show RGB and NDVI layers, and prepare a GeoTIFF export.

Expected pressure points: interactive AOI fallback, Cloud Score+/SCL masking,
explicit scale/region, non-started export, review warnings explained.

### 2. Flood Area By Watershed

> Estimate flood water area by watershed after a storm, preferably in a notebook
> where I can inspect the mask and export a CSV.

Expected pressure points: optical vs SAR choice, threshold caveat, pixelArea,
zonal stats, one-feature probe, table export instead of large `getInfo()`.

### 3. Land-Cover Classification

> Create a land-cover classification workflow with Sentinel or Landsat imagery
> and training polygons, then report accuracy.

Expected pressure points: predictor band order, class labels numeric/consecutive,
train/validation split, confusion matrix, QA mask, classification map export.

### 4. MODIS Vegetation Time Series

> Extract a monthly/16-day vegetation time series for multiple polygons and
> export the result for plotting.

Expected pressure points: MOD13Q1 scale factor, QA filtering, image-to-feature
mapping, export table, avoid large client-side downloads.

### 5. JS To Python Migration

> Convert this Earth Engine JavaScript project into a Python geemap notebook and
> make sure it can run outside the Code Editor.

Expected pressure points: geemap conversion helper, explicit initialization,
Code Editor UI assumptions, `print()`/`getInfo()` changes, export start review.

### 6. Communication Map

> Make a polished interactive map showing before/after urban expansion and share
> it as HTML/PNG.

Expected pressure points: split map/legends, map export vs analytic export,
change detection caveats, source dates, not treating a pretty map as proof.

### 7. Local Boundary File

> Use my local shapefile of field boundaries to summarize mean NDVI and export a
> table.

Expected pressure points: local vector bridge, CRS/validity/privacy, simplify
if huge, `geemap.zonal_stats` or `reduceRegions`, explicit scale and export.

### 8. Dataset Discovery

> I need the best GEE dataset for mapping population exposure to flood-prone
> areas and want a short notebook starter.

Expected pressure points: geemap/catalog search as discovery only, official
catalog verification, units/resolution/terms, task decomposition into hazard,
population, AOI, and zonal exposure summary.

### 9. HLS Cross-Sensor Series

> Build a harmonized Landsat 8/9 and Sentinel-2 reflectance time series with
> HLS, common bands, Fmask, sensor labels, and valid-observation counts.

Expected pressure points: HLSL30/HLSS30 choice, B5/B8A narrow-NIR mapping,
Fmask semantics, common 30 m grid, retained sensor provenance, residual-bias
check, and no reuse of Landsat C2 DN scaling.

### 10. Sentinel-1 Geometry-Aware Flood Comparison

> Build a Sentinel-1 SAR flood comparison using the same relative orbit and
> pass, explain dB versus linear ratios, speckle, incidence angle, and terrain
> shadow.

Expected pressure points: homogeneous acquisition filtering, dB/log-ratio
semantics, matched pre/post composites, valid acquisition counts, no universal
threshold, and orthorectification versus radiometric terrain limitations.

### 11. Temporal Composite Semantics

> Compare monthly median composites, mosaic, and qualityMosaic in a time
> series; preserve source dates, valid observation counts, and empty intervals.

Expected pressure points: reducer versus ordering semantics, synthetic
composite language, source-time band, observation support, interval boundaries,
quality-score bias, and explicit missing periods.

## Failure Smells

- Uses scene-level cloud metadata as the only cloud mask for Sentinel/Landsat.
- Uses `Map.addLayer()` output as evidence that an export/statistic is correct.
- Exports without region/scale or without stating whether the task was started.
- Uses `getInfo()` on a large image collection, feature collection, or time
  series table.
- Averages categorical class labels instead of summarizing area by class.
- Leaves drawn/clicked AOI state implicit.
- Omits project initialization or silently calls authentication.
- Copies upstream code without source attribution or license awareness.
- Calls an HLS/native merge "harmonized" after only renaming or resampling.
- Mixes Sentinel-1 pass/relative orbit or divides dB values as a power ratio.
- Describes a reducer or quality mosaic as one real acquisition and omits
  valid-observation count/source date.

## Scripts

- Use `scripts/audit_skill_coverage.py` after editing this skill to check that
  core references, scripts, source markers, planners, routers, and reviewer
  findings still work offline.
- Use `scripts/run_evaluation_prompts.py` to regression-test the eleven
  evaluation prompts across task planning, geemap routing, and dataset search.
