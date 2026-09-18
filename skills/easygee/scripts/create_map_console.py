#!/usr/bin/env python
"""Create a fixed EasyGEE Map Console HTML page.

The console is a lightweight local browser interface for Earth Engine map
preview work. It uses ee only to create short-lived tile URLs and writes a
standalone HTML page with a stable EasyGEE shell: layer list, map, inspector,
and compact quota/project-state details. It does not read credential files or
print tile URLs.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import csv
import functools
import hashlib
import html
import json
import math
import os
import re
import tempfile
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import easygee_project


DEFAULT_PROJECT = easygee_project.DEFAULT_PROJECT
DEFAULT_EMPTY_CENTER = [20.0, 0.0]
DEFAULT_EMPTY_ZOOM = 2
UNLIMITED_QUOTA_THRESHOLD = 9_000_000_000_000_000_000
LEAFLET_CDN = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
LEAFLET_LOCAL = "leaflet-1.9.4.js"
PMTILES_VERSION = "4.5.0"
PMTILES_CDN = f"https://unpkg.com/pmtiles@{PMTILES_VERSION}/dist/pmtiles.js"
PMTILES_LOCAL = f"pmtiles-{PMTILES_VERSION}.js"
MAPLIBRE_VERSION = "5.6.1"
MAPLIBRE_JS_CDN = f"https://unpkg.com/maplibre-gl@{MAPLIBRE_VERSION}/dist/maplibre-gl.js"
MAPLIBRE_CSS_CDN = f"https://unpkg.com/maplibre-gl@{MAPLIBRE_VERSION}/dist/maplibre-gl.css"
MAPLIBRE_JS_LOCAL = f"maplibre-gl-{MAPLIBRE_VERSION}.js"
MAPLIBRE_CSS_LOCAL = f"maplibre-gl-{MAPLIBRE_VERSION}.css"
MAPLIBRE_LEAFLET_VERSION = "0.1.4"
MAPLIBRE_LEAFLET_CDN = (
    f"https://unpkg.com/@maplibre/maplibre-gl-leaflet@{MAPLIBRE_LEAFLET_VERSION}/dist/leaflet-maplibre-gl.js"
)
MAPLIBRE_LEAFLET_LOCAL = f"maplibre-gl-leaflet-{MAPLIBRE_LEAFLET_VERSION}.js"
COG_PROTOCOL_VERSION = "0.9.2"
COG_PROTOCOL_CDN = (
    f"https://unpkg.com/@geomatico/maplibre-cog-protocol@{COG_PROTOCOL_VERSION}/dist/index.js"
)
COG_PROTOCOL_LOCAL = f"maplibre-cog-protocol-{COG_PROTOCOL_VERSION}.js"
GEE_CATALOG_INDEX_URL = "https://raw.githubusercontent.com/giswqs/Earth-Engine-Catalog/master/gee_catalog.json"
GEE_STAC_ROOT_URL = "https://storage.googleapis.com/earthengine-stac/catalog/catalog.json"
GEE_COMMUNITY_DATASETS_CSV_URL = "https://raw.githubusercontent.com/sadassimov/geemu-skill/main/awesome-gee-community-datasets/community_datasets.csv"
GEE_CATALOG_URL_BASE = "https://developers.google.com/earth-engine/datasets/catalog/"
CATALOG_FETCH_TIMEOUT = 20
CATALOG_CACHE_VERSION = 3
CATALOG_CACHE_MAX_AGE_HOURS = 168
CATALOG_FETCH_SECONDS = 45
CATALOG_MAX_URLS = 5000
CATALOG_MAX_WORKERS = 32
S2_NDVI_DERIVED_IDS = {"EASYGEE/S2_NDVI", "easygee:s2-ndvi", "s2-ndvi", "ndvi"}
SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"
EASYGEE_LOGO = ASSETS_DIR / "easygee-logo-square-simple-256.png"
NONCOMMERCIAL_TIER_LIMITS = {
    540_000: ("Community", "Community（非商业）", "Community (noncommercial)"),
    3_600_000: ("Contributor", "Contributor（非商业）", "Contributor (noncommercial)"),
    360_000_000: ("Partner", "Partner（非商业）", "Partner (noncommercial)"),
}
QUOTA_LABELS = {
    "Average concurrent batch tasks": ("平均批任务", "Average concurrent batch tasks"),
    "BigQuery slot-time per day in seconds (consumed on Earth Engine)": (
        "BigQuery 槽时",
        "BigQuery slot-time per day in seconds (consumed on Earth Engine)",
    ),
    "BigQuery raster function slot-time per day": (
        "BigQuery 槽时",
        "BigQuery raster function slot-time per day",
    ),
    "EECU-seconds per day": ("每日 EECU", "EECU-seconds per day"),
    "Earth Engine compute time (EECU-time) per day": (
        "每日 EECU",
        "Earth Engine compute time (EECU-time) per day",
    ),
    "Noncommercial EECU-seconds per month": (
        "非商业月度 EECU",
        "Noncommercial EECU-seconds per month",
    ),
    "ReadsPerMinutePerProject": ("项目读取/分钟", "ReadsPerMinutePerProject"),
    "ReadsPerMinutePerUser": ("用户读取/分钟", "ReadsPerMinutePerUser"),
    "Large aggregation result size": ("大型聚合结果", "Large aggregation result size"),
    "Max asset storage space": ("资产存储", "Max asset storage space"),
    "Max concurrent requests (high-volume endpoint)": (
        "高容量并发请求",
        "Max concurrent requests (high-volume endpoint)",
    ),
    "Max concurrent requests (standard endpoint)": (
        "标准并发请求",
        "Max concurrent requests (standard endpoint)",
    ),
    "Max number of assets": ("资产数量", "Max number of assets"),
    "Max rate of requests (per account)": (
        "账号请求速率",
        "Max rate of requests (per account)",
    ),
    "Max rate of requests (per project)": (
        "项目请求速率",
        "Max rate of requests (per project)",
    ),
    "Request payload size": ("请求大小", "Request payload size"),
    "Task queue length": ("任务队列", "Task queue length"),
}


# Front-end sources of the generated page live in assets/map-console/.
# Placeholders are __EASYGEE_<NAME>__ tokens, filled in one regex pass by
# render_html(); ICON_<NAME> tokens map to svg_icon("<name>").
MAP_CONSOLE_ASSETS_DIR = ASSETS_DIR / "map-console"
MAP_CONSOLE_TOKEN = re.compile(r"__EASYGEE_([A-Z0-9_]+)__")


@functools.lru_cache(maxsize=None)
def map_console_asset(name: str) -> str:
    """Return a Map Console asset as UTF-8 text with its LF newlines untouched."""
    return (MAP_CONSOLE_ASSETS_DIR / name).read_bytes().decode("utf-8")


@functools.lru_cache(maxsize=None)
def map_console_page_template() -> str:
    template = map_console_asset("template.html")
    marker = "__EASYGEE_CONSOLE_JS__\n"  # console.js supplies its own final newline
    if template.count(marker) != 1:
        raise RuntimeError("Map Console template must contain __EASYGEE_CONSOLE_JS__ on its own line exactly once")
    return template.replace(marker, map_console_asset("console.js"))


def easygee_logo_data_uri() -> str:
    if not EASYGEE_LOGO.exists():
        return ""
    encoded = base64.b64encode(EASYGEE_LOGO.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


@dataclass(frozen=True)
class ConsolePlan:
    output: str
    project: str
    project_source: str
    title: str
    center: tuple[float, float]
    layer_count: int
    uses_live_ee: bool
    quota_source: str
    quota_usage_source: str


def default_output() -> Path:
    return easygee_project.workspace_root() / "interactive-map" / "index.html"


def parse_float(value: str | None) -> float | None:
    if not value:
        return None
    text = str(value).replace(",", "").strip()
    if not text or is_unlimited_quota_value(text) or ";" in text:
        return None
    number = ""
    for char in text:
        if char.isdigit() or char in ".-":
            number += char
        elif number:
            break
    try:
        return float(number) if number else None
    except ValueError:
        return None


def is_unlimited_quota_value(value: Any) -> bool:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return False
    lowered = text.lower()
    if "unlimited" in lowered or lowered in {"inf", "infinity", "∞"}:
        return True
    try:
        return int(text) >= UNLIMITED_QUOTA_THRESHOLD
    except ValueError:
        return False


def compact_value(value: str | None, unit: str | None = None) -> str:
    text = str(value or "").strip()
    suffix = str(unit or "").strip()
    if not text:
        return "N/A"
    if is_unlimited_quota_value(text):
        return "Unlimited"
    if ";" in text:
        return text
    if suffix and suffix != "-" and suffix.lower() not in text.lower():
        return f"{text} {suffix}"
    return text


def quota_label_pair(name: str) -> tuple[str, str]:
    return QUOTA_LABELS.get(name, (name, name))


def catalog_url_for_id(dataset_id: str) -> str:
    return GEE_CATALOG_URL_BASE + dataset_id.replace("/", "_")


def catalog_entry(
    dataset_id: str,
    label: str,
    tags: str = "",
    scale: str = "catalog",
    url: str | None = None,
    provider: str = "",
    kind: str = "",
    category: str = "",
    thumbnail: str = "",
    start_date: str = "",
    end_date: str = "",
    deprecated: bool = False,
    license_name: str = "",
    description: str = "",
    source_name: str = "official",
    sample_code: str = "",
) -> dict[str, Any]:
    return {
        "id": dataset_id,
        "label": label or dataset_id,
        "tags": tags,
        "scale": scale or "catalog",
        "url": url or catalog_url_for_id(dataset_id),
        "provider": provider,
        "type": kind,
        "category": category,
        "thumbnail": thumbnail,
        "startDate": start_date,
        "endDate": end_date,
        "deprecated": deprecated,
        "license": license_name,
        "description": description,
        "source": source_name,
        "sampleCode": sample_code,
    }


def catalog_cache_dir() -> Path:
    return easygee_project.cache_root()


def official_stac_cache_path() -> Path:
    return catalog_cache_dir() / "official-stac-catalog.json"


def community_catalog_cache_path() -> Path:
    return catalog_cache_dir() / "community-catalog.json"


def cached_official_catalog(max_age_hours: int) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    path = official_stac_cache_path()
    if not path.exists():
        return None
    try:
        age_seconds = time.time() - path.stat().st_mtime
        if max_age_hours > 0 and age_seconds > max_age_hours * 3600:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("version") != CATALOG_CACHE_VERSION:
            return None
        entries = payload.get("catalog")
        if not isinstance(entries, list) or not entries:
            return None
        source = {
            "source": "Google Earth Engine STAC cache",
            "url": GEE_STAC_ROOT_URL,
            "officialRoot": GEE_STAC_ROOT_URL,
            "cachePath": str(path),
            "fetchedAt": payload.get("fetchedAt") or "",
            "cached": True,
        }
        return entries, source
    except Exception:
        return None


def write_official_catalog_cache(entries: list[dict[str, Any]], source: dict[str, Any]) -> None:
    if not entries:
        return
    path = official_stac_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": CATALOG_CACHE_VERSION,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "catalog": entries,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def cached_community_catalog(max_age_hours: int) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    path = community_catalog_cache_path()
    if not path.exists():
        return None
    try:
        age_seconds = time.time() - path.stat().st_mtime
        if max_age_hours > 0 and age_seconds > max_age_hours * 3600:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("version") != CATALOG_CACHE_VERSION:
            return None
        entries = payload.get("catalog")
        if not isinstance(entries, list) or not entries:
            return None
        source = {
            "source": "GEE Community Catalog cache",
            "url": GEE_COMMUNITY_DATASETS_CSV_URL,
            "cachePath": str(path),
            "fetchedAt": payload.get("fetchedAt") or "",
            "cached": True,
            "count": len(entries),
        }
        return entries, source
    except Exception:
        return None


def write_community_catalog_cache(entries: list[dict[str, Any]], source: dict[str, Any]) -> None:
    if not entries:
        return
    path = community_catalog_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": CATALOG_CACHE_VERSION,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "catalog": entries,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def fetch_json_url(url: str) -> tuple[str, dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=CATALOG_FETCH_TIMEOUT) as response:
        payload = json.load(response)
    return url, payload


def stac_provider_text(collection: dict[str, Any]) -> str:
    providers = collection.get("providers") or []
    if not isinstance(providers, list):
        return ""
    names = []
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        name = str(provider.get("name") or "").strip()
        if name and name != "Google Earth Engine":
            names.append(name)
    return " / ".join(names[:3])


def stac_link(collection: dict[str, Any], rel: str) -> str:
    links = collection.get("links") or []
    if not isinstance(links, list):
        return ""
    for link in links:
        if isinstance(link, dict) and link.get("rel") == rel and link.get("href"):
            return str(link["href"])
    return ""


def stac_date_range(collection: dict[str, Any]) -> tuple[str, str]:
    interval = (((collection.get("extent") or {}).get("temporal") or {}).get("interval") or [])
    if not interval or not isinstance(interval, list) or not isinstance(interval[0], list):
        return "", ""

    def compact_date(value: Any) -> str:
        text = str(value or "")
        return text[:10] if len(text) >= 10 else text

    return compact_date(interval[0][0] if interval[0] else ""), compact_date(interval[0][1] if len(interval[0]) > 1 else "")


def stac_collection_entry(collection: dict[str, Any]) -> dict[str, Any] | None:
    dataset_id = str(collection.get("id") or "").strip()
    if not dataset_id:
        return None
    keywords = collection.get("keywords") or []
    if not isinstance(keywords, list):
        keywords = [str(keywords)]
    categories = collection.get("gee:categories") or []
    if not isinstance(categories, list):
        categories = [str(categories)]
    start_date, end_date = stac_date_range(collection)
    description = str(collection.get("description") or "").replace("\n", " ")[:700]
    tags = " ".join(
        str(value)
        for value in [
            " ".join(str(keyword) for keyword in keywords),
            " ".join(str(category) for category in categories),
            start_date,
            end_date,
        ]
        if value
    )
    license_name = str(collection.get("license") or "")
    return catalog_entry(
        dataset_id,
        str(collection.get("title") or dataset_id),
        tags,
        str(collection.get("gee:type") or "official catalog").replace("_", " "),
        catalog_url_for_id(dataset_id),
        provider=stac_provider_text(collection),
        kind=str(collection.get("gee:type") or ""),
        category=", ".join(str(category) for category in categories if category),
        thumbnail=stac_link(collection, "preview"),
        start_date=start_date,
        end_date=end_date,
        deprecated=bool(collection.get("deprecated") or False),
        license_name=license_name,
        description=description,
    )


def official_stac_catalog_entries(
    *,
    refresh: bool = False,
    max_age_hours: int = CATALOG_CACHE_MAX_AGE_HOURS,
    max_seconds: int = CATALOG_FETCH_SECONDS,
    max_urls: int = CATALOG_MAX_URLS,
    max_workers: int = CATALOG_MAX_WORKERS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cached = None if refresh else cached_official_catalog(max_age_hours)
    if cached:
        return cached

    deadline = time.time() + max(1, max_seconds)
    seen: set[str] = set()
    frontier = [GEE_STAC_ROOT_URL]
    entries: dict[str, dict[str, Any]] = {}
    catalog_count = 0
    errors: list[str] = []

    while frontier and time.time() < deadline and len(seen) < max_urls:
        batch = []
        for url in frontier:
            if url not in seen:
                seen.add(url)
                batch.append(url)
        frontier = []
        if not batch:
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
            futures = {executor.submit(fetch_json_url, url): url for url in batch}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    _, payload = future.result()
                except Exception as exc:
                    errors.append(f"{url}: {exc}")
                    continue
                if payload.get("type") == "Collection":
                    entry = stac_collection_entry(payload)
                    if entry:
                        entries[entry["id"]] = entry
                    continue
                catalog_count += 1
                for link in payload.get("links") or []:
                    if isinstance(link, dict) and link.get("rel") == "child" and link.get("href"):
                        frontier.append(str(link["href"]))

    warnings: list[str] = []
    if frontier:
        warnings.append(
            f"Official STAC catalog refresh stopped after {max_seconds}s; using {len(entries)} collections found so far."
        )
    if errors:
        warnings.append(f"Official STAC catalog skipped {len(errors)} URLs; first error: {errors[0]}")
    catalog = sorted(entries.values(), key=lambda item: (str(item.get("label") or item["id"]).casefold(), item["id"]))
    source = {
        "source": "Google Earth Engine STAC",
        "url": GEE_STAC_ROOT_URL,
        "officialRoot": GEE_STAC_ROOT_URL,
        "count": len(catalog),
        "visited": len(seen),
        "catalogs": catalog_count,
        "cached": False,
        "warnings": warnings,
    }
    if catalog:
        write_official_catalog_cache(catalog, source)
    return catalog, source


def curated_catalog_entries() -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    seeds = [
        catalog_entry(
            "EASYGEE/S2_NDVI",
            "Sentinel-2 NDVI (Cloud Score+)",
            "ndvi vegetation sentinel cloud score plus easygee derived 植被 归一化差异植被指数",
            "10 m",
            catalog_url_for_id("COPERNICUS/S2_SR_HARMONIZED"),
            provider="EasyGEE",
            kind="derived",
            source_name="derived",
        ),
        catalog_entry("COPERNICUS/S2_SR_HARMONIZED", "Sentinel-2 SR", "optical rgb ndvi vegetation 哨兵 光学 植被", "10 m"),
        catalog_entry("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED", "Cloud Score+", "sentinel cloud mask qa 云 掩膜", "10 m"),
        catalog_entry("COPERNICUS/S2_CLOUD_PROBABILITY", "Sentinel-2 Cloud Probability", "sentinel cloud probability s2cloudless 云概率", "10 m"),
        catalog_entry("COPERNICUS/S1_GRD", "Sentinel-1 GRD", "sar radar flood water all weather 洪水 雷达", "10 m"),
        catalog_entry("GOOGLE/DYNAMICWORLD/V1", "Dynamic World", "land cover classes probability 土地覆盖 分类", "10 m"),
        catalog_entry("JRC/GSW1_4/GlobalSurfaceWater", "JRC Global Surface Water", "water occurrence seasonality surface water 水体 地表水", "30 m"),
        catalog_entry("USGS/SRTMGL1_003", "SRTM elevation", "terrain dem elevation 高程 地形", "30 m"),
        catalog_entry("ESA/WorldCover/v200", "ESA WorldCover 2021", "land cover worldcover 土地覆盖", "10 m"),
        catalog_entry("MODIS/061/MOD13Q1", "MODIS Vegetation Indices", "modis ndvi evi vegetation time series 植被", "250 m"),
        catalog_entry("MODIS/061/MOD11A2", "MODIS Land Surface Temperature", "modis lst temperature heat 温度 地表温度", "1 km"),
        catalog_entry("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG", "VIIRS Nighttime Lights", "nighttime lights viirs radiance 夜光", "500 m"),
        catalog_entry("WorldPop/GP/100m/pop", "WorldPop Population", "population exposure people 人口", "100 m"),
        catalog_entry("JRC/GHSL/P2023A/GHS_POP", "GHSL Population", "population ghsl built exposure 人口", "100 m"),
        catalog_entry("GOOGLE/Research/open-buildings/v3/polygons", "Open Buildings V3", "buildings footprints exposure 建筑 建筑物", "vector"),
        catalog_entry("COPERNICUS/DEM/GLO30", "Copernicus DEM GLO-30", "dem terrain elevation 高程 地形", "30 m"),
        catalog_entry("ECMWF/ERA5_LAND/DAILY_AGGR", "ERA5-Land Daily Aggregates", "climate temperature precipitation wind 气候 降水 温度", "0.1 deg"),
        catalog_entry("UCSB-CHG/CHIRPS/DAILY", "CHIRPS Daily Precipitation", "rain precipitation drought rainfall 降水 雨量 干旱", "0.05 deg"),
    ]
    for entry in seeds:
        entries[entry["id"]] = entry
    try:
        from search_gee_dataset import DATASETS

        for dataset in DATASETS:
            keywords = " ".join([*dataset.tasks, *dataset.keywords, *dataset.bands])
            dataset_ids = [value.strip() for value in dataset.id.split(" and ") if value.strip()]
            for dataset_id in dataset_ids:
                entries.setdefault(
                    dataset_id,
                    catalog_entry(dataset_id, dataset.title, keywords, dataset.scale, catalog_url_for_id(dataset_id), kind=dataset.kind),
                )
    except Exception:
        pass
    for entry in entries.values():
        entry["source"] = "curated"
    return list(entries.values())


def remote_catalog_entries() -> list[dict[str, Any]]:
    with urllib.request.urlopen(GEE_CATALOG_INDEX_URL, timeout=CATALOG_FETCH_TIMEOUT) as response:
        payload = json.load(response)
    entries: list[dict[str, Any]] = []
    if not isinstance(payload, list):
        return entries
    for item in payload:
        if not isinstance(item, dict):
            continue
        dataset_id = str(item.get("id") or "").strip()
        if not dataset_id:
            continue
        keywords = item.get("keywords") or ""
        if isinstance(keywords, list):
            keywords = " ".join(str(value) for value in keywords)
        tags = " ".join(
            str(value)
            for value in [
                keywords,
                item.get("category"),
                item.get("provider"),
                item.get("type"),
                item.get("start_date") or item.get("state_date"),
                item.get("end_date"),
            ]
            if value
        )
        scale = str(item.get("type") or item.get("category") or "catalog").replace("_", " ")
        entries.append(
            catalog_entry(
                dataset_id,
                str(item.get("title") or dataset_id),
                tags,
                scale,
                str(item.get("url") or "") or catalog_url_for_id(dataset_id),
                provider=str(item.get("provider") or ""),
                kind=str(item.get("type") or ""),
                category=str(item.get("category") or ""),
                thumbnail=str(item.get("thumbnail") or ""),
                start_date=str(item.get("start_date") or item.get("state_date") or ""),
                end_date=str(item.get("end_date") or ""),
                deprecated=bool(item.get("deprecated") or False),
                license_name=str(item.get("license") or ""),
            )
        )
    return entries


def community_catalog_entries(
    *,
    refresh: bool = False,
    max_age_hours: int = CATALOG_CACHE_MAX_AGE_HOURS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cached = None if refresh else cached_community_catalog(max_age_hours)
    if cached:
        return cached

    with urllib.request.urlopen(GEE_COMMUNITY_DATASETS_CSV_URL, timeout=CATALOG_FETCH_TIMEOUT) as response:
        text = response.read().decode("utf-8-sig")

    entries: dict[str, dict[str, Any]] = {}
    for row in csv.DictReader(text.splitlines()):
        dataset_id = str(row.get("id") or "").strip()
        if not dataset_id:
            continue
        title = str(row.get("title") or dataset_id).strip()
        thematic_group = str(row.get("thematic_group") or "").strip()
        provider = str(row.get("provider") or "").strip()
        kind = str(row.get("type") or "").strip().lower()
        tags = " ".join(
            value
            for value in [
                "community catalog",
                thematic_group,
                str(row.get("tags") or "").strip(),
                provider,
                kind,
            ]
            if value
        )
        entry = catalog_entry(
            dataset_id,
            title,
            tags,
            kind.replace("_", " ") or "community catalog",
            str(row.get("docs_page") or "") or catalog_url_for_id(dataset_id),
            provider=provider,
            kind=kind,
            category=thematic_group,
            thumbnail=str(row.get("thumbnail") or "").strip(),
            license_name=str(row.get("license") or "").strip(),
            description=str(row.get("license_text") or "").strip(),
            source_name="community",
            sample_code=str(row.get("sample_code") or "").strip(),
        )
        entries[dataset_id] = entry

    catalog = sorted(entries.values(), key=lambda item: (str(item.get("label") or item["id"]).casefold(), item["id"]))
    source = {
        "source": "GEE Community Catalog",
        "url": GEE_COMMUNITY_DATASETS_CSV_URL,
        "count": len(catalog),
        "cached": False,
    }
    write_community_catalog_cache(catalog, source)
    return catalog, source


def build_catalog(
    layers: list[dict[str, Any]],
    include_remote: bool,
    catalog_mode: str = "auto",
    refresh_catalog: bool = False,
    catalog_cache_hours: int = CATALOG_CACHE_MAX_AGE_HOURS,
    catalog_fetch_seconds: int = CATALOG_FETCH_SECONDS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {entry["id"]: entry for entry in curated_catalog_entries()}
    source = "curated fallback"
    source_url = GEE_STAC_ROOT_URL
    source_extra: dict[str, Any] = {}
    warnings: list[str] = []
    source_counts: dict[str, int] = {"curated": len(entries)}
    mode = (catalog_mode or "auto").lower()
    if include_remote and mode != "curated":
        if mode in {"auto", "official", "all"}:
            try:
                official_entries, official_source = official_stac_catalog_entries(
                    refresh=refresh_catalog,
                    max_age_hours=catalog_cache_hours,
                    max_seconds=catalog_fetch_seconds,
                )
                if official_entries:
                    entries.update({entry["id"]: entry for entry in official_entries})
                    source_counts["official"] = len(official_entries)
                    source = str(official_source.get("source") or "Google Earth Engine STAC")
                    source_url = str(official_source.get("url") or GEE_STAC_ROOT_URL)
                    source_extra = {
                        key: value
                        for key, value in official_source.items()
                        if key not in {"source", "url", "officialRoot", "warnings"}
                    }
                warnings.extend(str(warning) for warning in official_source.get("warnings") or [])
            except Exception as exc:
                warnings.append(f"Official STAC catalog fetch failed: {exc}")
        if mode in {"auto", "all", "community"}:
            try:
                community_entries, community_source = community_catalog_entries(
                    refresh=refresh_catalog,
                    max_age_hours=catalog_cache_hours,
                )
                if community_entries:
                    for entry in community_entries:
                        if entry["id"] in entries:
                            entries[entry["id"]].setdefault("source", "official")
                            entries[entry["id"]]["communityUrl"] = entry.get("url") or ""
                            entries[entry["id"]]["sampleCode"] = entry.get("sampleCode") or entries[entry["id"]].get("sampleCode", "")
                        else:
                            entries[entry["id"]] = entry
                    source_counts["community"] = len(community_entries)
                    if source == "curated fallback":
                        source = str(community_source.get("source") or "GEE Community Catalog")
                        source_url = str(community_source.get("url") or GEE_COMMUNITY_DATASETS_CSV_URL)
                    else:
                        source = f"{source} + GEE Community Catalog"
                if community_source.get("cached"):
                    source_extra["communityCachePath"] = community_source.get("cachePath")
            except Exception as exc:
                warnings.append(f"Community catalog fetch failed: {exc}")
        if mode in {"auto", "giswqs"} and source == "curated fallback":
            try:
                remote_entries = remote_catalog_entries()
                if remote_entries:
                    entries.update({entry["id"]: entry for entry in remote_entries})
                    source_counts["giswqs"] = len(remote_entries)
                    source = "Earth Engine Catalog index"
                    source_url = GEE_CATALOG_INDEX_URL
            except Exception as exc:
                warnings.append(f"Catalog index fetch failed: {exc}")
        elif mode == "giswqs":
            warnings.append("Catalog mode giswqs was requested but did not return entries.")
    elif include_remote:
        source = "curated fallback"
    if include_remote and mode not in {"auto", "official", "giswqs", "curated", "community", "all"}:
        try:
            remote_entries = remote_catalog_entries()
            if remote_entries:
                entries.update({entry["id"]: entry for entry in remote_entries})
                source_counts["giswqs"] = len(remote_entries)
                source = "Earth Engine Catalog index"
                source_url = GEE_CATALOG_INDEX_URL
        except Exception as exc:
            warnings.append(f"Catalog index fetch failed: {exc}")
    for layer in layers:
        dataset_id = str(layer.get("dataset") or "")
        if not dataset_id:
            continue
        ready_entry = catalog_entry(
            dataset_id,
            str(layer.get("name") or dataset_id),
            f"map-ready layer {layer.get('type') or ''}",
            "ready layer",
        )
        entries.setdefault(dataset_id, ready_entry)
        entries[dataset_id]["ready"] = True
    ready_ids = {str(layer.get("dataset") or "") for layer in layers}
    catalog = sorted(
        entries.values(),
        key=lambda item: (
            0 if item["id"] in ready_ids else 1,
            str(item.get("label") or item["id"]).casefold(),
            item["id"],
        ),
    )
    return catalog, {
        "source": source,
        "url": source_url,
        "officialRoot": GEE_STAC_ROOT_URL,
        "count": len(catalog),
        "warnings": warnings,
        "counts": source_counts,
        **source_extra,
    }


def layer_id_for_dataset(dataset_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", dataset_id.lower()).strip("-")
    slug = slug[:34] or "catalog-layer"
    digest = hashlib.sha1(dataset_id.encode("utf-8")).hexdigest()[:8]
    return f"gee-{slug}-{digest}"


def normalize_bounds(bounds: Any) -> tuple[float, float, float, float]:
    """Return west, south, east, north from Leaflet-style bounds."""
    try:
        south = float(bounds[0][0])
        west = float(bounds[0][1])
        north = float(bounds[1][0])
        east = float(bounds[1][1])
    except Exception as exc:
        raise ValueError("bounds must be [[south, west], [north, east]]") from exc
    if south >= north or west >= east:
        raise ValueError("bounds must have south < north and west < east")
    if not (-90 <= south <= 90 and -90 <= north <= 90 and -180 <= west <= 180 and -180 <= east <= 180):
        raise ValueError("bounds are outside valid longitude/latitude ranges")
    return west, south, east, north


def normalize_latlng_pair(pair: Any) -> tuple[float, float]:
    try:
        lat = float(pair[0])
        lon = float(pair[1])
    except Exception as exc:
        raise ValueError("AOI coordinates must be [lat, lon] pairs") from exc
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("AOI coordinates are outside valid longitude/latitude ranges")
    return lat, lon


def normalize_lonlat_pair(pair: Any) -> tuple[float, float]:
    try:
        lon = float(pair[0])
        lat = float(pair[1])
    except Exception as exc:
        raise ValueError("GeoJSON AOI coordinates must be [lon, lat] pairs") from exc
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("AOI coordinates are outside valid longitude/latitude ranges")
    return lat, lon


def aoi_bounds_from_coordinates(coordinates: list[list[float]]) -> tuple[float, float, float, float]:
    if len(coordinates) < 3:
        raise ValueError("polygon AOI must contain at least three vertices")
    lats = [point[0] for point in coordinates]
    lons = [point[1] for point in coordinates]
    south, north = min(lats), max(lats)
    west, east = min(lons), max(lons)
    if south >= north or west >= east:
        raise ValueError("AOI bounds must have south < north and west < east")
    return west, south, east, north


def normalize_polygon_coordinates(aoi: dict[str, Any]) -> list[list[float]]:
    raw = aoi.get("coordinates") or aoi.get("latLngs") or aoi.get("points")
    if raw is None and isinstance(aoi.get("geometry"), dict):
        return normalize_polygon_coordinates(aoi["geometry"])
    if not isinstance(raw, list) or not raw:
        raise ValueError("polygon AOI must include coordinates")
    coordinate_order = str(aoi.get("coordinateOrder") or "").lower()
    if raw and isinstance(raw[0], list) and raw[0] and isinstance(raw[0][0], list):
        ring = raw[0]
        points = [normalize_lonlat_pair(point) for point in ring]
    elif coordinate_order == "lonlat":
        points = [normalize_lonlat_pair(point) for point in raw]
    else:
        points = [normalize_latlng_pair(point) for point in raw]

    deduped: list[list[float]] = []
    for lat, lon in points:
        if deduped and abs(deduped[-1][0] - lat) < 1e-12 and abs(deduped[-1][1] - lon) < 1e-12:
            continue
        deduped.append([lat, lon])
    if len(deduped) > 3 and abs(deduped[0][0] - deduped[-1][0]) < 1e-12 and abs(deduped[0][1] - deduped[-1][1]) < 1e-12:
        deduped.pop()
    if len(deduped) < 3:
        raise ValueError("polygon AOI must contain at least three distinct vertices")
    aoi_bounds_from_coordinates(deduped)
    return deduped


def normalize_aoi(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a stable AOI dict from a new AOI payload or legacy bounds."""
    raw_aoi = payload.get("aoi") if isinstance(payload.get("aoi"), dict) else None
    if not raw_aoi:
        west, south, east, north = normalize_bounds(payload.get("bounds"))
        return {
            "type": "rectangle",
            "bounds": [[south, west], [north, east]],
            "coordinates": [[south, west], [south, east], [north, east], [north, west]],
            "coordinateOrder": "latlng",
        }

    if str(raw_aoi.get("type") or "").lower() == "feature" and isinstance(raw_aoi.get("geometry"), dict):
        raw_aoi = raw_aoi["geometry"]
    aoi_type = str(raw_aoi.get("type") or "").lower()
    if aoi_type in {"polygon", "multipolygon"}:
        coordinates = normalize_polygon_coordinates(raw_aoi)
        west, south, east, north = aoi_bounds_from_coordinates(coordinates)
        return {
            "type": "polygon",
            "bounds": [[south, west], [north, east]],
            "coordinates": coordinates,
            "coordinateOrder": "latlng",
        }

    bounds = raw_aoi.get("bounds") or raw_aoi.get("bbox") or payload.get("bounds")
    west, south, east, north = normalize_bounds(bounds)
    return {
        "type": "rectangle",
        "bounds": [[south, west], [north, east]],
        "coordinates": [[south, west], [south, east], [north, east], [north, west]],
        "coordinateOrder": "latlng",
    }


