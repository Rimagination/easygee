# Workflow Templates

Use this reference when a user asks for a ready-to-edit notebook or script for
a common Earth Engine/geemap task. Prefer `scripts/scaffold_gee_template.py`
over writing these templates from memory.

## Template Generator

```bash
python scripts/scaffold_gee_template.py <EASYGEE_WORKSPACE>/s2_ndvi.ipynb --profile s2-ndvi-cloud-score --project YOUR_EE_PROJECT
python scripts/scaffold_gee_template.py <EASYGEE_WORKSPACE>/flood.py --mode script --profile s1-flood-area --project YOUR_EE_PROJECT
```

List available profiles:

```bash
python scripts/scaffold_gee_template.py --list-profiles
```

All templates:

- initialize with an explicit Earth Engine project placeholder,
- use an explicit fallback rectangle AOI,
- prepare exports without starting them automatically,
- include a small visual or numeric probe,
- preserve dataset ids, QA assumptions, and limitations in the generated file,
- pair reusable exports with data-layer and boundary/compute notes when the
  dataset semantics, AOI complexity, tiling, or task count affects correctness.

## Profiles

| Profile | Use For | Main Datasets | Review Before Export |
|---|---|---|---|
| `s2-ndvi-cloud-score` | recent NDVI/vegetation maps, clear-sky S2 composites | `COPERNICUS/S2_SR_HARMONIZED`, `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED` | Cloud Score+ threshold, AOI/date, export scale/region |
| `s1-flood-area` | cloudy flood/event water candidate mapping | `COPERNICUS/S1_GRD` | local threshold calibration, speckle/terrain/urban false positives, area units |
| `landsat-lst` | LST and urban heat maps | `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2` | QA_PIXEL mask, thermal conversion, seasonality |
| `modis-vi-timeseries` | long vegetation time series by polygons | `MODIS/061/MOD13Q1` | 0.0001 scale factor, SummaryQA mask, table export instead of large `getInfo()` |
| `dynamic-world-area` | land-cover class area summaries | `GOOGLE/DYNAMICWORLD/V1` | categorical label handling, probability/confidence, grouped `pixelArea` |
| `jrc-water-change` | historical water occurrence baseline | `JRC/GSW1_4/GlobalSurfaceWater` | historical baseline limit, occurrence threshold, area reducer scale |

## Template Selection Rules

- If the user asks for "best dataset" before asking for a template, run
  `scripts/search_gee_dataset.py "<task>" --workflow` first.
- If the user asks in Chinese, run both `plan_gee_task.py` and
  `search_gee_dataset.py`; the scripts include Chinese routing terms.
- If a template threshold is included, label it as a starting candidate, not a
  scientifically validated value.
- If the user supplies local boundaries, combine the template with
  `geemap.shp_to_ee` or `geemap.geojson_to_ee`, and check CRS/validity/privacy.
- If the deliverable is a notebook, run `scripts/review_ee_code.py` on it
  before handoff and explain any remaining warnings.

## Scripts

- Use `scripts/scaffold_gee_template.py <output> --profile <profile>` for
  stronger task-specific starter notebooks/scripts.
