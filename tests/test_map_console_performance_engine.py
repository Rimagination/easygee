from __future__ import annotations

import functools
import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "easygee" / "scripts"


def load_script(name: str):
    path = SCRIPT_DIR / f"{name}.py"
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_map_console_template_accepts_platform_newlines(tmp_path: Path, monkeypatch, newline: str) -> None:
    console = load_script("create_map_console")
    monkeypatch.setattr(console, "MAP_CONSOLE_ASSETS_DIR", tmp_path)
    template = "<script>\n__EASYGEE_CONSOLE_JS__\n</script>\n"
    script = "const message = '你好';\n"
    (tmp_path / "template.html").write_bytes(template.replace("\n", newline).encode("utf-8"))
    (tmp_path / "console.js").write_bytes(script.replace("\n", newline).encode("utf-8"))
    assert console.map_console_page_template() == f"<script>\n{script}</script>\n"


def test_map_console_embeds_raster_pmtiles_adapter() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "PMTiles Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert '<option value="pmtiles">PMTiles (raster)</option>' in html
    assert "pmtiles.leafletRasterLayer" in html
    assert "getPmtilesArchive" in html
    assert "archive.getZxy" in html
    assert "tryCreateBasemapLayer" in html
    assert "await inspectPmtilesArchive(meta" in html
    assert console.PMTILES_CDN in html


def test_sample_console_has_no_mislabeled_srtm_placeholder() -> None:
    console = load_script("create_map_console")
    state = console.sample_state("demo-project", "Empty Sample Console")

    assert state["layers"] == []
    assert "sample-dem" not in json.dumps(state)
    assert "tile.openstreetmap.org" not in json.dumps(state)


def test_console_syncs_layer_controls_and_recent_profile_state() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "Layer State Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert "stateLayer.shown = nextShown" in html
    assert "stateLayer.opacity = opacity" in html
    assert "Array.isArray(entry.recentLayers)" in html
    assert "tileUrl: layer.tileUrl" in html
    assert "function restoreProfileMapView()" in html
    assert "function rebuildProfileLayer(saved)" in html
    assert "await restoreRecentProfileLayers()" in html
    assert "type: 'ee-restore-pending'" in html
    assert "restoredProfileActiveLayerId" in html


def test_console_exposes_primary_basemap_and_overlay_layer_workflow() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "Basemap Layer Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert "const PRIMARY_BASEMAP_LAYER_ID = '__easygee_primary_basemap__';" in html
    assert 'data-basemap-overlay="${escapeHtml(meta.id)}"' in html
    assert "function addBasemapOverlay(sourceId)" in html
    assert "function primaryBasemapLayerModel()" in html
    assert "primaryBasemapOpacity = opacity" in html
    assert "primaryBasemapShown = nextShown" in html
    assert "addBasemapOverlay: id => addBasemapOverlay" in html


def test_console_exposes_tianditu_wmts_presets_without_syncing_the_key() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "Tianditu Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert "TiandituVector" in html
    assert "TiandituImagery" in html
    assert "TiandituTerrain" in html
    assert "WMTS vec_w + cva_w" in html
    assert "WMTS img_w + cia_w" in html
    assert "WMTS ter_w + cta_w" in html
    assert 'id="tianditu-auth-toggle"' in html
    assert 'id="tianditu-auth-body" hidden' in html
    assert 'id="tianditu-auth-summary" hidden' in html
    assert 'id="tianditu-auth-editor"' in html
    assert 'id="tianditu-token-change"' in html
    assert 'id="tianditu-token-remember"' in html
    assert 'id="tianditu-token-persistence"' in html
    assert "grid-auto-rows: max-content" in html
    assert "function setTiandituAuthOpen(open)" in html
    assert "function editTiandituToken()" in html
    assert "setTiandituAuthOpen(false)" in html
    assert "https://t{s}.tianditu.gov.cn/${layer}_w/wmts" in html
    assert "TILEMATRIXSET=w" in html
    assert "window.sessionStorage.setItem(TIANDITU_TOKEN_STORAGE_KEY, token)" in html
    assert "/api/session/credentials/tianditu" in html
    assert "function urlContainsCredentials(value)" in html
    project_state = html.split("function buildProjectState()", 1)[1].split("function syncSessionState", 1)[0]
    assert "tiandituToken" not in project_state