def ee_geometry_from_aoi(ee: Any, aoi: dict[str, Any]) -> Any:
    if aoi.get("type") == "polygon":
        ring = [[lon, lat] for lat, lon in aoi["coordinates"]]
        return ee.Geometry.Polygon([ring], None, False)
    west, south, east, north = normalize_bounds(aoi["bounds"])
    return ee.Geometry.Rectangle([west, south, east, north], None, False)


def sentinel2_ndvi_image(
    ee: Any,
    roi: Any,
    start_date: str,
    end_date: str,
    cloud_pct: float,
    warnings: list[str],
    cloud_score_min: float = 0.60,
) -> tuple[Any, Any, str]:
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))
    )
    method = "sentinel-2-ndvi"
    try:
        collection = collection.linkCollection(
            ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"),
            ["cs_cdf"],
        ).map(lambda image: image.updateMask(image.select("cs_cdf").gte(cloud_score_min)))
        method = "sentinel-2-ndvi-cloud-score"
    except Exception:
        warnings.append("Cloud Score+ masking was unavailable; using CLOUDY_PIXEL_PERCENTAGE only.")
    image = collection.median().normalizedDifference(["B8", "B4"]).rename("NDVI").clip(roi)
    return image, collection, method


def sanitize_drive_folder(value: Any, default: str = "EasyGEE") -> str:
    text = str(value or "").strip() or default
    text = re.sub(r"[\\/]+", "_", text)
    return text[:120].strip() or default


