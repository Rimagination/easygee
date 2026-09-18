# Data Layer Records

Use this reference when a task depends on dataset choice, band semantics,
physical units, QA masks, scale factors, community catalog rows, or output
formats. It turns a vague "use this dataset" decision into a small auditable
record that another agent or user can inspect later.

## When To Use

Create or summarize a data-layer record when:

- the user asks which GEE dataset to use,
- the workflow mixes official and community datasets,
- a result depends on band names, scale factors, offsets, QA bits, class codes,
  or nodata behavior,
- data will be exported to Drive, Cloud Storage, Asset, BigQuery, or local files,
- downstream local GIS/ML work needs the same semantics preserved.

For quick map-only previews, a compact record inside layer `recipe` metadata is
enough. For reusable notebooks, scripts, or exports, write the record into the
notebook/script comments or a Markdown run note.

## Record Fields

Use these fields as the minimum contract:

| Field | What To Record |
|---|---|
| Target variable | What the user wants to measure, classify, visualize, or export. |
| Dataset source | Official Earth Engine catalog, GEE Community Catalog, user asset, local file, or derived layer. |
| Dataset id | Exact `ee.Image`, `ee.ImageCollection`, or `ee.FeatureCollection` id when known. |
| Time range | Requested range, compositing window, cadence, and temporal reducer. |
| Spatial extent | AOI source: drawn AOI, viewport, named place, uploaded asset, local vector, bbox, or global. |
| Scale/projection | Native scale if known, chosen analysis/export scale, CRS/transform when alignment matters. |
| Bands/fields | Names, meanings, units, valid ranges, scale/offset, dtype, nodata/mask, and QA rules. |
| Transformations | Formula, reducer, thresholds, classification labels, storage scaling, and reversibility. |
| Output target | Map layer, statistic, CSV/table, time series, GeoTIFF/COG, Asset, BigQuery, or communication map. |
| Verification | Official catalog/docs checked, community docs checked, sample probed, or still `UNKNOWN`. |

Never infer band schemas, QA rules, or scale factors from a community CSV row
alone. Community rows are discovery hints; dataset docs and sample code are the
verification layer.

## Dataset Candidate Table

For dataset selection requests, produce a compact shortlist before coding:

| Source | Dataset ID | Title | Type | Why It Fits | Limits | License/Terms | Verification |
|---|---|---|---|---|---|---|---|
| Official/Community/User |  |  | image/image_collection/table |  |  |  | checked/UNKNOWN |

Prefer official catalog datasets when they answer the question at suitable
resolution and cadence. Use community datasets when they offer a unique product,
but label them visibly as community-hosted and carry license/docs links forward
into the result.

## Band And Transformation Table

Before numeric transforms or exports, record:

| Band/Field | Meaning | Unit | Raw Range | Scale/Offset | Valid Range | QA/Mask | Export Dtype |
|---|---|---|---|---|---|---|---|
|  |  | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |  |

Then record transformations:

| Step | Input | Formula/Reducer | Output Meaning | Output Range | Risk |
|---|---|---|---|---|---|
|  |  |  |  | UNKNOWN |  |

Examples:

- NDVI: `(NIR - Red) / (NIR + Red)`, continuous index, usually `[-1, 1]`.
- Class area: class mask multiplied by `pixelArea()`, summed by class; do not
  average categorical class labels.
- LST: apply documented scale/offset, then state Kelvin/Celsius conversion.
- MODIS VI: apply the product scale factor before statistics or export.

## EasyGEE Workbench Behavior

- Store compact semantics in layer `recipe` metadata: dataset id, source label,
  bands/index, time range, reducer, scale, QA/mask choice, and visualization.
- Show official/community provenance in dataset detail and layer summaries.
- If a user asks "why this dataset", answer from the data-layer record rather
  than rereading generated HTML or guessing from the visible layer name.
- When exporting, attach the data-layer record fields to the task summary so a
  Drive file can be traced back to the source recipe.

## Clarification Triggers

Ask one focused question when missing semantics changes the result:

- official-only vs community-allowed datasets,
- target variable or class definition is vague,
- scale/resolution is finer than the dataset can support,
- time aggregation is unspecified for an ImageCollection,
- QA/cloud/shadow mask choice affects interpretation,
- output is ambiguous between raster, table, vector, or map artifact.

If a routine default is safe, proceed but mark it as assumed in the record.

## Operating Rules

- Treat data-layer semantics as part of the deliverable, not hidden background
  reasoning. For datasets and exports, record target variable, official or
  community source, dataset id, time range, AOI source, bands/fields, units,
  scale/offset, QA/mask, transformations, output target, and verification
  status.