def test_console_exposes_zoom_to_layer_workflow() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "Zoom To Layer Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert 'class="lucide lucide-scan"' in html
    assert 'data-action="zoom"' in html
    assert "function layerExtentById(id)" in html
    assert "function zoomToLayer(id, options = {})" in html
    assert "zoomToLayer: (id, options) => zoomToLayer" in html


def test_profile_persists_primary_basemap_controls_and_overlay_instances(tmp_path: Path) -> None:
    preview = load_script("serve_map_preview")
    preview.configure_profile_path(tmp_path / "profile.json")

    profile = preview.merge_profile_with_state(
        {
            "title": "Basemap Layers",
            "project": "demo-project",
            "center": [30.25, 120.16],
            "zoom": 10,
            "basemap": "Imagery",
            "basemapShown": False,
            "basemapOpacity": 0.42,
            "activeLayerId": "basemap-overlay-CartoDark-test",
            "layers": [
                {
                    "id": "basemap-overlay-CartoDark-test",
                    "name": "Dark",
                    "dataset": "CARTO",
                    "type": "basemap-overlay",
                    "role": "overlay",
                    "sourceId": "CartoDark",
                    "shown": True,
                    "opacity": 0.7,
                }
            ],
            "sessionReason": "basemap-overlay-added",
        }
    )

    entry = profile["projects"]["demo-project"]
    assert entry["view"]["basemap"] == "Imagery"
    assert entry["view"]["basemapShown"] is False
    assert entry["view"]["basemapOpacity"] == 0.42
    assert entry["activeLayerId"] == "basemap-overlay-CartoDark-test"
    assert entry["recentLayers"] == [
        {
            "id": "basemap-overlay-CartoDark-test",
            "name": "Dark",
            "dataset": "CARTO",
            "type": "basemap-overlay",
            "role": "overlay",
            "sourceId": "CartoDark",
            "shown": True,
            "opacity": 0.7,
        }
    ]


def test_pmtiles_asset_validation_rejects_truncated_or_unrelated_scripts() -> None:
    console = load_script("create_map_console")
    valid = b"PMTiles leafletRasterLayer" + (b"x" * 12_000)

    assert console.valid_pmtiles_js(valid)
    assert not console.valid_pmtiles_js(b"PMTiles" + (b"x" * 12_000))
    assert not console.valid_pmtiles_js(b"leafletRasterLayer" + (b"x" * 100))


def test_map_console_embeds_lazy_maplibre_cog_adapter() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "COG Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )

    assert '<option value="cog">COG (MapLibre WebGL)</option>' in html
    assert "const COG_ENGINE_ASSETS =" in html
    assert "ensureCogEngine" in html
    assert "MaplibreCOGProtocol.getCogMetadata" in html
    assert "L.maplibreGL" in html
    assert "cog://" in html
    assert "function fitCogBasemapBounds" in html
    assert "!aoiBounds.intersects(activeCogBounds)" in html
    assert console.MAPLIBRE_JS_CDN in html
    assert console.COG_PROTOCOL_CDN in html
    assert '<script src="https://unpkg.com/maplibre-gl@' not in html


def test_cog_engine_asset_validation_rejects_unrelated_files() -> None:
    console = load_script("create_map_console")

    assert console.valid_maplibre_js(b"maplibregl addProtocol" + (b"x" * 900_000))
    assert console.valid_maplibre_css(b".maplibregl-map .maplibregl-canvas" + (b"x" * 60_000))
    assert console.valid_maplibre_leaflet_js(b"maplibreGL getMaplibreMap" + (b"x" * 8_000))
    assert console.valid_cog_protocol_js(b"MaplibreCOGProtocol getCogMetadata" + (b"x" * 500_000))
    assert not console.valid_maplibre_js(b"maplibregl" + (b"x" * 900_000))
    assert not console.valid_cog_protocol_js(b"getCogMetadata" + (b"x" * 500_000))


def test_profile_accepts_pmtiles_basemap() -> None:
    preview = load_script("serve_map_preview")
    items = preview.sanitize_custom_basemaps(
        [
            {
                "id": "custom-pmtiles",
                "name": "Local raster archive",
                "type": "pmtiles",
                "url": "http://127.0.0.1:8765/data/imagery.pmtiles",
                "provider": "Local",
                "maxZoom": 14,
            }
        ]
    )

    assert len(items) == 1
    assert items[0]["type"] == "pmtiles"
    assert items[0]["url"].endswith(".pmtiles")