def sanitize_export_token(value: Any, default: str, max_len: int = 90) -> str:
    text = str(value or "").strip() or default
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_")
    return (text[:max_len].strip("_") or default)


def truthy_export_flag(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"0", "false", "no", "off"}:
        return False
    if text in {"1", "true", "yes", "on"}:
        return True
    return default


def build_ndvi_drive_export(payload: dict[str, Any]) -> dict[str, Any]:
    import ee

    resolved_project = easygee_project.resolve_project(payload.get("project"), remember_discovered=True)
    project = resolved_project.project
    if not project or project == DEFAULT_PROJECT:
        raise ValueError("A concrete Earth Engine project id is required")
    aoi = normalize_aoi(payload)
    start_date = str(payload.get("startDate") or "2024-01-01")
    end_date = str(payload.get("endDate") or datetime.now(timezone.utc).date().isoformat())
    try:
        cloud_pct = float(payload.get("cloudPct") or 80)
    except Exception:
        cloud_pct = 80.0
    try:
        scale = float(payload.get("scale") or 10)
    except Exception:
        scale = 10.0
    if scale <= 0:
        raise ValueError("scale must be greater than 0")
    try:
        max_pixels = int(float(payload.get("maxPixels") or 1_000_000_000))
    except Exception:
        max_pixels = 1_000_000_000
    max_pixels = max(1, max_pixels)

    ee.Initialize(project=project)
    roi = ee_geometry_from_aoi(ee, aoi)
    warnings: list[str] = []
    ndvi, collection, method = sentinel2_ndvi_image(ee, roi, start_date, end_date, cloud_pct, warnings)
    aoi_digest = hashlib.sha1(json.dumps(aoi, sort_keys=True).encode("utf-8")).hexdigest()[:8]
    date_token = sanitize_export_token(f"{start_date}_{end_date}", "date_range", max_len=32)
    default_prefix = f"easygee_ndvi_{date_token}_{aoi_digest}"
    folder = sanitize_drive_folder(payload.get("folder"), "EasyGEE")
    file_name_prefix = sanitize_export_token(payload.get("fileNamePrefix"), default_prefix)
    description = sanitize_export_token(payload.get("description"), file_name_prefix, max_len=100)
    file_format = str(payload.get("fileFormat") or "GeoTIFF").strip() or "GeoTIFF"
    cloud_optimized = truthy_export_flag(payload.get("cloudOptimized"), True)
    start_task = truthy_export_flag(payload.get("start"), True)
    crs = str(payload.get("crs") or "").strip()

    export_kwargs: dict[str, Any] = {
        "image": ndvi.rename("NDVI").toFloat(),
        "description": description,
        "folder": folder,
        "fileNamePrefix": file_name_prefix,
        "region": roi,
        "scale": scale,
        "maxPixels": max_pixels,
        "fileFormat": file_format,
    }
    if crs:
        export_kwargs["crs"] = crs
    if file_format.lower() == "geotiff" and cloud_optimized:
        export_kwargs["formatOptions"] = {"cloudOptimized": True}

    task = ee.batch.Export.image.toDrive(**export_kwargs)
    if start_task:
        task.start()
    try:
        status = task.status()
    except Exception:
        status = {}
    try:
        scene_count = int(collection.size().getInfo())
    except Exception:
        scene_count = None
    task_id = str(status.get("id") or getattr(task, "id", "") or "")
    state = str(status.get("state") or ("STARTED" if start_task else "READY"))
    created_at = datetime.now(timezone.utc).isoformat()
    drive_search_url = "https://drive.google.com/drive/search?q=" + urllib.parse.quote(file_name_prefix)
    task_record = {
        "id": task_id or f"drive-{description}-{aoi_digest}",
        "type": "drive-export",
        "analysis": "ndvi",
        "title": "NDVI export to Google Drive",
        "status": state,
        "destination": "Google Drive",
        "folder": folder,
        "fileNamePrefix": file_name_prefix,
        "taskId": task_id,
        "taskName": description,
        "driveSearchUrl": drive_search_url,
        "createdAt": created_at,
        "updatedAt": created_at,
        "params": {
            "dataset": "COPERNICUS/S2_SR_HARMONIZED",
            "index": "NDVI",
            "method": method,
            "startDate": start_date,
            "endDate": end_date,
            "cloudPct": cloud_pct,
            "scale": scale,
            "fileFormat": file_format,
            "cloudOptimized": cloud_optimized if file_format.lower() == "geotiff" else False,
            "maxPixels": max_pixels,
            "sceneCount": scene_count,
            "aoi": aoi,
        },
        "notes": [
            "Drive file URLs are only available after the Earth Engine task finishes; search Drive by fileNamePrefix.",
        ],
        "warnings": warnings,
    }
    return {"ok": True, "task": task_record, "export": task_record, "warnings": warnings}


def safe_band_names(image: Any, limit: int = 16) -> list[str]:
    try:
        bands = image.bandNames().getInfo()
        if isinstance(bands, list):
            return [str(band) for band in bands[:limit]]
    except Exception:
        pass
    return []


