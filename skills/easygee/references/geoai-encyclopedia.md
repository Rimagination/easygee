# GeoAI Encyclopedia Integration

Use this reference when an EasyGEE request asks to execute a remote-sensing AI
method, choose a model family, prepare training data, run inference, or evaluate
spatial predictions. The bundled method library is a self-contained snapshot of
the `geoai-with-python` skill at
`references/geoai-with-python/SKILL.md`; it keeps the book's task-oriented
chapters, patterns, glossary, cheatsheet, and source map available inside the
EasyGEE plugin.

## Division of Responsibility

EasyGEE remains responsible for Earth Engine authentication, project and quota
checks, catalog discovery, server-side computation, exports, browser map state,
and the final handoff. The GeoAI Encyclopedia supplies the method layer for
remote-sensing AI. GeoMaster supplies broader GIS, CRS, scientific-domain, and
local data engineering knowledge.

Do not bulk-load all chapters. Route to the smallest useful chapter set and
keep the three layers distinct:

| Layer | Owns | Typical artifact |
| --- | --- | --- |
| EasyGEE | GEE/geemap orchestration and reproducibility | EE object, export task, map layer, dataset candidates |
| GeoAI Encyclopedia | AI task selection, data contract, training/inference/evaluation | training plan, model, prediction raster/vector, metrics |
| GeoMaster | General GIS correctness and local/cloud-native tooling | CRS-safe file, COG/STAC package, spatial table, GIS workflow |

## When To Route Here

Load this layer for object detection, semantic or instance segmentation, change
detection, image translation, pixel regression, image recognition,
embeddings/foundation models, SAM, vision-language models, QGIS GeoAI
workflows, training-data design, model inference, or spatial evaluation of AI
outputs. A request that only computes NDVI, selects a dataset, draws an AOI, or
exports a normal GEE image stays in the normal EasyGEE route unless the user
also asks for an AI method.

## Method Loop

Apply this loop to every GeoAI task:

1. **Acquire**: choose GEE, local files, STAC/COG, or a hybrid source; verify
   coverage, time range, resolution, bands, labels, licensing, and provenance.
2. **Inspect**: check CRS/projection, band names and scaling, nodata, masks,
   label schema, class balance, geometry validity, and spatial coverage.
3. **Prepare**: define chips/patches, tile size, overlap, resampling, feature
   stack, train/validation/test split, and leakage controls.
4. **Learn or infer**: select a baseline appropriate to the task, document
   pretrained weights and fine-tuning choices, and make device/dependency
   assumptions explicit.
5. **Evaluate**: use task-appropriate metrics and spatially honest splits;
   inspect errors by geography, class, season, sensor, and cloud/quality level.
6. **Spatialize**: restore CRS, transform pixel predictions into georeferenced
   rasters/vectors, preserve masks and nodata, and write provenance metadata.
7. **Validate and publish**: compare against a baseline, visually inspect map
   layers, check geometry and units, and report reproducible artifacts and
   unrun steps.

Never treat a model score alone as proof of map quality. A useful result must
retain spatial reference, source imagery, preprocessing, model/version,
thresholds, and evaluation scope.

## Task Router

Read the task chapter plus the cross-cutting data and evaluation guidance. The
chapter files are deliberately short and should be combined with the live
EasyGEE/GeoMaster references when the workflow touches GEE or GIS.

| User task | Read first | Add when needed |
| --- | --- | --- |
| General image recognition | `geoai-with-python/chapters/ch07-image-recognition.md` | `ch03`, `ch05`, `ch06` |
| Object detection | `geoai-with-python/chapters/ch08-object-detection.md` | `ch03`, `ch06`, `ch07` |
| Semantic segmentation | `geoai-with-python/chapters/ch09-semantic-segmentation.md` | `ch03`, `ch06`, `ch22` for QGIS |
| Instance segmentation | `geoai-with-python/chapters/ch10-instance-segmentation.md` | `ch06`, `ch14` for SAM |
| Image translation | `geoai-with-python/chapters/ch11-image-translation.md` | `ch03`, `ch06` |
| Change detection | `geoai-with-python/chapters/ch12-change-detection.md` | `ch03`, `ch04`, `ch06` |
| Pixel regression | `geoai-with-python/chapters/ch13-pixel-regression.md` | `ch03`, `ch06`, `ch07` |
| SAM/geospatial segmentation | `geoai-with-python/chapters/ch14-sam-geospatial.md` | `ch06`, `ch10`, `ch21` |
| Vision-language models | `geoai-with-python/chapters/ch15-vision-language-models.md` | `ch20` for QGIS |
| Satellite embeddings | `geoai-with-python/chapters/ch16-satellite-embeddings.md` | `ch03`, `ch06`, `ch07` |
| QGIS GeoAI | `geoai-with-python/chapters/ch17-qgis-plugin-setup.md` | `ch18`–`ch23` as applicable |
| Training/inference design | `geoai-with-python/SKILL.md` | `geoai-with-python/references/qgis-training-inference.md` |

