# GeoAI with Python

**Source**: Qiusheng Wu, *GeoAI with Python: A Practical Guide to Open-Source Geospatial AI*  
**Edition context**: official web book, 430-page print edition, 23 chapters  
**Generated**: 2026-08-01

## How to use this guide

Read this reference through the EasyGEE router. The plugin registers only the
top-level `easygee` and `multimodal-geo-vector` skills.

- Ask for a workflow: “map water bodies from Sentinel-2”, “train a building detector”, or “compare two dates”. I will choose a task, data contract, baseline, and validation plan.
- Ask for a chapter or topic: `ch09`, `STAC`, `SAM`, `QGIS`, `tile overlap`, or `embeddings`. I will read the linked chapter before answering.
- Ask to diagnose an error. I will inspect the first failed boundary—environment, data shape/CRS, tiling, model configuration, inference, or export—before suggesting a rerun.
- If the task depends on current package APIs, data endpoints, model access, or GPU/CUDA compatibility, verify the live official documentation before executing.

## Operating loop: goal → evidence → adjustment

1. **Define the target and success evidence.** State the geographic area, dates, input sensors/bands, target object/value, output format, acceptable quality, and compute limit.
2. **Inspect before modeling.** Confirm raster shape, band count/order, dtype, nodata, CRS, resolution, bounds, temporal coverage, and vector label CRS/geometry. Never assume a downloaded file is model-ready.
3. **Choose the smallest useful method.** Use pre-trained/foundation models for rapid extraction; use supervised training when labels, repeatability, or domain adaptation justify it; use classical differencing as a change-detection baseline.
4. **Prepare spatially.** Reproject labels to the raster CRS, align grids, rasterize or vectorize deliberately, tile large rasters, and split by geographic scene/region where possible to avoid spatial leakage.
5. **Run a small baseline first.** Use one tile or a small sample, low epochs, and saved outputs. Check that the model learns and that predictions overlap the source imagery before scaling up.
6. **Validate the map, not only the metric.** Inspect overlays and failure cases; report task metrics plus spatial artifacts, edge effects, small-object loss, class imbalance, and transfer limitations.
7. **Export reproducibly.** Keep the model/config/data provenance, save georeferenced rasters or vectors, add geometric properties, filter artifacts with explicit thresholds, and preserve intermediate masks/probabilities when they explain decisions.

## Task selection

| Need | Task / output | Starting method |
|---|---|---|
| One label for each image/tile | Image recognition / class probabilities | Transfer learning with ResNet, EfficientNet, ViT, or ConvNeXt |
| Locate separate objects | Object detection / boxes and scores | COCO annotations; Faster R-CNN, YOLO, or transformer detector |
| Label every pixel by class | Semantic segmentation / class mask | U-Net or DeepLabV3+; raster/vector labels |
| Separate each object instance | Instance segmentation / instance IDs and masks | Mask R-CNN or SAM prompts |
| Convert one image domain to another | Image translation / super-resolution | `geoai.super_resolution`; inspect uncertainty and tiling seams |
| Compare two dates | Change detection / change raster or vector | aligned differencing first, then ChangeStar/deep model |
| Predict a continuous value per pixel | Pixel regression / continuous raster | segmentation architecture with regression head and valid-range checks |
| Extract unfamiliar objects with little labeling | Foundation model | SAM text/box/point prompts; validate and post-process |
| Ask questions about imagery | Vision-language model | caption/query/detection, then map returned geometries |
| Search or classify scenes at scale | Satellite embeddings | similarity, clustering, or lightweight classifier on vectors |

## Non-negotiable data contract

- **Spatial**: inputs and labels cover the same area; CRS is explicit; vector operations use a projected CRS when measuring area/length.
- **Raster**: band order and sensor-specific scaling are recorded; nodata is handled; multispectral channel count matches the model.
- **Tiles**: choose `tile_size` from object scale and GPU memory; use `stride < tile_size` for overlap; inspect edge artifacts and duplicate detections.
- **Splits**: make train/validation/test spatially independent where the scene permits; do not split adjacent chips from one image randomly and call that geographic generalization.
- **Outputs**: retain probability/score rasters for threshold analysis; vectorize only after mask cleanup; filter by area/shape only with a documented reason.

## Core frameworks and reusable methods

### The GeoAI pipeline

Treat every project as **acquire → inspect → prepare → learn/infer → evaluate → spatialize → validate → publish**. A failure in a later stage should send you back to the earliest violated contract, not trigger blind retries.

### Raster–label alignment

Use the raster as the reference grid. Reproject vector labels, rasterize with the reference transform, and verify an overlay before tiling. For masks, distinguish background, nodata, and “unknown”; they are not interchangeable.

### Patch-based scale-out

For large imagery, tile with overlap, infer batches, and stitch in the source CRS. Increase overlap when objects are cut at edges; reduce it only after checking seam quality and memory. Use a smaller window or batch size before changing the model when CUDA memory fails.

### Model choice by evidence

Prefer a pre-trained model when the target is visually recognizable and the goal is a fast baseline. Prefer supervised training when the target definition, sensor, geography, or output precision differs from the pre-training domain. Compare architectures only after the data pipeline and validation split are stable.

### Prompt → mask → geometry