def collection_with_fallback(collection: Any, roi: Any, start_date: str, end_date: str, warnings: list[str]) -> Any:
    filtered = collection.filterBounds(roi)
    if start_date and end_date:
        dated = filtered.filterDate(start_date, end_date)
        try:
            if int(dated.limit(1).size().getInfo()) > 0:
                return dated
            warnings.append("No images matched the selected date range; using recent nearby images.")
        except Exception:
            return dated
    try:
        return filtered.sort("system:time_start", False).limit(24)
    except Exception:
        return filtered


def percentile_vis(image: Any, roi: Any, band: str) -> dict[str, Any]:
    try:
        import ee

        stats = (
            image.select(band)
            .reduceRegion(
                reducer=ee.Reducer.percentile([2, 98]),
                geometry=roi,
                scale=1000,
                bestEffort=True,
                maxPixels=100000,
                tileScale=2,
            )
            .getInfo()
        )
        values = [float(value) for value in stats.values() if value is not None]
        if len(values) >= 2 and min(values) < max(values):
            return {"min": min(values), "max": max(values), "palette": ["#132b43", "#2c7fb8", "#7fcdbb", "#ffffcc"]}
    except Exception:
        pass
    return {"min": 0, "max": 1, "palette": ["#132b43", "#2c7fb8", "#7fcdbb", "#ffffcc"]}


def generic_vis_for_image(image: Any, roi: Any, dataset_id: str) -> tuple[dict[str, Any], list[list[str]], str]:
    bands = safe_band_names(image)
    band_set = set(bands)
    rgb_candidates = [
        (["B4", "B3", "B2"], {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000, "gamma": 1.15}),
        (["SR_B4", "SR_B3", "SR_B2"], {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 5000, "max": 18000, "gamma": 1.2}),
        (["red", "green", "blue"], {"bands": ["red", "green", "blue"], "min": 0, "max": 1}),
        (["Red", "Green", "Blue"], {"bands": ["Red", "Green", "Blue"], "min": 0, "max": 1}),
    ]
    for required, vis in rgb_candidates:
        if set(required).issubset(band_set):
            return vis, [["#6f9fcf", "Auto RGB composite"]], "auto-rgb"
    if not bands:
        return {"min": 0, "max": 1}, [["#7fcdbb", "Default visualization"]], "default"
    band = bands[0]
    lowered = f"{dataset_id} {band}".lower()
    if "ndvi" in lowered or band.upper() in {"NDVI", "EVI"}:
        return (
            {"bands": [band], "min": 0, "max": 0.8, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]},
            [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]],
            "auto-index",
        )
    if any(term in lowered for term in ["temperature", "lst", "thermal"]):
        return (
            {"bands": [band], "min": 0, "max": 45, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]},
            [["#313695", "Cool"], ["#ffffbf", "Moderate"], ["#a50026", "Hot"]],
            "auto-temperature",
        )
    vis = percentile_vis(image, roi, band)
    vis["bands"] = [band]
    return vis, [["#132b43", "Low"], ["#7fcdbb", "Mid"], ["#ffffcc", "High"]], "auto-percentile"


def sanitize_color(value: Any) -> str | None:
    text = str(value or "").strip()
    if len(text) in {4, 7} and text.startswith("#") and all(ch in "0123456789abcdefABCDEF" for ch in text[1:]):
        return text
    return None


def sanitize_vis_params(value: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return dict(fallback)
    vis = dict(fallback)
    for key in ("min", "max", "gamma"):
        if key in value:
            try:
                number = float(value[key])
            except Exception:
                continue
            if math.isfinite(number):
                vis[key] = number
    if isinstance(value.get("bands"), list):
        bands = [str(item) for item in value["bands"] if str(item).strip()]
        if bands:
            vis["bands"] = bands[:4]
    if isinstance(value.get("palette"), list):
        palette = [color for color in (sanitize_color(item) for item in value["palette"]) if color]
        if len(palette) >= 2:
            vis["palette"] = palette[:32]
    return vis


def sanitize_legend(value: Any, fallback: list[list[str]]) -> list[list[str]]:
    if not isinstance(value, list):
        return fallback
    rows: list[list[str]] = []
    for item in value[:32]:
        if not isinstance(item, list) or len(item) < 2:
            continue
        color = sanitize_color(item[0])
        label = str(item[1] or "").strip()
        if color and label:
            rows.append([color, label[:80]])
    return rows or fallback


def parse_recipe_float(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except Exception:
        return fallback
    return number if math.isfinite(number) else fallback


def parse_months(value: Any) -> list[int]:
    if value is None:
        return []
    raw_items: list[Any]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if "-" in text and "," not in text:
            start, end = text.split("-", 1)
            try:
                start_i = int(start)
                end_i = int(end)
            except Exception:
                return []
            raw_items = list(range(min(start_i, end_i), max(start_i, end_i) + 1))
        else:
            raw_items = re.split(r"[\s,;]+", text)
    elif isinstance(value, list):
        raw_items = value
    else:
        raw_items = [value]
    months: list[int] = []
    for item in raw_items:
        try:
            month = int(item)
        except Exception:
            continue
        if 1 <= month <= 12 and month not in months:
            months.append(month)
    return sorted(months)


def recipe_date_range(recipe: dict[str, Any], fallback_start: str, fallback_end: str) -> tuple[str, str, list[int]]:
    months = parse_months(recipe.get("months") or recipe.get("calendarMonths"))
    year: int | None = None
    try:
        if recipe.get("year") not in (None, ""):
            year = int(recipe["year"])
    except Exception:
        year = None
    if year and months:
        start_month = min(months)
        end_month = max(months)
        start_date = f"{year:04d}-{start_month:02d}-01"
        if end_month == 12:
            end_date = f"{year + 1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{end_month + 1:02d}-01"
        return start_date, end_date, months
    start_date = str(recipe.get("startDate") or fallback_start)
    end_date = str(recipe.get("endDate") or fallback_end)
    return start_date, end_date, months


def default_recipe_scale(dataset_id: str, band: str, recipe: dict[str, Any]) -> tuple[float, float]:
    if recipe.get("scaleFactor") not in (None, "") or recipe.get("offset") not in (None, ""):
        return parse_recipe_float(recipe.get("scaleFactor"), 1.0), parse_recipe_float(recipe.get("offset"), 0.0)
    band_upper = band.upper()
    if dataset_id == "MODIS/061/MOD13Q1" and band_upper in {"NDVI", "EVI"}:
        return 0.0001, 0.0
    if dataset_id == "MODIS/061/MOD11A2" and band_upper.startswith("LST_"):
        return 0.02, -273.15
    return 1.0, 0.0


def normalize_layer_recipe(payload: dict[str, Any], dataset_id: str, start_date: str, end_date: str) -> dict[str, Any] | None:
    raw = payload.get("recipe") if isinstance(payload.get("recipe"), dict) else None
    if not raw:
        return None
    if str(raw.get("kind") or "").lower() == "preview":
        return None
    recipe = dict(raw)
    recipe_dataset = str(recipe.get("datasetId") or dataset_id).strip()
    if recipe_dataset and recipe_dataset != dataset_id:
        raise ValueError("recipe.datasetId must match datasetId")
    band = str(recipe.get("band") or recipe.get("index") or "").strip()
    if not band:
        raise ValueError("recipe.band is required for ImageCollection recipes")
    reducer = str(recipe.get("temporalReducer") or recipe.get("reducer") or "median").strip().lower()
    aliases = {"maximum": "max", "minimum": "min", "avg": "mean", "average": "mean"}
    reducer = aliases.get(reducer, reducer)
    if reducer not in {"median", "mean", "max", "min", "mode", "mosaic"}:
        raise ValueError("recipe.temporalReducer must be one of median, mean, max, min, mode, or mosaic")
    recipe_start, recipe_end, months = recipe_date_range(recipe, start_date, end_date)
    scale_factor, offset = default_recipe_scale(dataset_id, band, recipe)
    normalized: dict[str, Any] = {
        "kind": str(recipe.get("kind") or "imageCollection").strip() or "imageCollection",
        "source": str(recipe.get("source") or "agent-recipe"),
        "datasetId": dataset_id,
        "band": band,
        "outputBand": str(recipe.get("outputBand") or band).strip() or band,
        "temporalReducer": reducer,
        "startDate": recipe_start,
        "endDate": recipe_end,
        "scaleFactor": scale_factor,
        "offset": offset,
        "aoi": "currentAOI",
    }
    if recipe.get("year") not in (None, ""):
        try:
            normalized["year"] = int(recipe["year"])
        except Exception:
            pass
    if months:
        normalized["months"] = months
    if recipe.get("name"):
        normalized["name"] = str(recipe["name"])[:120]
    if recipe.get("description"):
        normalized["description"] = str(recipe["description"])[:500]
    if isinstance(recipe.get("visParams"), dict):
        normalized["visParams"] = recipe["visParams"]
    if isinstance(recipe.get("legend"), list):
        normalized["legend"] = recipe["legend"]
    return normalized


def recipe_default_vis(dataset_id: str, band: str) -> tuple[dict[str, Any], list[list[str]], str]:
    text = f"{dataset_id} {band}".lower()
    if "ndvi" in text or band.upper() in {"NDVI", "EVI"}:
        return (
            {"bands": [band], "min": 0, "max": 0.9, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]},
            [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]],
            "ndvi",
        )
    if any(term in text for term in ["lst", "temperature", "thermal"]):
        return (
            {"bands": [band], "min": 0, "max": 45, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]},
            [["#313695", "Cool"], ["#ffffbf", "Moderate"], ["#a50026", "Hot"]],
            "temperature",
        )
    return (
        {"bands": [band], "min": 0, "max": 1, "palette": ["#132b43", "#2c7fb8", "#7fcdbb", "#ffffcc"]},
        [["#132b43", "Low"], ["#7fcdbb", "Mid"], ["#ffffcc", "High"]],
        "raster",
    )


def recipe_period_label(recipe: dict[str, Any]) -> str:
    if recipe.get("year") and recipe.get("months"):
        months = recipe["months"]
        if isinstance(months, list) and months:
            if len(months) > 1 and months == list(range(min(months), max(months) + 1)):
                return f"{recipe['year']} months {min(months)}-{max(months)}"
            return f"{recipe['year']} months {','.join(str(item) for item in months)}"
    return f"{recipe.get('startDate')}..{recipe.get('endDate')}"


def recipe_layer_name(catalog_item: dict[str, Any], recipe: dict[str, Any]) -> str:
    if recipe.get("name"):
        return str(recipe["name"])
    label = str(catalog_item.get("label") or recipe.get("datasetId") or "GEE layer")
    reducer = str(recipe.get("temporalReducer") or "").upper()
    band = str(recipe.get("outputBand") or recipe.get("band") or "")
    return f"{label} {band} {reducer}".strip()


def preview_recipe(dataset_id: str, catalog_item: dict[str, Any], start_date: str, end_date: str, method: str) -> dict[str, Any]:
    label = str(catalog_item.get("label") or dataset_id)
    return {
        "kind": "preview",
        "source": "map-console-default-preview",
        "datasetId": dataset_id,
        "label": label,
        "operation": method,
        "startDate": start_date,
        "endDate": end_date,
        "aoi": "currentAOI",
        "description": "Default quick-preview recipe. Use an explicit recipe for analytical requests.",
    }


def build_recipe_image(
    ee: Any,
    dataset_id: str,
    catalog_item: dict[str, Any],
    roi: Any,
    recipe: dict[str, Any],
    warnings: list[str],
) -> tuple[Any, dict[str, Any], str, str, list[list[str]], str, dict[str, Any]]:
    collection = (
        ee.ImageCollection(dataset_id)
        .filterBounds(roi)
        .filterDate(str(recipe["startDate"]), str(recipe["endDate"]))
    )
    months = recipe.get("months")
    if isinstance(months, list) and months:
        month_values = [int(month) for month in months]
        if month_values == list(range(min(month_values), max(month_values) + 1)):
            collection = collection.filter(ee.Filter.calendarRange(min(month_values), max(month_values), "month"))
        else:
            collection = collection.map(lambda image: image.set("easygee_month", ee.Date(image.get("system:time_start")).get("month")))
            collection = collection.filter(ee.Filter.inList("easygee_month", month_values))
    band = str(recipe["band"])
    output_band = str(recipe.get("outputBand") or band)
    scale_factor = float(recipe.get("scaleFactor") or 1)
    offset = float(recipe.get("offset") or 0)

    def transform(image: Any) -> Any:
        selected = image.select(band)
        if scale_factor != 1:
            selected = selected.multiply(scale_factor)
        if offset:
            selected = selected.add(offset)
        return selected.rename(output_band).copyProperties(image, ["system:time_start"])

    prepared = collection.map(transform)
    reducer = str(recipe["temporalReducer"])
    if reducer == "max":
        image = prepared.max()
    elif reducer == "min":
        image = prepared.min()
    elif reducer == "mean":
        image = prepared.mean()
    elif reducer == "mode":
        image = prepared.mode()
    elif reducer == "mosaic":
        image = prepared.mosaic()
    else:
        image = prepared.median()
    image = image.rename(output_band).clip(roi)
    vis, legend, profile = recipe_default_vis(dataset_id, output_band)
    method = f"recipe:{reducer}:{band}"
    recipe["periodLabel"] = recipe_period_label(recipe)
    recipe["styleProfile"] = profile
    recipe["label"] = recipe_layer_name(catalog_item, recipe)
    return image, vis, recipe["label"], "ee-derived", legend, method, recipe


