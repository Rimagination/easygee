# Boundary And Compute Patterns

Use this reference when AOI complexity, boundary source, export region, reducer
scale, tiling, or EECU/performance risk affects a GEE/geemap workflow.

## Boundary Record

Before expensive computation, record:

| Field | What To Check |
|---|---|
| AOI source | Drawn AOI, viewport, named place, uploaded asset, local file, generated grid, or global. |
| Exactness need | Exact geometry, buffered geometry, bbox approximation, or visual-only extent. |
| Geometry risk | Feature count, vertex count, holes, multipart geometry, long thin shapes, invalid geometry. |
| Filter geometry | Usually bbox or simplified bounds for collection filtering. |
| Final geometry | Exact ROI for final statistics, masks, or export when exactness matters. |
| Scale risk | Pixel count implied by region and scale; coarser test scale if needed. |
| Output risk | Large raster, many tiles, large table, many task submissions, or local download timeout. |

Use the current Map Console AOI when present. If AOI is cleared, EasyGEE may use
the processing viewport for previews, but exports and statistics should say so
explicitly before running.

## Practical Rules

- Use `filterBounds(roi.bounds())` or a simplified bbox for coarse collection
  filtering when it reduces catalog work.
- Use the exact ROI for final `reduceRegion`, `reduceRegions`, masks, and
  export `region` when boundary precision matters.
- Avoid early repeated `.clip()` calls unless clipping is needed for correctness
  or export size. Prefer filtering and masking first.
- Avoid `FeatureCollection.geometry()` on very large collections when a
  collection-aware reducer or per-feature workflow is available.
- For reducers, specify `geometry`, `scale`, and `maxPixels` or an intentional
  `bestEffort`/`tileScale` choice. Explain the tradeoff when using them.
- For local downloads, switch to Drive/Cloud Storage/Asset exports when the AOI
  is large, geometry is complex, or tile stitching would be fragile.

## Tiling Decision

Tile only when the algorithm is tile-safe and the user needs a large raster or
large-area local handoff.

Usually tile-safe:

- per-pixel spectral indices,
- independent composite/export patches,
- per-pixel trends after each tile uses the same date filters and masks,
- neighborhood operations when each tile includes enough buffer,
- ML inference when the model is already fixed.

Use caution or avoid tiling:

- PCA/RSEI or any workflow needing global normalization,
- reducers that require whole-AOI statistics,
- connected components, segmentation, region-growing, or watershed operations,
- classification training where sample distribution changes by tile,
- mosaics where tile edges would change visual or numeric interpretation.

## Tiled Export Pattern

A safe tiled export should record:

- grid CRS and tile size,
- number of candidate tiles and maximum allowed task count,
- whether tiles are clipped to exact AOI or exported as full grid cells,
- scale, CRS, format, dtype, nodata/mask behavior,
- task naming convention and destination folder/bucket/asset prefix,
- how the user will mosaic or consume tiles downstream.

For generated GEE code, expose a dry-run path that reports tile count and export
parameters before starting tasks. Start tasks only when the user explicitly asks
or passes a flag such as `--start-export`.

## Workload Tags

For long scripts, set a readable workload tag when available:

```python
try:
    ee.data.setDefaultWorkloadTag("easygee-task-name")
except Exception:
    pass
```

Do not rely on workload tags for correctness. They are for monitoring and
debugging, not a substitute for task metadata persisted in the EasyGEE workbench.

## EasyGEE Workbench Behavior

- Keep AOI and processing extent separate. Clearing AOI should not delete result
  layers or task records.
- Export tasks should store boundary summary: AOI source, bbox/area if known,
  scale, and whether exact or viewport geometry was used.
- For large exports, offer test scale, smaller date window, or tiled export
  before changing the scientific method.
- Do not submit many tasks silently. Show the tile count and ask/confirm when
  task count, Drive clutter, or quota pressure is likely.

## Operating Rules

- Treat boundary and compute risk as a separate gate. Use bbox/simplified
  geometry for coarse filtering when helpful, exact AOI for final statistics or
  exports when needed, and tiled export only for tile-safe algorithms after
  reporting tile count and task naming.
