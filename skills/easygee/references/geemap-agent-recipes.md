# geemap Agent Recipes

Use this reference when building geemap notebooks, scripts, conversion flows,
interactive inspectors, exports, local-data bridges, or educational examples.

## Backend Choice

Choose the map backend before writing the notebook:

- **Local Jupyter / JupyterLab**: prefer `import geemap`; it uses ipyleaflet and
  ipywidgets, supports bidirectional interactions, drawing tools, click events,
  inspectors, and richer input capture.
- **Google Colab**: prefer `import geemap.foliumap as geemap` or
  `import geemap.core as geemap` for official examples when ipyleaflet support
  is not available or is limited.
- **Static report / shareable HTML**: use folium-style exports or geemap HTML
  export; document that static maps cannot capture future user clicks.
- **App/QGIS integration**: keep analysis functions independent from UI code so
  QGIS, notebooks, and browser apps can reuse them.

## Minimal Notebook Skeleton

For a blank workflow, prefer generating a scaffold first:

```bash
python scripts/scaffold_geemap_workflow.py <EASYGEE_WORKSPACE>/s2_ndvi.ipynb --mode notebook --project my-ee-project
```

Then edit the generated AOI, dataset, cloud masking, reducer, and export cells
instead of composing an unstructured notebook from scratch.

The scaffold defaults to `COPERNICUS/S2_SR_HARMONIZED` with Cloud Score+
masking via `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`. Use
`--no-s2-cloud-score` only when the workflow deliberately supplies another
pixel-level cloud/shadow mask.

Before handoff, run:

```bash
python scripts/review_ee_code.py <EASYGEE_WORKSPACE>/s2_ndvi.ipynb
```

Treat warnings as review prompts. Fix real issues or record why the workflow is
intentionally different.

```python
import ee
import geemap

PROJECT = "my-earthengine-project"
ee.Initialize(project=PROJECT)

Map = geemap.Map()
Map.add_basemap("HYBRID")
Map
```

Then add:

1. AOI cell: drawn ROI fallback plus explicit geometry fallback.
2. Dataset cell: dataset id, filters, QA/cloud mask, selected bands.
3. Visual probe cell: `Map.addLayer(...)`, `Map.centerObject(...)`.
4. Numeric probe cell: small reducer/sample.
5. Export cell: Drive/Cloud/Asset/local geemap export with explicit params.
6. Provenance cell: source URLs, date, project id placeholder, limitations.

## Interactive AOI Pattern

```python
feature = Map.draw_last_feature
if feature is None:
    roi = ee.Geometry.Rectangle([119.8, 30.0, 120.5, 30.5])
else:
    roi = ee.Feature(feature).geometry()
Map.centerObject(roi, 10)
```

Agent rule: if the user did not draw/select an AOI in the current notebook
session, provide an explicit fallback and label it as a placeholder.

## Visualization Pattern

```python
vis = {
    "bands": ["B4", "B3", "B2"],
    "min": 0,
    "max": 3000,
    "gamma": 1.1,
}
Map.addLayer(image, vis, "S2 true color 2024 median", shown=True, opacity=0.85)
```

Always choose layer names that encode dataset, metric, date/composite, and AOI
when helpful. For single-band indices, use `palette`, `min`, and `max`.

## Inspector And Plotting

- Use geemap inspector/click workflows to validate map values before exporting.
- Use chart notebooks for `FeatureCollection`, `Image`, and `ImageCollection`
  plots when the user needs a visual diagnostic.
- Convert interactive clicks into reproducible geometry or point lists before
  finalizing the workflow.

## Export Recipes

### Local GeoTIFF Through geemap

```python
geemap.ee_export_image(
    image.clip(roi),
    filename="output.tif",
    scale=30,
    region=roi,
    file_per_band=False,
)
```

Use for modest images and local exploration. For large outputs, prefer
asynchronous Earth Engine exports.

### Drive Export

```python
geemap.ee_export_image_to_drive(
    image=image.clip(roi),
    description="s2_ndvi_2024",
    folder="earthengine_exports",
    region=roi,
    scale=10,
)
```

### Zonal Statistics

```python
geemap.zonal_stats(
    image,
    zones,
    "zonal_stats.csv",
    stat_type="MEAN",
    scale=30,
)
```

Allowed output formats in geemap examples include CSV, SHP, JSON, KML, and KMZ;
stat types include MEAN, MAXIMUM, MINIMUM, MEDIAN, STD, MIN_MAX, VARIANCE, and
SUM.

## JavaScript To Python Migration

Use geemap conversion tools for first-pass migration, then review manually:

```python
from geemap.conversion import js_to_python_dir
js_to_python_dir(in_dir="gee-js", out_dir="gee-python", use_qgis=True)
```

Manual review must check:

- Code Editor-only UI assumptions,
- implicit `print()`/`getInfo()` behavior,
- JavaScript anonymous function conversion,
- `Map` object backend,
- Python package imports,
- auth/project initialization,
- export task start behavior.

## Local Data Bridge

- Small GeoJSON: convert to Earth Engine geometry/FeatureCollection.
- Shapefile: geemap can use shapefiles with Earth Engine without uploading to
  the user's GEE account; still check size, CRS, privacy, and simplification.
- Large private vector/raster: process locally with GeoPandas/Rasterio/GDAL and
  only pass derived AOIs/statistics when possible.

## ML With geemap

For local scikit-learn random forest style examples:

1. Train locally on a small, documented feature table.
2. Convert the estimator into an Earth Engine-compatible classifier.
3. Apply to an Earth Engine image.
4. Preserve feature band order and class labels.
5. Record training data source, model parameters, and validation method.

Do not imply local ML conversion generalizes to arbitrary estimators. Keep the
example constrained to supported tree ensemble patterns unless verified.

## Agent Notebook Quality Bar

A finished notebook should:

- run top-to-bottom after credentials/project setup,
- not rely on hidden clicked/drawn state unless that interaction is documented,
- include small probes before expensive exports,
- include exact dataset ids and source URLs,
- keep credentials and project-specific secrets out of the file,
- preserve output paths and export task ids,
- include a final "limitations and next checks" cell.

## Scripts

- Use `scripts/scaffold_geemap_workflow.py` to generate a clean notebook or
  headless script skeleton with explicit project, AOI, dataset, probes, and
  non-started export task code.
- Use `scripts/choose_geemap_tool.py "<requested action>"` to route a notebook
  or workflow action to likely geemap functions and cautions.