def test_profile_accepts_cog_basemap_metadata() -> None:
    preview = load_script("serve_map_preview")
    items = preview.sanitize_custom_basemaps(
        [
            {
                "id": "custom-cog",
                "name": "Browser COG",
                "type": "cog",
                "url": "https://example.com/imagery.tif",
                "provider": "Example",
                "bounds": [120.0, 30.0, 121.0, 31.0],
                "crs": "EPSG:3857",
                "bandCount": 3,
            }
        ]
    )

    assert len(items) == 1
    assert items[0]["type"] == "cog"
    assert items[0]["bounds"] == [120.0, 30.0, 121.0, 31.0]
    assert items[0]["crs"] == "EPSG:3857"
    assert items[0]["bandCount"] == 3


def test_profile_rejects_custom_basemap_urls_with_embedded_credentials() -> None:
    preview = load_script("serve_map_preview")
    unsafe_urls = [
        "https://example.com/{z}/{x}/{y}.png?token=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png?API-KEY=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png?%74oken=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png?%2574oken=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png?service=tiles;subscription-key=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png?X-Amz-Signature=fake-test-value",
        "https://example.com/{z}/{x}/{y}.png#token=fake-test-value",
        "https://user:fake-test-value@example.com/{z}/{x}/{y}.png",
    ]

    for index, url in enumerate(unsafe_urls):
        items = preview.sanitize_custom_basemaps(
            [{"id": f"custom-unsafe-{index}", "name": "Unsafe", "type": "xyz", "url": url}]
        )
        assert items == []

    safe = preview.sanitize_custom_basemaps(
        [
            {
                "id": "custom-wms-safe",
                "name": "Public WMS",
                "type": "wms",
                "url": "https://example.com/wms?service=WMS&request=GetMap",
                "layers": "public-layer",
            }
        ]
    )
    assert len(safe) == 1
    assert safe[0]["url"].endswith("request=GetMap")

    source_url_filtered = preview.sanitize_custom_basemaps(
        [
            {
                "id": "custom-safe-source",
                "name": "Safe tiles",
                "type": "xyz",
                "url": "https://example.com/{z}/{x}/{y}.png",
                "sourceUrl": "https://example.com/details?X-Goog-Credential=fake-test-value",
            }
        ]
    )
    assert len(source_url_filtered) == 1
    assert "sourceUrl" not in source_url_filtered[0]


def test_profile_normalization_scrubs_legacy_secret_fields_and_urls() -> None:
    preview = load_script("serve_map_preview")
    fake_token = "fake-test-key-123"
    normalized = preview.normalize_profile(
        {
            "tiandituToken": fake_token,
            "favoriteDatasets": [],
            "projects": {
                "demo": {
                    "token": fake_token,
                    "sourceUrl": f"https://example.com/source?key={fake_token}",
                    "title": "Safe title",
                }
            },
        }
    )

    serialized = json.dumps(normalized)
    assert fake_token not in serialized
    assert normalized["projects"]["demo"] == {"title": "Safe title"}