def style_profile_for_layer(dataset_id: str, layer_type: str, method: str, name: str) -> str:
    text = f"{dataset_id} {layer_type} {method} {name}".lower()
    if "ndvi" in text or "vegetation" in text:
        return "ndvi"
    if "jrc" in text or "water" in text or "gsw" in text:
        return "water"
    if "lst" in text or "temperature" in text or "thermal" in text:
        return "temperature"
    if "dem" in text or "elevation" in text or "terrain" in text:
        return "terrain"
    if "viirs" in text or "night" in text:
        return "nightlights"
    if "population" in text or "worldpop" in text or "ghsl" in text:
        return "population"
    if "categorical" in layer_type:
        return "categorical"
    if "vector" in layer_type:
        return "vector"
    return "raster"


def known_catalog_image(
    ee: Any,
    dataset_id: str,
    roi: Any,
    start_date: str,
    end_date: str,
    cloud_pct: float,
    warnings: list[str],
) -> tuple[Any, dict[str, Any], str, str, list[list[str]], str] | None:
    if dataset_id in S2_NDVI_DERIVED_IDS:
        image, _, method = sentinel2_ndvi_image(ee, roi, start_date, end_date, cloud_pct, warnings)
        return image, {"min": 0, "max": 0.8, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]}, "Sentinel-2 NDVI", "ee-derived", [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]], method
    if dataset_id == "COPERNICUS/S2_SR_HARMONIZED":
        image = (
            ee.ImageCollection(dataset_id)
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))
            .median()
            .clip(roi)
        )
        return image, {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000, "gamma": 1.15}, "Sentinel-2 RGB", "ee-raster", [["#6f9fcf", "Median RGB composite"]], "sentinel-2-rgb"
    if dataset_id == "COPERNICUS/S1_GRD":
        image = (
            ee.ImageCollection(dataset_id)
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .select("VV")
            .median()
            .clip(roi)
        )
        return image, {"min": -25, "max": 0, "palette": ["#0b132b", "#1c7293", "#f4f1de"]}, "Sentinel-1 VV", "ee-raster", [["#0b132b", "Low backscatter"], ["#f4f1de", "High backscatter"]], "sentinel-1-vv"
    if dataset_id == "GOOGLE/DYNAMICWORLD/V1":
        image = (
            ee.ImageCollection(dataset_id)
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .select("label")
            .mode()
            .clip(roi)
        )
        return (
            image,
            {
                "min": 0,
                "max": 8,
                "palette": ["#419bdf", "#397d49", "#88b053", "#7a87c6", "#e49635", "#dfc35a", "#c4281b", "#a59b8f", "#b39fe1"],
            },
            "Dynamic World mode",
            "ee-categorical",
            [["#419bdf", "Water"], ["#397d49", "Trees"], ["#c4281b", "Built"]],
            "dynamic-world-mode",
        )
    if dataset_id == "JRC/GSW1_4/GlobalSurfaceWater":
        image = ee.Image(dataset_id).select("occurrence").clip(roi)
        return image, {"min": 0, "max": 100, "palette": ["#f7fbff", "#6baed6", "#08306b"]}, "JRC water occurrence", "ee-raster", [["#f7fbff", "Rare"], ["#6baed6", "Seasonal"], ["#08306b", "Persistent"]], "jrc-water-occurrence"
    if dataset_id in {"USGS/SRTMGL1_003", "COPERNICUS/DEM/GLO30"}:
        band = "elevation" if dataset_id == "USGS/SRTMGL1_003" else "DEM"
        image = ee.Image(dataset_id).select(band).clip(roi)
        return image, {"min": 0, "max": 1000, "palette": ["#0f3b2e", "#3f7d3f", "#c9b96d", "#a2673f", "#f4f1e8"]}, "Elevation", "ee-raster", [["#0f3b2e", "Low"], ["#c9b96d", "Mid"], ["#f4f1e8", "High"]], "dem"
    if dataset_id == "ESA/WorldCover/v200":
        image = ee.ImageCollection(dataset_id).first().select("Map").clip(roi)
        return image, {"min": 10, "max": 100, "palette": ["#006400", "#ffbb22", "#ffff4c", "#f096ff", "#fa0000", "#b4b4b4", "#f0f0f0", "#0064c8", "#0096a0", "#00cf75", "#fae6a0"]}, "ESA WorldCover", "ee-categorical", [["#006400", "Trees"], ["#fa0000", "Built"], ["#0064c8", "Water"]], "worldcover"
    if dataset_id == "MODIS/061/MOD13Q1":
        coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
        image = coll.select("NDVI").median().multiply(0.0001).clip(roi)
        return image, {"min": 0, "max": 0.9, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]}, "MODIS NDVI", "ee-derived", [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]], "modis-ndvi"
    if dataset_id == "MODIS/061/MOD11A2":
        coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
        image = coll.select("LST_Day_1km").median().multiply(0.02).subtract(273.15).clip(roi)
        return image, {"min": 0, "max": 45, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]}, "MODIS LST Day", "ee-derived", [["#313695", "Cool"], ["#ffffbf", "Moderate"], ["#a50026", "Hot"]], "modis-lst"
    if dataset_id == "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG":
        coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
        image = coll.select("avg_rad").median().clip(roi)
        return image, {"min": 0, "max": 60, "palette": ["#03071e", "#370617", "#f48c06", "#ffba08"]}, "VIIRS nighttime lights", "ee-raster", [["#03071e", "Low"], ["#f48c06", "Medium"], ["#ffba08", "High"]], "viirs-nightlights"
    if dataset_id == "WorldPop/GP/100m/pop":
        coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
        image = coll.select("population").mosaic().clip(roi)
        return image, {"min": 0, "max": 100, "palette": ["#fff7ec", "#fdbb84", "#e34a33", "#7f0000"]}, "WorldPop population", "ee-raster", [["#fff7ec", "Sparse"], ["#e34a33", "Dense"]], "worldpop"
    return None


def build_catalog_layer(payload: dict[str, Any]) -> dict[str, Any]:
    import ee

    resolved_project = easygee_project.resolve_project(payload.get("project"), remember_discovered=True)
    project = resolved_project.project
    dataset_id = str(payload.get("datasetId") or payload.get("dataset") or "").strip()
    if not dataset_id:
        raise ValueError("datasetId is required")
    if not project or project == DEFAULT_PROJECT:
        raise ValueError("A concrete Earth Engine project id is required")
    aoi = normalize_aoi(payload)
    west, south, east, north = normalize_bounds(aoi["bounds"])
    start_date = str(payload.get("startDate") or "2024-01-01")
    end_date = str(payload.get("endDate") or datetime.now(timezone.utc).date().isoformat())
    try:
        cloud_pct = float(payload.get("cloudPct") or 80)
    except Exception:
        cloud_pct = 80.0
    catalog_item = payload.get("catalogItem") if isinstance(payload.get("catalogItem"), dict) else {}
    style_profile_hint = str(payload.get("styleProfile") or "").strip().lower()
    explicit_recipe = normalize_layer_recipe(payload, dataset_id, start_date, end_date)

    ee.Initialize(project=project)
    roi = ee_geometry_from_aoi(ee, aoi)
    warnings: list[str] = []

    def tile_url(image: Any, vis: dict[str, Any]) -> str:
        return image.getMapId(vis)["tile_fetcher"].url_format

    asset: dict[str, Any] = {}
    try:
        asset = ee.data.getAsset(dataset_id) or {}
    except Exception:
        asset = {}
    asset_type = str(asset.get("type") or catalog_item.get("type") or "").upper()
    known = None if explicit_recipe else known_catalog_image(ee, dataset_id, roi, start_date, end_date, cloud_pct, warnings)
    if not explicit_recipe and style_profile_hint == "ndvi" and dataset_id == "COPERNICUS/S2_SR_HARMONIZED":
        ndvi_image, _, ndvi_method = sentinel2_ndvi_image(ee, roi, start_date, end_date, cloud_pct, warnings)
        known = (
            ndvi_image,
            {"min": 0, "max": 0.8, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]},
            "Sentinel-2 NDVI",
            "ee-derived",
            [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]],
            ndvi_method,
        )
    image: Any
    vis: dict[str, Any]
    name: str
    layer_type: str
    legend: list[list[str]]
    method: str
    layer_recipe: dict[str, Any]
    if explicit_recipe:
        image, vis, name, layer_type, legend, method, layer_recipe = build_recipe_image(
            ee,
            dataset_id,
            catalog_item,
            roi,
            explicit_recipe,
            warnings,
        )
    elif known:
        image, vis, name, layer_type, legend, method = known
        layer_recipe = preview_recipe(dataset_id, catalog_item, start_date, end_date, method)
    else:
        attempts: list[str] = []
        if "TABLE" in asset_type or str(catalog_item.get("type") or "").lower() == "table":
            try:
                fc = ee.FeatureCollection(dataset_id).filterBounds(roi)
                image = fc.style(color="#16734d", fillColor="#16734d33", width=2).clip(roi)
                vis = {}
                name = str(catalog_item.get("label") or dataset_id)
                layer_type = "ee-vector"
                legend = [["#16734d", "Styled features"]]
                method = "featurecollection-style"
                layer_recipe = preview_recipe(dataset_id, catalog_item, start_date, end_date, method)
            except Exception as exc:
                attempts.append(f"FeatureCollection failed: {exc}")
                raise ValueError("; ".join(attempts) or "Could not render FeatureCollection") from exc
        else:
            try:
                if "IMAGE_COLLECTION" in asset_type or str(catalog_item.get("type") or "").lower() == "image_collection":
                    coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
                    image = coll.median().clip(roi)
                    method = "imagecollection-median"
                elif "IMAGE" in asset_type or str(catalog_item.get("type") or "").lower() == "image":
                    image = ee.Image(dataset_id).clip(roi)
                    method = "image"
                else:
                    try:
                        coll = collection_with_fallback(ee.ImageCollection(dataset_id), roi, start_date, end_date, warnings)
                        image = coll.median().clip(roi)
                        method = "imagecollection-median"
                    except Exception as exc:
                        attempts.append(f"ImageCollection failed: {exc}")
                        image = ee.Image(dataset_id).clip(roi)
                        method = "image"
                vis, legend, vis_method = generic_vis_for_image(image, roi, dataset_id)
                method = f"{method}:{vis_method}"
                name = str(catalog_item.get("label") or dataset_id)
                layer_type = "ee-raster"
                layer_recipe = preview_recipe(dataset_id, catalog_item, start_date, end_date, method)
            except Exception as exc:
                attempts.append(f"Image failed: {exc}")
                try:
                    fc = ee.FeatureCollection(dataset_id).filterBounds(roi)
                    image = fc.style(color="#16734d", fillColor="#16734d33", width=2).clip(roi)
                    vis = {}
                    name = str(catalog_item.get("label") or dataset_id)
                    layer_type = "ee-vector"
                    legend = [["#16734d", "Styled features"]]
                    method = "featurecollection-style"
                    layer_recipe = preview_recipe(dataset_id, catalog_item, start_date, end_date, method)
                except Exception as vector_exc:
                    attempts.append(f"FeatureCollection failed: {vector_exc}")
                    raise ValueError("; ".join(attempts)) from vector_exc

    requested_name = str(payload.get("name") or "").strip()
    if requested_name:
        name = requested_name[:120]
        layer_recipe["name"] = name
        layer_recipe["label"] = name
    style_profile = style_profile_for_layer(dataset_id, layer_type, method, name)
    default_style_preset = str(payload.get("stylePreset") or "default")
    vis_override = payload.get("visParams") if isinstance(payload.get("visParams"), dict) else layer_recipe.get("visParams")
    if isinstance(vis_override, dict):
        vis = sanitize_vis_params(vis_override, vis)
        default_style_preset = default_style_preset if default_style_preset != "default" else "custom"
    legend_override = payload.get("legend") if isinstance(payload.get("legend"), list) else layer_recipe.get("legend")
    legend = sanitize_legend(legend_override, legend)
    layer_recipe["visParams"] = vis
    layer_recipe["legend"] = legend
    layer = {
        "id": layer_id_for_dataset(f"{dataset_id}:{hashlib.sha1(json.dumps({'aoi': aoi, 'recipe': layer_recipe}, sort_keys=True).encode('utf-8')).hexdigest()[:12]}"),
        "name": name,
        "dataset": dataset_id,
        "type": layer_type,
        "shown": True,
        "opacity": 0.78 if layer_type == "ee-vector" else 0.82,
        "tileUrl": tile_url(image, vis),
        "legend": legend,
        "visParams": vis,
        "styleProfile": style_profile,
        "stylePreset": default_style_preset,
        "method": method,
        "recipe": layer_recipe,
        "summary": {
            "startDate": layer_recipe.get("startDate", start_date),
            "endDate": layer_recipe.get("endDate", end_date),
            "band": layer_recipe.get("band"),
            "temporalReducer": layer_recipe.get("temporalReducer") or layer_recipe.get("operation"),
            "periodLabel": layer_recipe.get("periodLabel"),
            "cloudPct": cloud_pct,
        },
        "aoi": aoi,
        "bounds": aoi["bounds"],
        "warnings": warnings,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    return {"ok": True, "layer": layer, "warnings": warnings}


def build_ndvi_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    import ee

    resolved_project = easygee_project.resolve_project(payload.get("project"), remember_discovered=True)
    project = resolved_project.project
    if not project or project == DEFAULT_PROJECT:
        raise ValueError("A concrete Earth Engine project id is required")
    aoi = normalize_aoi(payload)
    start_date = str(payload.get("startDate") or "2024-01-01")
    end_date = str(payload.get("endDate") or datetime.now(timezone.utc).date().isoformat())
    try:
        cloud_pct = float(payload.get("cloudPct") or 80)
    except Exception:
        cloud_pct = 80.0
    try:
        scale = float(payload.get("scale") or 10)
    except Exception:
        scale = 10.0

    ee.Initialize(project=project)
    roi = ee_geometry_from_aoi(ee, aoi)
    warnings: list[str] = []
    ndvi, collection, method = sentinel2_ndvi_image(ee, roi, start_date, end_date, cloud_pct, warnings)
    vis = {"min": 0, "max": 0.8, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]}
    reducer = (
        ee.Reducer.mean()
        .combine(ee.Reducer.median(), sharedInputs=True)
        .combine(ee.Reducer.minMax(), sharedInputs=True)
        .combine(ee.Reducer.stdDev(), sharedInputs=True)
        .combine(ee.Reducer.count(), sharedInputs=True)
    )
    stats = ndvi.reduceRegion(
        reducer=reducer,
        geometry=roi,
        scale=scale,
        bestEffort=True,
        maxPixels=1_000_000_000,
        tileScale=4,
    ).getInfo()
    valid_area = (
        ee.Image.pixelArea()
        .updateMask(ndvi.mask())
        .rename("valid_ndvi_area_m2")
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=roi,
            scale=scale,
            bestEffort=True,
            maxPixels=1_000_000_000,
            tileScale=4,
        )
        .getInfo()
    )
    try:
        scene_count = int(collection.size().getInfo())
    except Exception:
        scene_count = None
    summary = {
        "dataset": "COPERNICUS/S2_SR_HARMONIZED",
        "index": "NDVI",
        "method": method,
        "project": project,
        "startDate": start_date,
        "endDate": end_date,
        "cloudPct": cloud_pct,
        "scale": scale,
        "aoi": aoi,
        "aoiAreaM2": roi.area(maxError=1).getInfo(),
        "validNdviAreaM2": valid_area.get("valid_ndvi_area_m2"),
        "sceneCount": scene_count,
        "mean": stats.get("NDVI_mean"),
        "median": stats.get("NDVI_median"),
        "min": stats.get("NDVI_min"),
        "max": stats.get("NDVI_max"),
        "stdDev": stats.get("NDVI_stdDev"),
        "count": stats.get("NDVI_count"),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    layer = {
        "id": layer_id_for_dataset(
            "easygee-s2-ndvi:"
            + start_date
            + ":"
            + end_date
            + ":"
            + hashlib.sha1(json.dumps(aoi, sort_keys=True).encode("utf-8")).hexdigest()[:10]
        ),
        "name": "Sentinel-2 NDVI",
        "dataset": "EASYGEE/S2_NDVI",
        "type": "ee-derived",
        "shown": True,
        "opacity": 0.86,
        "tileUrl": ndvi.getMapId(vis)["tile_fetcher"].url_format,
        "legend": [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]],
        "visParams": vis,
        "styleProfile": "ndvi",
        "stylePreset": "default",
        "method": method,
        "aoi": aoi,
        "bounds": aoi["bounds"],
        "summary": summary,
        "warnings": warnings,
        "generatedAt": summary["generatedAt"],
    }
    return {"ok": True, "layer": layer, "summary": summary, "warnings": warnings}


