#!/usr/bin/env python3
"""Build a visual and numeric comparison of common Sentinel-2 cloud masks.

The case uses one cloudy Sentinel-2 overpass from the public s2cloudless
tutorial area near Portland, Oregon. It creates a local HTML comparison page
with Earth Engine tiles and a small JSON summary. No export task is started.
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
        S2_SR_ID,
        add_s2_cloud_probability,
        mask_s2_cloud_probability_shadow,
        mask_s2_cloud_score_plus,
        mask_s2_qa60,
        mask_s2_scl,
    )
    from easygee_project import resolve_project, workspace_root
except ImportError:  # pragma: no cover - useful when imported as a package
    from skills.easygee.scripts.cloud_mask_workflows import (
        S2_SR_ID,
        add_s2_cloud_probability,
        mask_s2_cloud_probability_shadow,
        mask_s2_cloud_score_plus,
        mask_s2_qa60,
        mask_s2_scl,
    )
    from skills.easygee.scripts.easygee_project import resolve_project, workspace_root


IMAGE_INDEX = "20200601T185919_20200601T190551_T10TER"
CENTER = [-122.269, 45.701]
START = "2020-06-01"
END = "2020-06-02"
AOI_BUFFER_M = 5_000
RGB_VIS = {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000}
MASK_VIS = {"min": 0, "max": 1, "palette": ["d73027", "1a9850"]}
CONSENSUS_PALETTE = ["f1f1f1", "fdae61", "fee08b", "91cf60", "1a9850"]
DEFAULT_OUTPUT = workspace_root() / "cloud-mask-comparison" / "cloud-mask-comparison.html"


def _clear_band(masked_image: ee.Image) -> ee.Image:
    """Return a small 0/1 clear-pixel image from the B4 mask."""

    return masked_image.select("B4").mask().unmask(0).rename("clear")


def _append_band(image: ee.Image, band: ee.Image, name: str) -> ee.Image:
    if image is None:
        return band.rename(name)
    return image.addBands(band.rename(name))


def _tile_url(image: ee.Image, vis_params: dict[str, Any], roi: ee.Geometry) -> str:
    """Return a short-lived Earth Engine tile template for the local preview."""

    map_id = image.clip(roi).getMapId(vis_params)
    return map_id["tile_fetcher"].url_format


def _build_case() -> dict[str, Any]:
    roi = ee.Geometry.Point(CENTER).buffer(AOI_BUFFER_M)
    source = (
        ee.ImageCollection(S2_SR_ID)
        .filterBounds(roi)
        .filterDate(START, END)
        .filter(ee.Filter.eq("system:index", IMAGE_INDEX))
        .first()
    )

    source_collection = ee.ImageCollection.fromImages([source])
    probability_image = add_s2_cloud_probability(source_collection).first()

    masked_images = {
        "qa60": mask_s2_qa60(source),
        "scl": mask_s2_scl(source),
        "cloud_probability": mask_s2_cloud_probability_shadow(
            probability_image,
            threshold=40.0,
            nir_dark_threshold=0.15,
            shadow_distance_km=1.0,
            buffer_m=50.0,
        ),
        "cloud_score_plus": mask_s2_cloud_score_plus(
            source_collection, 0.60
        ).first(),
    }
    clear_bands: dict[str, ee.Image] = {
        name: _clear_band(image) for name, image in masked_images.items()
    }

    # Use valid source pixels as the denominator. This prevents no-data at the
    # edge of an AOI from being incorrectly counted as cloud.
    source_valid = _clear_band(source).rename("source_valid")
    metric_image: ee.Image | None = source_valid
    for name, band in clear_bands.items():
        metric_image = _append_band(metric_image, band, name)
    metric_sums = metric_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=roi,
        scale=10,
        maxPixels=1e8,
    ).getInfo()
    source_pixels = float(metric_sums.get("source_valid", 0.0) or 0.0)
    metrics = {
        "source_valid_pixels": source_pixels,
        **{
            name: (
                float(metric_sums.get(name, 0.0) or 0.0) / source_pixels
                if source_pixels
                else 0.0
            )
            for name in clear_bands
        },
    }

    cloud_score_clear = clear_bands["cloud_score_plus"]
    agreement_image: ee.Image | None = source_valid
    for name, band in clear_bands.items():
        if name == "cloud_score_plus":
            continue
        agreement_image = _append_band(
            agreement_image,
            band.eq(cloud_score_clear).And(source_valid),
            f"{name}_vs_cloud_score_plus",
        )
    agreement_sums = agreement_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=roi,
        scale=10,
        maxPixels=1e8,
    ).getInfo()
    agreements = {
        name: (
            float(agreement_sums.get(name, 0.0) or 0.0) / source_pixels
            if source_pixels
            else 0.0
        )
        for name in agreement_sums
        if name != "source_valid"
    }

    # A single binary difference map is ambiguous when four methods are being
    # compared. Count how many methods retain each source pixel instead:
    # 0 = all four mask it, 4 = all four retain it, and 1-3 show disagreement.
    clear_count = (
        clear_bands["qa60"]
        .add(clear_bands["scl"])
        .add(clear_bands["cloud_probability"])
        .add(clear_bands["cloud_score_plus"])
        .updateMask(source_valid)
        .rename("clear_count")
    )

    scene_metadata = source.toDictionary(
        ["system:index", "CLOUDY_PIXEL_PERCENTAGE", "MGRS_TILE"]
    ).getInfo()
    return {
        "roi": roi,
        "source": source,
        "source_valid": source_valid,
        "masked_images": masked_images,
        "clear_bands": clear_bands,
        "clear_count": clear_count,
        "metrics": metrics,
        "agreements": agreements,
        "scene_metadata": scene_metadata,
    }


def _summary_rows(case: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "qa60": ("QA60", "位元云/卷云标记；没有独立云影判定"),
        "scl": ("SCL", "Sen2Cor scene classes; removes cloud shadow/cirrus"),
        "cloud_probability": ("s2cloudless", "概率 < 40，并加入云影投影"),
        "cloud_score_plus": ("Cloud Score+", "cs_cdf >= 0.60；连续清晰度评分"),
    }
    rows = []
    for key, (label, note) in labels.items():
        clear = float(case["metrics"].get(key, 0.0))
        rows.append(
            {
                "key": key,
                "label": label,
                "note": note,
                "clear_fraction": clear,
                "masked_fraction": 1.0 - clear,
                "agreement_with_cloud_score_plus": (
                    1.0
                    if key == "cloud_score_plus"
                    else float(case["agreements"].get(f"{key}_vs_cloud_score_plus", 0.0))
                ),
                "difference_with_cloud_score_plus": (
                    0.0
                    if key == "cloud_score_plus"
                    else 1.0
                    - float(case["agreements"].get(f"{key}_vs_cloud_score_plus", 0.0))
                ),
            }
        )
    return rows


def _table_html(rows: list[dict[str, Any]]) -> str:
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{html.escape(row['label'])}</td>"
            f"<td>{row['clear_fraction'] * 100:.1f}%</td>"
            f"<td>{row['masked_fraction'] * 100:.1f}%</td>"
            f"<td>{row['agreement_with_cloud_score_plus'] * 100:.1f}%</td>"
            f"<td>{html.escape(row['note'])}</td>"
            "</tr>"
        )
    return "".join(body)


def _metric_cards_html(rows: list[dict[str, Any]]) -> str:
    cards = []
    for row in rows:
        clear_pct = row["clear_fraction"] * 100
        cards.append(
            '<article class="metric-card">'
            f'<div class="metric-head"><strong>{html.escape(row["label"])}</strong>'
            f'<span>{clear_pct:.1f}% 保留</span></div>'
            f'<div class="bar"><span style="width:{clear_pct:.1f}%"></span></div>'
            f'<p>掩膜 {row["masked_fraction"] * 100:.1f}% · 与 Cloud Score+ 一致 {row["agreement_with_cloud_score_plus"] * 100:.1f}%</p>'
            "</article>"
        )
    return "".join(cards)


def _make_html(case: dict[str, Any], output: Path) -> dict[str, Any]:
    roi = case["roi"]
    tiles = {
        "raw": _tile_url(case["source"], RGB_VIS, roi),
        "qa60": _tile_url(case["masked_images"]["qa60"], RGB_VIS, roi),
        "scl": _tile_url(case["masked_images"]["scl"], RGB_VIS, roi),
        "cloud_probability": _tile_url(
            case["masked_images"]["cloud_probability"], RGB_VIS, roi
        ),
        "cloud_score_plus": _tile_url(
            case["masked_images"]["cloud_score_plus"], RGB_VIS, roi
        ),
        "consensus": _tile_url(
            case["clear_count"],
            {
                "min": 0,
                "max": 4,
                "palette": CONSENSUS_PALETTE,
            },
            roi,
        ),
    }
    mask_tiles = {
        name: _tile_url(case["clear_bands"][name], MASK_VIS, roi)
        for name in case["clear_bands"]
    }
    rows = _summary_rows(case)
    metadata = case["scene_metadata"]
    panels = [
        ("panel-raw", "原始真彩色", "同一景，未去云", "raw"),
        ("panel-qa60", "QA60", "位元云/卷云掩膜", "qa60"),
        ("panel-scl", "SCL", "Sen2Cor 场景分类", "scl"),
        ("panel-prob", "s2cloudless", "概率 < 40 + 云影投影", "cloud_probability"),
        ("panel-cs", "Cloud Score+", "cs_cdf ≥ 0.60", "cloud_score_plus"),
        ("panel-consensus", "四法共识图", "0–4 个方法保留该像元", "consensus"),
    ]
    panel_html_parts = []
    for panel_id, title, subtitle, tile_key in panels:
        legend = ""
        if tile_key == "consensus":
            legend = (
                '<div class="consensus-legend" aria-label="四法共识图图例">'
                '<div class="legend-title">保留方法数</div>'
                '<div class="legend-row">'
                '<span class="legend-item"><i class="legend-swatch c0"></i>0</span>'
                '<span class="legend-item"><i class="legend-swatch c1"></i>1</span>'
                '<span class="legend-item"><i class="legend-swatch c2"></i>2</span>'
                '<span class="legend-item"><i class="legend-swatch c3"></i>3</span>'
                '<span class="legend-item"><i class="legend-swatch c4"></i>4</span>'
                '</div>'
                '<div class="legend-note">0 全遮罩 · 1–3 有分歧 · 4 全保留</div>'
                '</div>'
            )
        panel_html_parts.append(
            f'<section class="panel"><h2>{title}</h2><p>{subtitle}</p>'
            f'<div id="{panel_id}" class="map">{legend}</div></section>'
        )
    panel_html = "".join(panel_html_parts)
    panel_data = [
        {"id": panel_id, "tile": tiles[tile_key], "title": title}
        for panel_id, title, _, tile_key in panels
    ]
    summary_json = {
        "case": "Sentinel-2 single-scene cloud-mask diagnostic",
        "dataset": S2_SR_ID,
        "image_index": IMAGE_INDEX,
        "date": START,
        "center": CENTER,
        "aoi_buffer_km": AOI_BUFFER_M / 1000,
        "scene_metadata": metadata,
        "design": {
            "controlled_variables": [
                "same Sentinel-2 SR scene",
                "same 5 km AOI",
                "same RGB visualization",
                "same 10 m diagnostic scale",
            ],
            "reference": "Cloud Score+ is a comparison reference, not ground truth.",
            "not_evaluated": "precision, recall, F1, and cloud-underlying-image reconstruction",
        },
        "rows": rows,
    }
    payload = json.dumps(summary_json, ensure_ascii=False, indent=2)
    panels_json = json.dumps(panel_data, ensure_ascii=False)
    mask_tiles_json = json.dumps(mask_tiles, ensure_ascii=False)
    center_json = json.dumps([CENTER[1], CENTER[0]])
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EasyGEE Sentinel-2 去云算法诊断实验</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    :root {{ color-scheme: light; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #f3f6f8; color: #1f2933; }}
    header {{ padding: 22px 28px 12px; background: #0f766e; color: white; }}
    header h1 {{ margin: 0 0 6px; font-size: 24px; }}
    header p {{ margin: 0; opacity: .9; }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 18px 22px 32px; }}
    .callout {{ background: white; border-left: 5px solid #0f766e; padding: 12px 16px; margin-bottom: 16px; box-shadow: 0 1px 3px #0001; }}
    .design {{ display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 10px; margin-bottom: 16px; }}
    .design-card {{ background: #e8f5f2; padding: 12px; border-radius: 8px; }}
    .design-card strong {{ display: block; margin-bottom: 4px; color: #0f766e; }}
    .design-card span {{ font-size: 13px; color: #344e41; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(260px, 1fr)); gap: 14px; }}
    .panel {{ background: white; padding: 10px 10px 12px; box-shadow: 0 1px 3px #0001; }}
    .panel h2 {{ margin: 0; font-size: 17px; }}
    .panel p {{ margin: 3px 0 8px; color: #52606d; font-size: 13px; }}
    .map {{ height: 300px; border: 1px solid #d9e2ec; }}
    .consensus-legend {{ position: absolute; z-index: 500; top: 8px; right: 8px; padding: 6px 8px; border: 1px solid #cbd5e1; border-radius: 5px; background: rgba(255,255,255,.94); color: #334e68; font-size: 11px; line-height: 1.25; box-shadow: 0 1px 3px #0002; pointer-events: none; }}
    .consensus-legend .legend-title {{ margin-bottom: 4px; font-weight: 700; }}
    .consensus-legend .legend-row {{ display: flex; gap: 5px; align-items: center; }}
    .consensus-legend .legend-item {{ display: inline-flex; align-items: center; gap: 2px; }}
    .consensus-legend .legend-swatch {{ display: inline-block; width: 12px; height: 10px; border: 1px solid #94a3b8; border-radius: 2px; }}
    .consensus-legend .c0 {{ background: #f1f1f1; }} .consensus-legend .c1 {{ background: #fdae61; }} .consensus-legend .c2 {{ background: #fee08b; }} .consensus-legend .c3 {{ background: #91cf60; }} .consensus-legend .c4 {{ background: #1a9850; }}
    .consensus-legend .legend-note {{ margin-top: 4px; color: #52606d; white-space: nowrap; }}
    .mask-explorer {{ background: white; padding: 12px; margin-top: 14px; box-shadow: 0 1px 3px #0001; }}
    .mask-explorer h2 {{ margin: 0 0 5px; font-size: 18px; }}
    .mask-explorer p {{ margin: 4px 0 10px; color: #52606d; font-size: 13px; }}
    .controls {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
    select {{ border: 1px solid #9fb3c8; border-radius: 5px; padding: 6px 8px; background: white; }}
    .legend {{ font-size: 12px; color: #52606d; }}
    .swatch {{ display: inline-block; width: 12px; height: 12px; margin-right: 3px; vertical-align: -1px; border-radius: 2px; }}
    .swatch.red {{ background: #d73027; }} .swatch.green {{ background: #1a9850; }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 10px; margin-top: 18px; }}
    .metric-card {{ background: white; padding: 12px; box-shadow: 0 1px 3px #0001; }}
    .metric-head {{ display: flex; justify-content: space-between; gap: 8px; font-size: 13px; }}
    .metric-head span {{ color: #0f766e; font-weight: 700; }}
    .bar {{ height: 9px; margin: 9px 0 6px; background: #e5e7eb; border-radius: 5px; overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: #0f766e; border-radius: 5px; }}
    .metric-card p {{ margin: 0; color: #52606d; font-size: 12px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 18px; box-shadow: 0 1px 3px #0001; }}
    th, td {{ border-bottom: 1px solid #e4e7eb; padding: 9px 10px; text-align: left; font-size: 13px; }}
    th {{ background: #e8f5f2; }}
    .foot {{ color: #52606d; font-size: 12px; margin-top: 14px; }}
    @media (max-width: 980px) {{ .grid {{ grid-template-columns: repeat(2, minmax(260px, 1fr)); }} .design, .metric-grid {{ grid-template-columns: repeat(2, minmax(180px, 1fr)); }} }}
    @media (max-width: 650px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 12px; }} }}
  </style>
</head>
<body>
  <header><h1>EasyGEE：Sentinel-2 去云算法诊断实验</h1>
    <p>同一景、同一 AOI、同一显示参数：先看空间差异，再看保留率与一致性。</p>
  </header>
  <main>
    <div class="callout">
      <strong>实验设置：</strong> {html.escape(str(metadata.get('system:index', IMAGE_INDEX)))}，日期 {START}，场景云量属性 {float(metadata.get('CLOUDY_PIXEL_PERCENTAGE', 0)):.1f}%。
      这里比较同一观测上的像元掩膜，不是场景级云量；s2cloudless 使用概率 40，Cloud Score+ 使用 <code>cs_cdf &gt;= 0.60</code>，也没有进行云下影像重建。
    </div>
    <div class="design">
      <div class="design-card"><strong>控制变量</strong><span>同一 S2 SR 景、同一 5 km AOI、同一 B4/B3/B2 真彩色参数。</span></div>
      <div class="design-card"><strong>比较对象</strong><span>QA60、SCL、s2cloudless + 云影投影、Cloud Score+。</span></div>
      <div class="design-card"><strong>统计指标</strong><span>有效像元保留率、掩膜率、与 Cloud Score+ 的参考一致率。</span></div>
      <div class="design-card"><strong>科学边界</strong><span>一致率不是准确率；无人工真值时不报告 precision/recall。</span></div>
    </div>
    <div class="grid">{panel_html}</div>
    <section class="mask-explorer">
      <h2>单独查看掩膜结果</h2>
      <p>绿色表示该方法保留的有效像元，红色表示被掩膜的像元；这一步把“看起来变干净”拆解成可检查的空间决策。</p>
      <div class="controls"><label for="mask-select">选择方法</label><select id="mask-select"><option value="qa60">QA60</option><option value="scl">SCL</option><option value="cloud_probability">s2cloudless</option><option value="cloud_score_plus">Cloud Score+</option></select><span class="legend"><i class="swatch green"></i>保留 <i class="swatch red"></i>掩膜</span></div>
      <div id="mask-map" class="map"></div>
    </section>
    <div class="metric-grid">{_metric_cards_html(rows)}</div>
    <table>
      <thead><tr><th>方法</th><th>保留清晰像元</th><th>掩膜像元</th><th>与 Cloud Score+ 一致率</th><th>方法说明</th></tr></thead>
      <tbody>{_table_html(rows)}</tbody>
    </table>
    <p class="foot">数据：{S2_SR_ID}。四法共识图表示每个像元有 0–4 个方法保留它：0 表示全部遮罩，4 表示全部保留，1–3 表示方法分歧。表格中的一致率仍把 Cloud Score+ 作为显式参考，不表示真值；若要报告精度，需要独立人工/高分辨率真值。地图瓦片是临时 Earth Engine 预览，不是导出结果。</p>
  </main>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const center = {center_json};
    const panels = {panels_json};
    const maskTiles = {mask_tiles_json};
    const addBase = (map) => {{
      L.control.attribution({{ prefix: false }}).addTo(map);
      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 19, attribution: '&copy; OpenStreetMap contributors', opacity: 0.55
      }}).addTo(map);
      L.control.scale({{ imperial: false }}).addTo(map);
    }};
    panels.forEach((panel) => {{
      const map = L.map(panel.id, {{ zoomControl: false, scrollWheelZoom: false, attributionControl: false }}).setView(center, 12);
      addBase(map);
      L.tileLayer(panel.tile, {{ opacity: 0.96, attribution: 'Google Earth Engine' }}).addTo(map);
    }});
    const maskMap = L.map('mask-map', {{ zoomControl: true, attributionControl: false }}).setView(center, 12);
    addBase(maskMap);
    let maskLayer = L.tileLayer(maskTiles.qa60, {{ opacity: 0.9, attribution: 'Google Earth Engine' }}).addTo(maskMap);
    document.getElementById('mask-select').addEventListener('change', (event) => {{
      maskMap.removeLayer(maskLayer);
      maskLayer = L.tileLayer(maskTiles[event.target.value], {{ opacity: 0.9, attribution: 'Google Earth Engine' }}).addTo(maskMap);
    }});
  </script>
</body>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_text, encoding="utf-8")
    output.with_suffix(".json").write_text(payload, encoding="utf-8")
    return summary_json


def main() -> int:
    global IMAGE_INDEX, CENTER, START, END, AOI_BUFFER_M
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="Earth Engine / Google Cloud project id")
    parser.add_argument("--image-index", default=IMAGE_INDEX)
    parser.add_argument("--start", default=START, help="Start date, inclusive")
    parser.add_argument("--end", default=END, help="End date, exclusive")
    parser.add_argument(
        "--center",
        default=f"{CENTER[0]},{CENTER[1]}",
        help="AOI center as longitude,latitude",
    )
    parser.add_argument(
        "--aoi-buffer-km",
        type=float,
        default=AOI_BUFFER_M / 1000,
        help="AOI point-buffer radius in kilometers",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        center = [float(value.strip()) for value in args.center.split(",")]
    except ValueError as exc:
        parser.error("--center must be longitude,latitude")
    if len(center) != 2 or not (-180 <= center[0] <= 180 and -90 <= center[1] <= 90):
        parser.error("--center must be a valid longitude,latitude pair")
    if args.aoi_buffer_km <= 0:
        parser.error("--aoi-buffer-km must be positive")

    IMAGE_INDEX = args.image_index
    CENTER = center
    START = args.start
    END = args.end
    AOI_BUFFER_M = args.aoi_buffer_km * 1000

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
        "image_index": summary["image_index"],
        "rows": summary["rows"],
        "note": "No export task was created.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
