# Article-Observed Workflow Patterns

This reference distills recurring task motifs from the 153-article GEE album.
Use it as an idea index after consulting EasyGEE's official-doc-grounded
references. It is not a maintained template library.

## Trust Boundary

- Verify dataset ids, collection versions, band names, scale factors, QA masks,
  and export syntax against official docs before use.
- Treat article snippets as historical examples. Do not copy them into a user
  deliverable without review.
- Prefer `easygee/references/task-patterns.md`,
  `easygee/references/dataset-qa-patterns.md`, and
  `easygee/references/workflow-templates.md` for canonical workflow details.
- Keep source articles as attribution and retrieval context, not as primary
  evidence.

## Known Age-Related Risks

The album spans several years of GEE practice. Some examples may mention older
or superseded patterns. Before reuse, check for:

- Landsat Collection 1 examples such as `LANDSAT/LC08/C01/T1_SR`; current
  EasyGEE workflows should generally prefer Landsat Collection 2 Level 2.
- MODIS v006 examples such as `MODIS/006/MOD13Q1`; current EasyGEE templates
  use `MODIS/061/MOD13Q1`.
- Sentinel-2 QA60-only cloud masking. EasyGEE favors Cloud Score+, SCL, or
  cloud-probability workflows depending on the task.
- Older JRC water/forest product versions or date ranges.
- Fixed thresholds copied across regions or sensors without local validation.

## ImageCollection Recipe Motif

Use an explicit recipe whenever the user asks for a temporal or seasonal layer,
for example "2024 年夏季 NDVI", "5-9 月 NDVImax", or "某年有效观测次数".

Recipe fields to verify:

- Dataset id and whether it is official GEE, community catalog, or user asset.
- Spatial extent: AOI, current viewport, administrative boundary, or points.
- Time window and calendar filters. For seasonal requests, include month range.
- QA/mask strategy and scale factors.
- Band/index formula and renamed output bands.
- Temporal reducer/composite: median, mean, max, min, percentile,
  `qualityMosaic`, monthly/yearly grouping, or valid-observation count.
- Visualization parameters: bands, min/max, palette, opacity.
- Statistics/export parameters: scale, CRS/projection, region, maxPixels,
  format, destination, and task name.

Article-inspired server-side mapping motif:

```javascript
function addIndex(img) {
  var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return img.addBands(ndvi).copyProperties(img, ['system:time_start']);
}

var seasonal = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filterDate('2024-05-01', '2024-10-01')
  .filter(ee.Filter.calendarRange(5, 9, 'month'))
  .map(maskS2)
  .map(addIndex);

var ndviMax = seasonal.select('NDVI').max().clip(roi);
```

## Preprocessing And QA Motifs

Common themes:

- Cloud/shadow masking matters more than the reducer. Choose the mask from the
  dataset: Landsat QA_PIXEL/QA_RADSAT for Collection 2 Level 2, Sentinel-2 SCL
  or cloud probability for SR, MODIS QA where applicable.
- Handle scale factors before indices and statistics when the dataset stores
  scaled integer reflectance, temperature, or aerosol values.
- Use `updateMask` to hide invalid pixels while preserving the image footprint;
  use `unmask` only when a replacement value has analytical meaning.
- Count valid observations with a mapped valid mask and `.sum()` when cloud
  gaps or sample reliability matter.
- Reproject only when a downstream algorithm truly needs a fixed projection;
  otherwise let Earth Engine choose projection at reduction/export scale.

## Index And Raster Statistics Motifs

Recurring index tasks include NDVI, EVI, kNDVI, MNDWI/NDWI, LST, night lights,
NO2, precipitation, soil moisture, and terrain-derived metrics.

Pattern:

1. Select and scale bands.
2. Add the derived band with `addBands`.
3. Keep `system:time_start`.
4. Reduce by image, month, year, class, region, or samples.
5. Return a layer, chart, table, CSV, or export image depending on the request.

