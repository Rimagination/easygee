# Secondary Dataset And Method Notes

Use this reference only as article-derived candidate notes. The canonical route
for EasyGEE work remains `easygee/references/task-patterns.md`,
`easygee/references/dataset-qa-patterns.md`, `search_gee_dataset.py`, and the
official Earth Engine catalog.

Do not treat this file as proof that a dataset id, version, date range, QA mask,
or scale factor is current.

## Product-First Routes

Prefer curated GEE products when the user's target matches the product
definition and scale, but verify the current catalog entry before coding.

| User intent | Candidate route | Notes |
|---|---|---|
| Long-term surface water, historical water occurrence, yearly water | JRC Global Surface Water candidates | Good for stable water history; less suited to a single cloudy image edge. Verify product version and available years. |
| Forest cover or forest change | JRC/Hansen/ESA/ESRI candidates depending on definition | Check year, forest definition, resolution, and whether the product actually matches the user's forest definition. |
| Land cover comparison | ESA WorldCover, ESRI land cover, Dynamic World, MODIS land-cover candidates | Explain class definitions and temporal mismatch. Do not average class labels. |
| NDVI time series over large areas | MODIS VI or Landsat/Sentinel derived NDVI | MODIS is faster/coarser; Sentinel-2 is finer but cloud-sensitive. Prefer current MODIS collection versions after catalog check. |
| 10 m seasonal vegetation | Sentinel-2 SR/Harmonized or HLS candidates if cross-sensor cadence matters | Use current S2 masking guidance and explicit month windows. Verify HLS asset ids before use. |
| LST time series | MODIS LST, Landsat thermal/L2 ST | MODIS is easier for time series; Landsat is finer but sparse. |
| Precipitation | CHIRPS daily/monthly | Aggregate to month/year before charting. |
| Temperature/humidity/reanalysis | ERA5/ERA5-Land/TerraClimate | Document units and temporal aggregation. |
| Night lights | VIIRS DNB monthly composites | Mask unstable lights/clouds if needed. |
| Atmospheric NO2 | Sentinel-5P NO2 | Coarse pixels; use QA and report units. |
| Terrain | SRTM, ALOS AW3D30 | Use projected CRS for slope/area/distance-sensitive calculations. |
| Burned area | MODIS MCD64A1 | Thresholds/classes should be documented. |

If the product definition does not match the user intent, switch to a derived
workflow and say why.

## Verification Ladder

1. Run EasyGEE dataset search or open the official catalog entry.
2. Confirm collection version, bands, scale factors, QA, date range, and terms.
3. Compare the candidate with EasyGEE's existing workflow templates.
4. Use article-derived notes only to improve phrasing, prompts, or edge-case
   cautions.

## Derived Remote-Sensing Routes

Use derivation when the user asks for:

- A specific season, year, cloud-free composite, maximum/minimum index, or
  image-specific feature.
- A target class not directly available as a curated product.
- A current visible layer or user-selected image.
- A custom threshold, palette, chart, export, or AOI summary.

Common article-observed derived routes:

- Vegetation: Sentinel-2/Landsat/HLS reflectance -> mask -> NDVI/EVI/kNDVI ->
  seasonal reducer -> layer/stat/export.
- Water: Sentinel-2/Landsat/Sentinel-1 -> water index or SAR contrast ->
  OTSU/fixed threshold -> mask/vector/stats.
- Urban/impervious: Sentinel-2/Landsat indices plus land-cover products or ML;
  verify against samples because indices alone are brittle.
- Crop/phenology: multi-date Sentinel/Landsat/MODIS features, seasonal windows,
  RF/CART/SVM, and area stats.
- Cloud-gap recovery: use MODIS/Sentinel/Landsat fusion, temporal smoothing, or
  median composites; report the loss of spatial or temporal detail.

## Ambiguity Prompts

Ask one question when the method changes the meaning:

- Water: "要用 JRC 历史水体产品、当前影像的 NDWI/MNDWI+阈值、Sentinel-1 洪水提取，还是识别当前屏幕图像里的水体边界？"
- Rooftops/buildings: "你是要用已有建筑物产品、遥感影像训练/规则提取，还是对当前显示影像做视觉识别标注？"
- Vegetation: "你需要 10 m Sentinel-2 细节、MODIS 长时间序列稳定性，还是指定影像的像素级 NDVI？"
- Land cover: "你要使用现成土地覆盖产品，还是用你自己的样本训练分类器？"

After the user chooses, proceed without another broad discussion.

## Recipe Examples

### MODIS May-Sep NDVI Max

- Dataset: current MODIS vegetation index product such as `MODIS/061/MOD13Q1`
  when 250 m is acceptable.
- Filter: year and months 5-9.
- Scale: apply NDVI scale factor from the dataset docs.
- Reducer: `max` over the NDVI band.
- Output: layer and AOI mean/max/min or export at MODIS scale.

### Sentinel-2 Summer NDVI At 10 m

- Dataset: `COPERNICUS/S2_SR_HARMONIZED`.
- Filter: AOI, date window, months 6-8 or user-defined summer, cloud metadata.
- Mask: SCL/cloud probability strategy.
- Index: `normalizedDifference(['B8', 'B4'])`.
- Reducer: median for stable greenness, max for peak vegetation, percentile for
  robust high greenness.
- Output: 10 m layer/export; warn about cloud gaps and phenological timing.

### JRC Water Area Change

- Dataset: current JRC Global Surface Water product after catalog verification.
- Select water class/occurrence band.
- Convert to binary water mask with documented class/threshold.
- Multiply by `ee.Image.pixelArea()` and group by year or region.
- Chart/export area in square meters or hectares.

### OTSU Water From A Single Image

- Choose an index such as MNDWI.
- Compute histogram over AOI at an explicit scale.
- Derive threshold with OTSU.
- Apply water mask, optional morphology, and vectorization.
- Compare against base imagery or JRC/product reference when available.

### Classification Area Statistics

- Build predictor stack and labeled samples.
- Split samples using `randomColumn`.
- Train classifier and classify image.
- Validate with held-out samples.
- Use `pixelArea` plus grouped reducer to summarize area by class.

## Pitfalls To Name

- Article snippets may use superseded collections or old QA assumptions.
- Product class definitions are not interchangeable.
- Map tiles are previews, not proof of reducer/export correctness.
- Cloud masking and scale factors are dataset-specific.
- `bestEffort` can silently change reduction scale.
- Vectorizing raster masks can be expensive; simplify or export raster first
  when AOI is large.
- `reproject()` can force expensive computation and should be used sparingly.
- A seasonal "max" composite can select different dates per pixel; this is
  correct for peak greenness but not for a single-date map.