def test_tianditu_credential_endpoint_uses_encrypted_local_store(tmp_path: Path) -> None:
    preview = load_script("serve_map_preview")
    preview.configure_profile_path(tmp_path / "profile.json")
    fake_token = "fake-test-key-123"

    handler = functools.partial(preview.EasyGeeHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}/api/session/credentials/tianditu"
    try:
        if preview.os.name != "nt":
            with urllib.request.urlopen(endpoint, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            assert payload == {"ok": True, "supported": False, "remembered": False, "token": ""}
            return

        body = json.dumps({"remember": True, "token": fake_token}).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            saved = json.loads(response.read().decode("utf-8"))
        assert saved["remembered"] is True

        secret_text = preview.secret_store_path().read_text(encoding="utf-8")
        assert fake_token not in secret_text
        assert fake_token not in (tmp_path / "profile.json").read_text(encoding="utf-8") if (tmp_path / "profile.json").exists() else True

        with urllib.request.urlopen(endpoint, timeout=5) as response:
            loaded = json.loads(response.read().decode("utf-8"))
        assert loaded["token"] == fake_token
        assert loaded["remembered"] is True

        forbidden = urllib.request.Request(endpoint, headers={"Origin": "https://example.invalid"})
        try:
            urllib.request.urlopen(forbidden, timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 403
        else:
            raise AssertionError("cross-origin credential access should be rejected")

        wrong_type = urllib.request.Request(endpoint, data=b"{}", headers={"Content-Type": "text/plain"}, method="POST")
        try:
            urllib.request.urlopen(wrong_type, timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 415
        else:
            raise AssertionError("credential writes require application/json")

        delete = urllib.request.Request(
            endpoint,
            data=json.dumps({"remember": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(delete, timeout=5) as response:
            removed = json.loads(response.read().decode("utf-8"))
        assert removed["remembered"] is False
        assert preview.load_tianditu_secret() == ""
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_preview_server_supports_single_http_byte_range(tmp_path: Path) -> None:
    preview = load_script("serve_map_preview")
    payload = bytes(range(256)) * 4
    target = tmp_path / "sample.pmtiles"
    target.write_bytes(payload)

    handler = functools.partial(preview.EasyGeeHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/{target.name}",
            headers={"Range": "bytes=100-199"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            assert response.status == 206
            assert response.headers["Accept-Ranges"] == "bytes"
            assert response.headers["Content-Range"] == f"bytes 100-199/{len(payload)}"
            assert response.read() == payload[100:200]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_preview_server_rejects_static_paths_resolved_outside_root(tmp_path: Path) -> None:
    preview = load_script("serve_map_preview")
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.pmtiles"
    outside.write_bytes(b"secret archive bytes")

    class OutsideHandler(preview.EasyGeeHandler):
        def translate_path(self, path: str) -> str:
            return str(outside)

    handler = functools.partial(OutsideHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for headers in ({}, {"Range": "bytes=0-5"}):
            request = urllib.request.Request(
                f"http://127.0.0.1:{server.server_port}/outside.pmtiles",
                headers=headers,
            )
            try:
                urllib.request.urlopen(request, timeout=5)
            except urllib.error.HTTPError as exc:
                assert exc.code == 404
            else:
                raise AssertionError("outside-root static file should be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_preview_server_ignores_stale_map_console_protocol(tmp_path: Path) -> None:
    preview = load_script("serve_map_preview")
    preview.configure_profile_path(tmp_path / "profile.json")
    preview.SESSION_STATE = {}
    preview.SESSION_SYNCED_AT = None

    handler = functools.partial(preview.EasyGeeHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_port}/api/session/state"

        def post_state(state: dict[str, object]) -> dict[str, object]:
            body = json.dumps({"state": state}).encode("utf-8")
            request = urllib.request.Request(
                endpoint,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))

        stale = post_state(
            {
                "agentProtocolVersion": 4,
                "title": "Stale tab",
                "project": "demo",
                "customBasemaps": [],
            }
        )
        assert stale["ok"] is True
        assert stale["ignored"] is True
        assert stale["reason"] == "stale-agent-protocol"
        assert preview.SESSION_STATE == {}

        current = post_state(
            {
                "agentProtocolVersion": 5,
                "title": "Current tab",
                "project": "demo",
                "center": [47.26, 11.39],
                "zoom": 16,
                "basemap": "custom-cog",
                "customBasemaps": [
                    {
                        "id": "custom-cog",
                        "name": "Current COG",
                        "type": "cog",
                        "url": "https://example.com/current.tif",
                        "bounds": [11.38, 47.25, 11.41, 47.27],
                        "crs": "EPSG:3857",
                    }
                ],
            }
        )
        assert current["ok"] is True
        assert "ignored" not in current
        assert preview.SESSION_STATE["agentProtocolVersion"] == 5
        assert preview.load_profile()["customBasemaps"][0]["type"] == "cog"

        filtered = post_state(
            {
                "agentProtocolVersion": 5,
                "title": "Unsafe state",
                "project": "demo",
                "center": [47.26, 11.39],
                "zoom": 16,
                "tiandituToken": "fake-test-key-123",
                "customBasemaps": [
                    {
                        "id": "custom-unsafe",
                        "name": "Unsafe",
                        "type": "xyz",
                        "url": "https://example.com/{z}/{x}/{y}.png?token=fake-test-key-123",
                    }
                ],
            }
        )
        assert filtered["ok"] is True
        state_text = json.dumps(preview.SESSION_STATE)
        profile_text = json.dumps(preview.load_profile())
        assert "fake-test-key-123" not in state_text
        assert "fake-test-key-123" not in profile_text
        assert preview.SESSION_STATE["customBasemaps"] == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_performance_engine_contract_and_console_use_protocol_v5() -> None:
    console = load_script("create_map_console")
    html = console.render_html(
        console.sample_state("demo-project", "Protocol Console"),
        console.LEAFLET_CDN,
        console.PMTILES_CDN,
    )
    contract = json.loads(
        (ROOT / "skills" / "easygee" / "references" / "map-console-agent-contract.json").read_text(encoding="utf-8")
    )
    agent_source = (SCRIPT_DIR / "map_console_agent.py").read_text(encoding="utf-8")

    assert contract["version"] == 5
    assert "const AGENT_PROTOCOL_VERSION = 5;" in html
    assert 'contract.get("version") == 5' in agent_source
    assert "cog" in contract["basemaps"]["customTypes"]
    assert "performanceEngine" in contract["stateFields"]
    assert contract["stateSyncPolicy"]["minimumProtocolVersion"] == 5
    assert "function beginBasemapPerformance" in html
    assert "function collectBasemapNetworkPerformance" in html
    assert 'id="basemap-source-performance"' in html
    assert 'id="basemap-source-delivery"' in html
    assert contract["basemaps"]["performanceEngine"]["diagnostics"]["fields"] == [
        "status",
        "cache",
        "firstRenderMs",
        "readyMs",
        "renderedBlocks",
        "sourceRequests",
        "transferredBytes",
    ]


def test_compact_agent_state_keeps_cog_binary_details_out() -> None:
    agent = load_script("map_console_agent")
    compact = agent.compact_state_response(
        {
            "state": {
                "basemapShown": False,
                "basemapOpacity": 0.42,
                "layers": [
                    {
                        "id": "basemap-overlay-CartoDark-test",
                        "name": "Dark",
                        "type": "basemap-overlay",
                        "role": "overlay",
                        "sourceId": "CartoDark",
                        "shown": True,
                        "opacity": 0.6,
                    }
                ],
                "customBasemaps": [
                    {
                        "id": "custom-cog",
                        "name": "Browser COG",
                        "type": "cog",
                        "provider": "Example",
                        "url": "https://example.com/large-secret-path.tif",
                        "bounds": [120, 30, 121, 31],
                    }
                ],
                "performanceEngine": {
                    "id": "maplibre-cog",
                    "status": "ready",
                    "access": "HTTP Range",
                    "renderer": "https://example.com/large-secret-path.tif",
                    "crs": "file:///large-secret-path.tif",
                    "resourceUrl": "https://example.com/large-secret-path.tif",
                    "diagnostics": {
                        "status": "ready",
                        "cache": "warm",
                        "firstRenderMs": 121.7,
                        "readyMs": 408.2,
                        "renderedBlocks": 8,
                        "sourceRequests": 5,
                        "transferredBytes": 20480,
                        "startedAt": 123456.7,
                        "resourceNames": ["https://example.com/large-secret-path.tif"],
                    },
                },
            }
        }
    )

    assert compact["state"]["customBasemaps"] == [
        {"id": "custom-cog", "name": "Browser COG", "type": "cog", "provider": "Example"}
    ]
    assert compact["state"]["basemapShown"] is False
    assert compact["state"]["basemapOpacity"] == 0.42
    assert compact["state"]["layers"] == [
        {
            "id": "basemap-overlay-CartoDark-test",
            "name": "Dark",
            "type": "basemap-overlay",
            "role": "overlay",
            "sourceId": "CartoDark",
            "shown": True,
            "opacity": 0.6,
        }
    ]
    assert "large-secret-path" not in json.dumps(compact)
    assert compact["state"]["performanceEngine"]["id"] == "maplibre-cog"
    assert compact["state"]["performanceEngine"]["diagnostics"] == {
        "status": "ready",
        "cache": "warm",
        "firstRenderMs": 122,
        "readyMs": 408,
        "renderedBlocks": 8,
        "sourceRequests": 5,
        "transferredBytes": 20480,
    }