Use `reduceRegion` for one geometry, `reduceRegions` for many features,
`sampleRegions` for labeled samples, and `sample` for exploratory points. Use
`tileScale` and `maxPixels` deliberately when reductions are large.

## Time-Series Motifs

Time-series articles repeatedly use MODIS NDVI/LST, Landsat NDVI/LST, CHIRPS
precipitation, ERA5 variables, soil moisture, NO2, and night lights.

Good time-series outputs are `FeatureCollection`s with at least:

- `date` or `year`/`month`
- value fields with units or scale-factor notes
- region/class/sample identifiers when there are multiple series
- source dataset id and reducer

Useful methods:

- Monthly/yearly grouping with `ee.List.sequence`, `ee.Date.fromYMD`, and
  `filterDate`.
- Seasonal windows with `calendarRange`.
- Gap-aware composites and valid-observation counts.
- Smoothing such as Savitzky-Golay only after documenting the window length,
  polynomial order, and edge behavior.
- Dual-axis charts only when two variables have different units; label both.

## Classification And Clustering Motifs

The collection discusses CART, RF, SVM, maximum entropy, KNN, K-Means, minimum
distance, Bayesian ideas, class area, feature importance, sample splits, and
classification comparison. Treat these as method families to consider, not as a
ranking of best algorithms.

Classification checklist:

- Define the class system and label source before model choice.
- Build a predictor stack from bands, indices, terrain, texture, SAR, seasonal
  composites, or product layers.
- Use `sampleRegions` with clean training geometries and a `class` property.
- Add a random split column for train/test when enough samples exist.
- Train server-side classifiers and classify an image, not individual pixels
  client-side.
- Report confusion matrix, accuracy, kappa, and class-specific errors when
  validation samples exist.
- For area statistics, classify first, multiply by `pixelArea`, then use a
  grouped reducer by class.

For unsupervised K-Means, do not treat cluster ids as classes until they are
interpreted against imagery, samples, or known products.

## Water, Thresholds, And Edge Motifs

Water extraction appears in three forms:

- Product-backed water: JRC Global Surface Water or other curated layers for
  long-term occurrence, yearly water, recurrence, or historical comparison.
- Optical derivation: NDWI/MNDWI/AWEI plus fixed threshold, OTSU histogram
  threshold, or local/adaptive thresholding.
- Event/flood derivation: Sentinel-1 SAR or optical pre/post comparison when
  clouds, timing, or flood dynamics make optical-only methods unreliable.

When using OTSU:

1. Define the candidate water index and AOI.
2. Build a histogram with a documented scale and maxPixels.
3. Compute threshold from between-class variance.
4. Apply morphology or connected-pixel filtering only when appropriate.
5. Validate visually and, when possible, against samples or known water data.

Edge detectors such as Canny or zero-crossing are useful for boundary cues and
QA, but they are not a complete class extraction workflow by themselves.

## Visualization, Charts, And UI Motifs

Visualization articles emphasize practical map communication:

- Use palettes with known semantics: vegetation, water, temperature, land
  cover, night lights, NO2, and uncertainty should not share ambiguous ramps.
- Add legends for categorical products and thresholds.
- Use `ui.Chart.image.series`, `ui.Chart.feature.byFeature`, histograms, and
  scatter charts for diagnostics before making claims.
- Keep UI apps small: map, AOI/selector controls, chart panel, legend, and
  export/download cues. Do not hide key assumptions in callbacks.
- For EasyGEE Map Console work, sync output as normal layers and layer style
  changes rather than adding task-specific toolbar buttons.

## Export Motifs

Use Drive/Asset exports only after the recipe is explicit.

Export checklist:

- `description` and file prefix are meaningful and deterministic.
- `region` is the AOI geometry, not an accidentally unbounded image footprint.
- `scale` matches dataset resolution and analysis purpose.
- CRS is set only when needed; otherwise document the native/projection choice.
- `maxPixels` is high enough for the AOI but not a substitute for checking
  extent mistakes.
- For tables, include date, region id, reducer, units, and dataset id.
- Tell the user whether the Earth Engine task was only created or actually
  started.