def sample_quota_state(project: str) -> dict[str, Any]:
    return {
        "project": project,
        "service": "earthengine.googleapis.com",
        "consoleUrl": f"https://console.cloud.google.com/iam-admin/quotas?service=earthengine.googleapis.com&project={project}",
        "source": "official Earth Engine default",
        "usageSource": None,
        "refreshedAt": datetime.now(timezone.utc).isoformat(),
        "status": "default-only",
        "indicator": "warn",
        "warnings": ["Live quota lookup was not run."],
        "rows": [
            {
                "name": "Daily EECU time",
                "nameZh": "每日 EECU 计算时间",
                "nameEn": "Daily EECU time",
                "metric": "earthengine.googleapis.com/daily_eecu_usage_time",
                "limit": "Unlimited by default",
                "used": "N/A",
                "remaining": "N/A",
                "unit": "seconds/day",
                "status": "unknown",
                "source": "official Earth Engine default",
                "note": "Usage requires Cloud Monitoring.",
                "percent": None,
            },
            {
                "name": "Average batch tasks",
                "nameZh": "平均批处理任务",
                "nameEn": "Average batch tasks",
                "metric": "earthengine.googleapis.com",
                "limit": "2 tasks on average",
                "used": "N/A",
                "remaining": "N/A",
                "unit": "tasks",
                "status": "unknown",
                "source": "official Earth Engine default",
                "note": "Usage requires Cloud Monitoring.",
                "percent": None,
            },
            {
                "name": "Asset storage",
                "nameZh": "资产存储",
                "nameEn": "Asset storage",
                "metric": "earthengine.googleapis.com",
                "limit": "250 GB",
                "used": "N/A",
                "remaining": "N/A",
                "unit": "GB",
                "status": "unknown",
                "source": "official Earth Engine default",
                "note": "Usage requires Cloud Monitoring.",
                "percent": None,
            },
        ],
    }


def is_user_read_quota(quota: dict[str, Any]) -> bool:
    quota_name = str(quota.get("quota") or quota.get("name") or "").lower()
    squashed = "".join(char for char in quota_name if char.isalnum())
    return "read" in quota_name and (
        "peruser" in squashed or "peraccount" in squashed or "per user" in quota_name or "per account" in quota_name
    )


def quota_allows_inferred_zero(quota: dict[str, Any]) -> bool:
    metric = str(quota.get("metric") or "").lower()
    quota_name = str(quota.get("quota") or quota.get("name") or "").lower()
    return "bigquery_slot_usage_time" in metric or "bigquery slot" in quota_name


def quota_usage_unit(quota: dict[str, Any]) -> str | None:
    unit = str(quota.get("unit") or "").strip()
    metric = str(quota.get("metric") or "").lower()
    quota_name = str(quota.get("quota") or quota.get("name") or "").lower()
    if unit == "s{CPU}" or "eecu" in metric or "eecu" in quota_name or "slot" in metric or "slot" in quota_name:
        return unit
    return None


def quota_limit_unit(quota: dict[str, Any]) -> str:
    unit = str(quota.get("unit") or "").strip()
    return "" if unit == "-" else unit