For SAM, choose the weakest prompt that identifies the intended object, inspect the mask, save scores/IDs, then convert and regularize polygons. A prompt is not ground truth; measure precision/recall or sample-based accuracy before operational use.

### Continuous prediction discipline

For pixel regression, constrain valid ranges, mask invalid target pixels, evaluate with MAE/RMSE/R² plus residual maps, and compare predictions against a held-out date or region. A visually smooth raster can still be systematically biased.

## Chapter index

| # | Chapter | Use it for |
|---|---|---|
| [ch00](chapters/ch00-preface.md) | Preface | prerequisites, learning order, reproducibility |
| [ch01](chapters/ch01-introduction.md) | Introduction to GeoAI | task vocabulary and ecosystem |
| [ch02](chapters/ch02-environment-setup.md) | Setting Up Your Environment | Python, PyTorch, CUDA, QGIS prerequisites |
| [ch03](chapters/ch03-geospatial-data-essentials.md) | Geospatial Data Essentials | raster/vector/CRS/annotation contracts |
| [ch04](chapters/ch04-downloading-remote-sensing-data.md) | Downloading Remote Sensing Data | STAC, Planetary Computer, Overture, OSM |
| [ch05](chapters/ch05-interactive-mapping-visualization.md) | Interactive Mapping and Visualization | inspect, compare, and communicate results |
| [ch06](chapters/ch06-preparing-training-data.md) | Preparing Training Data | rasterize, tile, pair, split, audit labels |
| [ch07](chapters/ch07-image-recognition.md) | Image Recognition | scene/image classification |
| [ch08](chapters/ch08-object-detection.md) | Object Detection | boxes, COCO, mAP, sliding-window inference |
| [ch09](chapters/ch09-semantic-segmentation.md) | Semantic Segmentation | per-pixel class masks |
| [ch10](chapters/ch10-instance-segmentation.md) | Instance Segmentation | object IDs, masks, geometry |
| [ch11](chapters/ch11-image-translation.md) | Image Translation | super-resolution and uncertainty |
| [ch12](chapters/ch12-change-detection.md) | Change Detection | temporal differences and ChangeStar |
| [ch13](chapters/ch13-pixel-regression.md) | Pixel-Level Regression | NDVI and continuous surfaces |
| [ch14](chapters/ch14-sam-geospatial.md) | SAM for Geospatial Applications | text, point, box, batch, tiled, video prompts |
| [ch15](chapters/ch15-vision-language-models.md) | Vision-Language Models | captioning, QA, detection, point localization |
| [ch16](chapters/ch16-satellite-embeddings.md) | Satellite Embeddings | similarity, clustering, classifiers, temporal embeddings |
| [ch17](chapters/ch17-qgis-plugin-setup.md) | Setting Up the GeoAI QGIS Plugin | install, dependencies, GPU/model access |
| [ch18](chapters/ch18-qgis-tree-segmentation.md) | Tree Segmentation in QGIS | pre-trained ecological object models |
| [ch19](chapters/ch19-qgis-water-segmentation.md) | Water Segmentation in QGIS | OmniWaterMask, bands, OSM refinement |
| [ch20](chapters/ch20-qgis-vision-language-models.md) | Vision-Language Models in QGIS | Moondream panel workflows |
| [ch21](chapters/ch21-qgis-sam.md) | Segment Anything in QGIS | interactive and batch segmentation |
| [ch22](chapters/ch22-qgis-semantic-segmentation.md) | Semantic Segmentation in QGIS | no-code train/infer/vectorize |
| [ch23](chapters/ch23-qgis-instance-segmentation.md) | Instance Segmentation in QGIS | Mask R-CNN training and per-object output |

## Topic index

- **COG / Cloud Optimized GeoTIFF** → ch03, ch05
- **CRS / reprojection / alignment** → ch03, ch06
- **CUDA / GPU / memory** → ch02, ch09, ch14, ch17
- **embeddings / TESSERA / AlphaEarth** → ch16
- **image recognition** → ch01, ch07
- **image translation / super-resolution** → ch11
- **instance segmentation / Mask R-CNN** → ch10, ch23
- **object detection / COCO / mAP** → ch08, ch18, ch20
- **QGIS** → ch17–ch23
- **SAM / prompts / regularization** → ch14, ch21
- **semantic segmentation / U-Net** → ch09, ch19, ch22
- **STAC / Planetary Computer** → ch04, ch05
- **training chips / tiling / label quality** → ch06
- **VLM / Moondream / CLIP** → ch15, ch20
- **water / cloud / land cover** → ch09, ch19, ch22

## Supporting files

- [glossary.md](glossary.md) — concise definitions and chapter pointers.
- [patterns.md](patterns.md) — executable workflow patterns and trade-offs.
- [cheatsheet.md](cheatsheet.md) — one-page decisions, parameters, and checks.
- [references/source-map.md](references/source-map.md) — official sources, code/data links, and license boundaries.
- [references/qgis-training-inference.md](references/qgis-training-inference.md) — supplementary QGIS page present in the repository but not in the 23-chapter table of contents.

## Scope and limits

This guide synthesizes the official book and repository into an execution guide. APIs, model access, datasets, and QGIS plugin behavior can change. Verify live official sources before production use, and validate model predictions in the target domain before treating them as measurements.