The cross-cutting files are:

- `geoai-with-python/patterns.md`: reusable acquisition, tiling, inference,
  evaluation, and spatialization patterns.
- `geoai-with-python/cheatsheet.md`: compact task-to-method lookup.
- `geoai-with-python/glossary.md`: terminology and output semantics.
- `geoai-with-python/references/source-map.md`: source and attribution map.

## GEE and Local Handoff

For `gee_first`, use Earth Engine for catalog filtering, compositing, masking,
sampling, visualization, and controlled exports. For `local_first`, inspect
local imagery and labels before building a model. For `hybrid`, make the handoff
explicit before exporting or training:

```text
AOI/region:
time range and compositing:
source asset(s) and label asset(s):
bands/features and scale factors:
cloud/shadow/quality masks:
projection/CRS and spatial resolution:
tile size, overlap, and resampling:
train/validation/test spatial split:
export destination, format, and nodata:
model, weights, threshold, and device:
prediction output and metrics:
```

Keep Earth Engine objects server-side and avoid large `getInfo()` calls. Use
durable `ee.batch.Export.*` tasks for substantial imagery/tables, then validate
the exported file locally before training. Do not claim a model was trained or
an export completed unless the execution was actually run and the artifact was
checked.

## Quality Gates

Before finalizing a GeoAI workflow, confirm:

- the task type and target label are unambiguous;
- source imagery and labels are compatible in CRS, scale, time, and coverage;
- train/validation/test geography prevents spatial leakage;
- preprocessing preserves band semantics, scaling, masks, and nodata;
- class imbalance, thresholds, and uncertainty are discussed;
- metrics match the task and are reported with evaluation geography;
- predictions are georeferenced and have an explicit output schema;
- visual QA and a simple baseline were used where practical;
- licensing, pretrained weights, credentials, and data privacy are safe;
- missing dependencies, quota limits, credentials, and unrun tasks are stated.

## Conflict Policy

- If the request is about a GEE dataset or export rather than an AI method,
  EasyGEE's catalog and export references take precedence.
- If a choice depends on CRS, geometry, raster IO, or domain science, consult
  GeoMaster in addition to this layer; neither method layer overrides current
  official Earth Engine API/catalog documentation.
- If the user asks for a QGIS workflow, use the GeoAI QGIS chapter and GeoMaster
  GIS references, but keep EasyGEE's GEE-to-file handoff explicit.
- If a model or library is unavailable, provide a runnable method plan and
  clearly separate it from executed results.

## Final Reporting Contract

Report the method route (`gee_first`, `local_first`, or `hybrid`), the AI task,
the chapters/references consulted, the data contract, the model/inference
choice, evaluation design, artifact handoff, and any unrun or unverifiable
steps. This makes a GeoAI answer operational rather than a collection of
library names.

## Entry Routing Rules

- If the user asks to execute a remote-sensing AI method, read
   `references/geoai-encyclopedia.md` first, then load only the relevant
   `references/geoai-with-python/chapters/` file(s). Use its data contract,
   training/inference loop, spatial evaluation, and georeferenced-output rules
   as the method layer; do not treat a model name or score as a completed
   analysis.
- Use the GeoAI Encyclopedia as the task-method backend for remote-sensing AI.
  Read `references/geoai-encyclopedia.md`, choose the smallest relevant
  chapter, and preserve its data, spatial-split, evaluation, and
  georeferenced-output contracts. Do not bulk-load the bundled chapters or
  claim training/inference ran without a checked artifact.
