#!/usr/bin/env python
"""Route EasyGEE requests to GEE, local GIS, hybrid, catalog, or browser methods."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


GEE_KEYWORDS = (
    "gee", "earth engine", "google earth engine", "geemap", "sentinel",
    "landsat", "modis", "viirs", "dynamic world", "imagecollection",
    "featurecollection", "ee.", "云端", "地球引擎", "谷歌地球引擎",
)

CATALOG_KEYWORDS = (
    "catalog", "dataset", "data set", "which data", "find data",
    "search data", "gee 数据", "gee数据", "数据集", "目录", "找",
    "搜索", "适合",
)

LOCAL_KEYWORDS = (
    "local", "geotiff", "tif", "tiff", "shapefile", "geojson",
    "geopackage", "gpkg", "rasterio", "geopandas", "gdal", "shapely",
    "pyproj", "postgis", "point cloud", "las", "laz", "osmnx",
    "networkx", "本地", "矢量", "栅格", "区划", "边界文件", "路网",
    "点云",
)

LOCAL_OPERATION_KEYWORDS = (
    "crs", "projection", "projected", "buffer", "spatial join",
    "overlay", "clip", "window", "windowed", "area", "distance", "cog",
    "stac", "planetary computer", "dask", "xarray", "zarr", "parquet",
    "投影", "坐标系", "缓冲区", "空间连接", "叠置", "裁剪", "窗口",
    "面积", "距离",
)

ML_KEYWORDS = (
    "machine learning", "deep learning", "random forest", "classification",
    "classify", "train", "model", "cnn", "torch", "xgboost", "机器学习",
    "深度学习", "随机森林", "分类", "训练", "模型",
)

GEOAI_KEYWORDS = (
    "geoai", "remote sensing ai", "remote-sensing ai", "image recognition", "object detection",
    "semantic segmentation", "instance segmentation", "segmentation",
    "change detection", "pixel regression", "image translation",
    "segment anything", "vision-language", "vision language model",
    "satellite embedding", "satellite embeddings", "foundation model",
    "qgis geoai", "qgis ai", "qgis plugin", "deep learning",
    "\u76ee\u6807\u68c0\u6d4b", "\u8bed\u4e49\u5206\u5272", "\u5b9e\u4f8b\u5206\u5272",
    "\u53d8\u5316\u68c0\u6d4b", "\u50cf\u7d20\u56de\u5f52", "\u56fe\u50cf\u7ffb\u8bd1",
    "\u5206\u5272", "\u89c6\u89c9\u8bed\u8a00", "\u536b\u661f\u5d4c\u5165",
    "\u57fa\u7840\u6a21\u578b", "\u9065\u611fai", "\u9065\u611f ai",
)

GEOAI_CHAPTER_RULES = (
    (("image recognition", "classification", "classify", "\u56fe\u50cf\u8bc6\u522b", "\u5206\u7c7b"), "geoai-with-python/chapters/ch07-image-recognition.md"),
    (("object detection", "\u76ee\u6807\u68c0\u6d4b"), "geoai-with-python/chapters/ch08-object-detection.md"),
    (("semantic segmentation", "\u8bed\u4e49\u5206\u5272"), "geoai-with-python/chapters/ch09-semantic-segmentation.md"),
    (("instance segmentation", "\u5b9e\u4f8b\u5206\u5272"), "geoai-with-python/chapters/ch10-instance-segmentation.md"),
    (("segmentation", "\u5206\u5272"), "geoai-with-python/chapters/ch09-semantic-segmentation.md"),
    (("change detection", "\u53d8\u5316\u68c0\u6d4b"), "geoai-with-python/chapters/ch12-change-detection.md"),
    (("pixel regression", "\u50cf\u7d20\u56de\u5f52"), "geoai-with-python/chapters/ch13-pixel-regression.md"),
    (("image translation", "\u56fe\u50cf\u7ffb\u8bd1"), "geoai-with-python/chapters/ch11-image-translation.md"),
    (("sam", "segment anything"), "geoai-with-python/chapters/ch14-sam-geospatial.md"),
    (("vision-language", "vision language model", "\u89c6\u89c9\u8bed\u8a00"), "geoai-with-python/chapters/ch15-vision-language-models.md"),
    (("satellite embedding", "satellite embeddings", "\u536b\u661f\u5d4c\u5165"), "geoai-with-python/chapters/ch16-satellite-embeddings.md"),
    (("qgis geoai", "qgis ai", "qgis plugin"), "geoai-with-python/chapters/ch17-qgis-plugin-setup.md"),
)

BROWSER_KEYWORDS = (
    "draw", "aoi", "roi", "show", "display", "map", "layer", "browser",
    "inspect", "画", "绘制", "看", "显示", "地图", "图层", "浏览器", "检查",
)

HYBRID_HINTS = (
    "then local", "export then", "download then", "gee to local",
    "cloud then local", "after export", "导出后", "下载后", "再用本地",
    "本地模型", "本地精算", "先用 gee", "gee 获取",
)


@dataclass(frozen=True)
class MethodRoute:
    method: str
    primary_backend: str
    secondary_backends: list[str]
    read: list[str]
    artifacts: list[str]
    reasons: list[str]
    cautions: list[str]
    next_actions: list[str]


def hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def add_many(items: list[str], values: list[str] | tuple[str, ...]) -> None:
    for value in values:
        add_unique(items, value)


def geoai_chapters(text: str) -> list[str]:
    selected: list[str] = []
    for keywords, chapter in GEOAI_CHAPTER_RULES:
        if any((re.search(r"(?<!\w)sam(?!\w)", text) if keyword == "sam" else keyword in text) for keyword in keywords):
            add_unique(selected, chapter)
    return selected


def route(prompt: str) -> MethodRoute:
    text = prompt.strip().lower()
    gee_hits = hits(text, GEE_KEYWORDS)
    catalog_hits = hits(text, CATALOG_KEYWORDS)
    local_hits = hits(text, LOCAL_KEYWORDS)
    local_operation_hits = hits(text, LOCAL_OPERATION_KEYWORDS)
    ml_hits = hits(text, ML_KEYWORDS)
    geoai_hits = hits(text, GEOAI_KEYWORDS)
    if re.search(r"(?<!\w)sam(?!\w)", text):
        add_unique(geoai_hits, "sam")
    browser_hits = hits(text, BROWSER_KEYWORDS)
    hybrid_hits = hits(text, HYBRID_HINTS)

    read: list[str] = ["geomaster-integration.md", "geomaster-knowledge-index.json"]
    artifacts: list[str] = []
    reasons: list[str] = []
    cautions: list[str] = []
    secondary: list[str] = []

    has_local = bool(local_hits or local_operation_hits)
    has_gee = bool(gee_hits)
    has_catalog = bool(catalog_hits and ("gee" in text or "earth engine" in text or "数据集" in text))
    has_hybrid = bool(hybrid_hits) or (has_gee and (has_local or bool(ml_hits)))

    if has_catalog and not has_hybrid:
        method = "catalog_first"
        primary_backend = "gee_catalog"
        add_many(read, ["search_gee_dataset.py", "dataset-qa-patterns.md", "geomaster:data-sources.md"])
        add_many(artifacts, ["dataset_candidates", "dataset_rationale"])
        reasons.append("The user is asking which Earth Engine data to use before analysis.")
        cautions.append("Treat catalog matches as candidates and verify scale, cadence, bands, masks, and licensing.")
        next_actions = [
            "Run search_gee_dataset.py or inspect the GEE catalog candidates.",
            "Use geomaster:data-sources.md for non-GEE alternatives or cross-catalog context.",
            "Return a short ranked dataset list with caveats and suggested next workflow.",
        ]
    elif browser_hits and not has_gee and not has_local and not ml_hits:
        method = "browser_first"
        primary_backend = "easygee_map_console"
        add_many(read, ["interaction-router.md", "browser-preview.md"])
        add_many(artifacts, ["aoi_needed", "map_layer"])
        reasons.append("The user is asking to draw, see, or inspect map state before choosing computation.")
        cautions.append("Use browser state as visual context, not proof of analytical correctness.")
        next_actions = [
            "Open or update the EasyGEE Map Console.",
            "Capture AOI/layer state explicitly before any computation handoff.",
            "Route follow-up analysis through this method router after AOI is known.",
        ]
    elif has_hybrid:
        method = "hybrid"
        primary_backend = "earth_engine_plus_local"
        add_many(secondary, ["earth_engine", "local_python"])
        add_many(read, [
            "gee-agent-playbook.md",
            "dataset-qa-patterns.md",
            "workflow-templates.md",
            "geomaster:core-libraries.md",
            "geomaster:machine-learning.md",
            "geomaster:big-data.md",
        ])
        add_many(artifacts, ["gee_asset_or_export", "local_file", "model_or_table"])
        reasons.append("The request crosses GEE-scale data access and local GIS/ML processing.")
        cautions.append("Make data handoff explicit: CRS, scale, nodata, bands, region, file format, and export status.")
        next_actions = [
            "Use GEE for catalog access, filtering, compositing, and controlled export.",
            "Use geomaster local references for COG/STAC/raster/vector/ML steps after export.",
            "Report which stage ran in GEE and which stage ran locally.",
        ]
    elif has_local:
        method = "local_first"
        primary_backend = "local_python"
        add_many(secondary, ["geopandas", "rasterio", "gdal"])
        add_many(read, [
            "geomaster:core-libraries.md",
            "geomaster:coordinate-systems.md",
            "geomaster:remote-sensing.md",
            "geomaster:big-data.md",
            "geomaster:troubleshooting.md",
        ])
        add_many(artifacts, ["local_file", "table_or_raster"])
        reasons.append("The request names local files, local GIS libraries, CRS operations, COG/STAC, or windowed raster work.")
        cautions.append("Check CRS, nodata, axis order, units, memory, and output format before computation.")
        next_actions = [
            "Inspect local file metadata and CRS before analysis.",
            "Use local Python/R tooling for windowed raster, vector, topology, network, or COG work.",
            "Use GEE only if remote catalog data or cloud-scale preprocessing is needed.",
        ]
    else:
        method = "gee_first"
        primary_backend = "earth_engine"
        add_many(secondary, ["geemap"])
        add_many(read, ["gee-agent-playbook.md", "dataset-qa-patterns.md", "task-patterns.md"])
        add_many(artifacts, ["ee_object", "stat_or_layer"])
        reasons.append("The request fits EasyGEE's default Earth Engine/geemap workflow.")
        cautions.append("Keep reducers server-side, set project explicitly, and avoid large getInfo calls.")
        next_actions = [
            "Use Earth Engine for filtering, compositing, reducers, visualization, and exports.",
            "Use geemap when notebook exploration or visible layer inspection is useful.",
            "Consult geomaster only for domain method details not covered by EasyGEE references.",
        ]

    if ml_hits and method != "hybrid":
        add_unique(read, "geomaster:machine-learning.md")
        add_unique(artifacts, "model_or_training_plan")
    if local_operation_hits and method == "gee_first":
        add_unique(read, "geomaster:coordinate-systems.md")
    needs_geoai = bool(geoai_hits) or (bool(ml_hits) and has_gee)
    if needs_geoai:
        add_unique(read, "geoai-encyclopedia.md")
        add_unique(read, "geoai-with-python/README.md")
        add_many(read, geoai_chapters(text))
        add_unique(artifacts, "geoai_method_or_model")
        add_unique(next_actions, "Read geoai-encyclopedia.md and the smallest task chapter before choosing a custom model.")

    return MethodRoute(
        method=method,
        primary_backend=primary_backend,
        secondary_backends=secondary,
        read=read,
        artifacts=artifacts,
        reasons=reasons,
        cautions=cautions,
        next_actions=next_actions,
    )


def print_text(result: MethodRoute) -> None:
    print(f"method: {result.method}")
    print(f"primary_backend: {result.primary_backend}")
    if result.secondary_backends:
        print("secondary_backends: " + ", ".join(result.secondary_backends))
    print("read: " + ", ".join(result.read))
    print("artifacts: " + ", ".join(result.artifacts))
    print("reasons:")
    for reason in result.reasons:
        print(f"  - {reason}")
    print("cautions:")
    for caution in result.cautions:
        print(f"  - {caution}")
    print("next actions:")
    for action in result.next_actions:
        print(f"  - {action}")


def smoke() -> None:
    cases = [
        ("Use GEE Sentinel-2 for semantic segmentation and train locally", "hybrid", "earth_engine_plus_local", {"geoai-encyclopedia.md", "geoai-with-python/README.md", "geoai-with-python/chapters/ch09-semantic-segmentation.md"}),
        ("用 GEE 算北京朝阳公园 NDVI 并导出表格", "gee_first", "earth_engine", {"gee-agent-playbook.md", "dataset-qa-patterns.md", "task-patterns.md"}),
        ("本地 GeoTIFF 计算 NDVI 并保存 COG", "local_first", "local_python", {"geomaster:core-libraries.md", "geomaster:remote-sensing.md", "geomaster:big-data.md"}),
        ("GEE 获取 Sentinel-2，导出 COG 后用本地模型分类", "hybrid", "earth_engine_plus_local", {"gee-agent-playbook.md", "geomaster:machine-learning.md", "geomaster:big-data.md"}),
        ("帮我找适合洪水监测的 GEE 数据集", "catalog_first", "gee_catalog", {"search_gee_dataset.py", "dataset-qa-patterns.md", "geomaster:data-sources.md"}),
        ("先画 AOI 再看图层", "browser_first", "easygee_map_console", {"interaction-router.md", "browser-preview.md"}),
    ]
    for prompt, method, backend, expected_reads in cases:
        result = route(prompt)
        if result.method != method:
            raise AssertionError(f"{prompt!r}: expected method {method}, got {result.method}")
        if result.primary_backend != backend:
            raise AssertionError(f"{prompt!r}: expected backend {backend}, got {result.primary_backend}")
        if not expected_reads.issubset(set(result.read)):
            raise AssertionError(f"{prompt!r}: expected reads {expected_reads}, got {result.read}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="*", help="EasyGEE user request text")
    parser.add_argument("--json", action="store_true", help="Print a JSON route payload")
    parser.add_argument("--smoke", action="store_true", help="Run built-in routing smoke checks")
    args = parser.parse_args()

    if args.smoke:
        smoke()
        print("route_geospatial_method smoke passed")
        return 0

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        parser.error("provide prompt text")
    result = route(prompt)
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