def infer_noncommercial_tier(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in rows:
        quota_name = str(row.get("quota") or row.get("name") or "").lower()
        if not ("noncommercial" in quota_name and "eecu" in quota_name and "month" in quota_name):
            continue
        limit = parse_float(row.get("value"))
        if limit is None:
            continue
        rounded = int(round(limit))
        for known_limit, (name, name_zh, name_en) in NONCOMMERCIAL_TIER_LIMITS.items():
            if abs(rounded - known_limit) <= max(1, known_limit * 0.001):
                return {
                    "name": name,
                    "nameZh": name_zh,
                    "nameEn": name_en,
                    "kind": "noncommercial",
                    "source": "monthly_eecu_system_limit",
                    "limit": compact_value(row.get("value"), row.get("unit")),
                    "inferred": True,
                }
        return {
            "name": "Custom / Unknown",
            "nameZh": "自定义（非商业）",
            "nameEn": "Custom (noncommercial)",
            "kind": "noncommercial",
            "source": "monthly_eecu_system_limit",
            "limit": compact_value(row.get("value"), row.get("unit")),
            "inferred": True,
        }
    return None


def infer_commercial_tier(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Best-effort usage tier inference from quota-like commercial plan limits."""

    by_name = {str(row.get("quota") or row.get("name") or "").lower(): row for row in rows}

    def find_value(*needles: str) -> float | None:
        for name, row in by_name.items():
            if all(needle in name for needle in needles):
                return parse_float(row.get("value"))
        return None

    storage_gb = find_value("asset", "storage")
    high_volume = find_value("high-volume", "concurrent")
    batch_tasks = find_value("batch", "tasks")
    if storage_gb is not None and storage_gb >= 1000:
        return {
            "name": "Professional",
            "nameZh": "Professional（商业）",
            "nameEn": "Professional (commercial)",
            "kind": "commercial",
            "source": "storage_or_high_volume_quota",
            "inferred": True,
        }
    if high_volume is not None and high_volume >= 100:
        return {
            "name": "Professional",
            "nameZh": "Professional（商业）",
            "nameEn": "Professional (commercial)",
            "kind": "commercial",
            "source": "high_volume_quota",
            "inferred": True,
        }
    if batch_tasks is not None and batch_tasks >= 8:
        return {
            "name": "Basic",
            "nameZh": "Basic（商业）",
            "nameEn": "Basic (commercial)",
            "kind": "commercial",
            "source": "batch_task_quota",
            "inferred": True,
        }
    return None


def usage_matches_quota(quota: dict[str, Any], usage_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metric = str(quota.get("metric") or "").lower()
    metric_tail = metric.rsplit("/", 1)[-1] if "/" in metric else ""
    quota_name = str(quota.get("quota") or quota.get("name") or "").lower()
    matches: list[dict[str, Any]] = []
    if is_user_read_quota(quota):
        for usage in usage_rows:
            haystack = f"{usage.get('quota_metric', '')} {usage.get('limit_name', '')} {usage.get('labels', '')}".lower()
            squashed = "".join(char for char in haystack if char.isalnum())
            if "read" in haystack and (
                "peruser" in squashed or "peraccount" in squashed or "user" in haystack or "account" in haystack
            ):
                matches.append(usage)
        return matches
    for usage in usage_rows:
        haystack = f"{usage.get('quota_metric', '')} {usage.get('limit_name', '')}".lower()
        if metric and metric != "earthengine.googleapis.com" and (metric in haystack or metric_tail in haystack):
            matches.append(usage)
            continue
        if "asset" in quota_name and "asset" in haystack:
            matches.append(usage)
            continue
        if "batch" in quota_name and ("task" in haystack or "batch" in haystack):
            matches.append(usage)
    return matches


def usage_for_quota(quota: dict[str, Any], usage_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = usage_matches_quota(quota, usage_rows)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    values = [parse_float(str(usage.get("value") or "")) for usage in matches]
    numeric_values = [value for value in values if value is not None]
    if not numeric_values:
        return matches[0]
    latest = max(str(usage.get("end_time") or "") for usage in matches)
    return {
        "quota_metric": matches[0].get("quota_metric") or "",
        "limit_name": matches[0].get("limit_name") or "",
        "metric_type": matches[0].get("metric_type") or "",
        "value": f"{sum(numeric_values):g}",
        "end_time": latest,
        "labels": f"{len(numeric_values)} series",
    }


def is_nonblocking_quota_fallback_warning(warning: Any) -> bool:
    text = str(warning or "").lower()
    return (
        "skipping gcloud quota command groups" in text
        and "local components" in text
        and ("alpha" in text or "beta" in text)
    )


def report_warnings_for_console(report_json: dict[str, Any]) -> list[str]:
    warnings = [str(item) for item in (report_json.get("warnings") or []) if str(item).strip()]
    if report_json.get("live_source"):
        warnings = [item for item in warnings if not is_nonblocking_quota_fallback_warning(item)]
    return warnings


def quota_state_from_report(report: Any) -> dict[str, Any]:
    report_json = report_to_plain_json(report)
    source_rows = report_json.get("live_quotas") or report_json.get("default_quotas") or []
    source = report_json.get("live_source") or "official Earth Engine default"
    usage_source = report_json.get("usage_source")
    usage_rows = report_json.get("usage_rows") or []
    source_is_default = "default" in str(source).lower()
    tier = infer_noncommercial_tier(source_rows)
    if tier is None and not source_is_default:
        tier = infer_commercial_tier(source_rows)
    rows: list[dict[str, Any]] = []
    preferred_terms = ("eecu", "batch", "asset", "request", "slot")
    ordered_rows = sorted(
        source_rows,
        key=lambda row: (
            0 if any(term in str(row.get("quota", "")).lower() for term in preferred_terms) else 1,
            str(row.get("quota", "")).lower(),
        ),
    )
    for row in ordered_rows[:8]:
        row_name = row.get("quota") or row.get("name") or "quota"
        name_zh, name_en = quota_label_pair(str(row_name))
        usage = usage_for_quota(row, usage_rows)
        unlimited_limit = is_unlimited_quota_value(row.get("value"))
        limit_number = parse_float(row.get("value"))
        used_number = parse_float(usage.get("value") if usage else None)
        inferred_zero_usage = False
        if usage_source and usage is None and limit_number is not None and quota_allows_inferred_zero(row):
            used_number = 0.0
            inferred_zero_usage = True
        percent = None
        remaining = "N/A"
        status = "unknown"
        note = ""
        usage_known = used_number is not None
        if not usage:
            note = (
                "No usage time series in the selected Monitoring window; displayed as zero."
                if inferred_zero_usage
                else "Usage time series is not provided for this quota dimension."
                if usage_source
                else "Usage requires Cloud Monitoring."
            )
        if unlimited_limit:
            remaining = "Unlimited"
            status = "ok" if usage_known else "unknown"
        elif limit_number is not None and used_number is not None:
            remaining_number = max(0.0, limit_number - used_number)
            remaining = f"{remaining_number:g} {quota_limit_unit(row)}".strip()
            percent = round(min(100.0, max(0.0, (used_number / limit_number) * 100.0)), 1) if limit_number else None
            status = "warn" if percent is not None and percent >= 80 else "ok"
        usage_unit = quota_usage_unit(row)
        rows.append(
            {
                "name": row_name,
                "nameZh": name_zh,
                "nameEn": name_en,
                "metric": row.get("metric") or "",
                "limit": compact_value(row.get("value"), row.get("unit")),
                "used": compact_value(
                    "0" if inferred_zero_usage else (usage.get("value") if usage else None),
                    usage_unit if (inferred_zero_usage or usage) else None,
                ),
                "remaining": remaining,
                "unit": row.get("unit") or "",
                "status": status,
                "source": row.get("source") or source,
                "note": note,
                "percent": percent,
                "unlimited": unlimited_limit,
                "usageKnown": usage_known,
                "inferredZeroUsage": inferred_zero_usage,
            }
        )
    status = "default-only"
    indicator = "warn"
    if report_json.get("live_source") and usage_source and any(item.get("percent") is not None for item in rows):
        status = "live-with-usage"
        indicator = "warn" if any(item.get("status") == "warn" for item in rows) else "ok"
    elif report_json.get("live_source"):
        status = "live-limit-only"
        indicator = "warn"
    return {
        "project": report_json.get("project"),
        "service": report_json.get("service"),
        "consoleUrl": report_json.get("console_url"),
        "source": source,
        "usageSource": usage_source,
        "refreshedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "indicator": indicator,
        "warnings": report_warnings_for_console(report_json),
        "tier": tier,
        "rows": rows,
    }


def report_to_plain_json(report: Any) -> dict[str, Any]:
    try:
        from show_ee_quotas import report_to_json

        return report_to_json(report)
    except Exception:
        return json.loads(json.dumps(asdict(report), ensure_ascii=False))


def build_quota_state(project: str, include_usage: bool, no_live: bool, minutes: int) -> dict[str, Any]:
    try:
        from show_ee_quotas import build_report

        args = argparse.Namespace(
            project=project,
            console_url=None,
            service=None,
            no_live=no_live,
            include_usage=include_usage,
            minutes=minutes,
        )
        return quota_state_from_report(build_report(args))
    except Exception as exc:
        state = sample_quota_state(project)
        state["warnings"] = [f"Quota lookup failed: {exc}"]
        return state


def leaflet_css() -> str:
    return "\n" + map_console_asset("leaflet.css") + "    "


def shell_css() -> str:
    return "\n" + map_console_asset("shell.css") + "    "


def sample_state(project: str, title: str) -> dict:
    layers: list[dict[str, object]] = []
    catalog, catalog_source = build_catalog(layers, include_remote=False)
    return {
        "title": title,
        "project": project,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "center": [30.25, 120.16],
        "zoom": 10,
        "bounds": [[29.9954, 119.8684], [30.5044, 120.4522]],
        "startDate": "2024-01-01",
        "endDate": datetime.now(timezone.utc).date().isoformat(),
        "cloudPct": 80,
        "layers": layers,
        "catalog": catalog,
        "catalogSource": catalog_source,
        "tasks": [
            {"name": "Generate console", "status": "done"},
            {"name": "Load EE tiles", "status": "waiting"},
            {"name": "Inspect map clicks", "status": "ready"},
        ],
        "quota": sample_quota_state(project),
    }


def empty_state(args: argparse.Namespace) -> dict:
    catalog, catalog_source = build_catalog(
        [],
        include_remote=True,
        catalog_mode=args.catalog_mode,
        refresh_catalog=args.refresh_catalog,
        catalog_cache_hours=args.catalog_cache_hours,
        catalog_fetch_seconds=args.catalog_fetch_seconds,
    )
    return {
        "title": args.title,
        "project": args.project,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "center": [args.lat, args.lon],
        "zoom": args.zoom,
        "bounds": None,
        "startDate": args.start_date,
        "endDate": args.end_date,
        "cloudPct": args.cloud_pct,
        "layers": [],
        "catalog": catalog,
        "catalogSource": catalog_source,
        "tasks": [
            {"name": "Open map console", "status": "done"},
            {"name": "Choose dataset or draw AOI", "status": "ready"},
            {"name": "Add first layer", "status": "ready"},
        ],
    }


def live_state(args: argparse.Namespace) -> dict:
    import ee

    ee.Initialize(project=args.project)
    roi = ee.Geometry.Point([args.lon, args.lat]).buffer(args.buffer_m).bounds()
    bounds_coords = roi.coordinates().getInfo()[0]
    lons = [pt[0] for pt in bounds_coords]
    lats = [pt[1] for pt in bounds_coords]
    bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(args.start_date, args.end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", args.cloud_pct))
        .median()
        .clip(roi)
    )
    rgb = s2.visualize(bands=["B4", "B3", "B2"], min=0, max=3000, gamma=1.15)
    ndvi = s2.normalizedDifference(["B8", "B4"]).rename("NDVI").clip(roi)
    dem = ee.Image("USGS/SRTMGL1_003").select("elevation").unmask(0).clip(roi)
    dynamic_world = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(roi)
        .filterDate(args.start_date, args.end_date)
        .select("label")
        .mode()
        .clip(roi)
    )
    water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").clip(roi)

    def tile_url(image: object, vis: dict) -> str:
        return image.getMapId(vis)["tile_fetcher"].url_format

    layers = [
        {
                "id": "srtm",
                "name": "SRTM elevation",
                "dataset": "USGS/SRTMGL1_003",
                "type": "ee-raster",
                "shown": True,
                "opacity": 0.58,
                "tileUrl": tile_url(
                    dem,
                    {
                        "min": 0,
                        "max": 600,
                        "palette": ["#0f3b2e", "#3f7d3f", "#c9b96d", "#a2673f", "#f4f1e8"],
                    },
                ),
                "legend": [
                    ["#0f3b2e", "Lower elevation"],
                    ["#c9b96d", "Mid elevation"],
                    ["#f4f1e8", "Higher elevation"],
                ],
                "visParams": {"min": 0, "max": 600, "palette": ["#0f3b2e", "#3f7d3f", "#c9b96d", "#a2673f", "#f4f1e8"]},
                "styleProfile": "terrain",
                "stylePreset": "default",
            },
            {
                "id": "s2-rgb",
                "name": "Sentinel-2 RGB",
                "dataset": "COPERNICUS/S2_SR_HARMONIZED",
                "type": "ee-raster",
                "shown": False,
                "opacity": 0.74,
                "tileUrl": tile_url(rgb, {}),
                "legend": [["#6f9fcf", "Median RGB composite"]],
            },
            {
                "id": "ndvi",
                "name": "NDVI",
                "dataset": "COPERNICUS/S2_SR_HARMONIZED",
                "type": "ee-derived",
                "shown": False,
                "opacity": 0.86,
                "tileUrl": tile_url(
                    ndvi,
                    {
                        "min": 0,
                        "max": 0.8,
                        "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"],
                    },
                ),
                "legend": [["#2c105c", "Low"], ["#31a354", "Medium"], ["#f7fcb9", "High"]],
                "visParams": {"min": 0, "max": 0.8, "palette": ["#2c105c", "#4856a5", "#31a354", "#addd8e", "#f7fcb9"]},
                "styleProfile": "ndvi",
                "stylePreset": "default",
            },
            {
                "id": "dynamic-world",
                "name": "Dynamic World mode",
                "dataset": "GOOGLE/DYNAMICWORLD/V1",
                "type": "ee-categorical",
                "shown": False,
                "opacity": 0.72,
                "tileUrl": tile_url(
                    dynamic_world,
                    {
                        "min": 0,
                        "max": 8,
                        "palette": [
                            "#419bdf",
                            "#397d49",
                            "#88b053",
                            "#7a87c6",
                            "#e49635",
                            "#dfc35a",
                            "#c4281b",
                            "#a59b8f",
                            "#b39fe1",
                        ],
                    },
                ),
                "legend": [["#419bdf", "Water"], ["#397d49", "Trees"], ["#e49635", "Built"]],
                "visParams": {"min": 0, "max": 8, "palette": ["#419bdf", "#397d49", "#88b053", "#7a87c6", "#e49635", "#dfc35a", "#c4281b", "#a59b8f", "#b39fe1"]},
                "styleProfile": "categorical",
                "stylePreset": "default",
            },
            {
                "id": "jrc-water",
                "name": "JRC water occurrence",
                "dataset": "JRC/GSW1_4/GlobalSurfaceWater",
                "type": "ee-raster",
                "shown": False,
                "opacity": 0.76,
                "tileUrl": tile_url(water, {"min": 0, "max": 100, "palette": ["#f7fbff", "#6baed6", "#08306b"]}),
                "legend": [["#f7fbff", "Rare"], ["#6baed6", "Seasonal"], ["#08306b", "Persistent"]],
                "visParams": {"min": 0, "max": 100, "palette": ["#f7fbff", "#6baed6", "#08306b"]},
                "styleProfile": "water",
                "stylePreset": "default",
            },
    ]
    if getattr(args, "default_layer", None):
        layer_ids = {layer["id"] for layer in layers}
        if args.default_layer in layer_ids:
            for layer in layers:
                layer["shown"] = layer["id"] == args.default_layer
    catalog, catalog_source = build_catalog(
        layers,
        include_remote=True,
        catalog_mode=args.catalog_mode,
        refresh_catalog=args.refresh_catalog,
        catalog_cache_hours=args.catalog_cache_hours,
        catalog_fetch_seconds=args.catalog_fetch_seconds,
    )
    return {
        "title": args.title,
        "project": args.project,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "center": [args.lat, args.lon],
        "zoom": args.zoom,
        "bounds": bounds,
        "startDate": args.start_date,
        "endDate": args.end_date,
        "cloudPct": args.cloud_pct,
        "layers": layers,
        "catalog": catalog,
        "catalogSource": catalog_source,
        "tasks": [
            {"name": "Authenticate Earth Engine", "status": "done"},
            {"name": "Set default project", "status": "done"},
            {"name": "Generate map console", "status": "done"},
            {"name": "Inspect map clicks", "status": "ready"},
        ],
    }


def ensure_leaflet_js(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    target = root / LEAFLET_LOCAL
    if target.exists() and target.stat().st_size > 100_000:
        return f"./{LEAFLET_LOCAL}"
    try:
        with urllib.request.urlopen(LEAFLET_CDN, timeout=20) as response:
            data = response.read()
        if len(data) > 100_000:
            target.write_bytes(data)
            return f"./{LEAFLET_LOCAL}"
    except Exception:
        pass
    return LEAFLET_CDN


def valid_pmtiles_js(data: bytes) -> bool:
    return len(data) > 10_000 and b"PMTiles" in data and b"leafletRasterLayer" in data


def ensure_pmtiles_js(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    target = root / PMTILES_LOCAL
    if target.exists():
        try:
            if valid_pmtiles_js(target.read_bytes()):
                return f"./{PMTILES_LOCAL}"
        except OSError:
            pass
    try:
        with urllib.request.urlopen(PMTILES_CDN, timeout=20) as response:
            data = response.read()
        if valid_pmtiles_js(data):
            target.write_bytes(data)
            return f"./{PMTILES_LOCAL}"
    except Exception:
        pass
    return PMTILES_CDN


def valid_maplibre_js(data: bytes) -> bool:
    return len(data) > 800_000 and b"maplibregl" in data and b"addProtocol" in data


def valid_maplibre_css(data: bytes) -> bool:
    return len(data) > 50_000 and b".maplibregl-map" in data and b".maplibregl-canvas" in data


def valid_maplibre_leaflet_js(data: bytes) -> bool:
    return len(data) > 7_000 and b"maplibreGL" in data and b"getMaplibreMap" in data


def valid_cog_protocol_js(data: bytes) -> bool:
    return len(data) > 400_000 and b"MaplibreCOGProtocol" in data and b"getCogMetadata" in data


def ensure_preview_asset(root: Path, local_name: str, url: str, validator: Any) -> str:
    root.mkdir(parents=True, exist_ok=True)
    target = root / local_name
    if target.exists():
        try:
            if validator(target.read_bytes()):
                return f"./{local_name}"
        except OSError:
            pass
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        if validator(data):
            target.write_bytes(data)
            return f"./{local_name}"
    except Exception:
        pass
    return url


def cog_engine_cdn_assets() -> dict[str, str]:
    return {
        "maplibreJs": MAPLIBRE_JS_CDN,
        "maplibreCss": MAPLIBRE_CSS_CDN,
        "leafletAdapterJs": MAPLIBRE_LEAFLET_CDN,
        "cogProtocolJs": COG_PROTOCOL_CDN,
    }


def ensure_cog_engine_assets(root: Path) -> dict[str, str]:
    return {
        "maplibreJs": ensure_preview_asset(root, MAPLIBRE_JS_LOCAL, MAPLIBRE_JS_CDN, valid_maplibre_js),
        "maplibreCss": ensure_preview_asset(root, MAPLIBRE_CSS_LOCAL, MAPLIBRE_CSS_CDN, valid_maplibre_css),
        "leafletAdapterJs": ensure_preview_asset(
            root,
            MAPLIBRE_LEAFLET_LOCAL,
            MAPLIBRE_LEAFLET_CDN,
            valid_maplibre_leaflet_js,
        ),
        "cogProtocolJs": ensure_preview_asset(
            root,
            COG_PROTOCOL_LOCAL,
            COG_PROTOCOL_CDN,
            valid_cog_protocol_js,
        ),
    }


def svg_icon(name: str) -> str:
    icons = {
        "data": '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5"/><path d="M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/></svg>',
        "layers": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 16 9 5 9-5"/></svg>',
        "add": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
        "overlay-add": '<svg class="lucide lucide-copy-plus" viewBox="0 0 24 24" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/><path d="M15 12v6M12 15h6"/></svg>',
        "info": '<svg class="lucide lucide-info" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
        "favorite": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2 7.5 14 3 9.6l6.2-.9L12 3Z"/></svg>',
        "external": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7H5v12h12v-3"/><path d="M11 5h8v8"/><path d="m10 14 9-9"/></svg>',
        "inspect": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>',
        "draw-aoi": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="12" height="10" rx="1.5"/><path d="M14 19h3l4-4-3-3-4 4v3Z"/><path d="m17 13 3 3"/></svg>',
        "measure": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 17 13-13 3 3L7 20l-3-3Z"/><path d="m14 6 2 2M11 9l2 2M8 12l2 2"/></svg>',
        "basemap": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="1.8"/><path d="M7 19c2.4-3.4 3.4-6.2 3.1-12"/><path d="M18 7c-3.9 1.1-6.7 3.2-9.2 6.2"/><path d="M13.4 19c.3-3 1.7-5.5 4.1-7.3"/><path d="M7 13h10"/></svg>',
        "quota": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 14a8 8 0 0 1 16 0"/><path d="M12 14l4-5"/><path d="M5 18h14"/><path d="M8 18v2M16 18v2"/></svg>',
        "drive": '<svg class="drive-mark" viewBox="0 0 24 24" aria-hidden="true"><path fill="#4f8f70" d="M8.4 3.1c.3-.5.8-.8 1.4-.8h4.7l6.3 10.9h-5.7L8.4 3.1Z"/><path fill="#5d86b6" d="M20.8 13.2 17.6 19c-.3.5-.8.8-1.4.8H4.8l3.3-6.6h12.7Z"/><path fill="#c2a44f" d="M20.8 13.2h-5.7L8.4 3.1l1.4-.8h4.7l6.3 10.9Z" fill-opacity=".88"/><path fill="#3e7f66" d="M8.4 3.1 2.2 13.8c-.3.5-.3 1.1 0 1.6l2.6 4.4 6.6-11.5-3-5.2Z"/><path fill="#fff" fill-opacity=".9" d="M11.4 8.3 15 13.2H8.1l3.3-4.9Z"/></svg>',
        "upload": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 16h2.2a3.8 3.8 0 0 0 .6-7.6A6.2 6.2 0 0 0 6.7 7.1 4.4 4.4 0 0 0 7.4 16H9"/><path d="M12 20V10"/><path d="m8.5 13.5 3.5-3.5 3.5 3.5"/></svg>',
        "tasks": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6h12M9 12h12M9 18h12"/><path d="m3 6 1 1 2-2M3 12l1 1 2-2M3 18l1 1 2-2"/></svg>',
        "home": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
        "zoom-layer": '<svg class="lucide lucide-scan" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>',
        "zoom-in": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="M10 7v6M7 10h6M15 15l5 5"/></svg>',
        "zoom-out": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="M7 10h6M15 15l5 5"/></svg>',
        "grip": '<svg class="lucide lucide-grip-vertical" viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="5" r="1"/><circle cx="15" cy="5" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="19" r="1"/><circle cx="15" cy="19" r="1"/></svg>',
        "language": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h9M8.5 5v2M11.5 5c-.8 4.7-3.5 7.3-7 8.8"/><path d="M5.5 9.5c1.2 2 3.1 3.5 5.5 4.4"/><path d="M14 20l4-9 4 9M15.2 17h5.6"/></svg>',
        "style": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0 0 18h1.5a1.8 1.8 0 0 0 .7-3.4 1.8 1.8 0 0 1 .7-3.4H16a5 5 0 0 0 0-10H12Z"/><circle cx="7.5" cy="10" r="1"/><circle cx="10.5" cy="7.5" r="1"/><circle cx="14" cy="7.5" r="1"/><circle cx="8.5" cy="14" r="1"/></svg>',
        "edit": '<svg class="lucide lucide-pencil" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.5z"/><path d="m15 5 4 4"/></svg>',
        "up": '<svg class="lucide lucide-chevron-up" viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>',
        "down": '<svg class="lucide lucide-chevron-down" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
        "undo": '<svg class="lucide lucide-undo-2" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-1"/></svg>',
        "refresh": '<svg class="lucide lucide-refresh-cw" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>',
        "trash": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16"/><path d="M9 7V5h6v2"/><path d="M7 7l1 13h8l1-13"/><path d="M10 11v5M14 11v5"/></svg>',
        "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    }
    return icons[name]


def render_html(
    state: dict,
    leaflet_src: str,
    pmtiles_src: str = PMTILES_CDN,
    cog_engine_assets: dict[str, str] | None = None,
) -> str:
    safe_title = html.escape(state["title"])
    safe_leaflet_src = html.escape(leaflet_src, quote=True)
    safe_pmtiles_src = html.escape(pmtiles_src, quote=True)
    cog_assets_json = json.dumps(cog_engine_assets or cog_engine_cdn_assets(), ensure_ascii=True).replace("</", "<\\/")
    logo_data_uri = html.escape(easygee_logo_data_uri(), quote=True)
    state_json = json.dumps(state, ensure_ascii=True).replace("</", "<\\/")
    logo_mark = (
        f'<img src="{logo_data_uri}" alt="" loading="eager" decoding="async">'
        if logo_data_uri
        else "EG"
    )
    values = {
        "TITLE": safe_title,
        "LOGO_DATA_URI": logo_data_uri,
        "LOGO_MARK": logo_mark,
        "LEAFLET_CSS": leaflet_css(),
        "SHELL_CSS": shell_css(),
        "LEAFLET_SRC": safe_leaflet_src,
        "PMTILES_SRC": safe_pmtiles_src,
        "STATE_JSON": state_json,
        "COG_ASSETS_JSON": cog_assets_json,
        "DEFAULT_CENTER_LAT": str(DEFAULT_EMPTY_CENTER[0]),
        "DEFAULT_CENTER_LON": str(DEFAULT_EMPTY_CENTER[1]),
        "DEFAULT_ZOOM": str(DEFAULT_EMPTY_ZOOM),
        "PMTILES_VERSION": PMTILES_VERSION,
        "MAPLIBRE_VERSION": MAPLIBRE_VERSION,
        "COG_PROTOCOL_VERSION": COG_PROTOCOL_VERSION,
    }

    def substitute(match: re.Match[str]) -> str:
        key = match.group(1)
        if key.startswith("ICON_"):
            return svg_icon(key[len("ICON_"):].lower().replace("_", "-"))
        return values[key]

    # Single pass: substituted values are never rescanned, so user text that
    # happens to look like a placeholder token is emitted verbatim.
    return MAP_CONSOLE_TOKEN.sub(substitute, map_console_page_template())


def write_console(
    output: Path,
    state: dict,
    leaflet_src: str,
    pmtiles_src: str = PMTILES_CDN,
    cog_engine_assets: dict[str, str] | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(state, leaflet_src, pmtiles_src, cog_engine_assets), encoding="utf-8")


def smoke() -> int:
    with tempfile.TemporaryDirectory(prefix="easygee-map-console-") as tmp:
        output = Path(tmp) / "index.html"
        state = sample_state("demo-project", "EasyGEE Smoke Console")
        write_console(output, state, LEAFLET_CDN, PMTILES_CDN)
        text = output.read_text(encoding="utf-8")
        required = [
            "EasyGEE Smoke Console",
            "Add layers",
            "Layers",
            "Inspector",
            "Tasks",
            "drive-btn",
            "Google Drive",
            "Quota items",
            "quota-stat-grid",
            "STATE =",
            ".leaflet-tile",
            "EsriClarity",
            "basemap-source-card",
            "basemapThumbSvg",
            "source.trigger",
            "basemap-editor",
            "addCustomBasemap",
            "customBasemaps",
            "PMTiles (raster)",
            "pmtiles.leafletRasterLayer",
            "HTTP Range",
            "maxNativeZoom: 13",
            "COG (MapLibre WebGL)",
            "COG_ENGINE_ASSETS",
            "MaplibreCOGProtocol.getCogMetadata",
            "L.maplibreGL",
            "maplibre-cog",
            "basemap-source-performance",
            "beginBasemapPerformance",
            "TiandituImagery",
            "TIANDITU_TOKEN_STORAGE_KEY",
            "TILEMATRIXSET=w",
            "collectBasemapNetworkPerformance",
            "const AGENT_PROTOCOL_VERSION = 5;",
        ]
        missing = [item for item in required if item not in text]
        if missing:
            print("FAIL missing markers: " + ", ".join(missing))
            return 1
        filtered = report_warnings_for_console(
            {
                "live_source": "Cloud Quotas REST API",
                "warnings": [
                    "Skipping gcloud quota command groups because local components are not installed: beta, alpha",
                    "Cloud Monitoring request failed: permission denied",
                ],
            }
        )
        if any("Skipping gcloud" in item for item in filtered) or not any("Monitoring" in item for item in filtered):
            print("FAIL quota fallback warning filtering")
            return 1
    print("create_map_console smoke passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="Earth Engine / Google Cloud project id")
    parser.add_argument("--output", type=Path, default=default_output(), help="HTML output path")
    parser.add_argument("--title", default="EasyGEE Map Console")
    parser.add_argument("--lat", type=float, default=DEFAULT_EMPTY_CENTER[0])
    parser.add_argument("--lon", type=float, default=DEFAULT_EMPTY_CENTER[1])
    parser.add_argument("--zoom", type=int, default=DEFAULT_EMPTY_ZOOM)
    parser.add_argument("--buffer-m", type=float, default=25000)
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--end-date", default="2024-12-31")
    parser.add_argument("--cloud-pct", type=float, default=35)
    parser.add_argument("--default-layer", default="", help="Layer id to show by default, for example ndvi, s2-rgb, dynamic-world, jrc-water, or srtm")
    parser.add_argument("--sample", action="store_true", help="Create the legacy sample console without Earth Engine calls")
    parser.add_argument("--live", action="store_true", help="Create a pre-populated Earth Engine demo with default layers")
    parser.add_argument("--no-live-quota", action="store_true", help="Skip Cloud Quotas / Monitoring quota lookup")
    parser.add_argument("--no-quota-usage", action="store_true", help="Skip recent Cloud Monitoring quota usage lookup")
    parser.add_argument(
        "--allow-default-quota-state",
        action="store_true",
        help="Allow --no-live-quota to write default-only quota state to a non-sample page. Use only for explicit no-network previews.",
    )
    parser.add_argument("--quota-minutes", type=int, default=60, help="Lookback window for quota usage metrics")
    parser.add_argument(
        "--catalog-mode",
        choices=("auto", "official", "community", "all", "giswqs", "curated"),
        default="auto",
        help="Dataset catalog source: auto merges official STAC and community CSV; also supports official, community, all, giswqs, or curated",
    )
    parser.add_argument("--refresh-catalog", action="store_true", help="Refresh the cached official STAC catalog")
    parser.add_argument("--catalog-cache-hours", type=int, default=CATALOG_CACHE_MAX_AGE_HOURS, help="Official STAC cache age")
    parser.add_argument("--catalog-fetch-seconds", type=int, default=CATALOG_FETCH_SECONDS, help="Official STAC refresh budget")
    parser.add_argument("--no-local-leaflet", action="store_true", help="Use the Leaflet CDN instead of downloading a local preview copy")
    parser.add_argument("--no-local-pmtiles", action="store_true", help="Use the PMTiles CDN instead of downloading a local preview copy")
    parser.add_argument("--no-local-cog-engine", action="store_true", help="Keep the lazy MapLibre COG engine on pinned CDNs instead of downloading local preview copies")
    parser.add_argument("--json", action="store_true", help="Print a credential-safe output summary as JSON")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.smoke:
        return smoke()
    if args.no_live_quota and not (args.sample or args.allow_default_quota_state):
        parser.error(
            "--no-live-quota would write default-only quota state to a user-facing page. "
            "Use live quota lookup, run refresh_map_console_quota.py for quota-only updates, "
            "or add --allow-default-quota-state only for an explicit no-network preview."
        )

    resolved_project = easygee_project.resolve_project(args.project, remember_discovered=True)
    args.project = resolved_project.project

    if args.sample:
        state = sample_state(args.project, args.title)
    elif args.live:
        state = live_state(args)
    else:
        state = empty_state(args)
    state["projectSource"] = resolved_project.source
    state["quota"] = build_quota_state(
        args.project,
        include_usage=not args.no_quota_usage,
        no_live=args.no_live_quota or args.sample,
        minutes=args.quota_minutes,
    )
    leaflet_src = LEAFLET_CDN if args.no_local_leaflet else ensure_leaflet_js(args.output.parent)
    pmtiles_src = PMTILES_CDN if args.no_local_pmtiles else ensure_pmtiles_js(args.output.parent)
    cog_assets = cog_engine_cdn_assets() if args.no_local_cog_engine else ensure_cog_engine_assets(args.output.parent)
    write_console(args.output, state, leaflet_src, pmtiles_src, cog_assets)
    plan = ConsolePlan(
        output=str(args.output),
        project=args.project,
        project_source=resolved_project.source,
        title=args.title,
        center=(args.lat, args.lon),
        layer_count=len(state["layers"]),
        uses_live_ee=bool(args.live),
        quota_source=state.get("quota", {}).get("source") or "not available",
        quota_usage_source=state.get("quota", {}).get("usageSource") or "not available",
    )
    if args.json:
        print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
    else:
        print(f"Wrote EasyGEE Map Console: {args.output}")
        print(f"Project: {args.project}")
        print(f"Project source: {resolved_project.source}")
        print(f"Layers: {len(state['layers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
