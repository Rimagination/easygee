#!/usr/bin/env python3
"""Build a same-day Landsat 8 versus Sentinel-2 teaching comparison.

The case uses the same Portland AOI and the same acquisition date for both
sensors. It shows raw RGB, cloud-masked RGB, and masked NDVI side by side,
plus native-resolution and valid-pixel diagnostics. No export task is started.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

import ee

try:
    from cloud_mask_workflows import (
        LANDSAT_8_ID,
        S2_SR_ID,
        mask_landsat_c2_qa_pixel,
        mask_s2_cloud_score_plus,
        scale_landsat_c2_l2,
    )
    from easygee_project import resolve_project, workspace_root
except ImportError:  # pragma: no cover - useful when imported as a package
    from skills.easygee.scripts.cloud_mask_workflows import (
        LANDSAT_8_ID,
        S2_SR_ID,
        mask_landsat_c2_qa_pixel,
        mask_s2_cloud_score_plus,
        scale_landsat_c2_l2,
    )
    from skills.easygee.scripts.easygee_project import resolve_project, workspace_root


LANDSAT_INDEX = "LC08_046028_20200604"
S2_INDEX = "20200604T190919_20200604T191606_T10TER"
CENTER = [-122.269, 45.701]
DATE = "2020-06-04"
ROI_BUFFER_M = 5_000
S2_RGB_VIS = {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000}
LANDSAT_RGB_VIS = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0, "max": 0.3}
NDVI_VIS = {
    "min": -0.2,
    "max": 0.8,
    "palette": ["440154", "3b528b", "21918c", "5ec962", "fde725"],
}
DEFAULT_OUTPUT = workspace_root() / "cloud-mask-comparison" / "landsat-sentinel-comparison.html"


def _tile_url(image: ee.Image, vis_params: dict[str, Any], roi: ee.Geometry) -> str:
    map_id = image.clip(roi).getMapId(vis_params)
    return map_id["tile_fetcher"].url_format


def _valid_fraction(image: ee.Image, band: str, roi: ee.Geometry, scale: int) -> float:
    value = (
        image.select(band)
        .mask()
        .unmask(0)
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=scale,
            maxPixels=1e8,
        )
        .get(band)
        .getInfo()
    )
    return float(value or 0.0)


def _mean_value(image: ee.Image, band: str, roi: ee.Geometry, scale: int) -> float | None:
    value = (
        image.select(band)
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=scale,
            maxPixels=1e8,
        )
        .get(band)
        .getInfo()
    )
    return float(value) if value is not None else None


def _build_case() -> dict[str, Any]:
    roi = ee.Geometry.Point(CENTER).buffer(ROI_BUFFER_M)
    s2 = (
        ee.ImageCollection(S2_SR_ID)
        .filterBounds(roi)
        .filterDate(DATE, "2020-06-05")
        .filter(ee.Filter.eq("system:index", S2_INDEX))
        .first()
    )
    landsat = (
        ee.ImageCollection(LANDSAT_8_ID)
        .filterBounds(roi)
        .filterDate(DATE, "2020-06-05")
        .filter(ee.Filter.eq("system:index", LANDSAT_INDEX))
        .first()
    )

    s2_masked = mask_s2_cloud_score_plus(
        ee.ImageCollection.fromImages([s2]), threshold=0.60
    ).first()
    landsat_masked_raw = mask_landsat_c2_qa_pixel(landsat)
    landsat_raw = scale_landsat_c2_l2(landsat)
    landsat_masked = scale_landsat_c2_l2(landsat_masked_raw)

    s2_ndvi = s2_masked.normalizedDifference(["B8", "B4"]).rename("NDVI")
    landsat_ndvi = landsat_masked.normalizedDifference(["SR_B5", "SR_B4"]).rename(
        "NDVI"
    )
    metrics = {
        "sentinel2_valid_fraction": _valid_fraction(s2_masked, "B4", roi, 10),
        "landsat_valid_fraction": _valid_fraction(
            landsat_masked, "SR_B4", roi, 30
        ),
        "sentinel2_mean_ndvi": _mean_value(s2_ndvi, "NDVI", roi, 10),
        "landsat_mean_ndvi": _mean_value(landsat_ndvi, "NDVI", roi, 30),
    }
    metadata = {
        "sentinel2": s2.toDictionary(
            ["system:index", "CLOUDY_PIXEL_PERCENTAGE", "MGRS_TILE"]
        ).getInfo(),
        "landsat8": landsat.toDictionary(
            ["system:index", "CLOUD_COVER", "DATE_ACQUIRED", "WRS_PATH", "WRS_ROW"]
        ).getInfo(),
    }
    return {
        "roi": roi,
        "s2_raw": s2,
        "s2_masked": s2_masked,
        "s2_ndvi": s2_ndvi,
        "landsat_raw": landsat_raw,
        "landsat_masked": landsat_masked,
        "landsat_ndvi": landsat_ndvi,
        "metrics": metrics,
        "metadata": metadata,
    }


def _make_html(case: dict[str, Any], output: Path) -> dict[str, Any]:
    roi = case["roi"]
    tiles = {
        "s2_raw": _tile_url(case["s2_raw"], S2_RGB_VIS, roi),
        "s2_masked": _tile_url(case["s2_masked"], S2_RGB_VIS, roi),
        "s2_ndvi": _tile_url(case["s2_ndvi"], NDVI_VIS, roi),
        "landsat_raw": _tile_url(case["landsat_raw"], LANDSAT_RGB_VIS, roi),
        "landsat_masked": _tile_url(
            case["landsat_masked"], LANDSAT_RGB_VIS, roi
        ),
        "landsat_ndvi": _tile_url(case["landsat_ndvi"], NDVI_VIS, roi),
    }
    s2_meta = case["metadata"]["sentinel2"]
    landsat_meta = case["metadata"]["landsat8"]
    metrics = case["metrics"]
    rows = [
        {
            "sensor": "Sentinel-2",
            "dataset": S2_SR_ID,
            "date": DATE,
            "resolution": "10 m（RGB/NDVI）",
            "mask": "Cloud Score+ cs_cdf ≥ 0.60",
            "scene_cloud": float(s2_meta.get("CLOUDY_PIXEL_PERCENTAGE", 0)),
            "valid_fraction": metrics["sentinel2_valid_fraction"],
            "mean_ndvi": metrics["sentinel2_mean_ndvi"],
        },
        {
            "sensor": "Landsat 8",
            "dataset": LANDSAT_8_ID,
            "date": DATE,
            "resolution": "30 m（RGB/NDVI）",
            "mask": "QA_PIXEL + C2 缩放因子",
            "scene_cloud": float(landsat_meta.get("CLOUD_COVER", 0)),
            "valid_fraction": metrics["landsat_valid_fraction"],
            "mean_ndvi": metrics["landsat_mean_ndvi"],
        },
    ]
    panels = [
        ("s2-raw", "Sentinel-2 原始 RGB", "10 m；同日原始影像", "s2_raw"),
        ("s2-masked", "Sentinel-2 去云 RGB", "Cloud Score+", "s2_masked"),
        ("s2-ndvi", "Sentinel-2 去云 NDVI", "B8/B4", "s2_ndvi"),
        ("landsat-raw", "Landsat 8 原始 RGB", "30 m；同日原始影像", "landsat_raw"),
        ("landsat-masked", "Landsat 8 去云 RGB", "QA_PIXEL", "landsat_masked"),
        ("landsat-ndvi", "Landsat 8 去云 NDVI", "SR_B5/SR_B4", "landsat_ndvi"),
    ]
    panel_html = "".join(
        f'<section class="panel"><h2>{title}</h2><p>{subtitle}</p><div id="{panel_id}" class="map"></div></section>'
        for panel_id, title, subtitle, _ in panels
    )
    panel_data = [
        {"id": panel_id, "tile": tiles[tile_key]}
        for panel_id, _, _, tile_key in panels
    ]
    summary = {
        "case": "Same-day Landsat 8 versus Sentinel-2",
        "date": DATE,
        "center": CENTER,
        "datasets": {"sentinel2": S2_SR_ID, "landsat8": LANDSAT_8_ID},
        "metadata": case["metadata"],
        "rows": rows,
        "limitations": [
            "The sensors have different native resolutions and spectral response functions.",
            "Scene cloud metadata is not a pixel-level cloud accuracy metric.",
            "Mean NDVI is a same-AOI diagnostic, not a pixel-to-pixel equivalence test.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    table_rows = []
    for row in rows:
        ndvi = "—" if row["mean_ndvi"] is None else f"{row['mean_ndvi']:.3f}"
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(row['sensor'])}</td>"
            f"<td>{html.escape(row['resolution'])}</td>"
            f"<td>{html.escape(row['mask'])}</td>"
            f"<td>{row['scene_cloud']:.1f}%</td>"
            f"<td>{row['valid_fraction'] * 100:.1f}%</td>"
            f"<td>{ndvi}</td>"
            "</tr>"
        )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EasyGEE：Landsat 与 Sentinel-2 对比</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    :root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #f3f6f8; color: #1f2933; }}
    header {{ padding: 22px 28px 12px; background: #185abc; color: white; }}
    header h1 {{ margin: 0 0 6px; font-size: 24px; }}
    header p {{ margin: 0; opacity: .9; }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 18px 22px 32px; }}
    .callout {{ background: white; border-left: 5px solid #185abc; padding: 12px 16px; margin-bottom: 16px; box-shadow: 0 1px 3px #0001; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(260px, 1fr)); gap: 14px; }}
    .panel {{ background: white; padding: 10px 10px 12px; box-shadow: 0 1px 3px #0001; }}
    .panel h2 {{ margin: 0; font-size: 17px; }}
    .panel p {{ margin: 3px 0 8px; color: #52606d; font-size: 13px; }}
    .map {{ height: 300px; border: 1px solid #d9e2ec; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 18px; box-shadow: 0 1px 3px #0001; }}
    th, td {{ border-bottom: 1px solid #e4e7eb; padding: 9px 10px; text-align: left; font-size: 13px; }}
    th {{ background: #e8f0fe; }}
    .foot {{ color: #52606d; font-size: 12px; margin-top: 14px; }}
    @media (max-width: 980px) {{ .grid {{ grid-template-columns: repeat(2, minmax(260px, 1fr)); }} }}
    @media (max-width: 650px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 12px; }} }}
  </style>
</head>
<body>
  <header><h1>EasyGEE：同日 Landsat 8 与 Sentinel-2 对比</h1>
    <p>同一 AOI、同一日期；先比较原始观测，再比较去云结果和 NDVI。</p>
  </header>
  <main>
    <div class="callout">
      <strong>教学重点：</strong> Sentinel-2 的 10 m 空间细节更丰富，Landsat 8 为 30 m；两者采用不同波段和 QA 掩膜。
      这里的 NDVI 是同一 AOI 的统计诊断，不应直接理解为逐像元等价或传感器精度排名。
    </div>
    <div class="grid">{panel_html}</div>
    <table>
      <thead><tr><th>传感器</th><th>原生分辨率</th><th>去云方法</th><th>场景云量元数据</th><th>去云后有效像元</th><th>AOI 平均 NDVI</th></tr></thead>
      <tbody>{''.join(table_rows)}</tbody>
    </table>
    <p class="foot">Sentinel-2：{S2_INDEX}；Landsat 8：{LANDSAT_INDEX}；日期：{DATE}。页面只做本地预览，不创建导出任务。</p>
  </main>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const center = {json.dumps([CENTER[1], CENTER[0]])};
    const panels = {json.dumps(panel_data, ensure_ascii=False)};
    panels.forEach((panel) => {{
      const map = L.map(panel.id, {{ zoomControl: false, scrollWheelZoom: false, attributionControl: false }}).setView(center, 12);
      L.control.attribution({{ prefix: false }}).addTo(map);
      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 19, attribution: '&copy; OpenStreetMap contributors', opacity: 0.55
      }}).addTo(map);
      L.tileLayer(panel.tile, {{ opacity: 0.96, attribution: 'Google Earth Engine' }}).addTo(map);
      L.control.scale({{ imperial: false }}).addTo(map);
    }});
  </script>
</body>
</html>
"""
    output.write_text(html_text, encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="Earth Engine / Google Cloud project id")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    resolved = resolve_project(args.project)
    if not resolved.project or resolved.project == "YOUR_EE_PROJECT":
        parser.error("No Earth Engine project was found; pass --project PROJECT_ID")
    ee.Initialize(project=resolved.project)
    case = _build_case()
    summary = _make_html(case, args.output)
    print(json.dumps({
        "output": str(args.output),
        "summary": str(args.output.with_suffix('.json')),
        "project_source": resolved.source,
        "date": summary["date"],
        "rows": summary["rows"],
        "note": "No export task was created.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
