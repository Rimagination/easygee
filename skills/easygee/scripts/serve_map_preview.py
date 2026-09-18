#!/usr/bin/env python
"""Serve an EasyGEE map preview page with Python's standard library.

Use this for lightweight, persistent browser previews of geemap-exported HTML
or other local map artifacts. The script does not authenticate to Earth Engine,
open OAuth, or read credential files.
"""

from __future__ import annotations

import argparse
import base64
import csv
import functools
import html
import ipaddress
import json
import os
import re
import socket
import tempfile
import threading
import time
import urllib.parse
import uuid
import zipfile
from dataclasses import asdict, dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.etree import ElementTree

from easygee_project import workspace_root, write_text_atomic_with_fallback


@dataclass(frozen=True)
class PreviewPlan:
    root: str
    url: str
    target: str
    target_type: str
    title: str
    notes: tuple[str, ...]


def default_preview_root() -> Path:
    return workspace_root() / "preview"


def write_placeholder(root: Path, title: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    index = root / "index.html"
    safe_title = html.escape(title)
    index.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: Inter, Segoe UI, system-ui, sans-serif;
      background: #f7f8fa;
      color: #111827;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
    }}
    main {{
      max-width: 760px;
      padding: 32px;
      line-height: 1.55;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    code {{
      background: rgba(17, 24, 39, 0.08);
      border-radius: 4px;
      padding: 2px 5px;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{ background: #101318; color: #e5e7eb; }}
      code {{ background: rgba(229, 231, 235, 0.14); }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>{safe_title}</h1>
    <p>This local preview server is running. Export a geemap map to HTML, then serve that file with <code>serve_map_preview.py map.html</code>.</p>
    <p>Keep this terminal session open while using the preview page.</p>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return index


def choose_port(host: str, requested: int) -> int:
    if requested:
        return requested
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def build_plan(target: Path | None, host: str, port: int, title: str, root_arg: Path | None) -> PreviewPlan:
    notes: list[str] = []
    root = root_arg or default_preview_root()
    target_type = "placeholder"
    target_label = "generated placeholder"

    if target:
        target = target.expanduser().resolve()
        if not target.exists():
            raise FileNotFoundError(f"Preview target does not exist: {target}")
        if target.is_dir():
            root = target
            path = "index.html"
            target_type = "directory"
            target_label = str(target)
            if not (target / "index.html").exists():
                notes.append("Directory has no index.html; the browser will show a directory listing.")
                path = ""
        else:
            root = target.parent
            path = urllib.parse.quote(target.name)
            target_type = "file"
            target_label = str(target)
            if target.suffix.lower() not in {".html", ".htm"}:
                notes.append("Target is not an HTML file; the browser may download or render it as plain text.")
    else:
        placeholder = write_placeholder(root, title)
        path = urllib.parse.quote(placeholder.name)
        target_label = str(placeholder)
        notes.append("Generated a placeholder preview page.")

    root.mkdir(parents=True, exist_ok=True)
    actual_port = choose_port(host, port)
    url_path = f"/{path}" if path else "/"
    url = f"http://{host}:{actual_port}{url_path}"
    return PreviewPlan(
        root=str(root),
        url=url,
        target=target_label,
        target_type=target_type,
        title=title,
        notes=tuple(notes),
    )


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} {format % args}")


CATALOG_CACHE: dict[str, object] | None = None
SESSION_LOCK = threading.Lock()
SESSION_STATE: dict[str, object] = {}
SESSION_SYNCED_AT: float | None = None
SESSION_ACTIONS: list[dict[str, object]] = []
SESSION_ACTION_COUNTER = 0
SESSION_ACTION_LIMIT = 100
PROFILE_VERSION = 3
PROFILE_LOCK = threading.Lock()
PROFILE_PATH: Path | None = None
SECRET_STORE_VERSION = 1
SECRET_LOCK = threading.Lock()
TIANDITU_SECRET_NAME = "tianditu"
SECRET_ENTROPY = b"EasyGEE Map Console credential v1"
EXACT_FAVORITE_REASONS = {"favorites", "favorite-updated"}
CLEAR_AOI_REASONS = {"aoi-cleared"}
CLEAR_MEASUREMENT_REASONS = {"measurements-cleared"}
CUSTOM_BASEMAP_TYPES = {"xyz", "tms", "arcgis", "wms", "wmts", "pmtiles", "cog"}
SENSITIVE_URL_QUERY_NAMES = {
    "access_key",
    "access_token",
    "accesskey",
    "api_key",
    "apikey",
    "app_key",
    "appkey",
    "auth",
    "authorization",
    "client_secret",
    "credential",
    "key",
    "passwd",
    "password",
    "private_key",
    "secret",
    "sig",
    "signature",
    "subscription_key",
    "tk",
    "token",
}


def contract_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "map-console-agent-contract.json"


def load_agent_contract() -> dict[str, object]:
    try:
        payload = json.loads(contract_path().read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {"name": "EasyGEE Map Console Agent Contract", "version": 1}


def agent_protocol_version() -> int:
    value = load_agent_contract().get("version")
    if isinstance(value, bool):
        return 1
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


AGENT_PROTOCOL_VERSION = agent_protocol_version()


def session_state_protocol_version(state: dict[str, object]) -> int:
    value = state.get("agentProtocolVersion")
    if isinstance(value, bool):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def session_state_protocol_is_current(state: dict[str, object]) -> bool:
    return session_state_protocol_version(state) >= AGENT_PROTOCOL_VERSION


def default_profile_path() -> Path:
    explicit = os.environ.get("EASYGEE_MAP_CONSOLE_PROFILE")
    if explicit:
        return Path(explicit).expanduser()
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        root = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state")
    return root / "EasyGEE" / "map-console-profile.json"


def configure_profile_path(path: Path | None) -> None:
    global PROFILE_PATH
    PROFILE_PATH = path.expanduser().resolve() if path else default_profile_path()


def profile_path() -> Path:
    global PROFILE_PATH
    if PROFILE_PATH is None:
        PROFILE_PATH = default_profile_path()
    return PROFILE_PATH


def secret_store_path() -> Path:
    explicit = os.environ.get("EASYGEE_MAP_CONSOLE_SECRETS")
    if explicit:
        return Path(explicit).expanduser().resolve()
    path = profile_path()
    return path.with_name("map-console-secrets.json")


def _dpapi_crypt(data: bytes, *, protect: bool) -> bytes:
    if os.name != "nt":
        raise RuntimeError("Encrypted local credentials require Windows DPAPI")
    import ctypes
    from ctypes import wintypes

    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    def make_blob(value: bytes) -> tuple[DataBlob, object]:
        buffer = ctypes.create_string_buffer(value)
        return DataBlob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))), buffer

    input_blob, input_buffer = make_blob(data)
    entropy_blob, entropy_buffer = make_blob(SECRET_ENTROPY)
    output_blob = DataBlob()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DataBlob),
        wintypes.LPCWSTR,
        ctypes.POINTER(DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DataBlob),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(DataBlob),
        ctypes.c_void_p,
        ctypes.POINTER(DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DataBlob),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    flags = 0x1  # CRYPTPROTECT_UI_FORBIDDEN
    if protect:
        succeeded = crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            "EasyGEE Map Console",
            ctypes.byref(entropy_blob),
            None,
            None,
            flags,
            ctypes.byref(output_blob),
        )
    else:
        succeeded = crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            None,
            ctypes.byref(entropy_blob),
            None,
            None,
            flags,
            ctypes.byref(output_blob),
        )
    _ = input_buffer, entropy_buffer
    if not succeeded:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output_blob.pbData, ctypes.c_void_p))


def encrypt_local_secret(value: str) -> str:
    return base64.b64encode(_dpapi_crypt(value.encode("utf-8"), protect=True)).decode("ascii")


def decrypt_local_secret(value: str) -> str:
    encrypted = base64.b64decode(value.encode("ascii"), validate=True)
    return _dpapi_crypt(encrypted, protect=False).decode("utf-8")


def sanitize_tianditu_token(value: object) -> str:
    token = str(value or "").strip()
    if not token or len(token) > 256 or re.search(r"[\s&?#]", token):
        return ""
    return token


def read_secret_store_unlocked() -> dict[str, object]:
    path = secret_store_path()
    if not path.exists():
        return {"version": SECRET_STORE_VERSION, "secrets": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": SECRET_STORE_VERSION, "secrets": {}}
    secrets = payload.get("secrets") if isinstance(payload, dict) else None
    return {
        "version": SECRET_STORE_VERSION,
        "secrets": secrets if isinstance(secrets, dict) else {},
    }


def write_secret_store_unlocked(store: dict[str, object]) -> None:
    path = secret_store_path()
    temporary = path.with_name(f"{path.name}.tmp")
    write_text_atomic_with_fallback(
        path,
        json.dumps(store, ensure_ascii=False, indent=2),
        temporary=temporary,
        replace=os.replace,
    )


def load_tianditu_secret() -> str:
    if os.name != "nt":
        return ""
    with SECRET_LOCK:
        store = read_secret_store_unlocked()
        secrets = store.get("secrets") if isinstance(store.get("secrets"), dict) else {}
        encrypted = secrets.get(TIANDITU_SECRET_NAME)
        if not isinstance(encrypted, str) or not encrypted:
            return ""
        try:
            return sanitize_tianditu_token(decrypt_local_secret(encrypted))
        except Exception:
            return ""


def save_tianditu_secret(value: object) -> bool:
    if os.name != "nt":
        raise RuntimeError("Encrypted local credentials require Windows DPAPI")
    token = sanitize_tianditu_token(value)
    if not token:
        raise ValueError("Invalid Tianditu key")
    with SECRET_LOCK:
        store = read_secret_store_unlocked()
        secrets = store.get("secrets") if isinstance(store.get("secrets"), dict) else {}
        secrets[TIANDITU_SECRET_NAME] = encrypt_local_secret(token)
        store["version"] = SECRET_STORE_VERSION
        store["secrets"] = secrets
        write_secret_store_unlocked(store)
    return True


def delete_tianditu_secret() -> None:
    with SECRET_LOCK:
        store = read_secret_store_unlocked()
        secrets = store.get("secrets") if isinstance(store.get("secrets"), dict) else {}
        if TIANDITU_SECRET_NAME not in secrets:
            return
        secrets.pop(TIANDITU_SECRET_NAME, None)
        store["secrets"] = secrets
        write_secret_store_unlocked(store)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def json_clone(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=False))


UPLOAD_MAX_BYTES = 50 * 1024 * 1024
UPLOAD_ALLOWED_EXTENSIONS = {
    ".shp",
    ".shx",
    ".dbf",
    ".prj",
    ".cpg",
    ".zip",
    ".kml",
    ".kmz",
    ".gpx",
    ".geojson",
    ".json",
    ".csv",
    ".gpkg",
}
UPLOAD_SHAPEFILE_EXTENSIONS = {".shp", ".shx", ".dbf", ".prj", ".cpg"}
UPLOAD_SHAPEFILE_SIDECAR_EXTENSIONS = UPLOAD_SHAPEFILE_EXTENSIONS - {".shp"}
UPLOAD_PREVIEW_MAX_FEATURES = 10000


def upload_format_for_extension(extension: str) -> str:
    ext = extension.lower()
    if ext in {".geojson", ".json"}:
        return "GeoJSON"
    if ext == ".zip":
        return "ZIP/Shapefile bundle"
    if ext in {".shp", ".shx", ".dbf", ".prj"}:
        return "Shapefile component"
    if ext in {".kml", ".kmz"}:
        return ext[1:].upper()
    if ext == ".gpx":
        return "GPX"
    if ext == ".csv":
        return "CSV"
    if ext == ".gpkg":
        return "GeoPackage"
    return "Unknown"


def sanitize_upload_name(filename: str) -> str:
    base = Path(str(filename).replace("\\", "/")).name.strip()
    if not base:
        base = "upload.dat"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._")
    return safe or "upload.dat"


def upload_url_for(path: Path) -> str:
    return f"/uploads/{urllib.parse.quote(path.name)}"


def geojson_feature_collection(features: list[dict[str, object]]) -> dict[str, object]:
    return {"type": "FeatureCollection", "features": features[:UPLOAD_PREVIEW_MAX_FEATURES]}


def write_geojson_preview(target: Path, features: list[dict[str, object]]) -> dict[str, object]:
    collection = geojson_feature_collection(features)
    target.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")
    return {
        "previewPath": str(target),
        "previewUrl": upload_url_for(target),
        "previewFormat": "GeoJSON",
        "previewFeatureCount": len(collection["features"]),
        "previewLimited": len(features) > UPLOAD_PREVIEW_MAX_FEATURES,
        "renderable": True,
        "status": "layer-ready",
    }


def csv_lon_lat_columns(fieldnames: list[str]) -> tuple[str, str] | tuple[None, None]:
    lower = {name.strip().lower(): name for name in fieldnames}
    lon_candidates = ("lon", "lng", "longitude", "x", "long")
    lat_candidates = ("lat", "latitude", "y")
    lon = next((lower[name] for name in lon_candidates if name in lower), None)
    lat = next((lower[name] for name in lat_candidates if name in lower), None)
    return lon, lat


def convert_csv_to_geojson(source: Path, target: Path) -> dict[str, object]:
    features: list[dict[str, object]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        lon_field, lat_field = csv_lon_lat_columns(reader.fieldnames or [])
        if not lon_field or not lat_field:
            raise ValueError("CSV preview needs lon/lng/longitude/x and lat/latitude/y columns")
        for row in reader:
            try:
                lon = float(str(row.get(lon_field, "")).strip())
                lat = float(str(row.get(lat_field, "")).strip())
            except ValueError:
                continue
            props = {key: value for key, value in row.items() if key not in {lon_field, lat_field}}
            features.append(
                {
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                }
            )
    if not features:
        raise ValueError("CSV preview found no valid lon/lat rows")
    return write_geojson_preview(target, features)


def parse_kml_coordinates(text: str) -> list[list[float]]:
    coords: list[list[float]] = []
    for chunk in re.split(r"\s+", (text or "").strip()):
        if not chunk:
            continue
        parts = chunk.split(",")
        if len(parts) < 2:
            continue
        try:
            coords.append([float(parts[0]), float(parts[1])])
        except ValueError:
            continue
    return coords


def find_xml_element(node: ElementTree.Element, *queries: tuple[str, dict[str, str] | None]) -> ElementTree.Element | None:
    for query, namespace in queries:
        found = node.find(query, namespace or {})
        if found is not None:
            return found
    return None


def kml_features_from_bytes(data: bytes) -> list[dict[str, object]]:
    root = ElementTree.fromstring(data)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = root.findall(".//kml:Placemark", ns) or root.findall(".//Placemark")
    features: list[dict[str, object]] = []
    for index, placemark in enumerate(placemarks, start=1):
        name_node = find_xml_element(placemark, ("kml:name", ns), ("name", None))
        props = {"name": name_node.text.strip()} if name_node is not None and name_node.text else {"id": index}
        point = find_xml_element(placemark, (".//kml:Point/kml:coordinates", ns), (".//Point/coordinates", None))
        line = find_xml_element(placemark, (".//kml:LineString/kml:coordinates", ns), (".//LineString/coordinates", None))
        polygon = find_xml_element(
            placemark,
            (".//kml:Polygon//kml:outerBoundaryIs//kml:coordinates", ns),
            (".//Polygon//outerBoundaryIs//coordinates", None),
        )
        geometry: dict[str, object] | None = None
        if point is not None and point.text:
            coords = parse_kml_coordinates(point.text)
            if coords:
                geometry = {"type": "Point", "coordinates": coords[0]}
        elif line is not None and line.text:
            coords = parse_kml_coordinates(line.text)
            if len(coords) >= 2:
                geometry = {"type": "LineString", "coordinates": coords}
        elif polygon is not None and polygon.text:
            coords = parse_kml_coordinates(polygon.text)
            if len(coords) >= 4:
                geometry = {"type": "Polygon", "coordinates": [coords]}
        if geometry:
            features.append({"type": "Feature", "properties": props, "geometry": geometry})
    return features


def convert_kml_to_geojson(source: Path, target: Path) -> dict[str, object]:
    features = kml_features_from_bytes(source.read_bytes())
    if not features:
        raise ValueError("KML preview found no Point, LineString, or Polygon placemarks")
    return write_geojson_preview(target, features)


def convert_kmz_to_geojson(source: Path, target: Path) -> dict[str, object]:
    with zipfile.ZipFile(source) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".kml")]
        if not names:
            raise ValueError("KMZ preview found no KML file")
        features = kml_features_from_bytes(archive.read(names[0]))
    if not features:
        raise ValueError("KMZ preview found no Point, LineString, or Polygon placemarks")
    return write_geojson_preview(target, features)


def gpx_features_from_bytes(data: bytes) -> list[dict[str, object]]:
    root = ElementTree.fromstring(data)
    ns = {"gpx": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
    prefix = "gpx:" if ns else ""
    features: list[dict[str, object]] = []
    for index, point in enumerate(root.findall(f".//{prefix}wpt", ns), start=1):
        try:
            lon = float(point.attrib["lon"])
            lat = float(point.attrib["lat"])
        except (KeyError, ValueError):
            continue
        name_node = point.find(f"{prefix}name", ns)
        props = {"name": name_node.text.strip()} if name_node is not None and name_node.text else {"id": index}
        features.append({"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": [lon, lat]}})
    for index, track in enumerate(root.findall(f".//{prefix}trk", ns), start=1):
        coords: list[list[float]] = []
        for point in track.findall(f".//{prefix}trkpt", ns):
            try:
                coords.append([float(point.attrib["lon"]), float(point.attrib["lat"])])
            except (KeyError, ValueError):
                continue
        if len(coords) >= 2:
            name_node = track.find(f"{prefix}name", ns)
            props = {"name": name_node.text.strip()} if name_node is not None and name_node.text else {"track": index}
            features.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": coords}})
    for index, route in enumerate(root.findall(f".//{prefix}rte", ns), start=1):
        coords = []
        for point in route.findall(f".//{prefix}rtept", ns):
            try:
                coords.append([float(point.attrib["lon"]), float(point.attrib["lat"])])
            except (KeyError, ValueError):
                continue
        if len(coords) >= 2:
            name_node = route.find(f"{prefix}name", ns)
            props = {"name": name_node.text.strip()} if name_node is not None and name_node.text else {"route": index}
            features.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": coords}})
    return features


def convert_gpx_to_geojson(source: Path, target: Path) -> dict[str, object]:
    features = gpx_features_from_bytes(source.read_bytes())
    if not features:
        raise ValueError("GPX preview found no waypoints, tracks, or routes")
    return write_geojson_preview(target, features)


def convert_with_geopandas(source: Path, target: Path, projection: str, extension: str) -> dict[str, object]:
    try:
        import geopandas as gpd
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ValueError(f"GeoPandas is unavailable: {exc}") from exc
    path_value = f"zip://{source.as_posix()}" if extension == ".zip" else str(source)
    gdf = gpd.read_file(path_value)
    if gdf.empty:
        raise ValueError("No features found")
    if gdf.crs is None and projection:
        gdf = gdf.set_crs(projection, allow_override=True)
    if gdf.crs is not None:
        gdf = gdf.to_crs("EPSG:4326")
    if len(gdf) > UPLOAD_PREVIEW_MAX_FEATURES:
        gdf = gdf.head(UPLOAD_PREVIEW_MAX_FEATURES)
        limited = True
    else:
        limited = False
    gdf.to_file(target, driver="GeoJSON")
    return {
        "previewPath": str(target),
        "previewUrl": upload_url_for(target),
        "previewFormat": "GeoJSON",
        "previewFeatureCount": int(len(gdf)),
        "previewLimited": limited,
        "renderable": True,
        "status": "layer-ready",
    }


def enrich_upload_preview(record: dict[str, object], upload_dir: Path) -> dict[str, object]:
    extension = str(record.get("extension") or "").lower()
    source = Path(str(record.get("savedPath") or ""))
    projection = str(record.get("projection") or "EPSG:4326")
    preview_target = upload_dir / f"{record['id']}-preview.geojson"
    try:
        if extension in {".geojson", ".json"}:
            record.update(
                {
                    "previewPath": str(source),
                    "previewUrl": record.get("url"),
                    "previewFormat": "GeoJSON",
                    "renderable": True,
                    "status": "layer-ready",
                }
            )
        elif extension == ".csv":
            record.update(convert_csv_to_geojson(source, preview_target))
        elif extension == ".kml":
            record.update(convert_kml_to_geojson(source, preview_target))
        elif extension == ".kmz":
            record.update(convert_kmz_to_geojson(source, preview_target))
        elif extension == ".gpx":
            record.update(convert_gpx_to_geojson(source, preview_target))
        elif extension in {".shp", ".zip", ".gpkg"}:
            record.update(convert_with_geopandas(source, preview_target, projection, extension))
        else:
            record["renderable"] = False
    except Exception as exc:
        record["renderable"] = False
        record["previewError"] = str(exc)
        record["status"] = "saved-needs-conversion"
    return record


def mark_missing_shapefile_components(record: dict[str, object], missing: list[str] | None = None) -> dict[str, object]:
    required = ", ".join(missing or [".shp"])
    record["renderable"] = False
    record["status"] = "missing-shapefile-components"
    record["previewError"] = (
        f"Shapefile upload is incomplete. Select the .shp geometry file together with .shx and .dbf "
        f"(and .prj/.cpg when available), or upload a ZIP containing all components. Missing: {required}."
    )
    return record


def parse_multipart_upload(body: bytes, content_type: str) -> tuple[list[dict[str, object]], dict[str, str]]:
    match = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not match:
        raise ValueError("Missing multipart boundary")
    boundary = (match.group(1) or match.group(2) or "").encode("utf-8")
    if not boundary:
        raise ValueError("Missing multipart boundary")
    marker = b"--" + boundary
    files: list[dict[str, object]] = []
    fields: dict[str, str] = {}
    for raw_part in body.split(marker):
        if raw_part.startswith(b"\r\n"):
            raw_part = raw_part[2:]
        if not raw_part or raw_part in {b"--", b"--\r\n"}:
            continue
        if raw_part.endswith(b"--"):
            raw_part = raw_part[:-2].rstrip(b"\r\n")
        elif raw_part.endswith(b"\r\n"):
            raw_part = raw_part[:-2]
        if b"\r\n\r\n" not in raw_part:
            continue
        header_blob, data = raw_part.split(b"\r\n\r\n", 1)
        headers = header_blob.decode("utf-8", errors="replace").split("\r\n")
        disposition = next((line for line in headers if line.lower().startswith("content-disposition:")), "")
        name_match = re.search(r'name="([^"]+)"', disposition)
        filename_match = re.search(r'filename="([^"]*)"', disposition)
        field_name = name_match.group(1) if name_match else ""
        if filename_match is not None:
            filename = filename_match.group(1)
            if filename:
                files.append({"field": field_name, "filename": filename, "data": data})
        elif field_name:
            fields[field_name] = data.decode("utf-8", errors="replace")
    return files, fields


def save_uploaded_files(root: Path, body: bytes, content_type: str) -> dict[str, object]:
    files, fields = parse_multipart_upload(body, content_type)
    projection = str(fields.get("projection") or "EPSG:4326").strip() or "EPSG:4326"
    upload_dir = root / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    shapefile_stems = {
        Path(str(item.get("filename") or "")).stem.lower()
        for item in files
        if Path(str(item.get("filename") or "")).suffix.lower() == ".shp"
    }
    shapefile_ids = {stem: f"upload-{int(time.time())}-{uuid.uuid4().hex[:10]}" for stem in shapefile_stems}
    shapefile_components: dict[str, dict[str, str]] = {stem: {} for stem in shapefile_stems}
    shapefile_originals: dict[str, str] = {}
    saved: list[dict[str, object]] = []
    for item in files:
        original_name = str(item.get("filename") or "")
        data = item.get("data")
        if not isinstance(data, bytes):
            continue
        if len(data) > UPLOAD_MAX_BYTES:
            raise ValueError(f"{original_name} exceeds 50 MB")
        extension = Path(original_name).suffix.lower()
        if extension not in UPLOAD_ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported upload format: {extension or original_name}")
        source_path = Path(original_name)
        source_stem = source_path.stem.lower()
        grouped_shapefile = extension in UPLOAD_SHAPEFILE_EXTENSIONS and source_stem in shapefile_ids
        upload_id = shapefile_ids[source_stem] if grouped_shapefile else f"upload-{int(time.time())}-{uuid.uuid4().hex[:10]}"
        if grouped_shapefile:
            safe_stem = sanitize_upload_name(source_path.stem)
            stored_name = f"{upload_id}-{safe_stem}{extension}"
        else:
            safe_name = sanitize_upload_name(original_name)
            stored_name = f"{upload_id}-{safe_name}"
        target = upload_dir / stored_name
        target.write_bytes(data)
        if grouped_shapefile:
            shapefile_components[source_stem][extension] = str(target)
            if extension == ".shp":
                shapefile_originals[source_stem] = original_name
            continue
        record = {
            "id": upload_id,
            "name": original_name,
            "storedName": stored_name,
            "extension": extension,
            "format": upload_format_for_extension(extension),
            "size": len(data),
            "projection": projection,
            "savedPath": str(target),
            "url": upload_url_for(target),
            "agentReadable": True,
            "status": "saved",
            "createdAt": now_iso(),
        }
        if extension in UPLOAD_SHAPEFILE_SIDECAR_EXTENSIONS:
            saved.append(mark_missing_shapefile_components(record, [".shp"]))
            continue
        saved.append(enrich_upload_preview(record, upload_dir))
    for stem, components in shapefile_components.items():
        shp_path = components.get(".shp")
        if not shp_path:
            continue
        target = Path(shp_path)
        upload_id = shapefile_ids[stem]
        record = {
            "id": upload_id,
            "name": shapefile_originals.get(stem) or target.name,
            "storedName": target.name,
            "extension": ".shp",
            "format": upload_format_for_extension(".shp"),
            "size": sum(Path(path).stat().st_size for path in components.values() if Path(path).exists()),
            "projection": projection,
            "savedPath": str(target),
            "url": upload_url_for(target),
            "componentPaths": components,
            "agentReadable": True,
            "status": "saved",
            "createdAt": now_iso(),
        }
        missing = [ext for ext in (".shx", ".dbf") if ext not in components]
        if missing:
            saved.append(mark_missing_shapefile_components(record, missing))
        else:
            saved.append(enrich_upload_preview(record, upload_dir))
    return {
        "ok": True,
        "uploads": saved,
        "projection": projection,
        "acceptedExtensions": sorted(UPLOAD_ALLOWED_EXTENSIONS),
        "maxBytes": UPLOAD_MAX_BYTES,
    }


def empty_profile() -> dict[str, object]:
    return {
        "version": PROFILE_VERSION,
        "favoriteDatasets": [],
        "visualPreferences": {},
        "customBasemaps": [],
        "defaultBasemap": "OSM",
        "projects": {},
        "updatedAt": None,
    }


def normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    seen: set[str] = set()
    result: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return sorted(result)


def sensitive_url_parameter_name(value: object) -> bool:
    name = str(value or "").strip().lower().replace("-", "_")
    return name in SENSITIVE_URL_QUERY_NAMES or name.endswith(
        ("_credential", "_key", "_password", "_secret", "_signature", "_token")
    )


def url_contains_credentials(value: object) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        parsed = urllib.parse.urlparse(text)
        if parsed.username is not None or parsed.password is not None:
            return True
        for component in (parsed.query, parsed.fragment):
            for raw_name, _ in urllib.parse.parse_qsl(component.replace(";", "&"), keep_blank_values=True):
                name = raw_name
                for _ in range(2):
                    name = urllib.parse.unquote_plus(name)
                name = name.strip().lower().replace("-", "_")
                if sensitive_url_parameter_name(name):
                    return True
    except (TypeError, ValueError):
        return True
    return False


def strip_profile_secrets(value: object) -> object:
    if isinstance(value, list):
        return [strip_profile_secrets(item) for item in value]
    if not isinstance(value, dict):
        return json_clone(value)
    safe: dict[str, object] = {}
    for raw_key, raw_value in value.items():
        key = str(raw_key)
        canonical = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower().replace("-", "_")
        if sensitive_url_parameter_name(canonical) or canonical in {"tianditu_key", "tianditu_token"}:
            continue
        if canonical.endswith("url") and isinstance(raw_value, str) and url_contains_credentials(raw_value):
            continue
        safe[key] = strip_profile_secrets(raw_value)
    return safe


def sanitize_custom_basemaps(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    def zoom_value(raw: object, fallback: int) -> int:
        try:
            return int(float(raw))
        except (TypeError, ValueError):
            return fallback

    result: list[dict[str, object]] = []
    seen: set[str] = set()
    text_limits = {
        "name": 120,
        "url": 4096,
        "provider": 240,
        "attribution": 1000,
        "sourceUrl": 4096,
        "note": 240,
        "subdomains": 120,
        "layers": 500,
        "styles": 500,
        "format": 80,
        "version": 20,
        "tileMatrixSet": 160,
        "matrixPrefix": 160,
        "crs": 80,
    }
    for index, item in enumerate(value[:100]):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("type") or "xyz").strip().lower()
        if kind not in CUSTOM_BASEMAP_TYPES:
            continue
        name = str(item.get("name") or "").strip()[: text_limits["name"]]
        url = str(item.get("url") or "").strip()[: text_limits["url"]]
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            continue
        if not name or parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc or url_contains_credentials(url):
            continue
        raw_id = str(item.get("id") or f"custom-{index + 1}").strip().lower()
        identifier = re.sub(r"-+", "-", re.sub(r"[^a-z0-9_-]+", "-", raw_id)).strip("-")[:80]
        if not identifier.startswith("custom-"):
            identifier = f"custom-{identifier or index + 1}"
        if identifier in seen:
            suffix = 2
            candidate = f"{identifier[:70]}-{suffix}"
            while candidate in seen:
                suffix += 1
                candidate = f"{identifier[:70]}-{suffix}"
            identifier = candidate
        seen.add(identifier)
        safe: dict[str, object] = {"id": identifier, "name": name, "type": kind, "url": url}
        for key, limit in text_limits.items():
            if key in {"name", "url"}:
                continue
            text = str(item.get(key) or "").strip()[:limit]
            if text:
                if key == "sourceUrl":
                    try:
                        source = urllib.parse.urlparse(text)
                    except ValueError:
                        continue
                    if source.scheme.lower() not in {"http", "https"} or not source.netloc or url_contains_credentials(text):
                        continue
                safe[key] = text
        min_zoom = max(0, min(24, zoom_value(item.get("minZoom"), 0)))
        max_zoom = max(min_zoom, min(24, zoom_value(item.get("maxZoom"), 19)))
        native_zoom = max(min_zoom, min(max_zoom, zoom_value(item.get("maxNativeZoom"), max_zoom)))
        safe.update(
            {
                "minZoom": min_zoom,
                "maxZoom": max_zoom,
                "maxNativeZoom": native_zoom,
                "transparent": item.get("transparent") is not False,
            }
        )
        if kind == "cog":
            bounds = item.get("bounds")
            if isinstance(bounds, list) and len(bounds) == 4:
                try:
                    west, south, east, north = (float(part) for part in bounds)
                except (TypeError, ValueError):
                    pass
                else:
                    if -180 <= west < east <= 180 and -90 <= south < north <= 90:
                        safe["bounds"] = [west, south, east, north]
            safe["crs"] = str(item.get("crs") or "EPSG:3857").strip()[: text_limits["crs"]]
            try:
                safe["bandCount"] = max(0, min(1024, int(float(item.get("bandCount") or 0))))
            except (TypeError, ValueError):
                safe["bandCount"] = 0
        result.append(safe)
    return result


def normalize_profile(payload: object) -> dict[str, object]:
    profile = empty_profile()
    if isinstance(payload, dict):
        for key in ("favoriteDatasets", "visualPreferences", "customBasemaps", "defaultBasemap", "projects", "updatedAt", "language"):
            if key in payload:
                profile[key] = payload[key]
    profile["version"] = PROFILE_VERSION
    profile["favoriteDatasets"] = normalize_string_list(profile.get("favoriteDatasets"))
    if not isinstance(profile.get("visualPreferences"), dict):
        profile["visualPreferences"] = {}
    profile["customBasemaps"] = sanitize_custom_basemaps(profile.get("customBasemaps"))
    default_basemap = re.sub(r"[^a-z0-9_-]+", "-", str(profile.get("defaultBasemap") or "OSM"), flags=re.IGNORECASE).strip("-")[:80]
    profile["defaultBasemap"] = default_basemap or "OSM"
    projects = profile.get("projects")
    profile["projects"] = strip_profile_secrets(projects) if isinstance(projects, dict) else {}
    return profile


def read_profile_unlocked() -> dict[str, object]:
    path = profile_path()
    if not path.exists():
        return empty_profile()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_profile(raw)
        if normalized != raw:
            write_profile_unlocked(normalized)
        return normalized
    except Exception:
        return empty_profile()


def write_profile_unlocked(profile: dict[str, object]) -> None:
    path = profile_path()
    temporary = path.with_name(f"{path.name}.tmp")
    write_text_atomic_with_fallback(
        path,
        json.dumps(normalize_profile(profile), ensure_ascii=False, indent=2),
        temporary=temporary,
        replace=os.replace,
    )


def load_profile() -> dict[str, object]:
    with PROFILE_LOCK:
        return json_clone(read_profile_unlocked())  # type: ignore[return-value]


def project_key_from_state(state: dict[str, object]) -> str:
    project = str(state.get("project") or "").strip()
    title = str(state.get("title") or "").strip()
    source = project if project and project != "YOUR_EE_PROJECT" else title
    source = source or "default"
    key = re.sub(r"[^a-z0-9_-]+", "-", source, flags=re.IGNORECASE).strip("-")[:80]
    return key or "default"


def state_project_entry(profile: dict[str, object], state: dict[str, object]) -> dict[str, object]:
    projects = profile.setdefault("projects", {})
    if not isinstance(projects, dict):
        projects = {}
        profile["projects"] = projects
    key = project_key_from_state(state)
    entry = projects.get(key)
    if not isinstance(entry, dict):
        entry = {}
        projects[key] = entry
    project = str(state.get("project") or "").strip()
    title = str(state.get("title") or "").strip()
    if project:
        entry["project"] = project
    if title:
        entry["title"] = title
    entry["updatedAt"] = now_iso()
    return entry


def sanitize_recent_layers(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    allowed = {
        "id",
        "name",
        "dataset",
        "type",
        "role",
        "sourceId",
        "shown",
        "opacity",
        "summary",
        "recipe",
        "aoi",
        "styleProfile",
        "stylePreset",
        "visParams",
        "legend",
    }
    layers: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        safe = {key: json_clone(item[key]) for key in allowed if key in item}
        if "sourceId" in safe:
            safe["sourceId"] = str(safe["sourceId"] or "").strip()[:80]
        if safe.get("role") not in {"base", "overlay"}:
            safe.pop("role", None)
        recipe = safe.get("recipe") if isinstance(safe.get("recipe"), dict) else {}
        if safe.get("type") == "local-upload" or recipe.get("kind") == "localUploadPlaceholder":
            continue
        if safe:
            layers.append(safe)  # type: ignore[arg-type]
    return layers[:50]


def sanitize_layer_order(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in value[:100]:
        if not isinstance(item, str):
            continue
        layer_id = item.strip()[:160]
        if layer_id and layer_id not in seen:
            seen.add(layer_id)
            result.append(layer_id)
    return result


def sanitize_recent_tasks(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    allowed = {
        "id",
        "type",
        "analysis",
        "title",
        "name",
        "status",
        "state",
        "destination",
        "folder",
        "fileNamePrefix",
        "taskId",
        "taskName",
        "driveSearchUrl",
        "createdAt",
        "updatedAt",
        "params",
        "notes",
        "warnings",
    }
    tasks: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        safe = {key: json_clone(item[key]) for key in allowed if key in item}
        if safe:
            tasks.append(safe)  # type: ignore[arg-type]
    return tasks[:30]


def sanitize_recent_uploads(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    allowed = {
        "id",
        "name",
        "storedName",
        "extension",
        "format",
        "size",
        "projection",
        "savedPath",
        "url",
        "componentPaths",
        "previewPath",
        "previewUrl",
        "previewFormat",
        "previewFeatureCount",
        "previewLimited",
        "previewError",
        "renderable",
        "agentReadable",
        "status",
        "createdAt",
        "updatedAt",
        "processingHints",
        "recommendedAgentAction",
        "layerId",
    }
    uploads: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        safe = {key: json_clone(item[key]) for key in allowed if key in item}
        extension = str(safe.get("extension") or "").lower()
        if extension in UPLOAD_SHAPEFILE_SIDECAR_EXTENSIONS and not safe.get("previewUrl"):
            safe["layerId"] = None
            safe["renderable"] = False
            safe["status"] = "missing-shapefile-components"
            safe["previewError"] = (
                "Shapefile upload is incomplete. Select the .shp geometry file together with .shx and .dbf, "
                "or upload a ZIP containing all components."
            )
        elif safe.get("renderable") is False:
            safe["layerId"] = None
        if safe:
            uploads.append(safe)  # type: ignore[arg-type]
    return uploads[:50]


def merge_profile_with_state(state: dict[str, object]) -> dict[str, object]:
    reason = str(state.get("sessionReason") or "").lower()
    with PROFILE_LOCK:
        profile = read_profile_unlocked()
        favorites = normalize_string_list(state.get("favoriteDatasets"))
        if reason in EXACT_FAVORITE_REASONS:
            profile["favoriteDatasets"] = favorites
        elif favorites:
            profile["favoriteDatasets"] = normalize_string_list([*normalize_string_list(profile.get("favoriteDatasets")), *favorites])

        language = state.get("language")
        if isinstance(language, str) and language:
            profile["language"] = language
        visual_preferences = state.get("visualPreferences")
        if isinstance(visual_preferences, dict):
            profile["visualPreferences"] = json_clone(visual_preferences)
        if isinstance(state.get("customBasemaps"), list):
            profile["customBasemaps"] = sanitize_custom_basemaps(state.get("customBasemaps"))
        default_basemap = state.get("defaultBasemap")
        if isinstance(default_basemap, str) and default_basemap.strip():
            safe_default = re.sub(r"[^a-z0-9_-]+", "-", default_basemap, flags=re.IGNORECASE).strip("-")[:80]
            if safe_default:
                profile["defaultBasemap"] = safe_default

        entry = state_project_entry(profile, state)
        center = state.get("center")
        zoom = state.get("zoom")
        basemap = state.get("basemap")
        if isinstance(center, list) and len(center) == 2 and isinstance(zoom, (int, float)):
            view: dict[str, object] = {"center": json_clone(center), "zoom": zoom, "basemap": basemap}
            if isinstance(state.get("basemapShown"), bool):
                view["basemapShown"] = state["basemapShown"]
            if isinstance(state.get("basemapOpacity"), (int, float)):
                view["basemapOpacity"] = max(0.0, min(1.0, float(state["basemapOpacity"])))
            entry["view"] = view
        active_layer_id = str(state.get("activeLayerId") or "").strip()[:160]
        if active_layer_id:
            entry["activeLayerId"] = active_layer_id
        elif "activeLayerId" in state:
            entry.pop("activeLayerId", None)
        if isinstance(state.get("aoi"), dict):
            entry["aoi"] = json_clone(state["aoi"])
        elif "aoi" in state and reason in CLEAR_AOI_REASONS:
            entry.pop("aoi", None)
            entry.pop("aoiStyle", None)
        if isinstance(state.get("aoiStyle"), dict) and reason not in CLEAR_AOI_REASONS:
            entry["aoiStyle"] = json_clone(state["aoiStyle"])
        if isinstance(state.get("aoiShown"), bool) and reason not in CLEAR_AOI_REASONS:
            entry["aoiShown"] = state["aoiShown"]
        measurements = state.get("measurements")
        if isinstance(measurements, list) and (measurements or reason in CLEAR_MEASUREMENT_REASONS):
            entry["measurements"] = json_clone(measurements)
            if reason in CLEAR_MEASUREMENT_REASONS:
                entry.pop("measurementsShown", None)
                entry.pop("measurementsOpacity", None)
        if reason not in CLEAR_MEASUREMENT_REASONS and isinstance(state.get("measurementsShown"), bool):
            entry["measurementsShown"] = state["measurementsShown"]
        if reason not in CLEAR_MEASUREMENT_REASONS and isinstance(state.get("measurementsOpacity"), (int, float)):
            entry["measurementsOpacity"] = state["measurementsOpacity"]
        layers_value = state.get("layers")
        layers = sanitize_recent_layers(layers_value)
        if isinstance(layers_value, list):
            entry["recentLayers"] = layers
        if isinstance(state.get("layerOrder"), list):
            entry["layerOrder"] = sanitize_layer_order(state.get("layerOrder"))
        tasks_value = state.get("tasks")
        if isinstance(tasks_value, list):
            entry["tasks"] = sanitize_recent_tasks(tasks_value)
        uploads_value = state.get("uploads")
        if isinstance(uploads_value, list):
            entry["uploads"] = sanitize_recent_uploads(uploads_value)

        profile["updatedAt"] = now_iso()
        write_profile_unlocked(profile)
        return json_clone(profile)  # type: ignore[return-value]


def session_state_payload() -> dict[str, object]:
    with SESSION_LOCK:
        state = json.loads(json.dumps(SESSION_STATE, ensure_ascii=False))
        synced_at = SESSION_SYNCED_AT
    profile = load_profile()
    return {
        "ok": True,
        "state": state,
        "syncedAt": synced_at,
        "profile": profile,
        "profileUpdatedAt": profile.get("updatedAt"),
    }


def enqueue_session_action(action: dict[str, object]) -> dict[str, object]:
    global SESSION_ACTION_COUNTER
    with SESSION_LOCK:
        SESSION_ACTION_COUNTER += 1
        queued = {
            "id": SESSION_ACTION_COUNTER,
            "queuedAt": time.time(),
            **action,
        }
        SESSION_ACTIONS.append(queued)
        del SESSION_ACTIONS[:-SESSION_ACTION_LIMIT]
        return {"ok": True, "action": queued, "pending": len(SESSION_ACTIONS)}


class EasyGeeHandler(QuietHandler):
    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            return {}
        if length > 1_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Request JSON must be an object")
        return payload

    def trusted_local_credential_request(self) -> bool:
        try:
            if not ipaddress.ip_address(str(self.client_address[0])).is_loopback:
                return False
        except ValueError:
            return False
        host_header = str(self.headers.get("Host") or "").strip()
        try:
            host = urllib.parse.urlsplit(f"//{host_header}").hostname or ""
            host_is_loopback = host.lower() == "localhost" or ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False
        if not host_is_loopback:
            return False
        origin = str(self.headers.get("Origin") or "").strip()
        if not origin:
            return True
        try:
            parsed_origin = urllib.parse.urlsplit(origin)
        except ValueError:
            return False
        return parsed_origin.scheme in {"http", "https"} and parsed_origin.netloc.lower() == host_header.lower()

    def require_json_content_type(self) -> bool:
        content_type = str(self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type == "application/json":
            return True
        self.send_json({"ok": False, "error": "Content-Type must be application/json"}, status=415)
        return False

    def read_upload_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            return b""
        if length > (UPLOAD_MAX_BYTES * 6):
            raise ValueError("Upload request is too large")
        return self.rfile.read(length)

    def resolved_static_path(self) -> tuple[Path, bool]:
        translated = Path(self.translate_path(self.path)).resolve()
        root = Path(self.directory or os.getcwd()).resolve()
        try:
            translated.relative_to(root)
        except ValueError:
            return translated, False
        return translated, True

    def serve_byte_range(self, *, head_only: bool = False) -> bool:
        range_header = str(self.headers.get("Range") or "").strip()
        if not range_header:
            return False
        translated, is_safe = self.resolved_static_path()
        if not is_safe:
            self.send_error(404)
            return True
        if not translated.is_file():
            return False
        size = translated.stat().st_size
        if not range_header.lower().startswith("bytes=") or "," in range_header:
            self.send_response(416)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        try:
            start_text, end_text = range_header[6:].strip().split("-", 1)
            if start_text:
                start = int(start_text)
                end = int(end_text) if end_text else size - 1
            else:
                suffix = int(end_text)
                if suffix <= 0:
                    raise ValueError
                start = max(0, size - suffix)
                end = size - 1
            if start < 0 or start >= size or end < start:
                raise ValueError
            end = min(end, size - 1)
        except (TypeError, ValueError):
            self.send_response(416)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        length = end - start + 1
        stat = translated.stat()
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(translated)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
        self.end_headers()
        if head_only:
            return True
        try:
            with translated.open("rb") as stream:
                stream.seek(start)
                remaining = length
                while remaining:
                    chunk = stream.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        return True

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/session/capabilities":
            self.send_json({"ok": True, "contract": load_agent_contract()})
            return
        if parsed.path == "/api/session/profile":
            profile = load_profile()
            self.send_json({"ok": True, "profile": profile, "profileUpdatedAt": profile.get("updatedAt")})
            return
        if parsed.path == "/api/session/credentials/tianditu":
            if not self.trusted_local_credential_request():
                self.send_json({"ok": False, "error": "Local same-origin request required"}, status=403)
                return
            token = load_tianditu_secret()
            self.send_json({"ok": True, "supported": os.name == "nt", "remembered": bool(token), "token": token})
            return
        if parsed.path == "/api/session/state":
            self.send_json(session_state_payload())
            return
        if parsed.path == "/api/session/actions":
            query = urllib.parse.parse_qs(parsed.query)
            try:
                since = int((query.get("since") or ["0"])[0] or "0")
            except Exception:
                since = 0
            with SESSION_LOCK:
                actions = [action for action in SESSION_ACTIONS if int(action.get("id") or 0) > since]
                latest = SESSION_ACTION_COUNTER
            self.send_json({"ok": True, "actions": actions, "latestActionId": latest})
            return
        if parsed.path == "/api/catalog":
            global CATALOG_CACHE
            try:
                if CATALOG_CACHE is None:
                    from create_map_console import build_catalog

                    catalog, source = build_catalog([], include_remote=True)
                    CATALOG_CACHE = {"ok": True, "catalog": catalog, "source": source}
                self.send_json(CATALOG_CACHE)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        _, is_safe = self.resolved_static_path()
        if not is_safe:
            self.send_error(404)
            return
        if self.serve_byte_range():
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        _, is_safe = self.resolved_static_path()
        if not is_safe:
            self.send_error(404)
            return
        if self.serve_byte_range(head_only=True):
            return
        super().do_HEAD()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/session/credentials/tianditu":
            if not self.trusted_local_credential_request():
                self.send_json({"ok": False, "error": "Local same-origin request required"}, status=403)
                return
            if not self.require_json_content_type():
                return
            try:
                payload = self.read_json()
                remember = payload.get("remember") is True
                if remember:
                    save_tianditu_secret(payload.get("token"))
                else:
                    delete_tianditu_secret()
                self.send_json({"ok": True, "supported": os.name == "nt", "remembered": remember})
            except ValueError as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=400)
            except Exception:
                self.send_json({"ok": False, "error": "Encrypted credential storage is unavailable"}, status=500)
            return
        if parsed.path == "/api/session/state":
            try:
                payload = self.read_json()
                state = payload.get("state") if isinstance(payload.get("state"), dict) else payload
                if not isinstance(state, dict):
                    raise ValueError("state must be a JSON object")
                if not session_state_protocol_is_current(state):
                    current = session_state_payload()
                    self.send_json(
                        {
                            "ok": True,
                            "ignored": True,
                            "reason": "stale-agent-protocol",
                            "expectedAgentProtocolVersion": AGENT_PROTOCOL_VERSION,
                            "receivedAgentProtocolVersion": session_state_protocol_version(state),
                            "syncedAt": current.get("syncedAt"),
                            "profileUpdatedAt": current.get("profileUpdatedAt"),
                        }
                    )
                    return
                global SESSION_STATE, SESSION_SYNCED_AT
                state_copy = strip_profile_secrets(json.loads(json.dumps(state, ensure_ascii=False)))
                if not isinstance(state_copy, dict):
                    state_copy = {}
                if isinstance(state_copy.get("customBasemaps"), list):
                    state_copy["customBasemaps"] = sanitize_custom_basemaps(state_copy["customBasemaps"])
                with SESSION_LOCK:
                    SESSION_STATE = state_copy
                    SESSION_SYNCED_AT = time.time()
                    synced_at = SESSION_SYNCED_AT
                profile = merge_profile_with_state(state_copy)
                self.send_json({"ok": True, "syncedAt": synced_at, "profileUpdatedAt": profile.get("updatedAt")})
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        if parsed.path == "/api/session/actions":
            try:
                payload = self.read_json()
                action = payload.get("action") if isinstance(payload.get("action"), dict) else payload
                if not isinstance(action, dict):
                    raise ValueError("action must be a JSON object")
                self.send_json(enqueue_session_action(action))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        if parsed.path == "/api/uploads":
            try:
                root = Path(str(self.directory)).resolve()
                payload = save_uploaded_files(root, self.read_upload_body(), self.headers.get("Content-Type") or "")
                self.send_json(payload)
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        if parsed.path == "/api/layer":
            try:
                from create_map_console import build_catalog_layer

                self.send_json(build_catalog_layer(self.read_json()))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        if parsed.path == "/api/analysis/ndvi":
            try:
                from create_map_console import build_ndvi_analysis

                self.send_json(build_ndvi_analysis(self.read_json()))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        if parsed.path == "/api/export/ndvi-drive":
            try:
                from create_map_console import build_ndvi_drive_export

                self.send_json(build_ndvi_drive_export(self.read_json()))
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        self.send_error(404, "Not Found")


def print_plan(plan: PreviewPlan) -> None:
    print("EasyGEE browser preview")
    print(f"  root: {plan.root}")
    print(f"  target: {plan.target}")
    print(f"  type: {plan.target_type}")
    print(f"  url: {plan.url}")
    if plan.notes:
        print("  notes:")
        for note in plan.notes:
            print(f"    - {note}")
    print("")
    print("Keep this process running while the in-app browser is using the preview.")


def serve(plan: PreviewPlan, host: str, port: int) -> None:
    parsed = urllib.parse.urlparse(plan.url)
    actual_port = port or int(parsed.port or 0)
    handler = functools.partial(EasyGeeHandler, directory=plan.root)
    with ThreadingHTTPServer((host, actual_port), handler) as server:
        print_plan(plan)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nEasyGEE browser preview stopped.")


def smoke() -> int:
    with tempfile.TemporaryDirectory(prefix="easygee-preview-smoke-") as tmp:
        root = Path(tmp)
        configure_profile_path(root / "profile.json")
        plan = build_plan(None, "127.0.0.1", 0, "EasyGEE Smoke", root)
        if not Path(plan.target).exists():
            print("FAIL: placeholder was not created")
            return 1
        if not plan.url.startswith("http://127.0.0.1:"):
            print("FAIL: preview URL was not generated")
            return 1
        sample = root / "map.html"
        sample.write_text("<!doctype html><title>map</title>", encoding="utf-8")
        file_plan = build_plan(sample, "127.0.0.1", 5000, "EasyGEE Smoke", None)
        if file_plan.root != str(root) or not file_plan.url.endswith("/map.html"):
            print("FAIL: file plan is wrong")
            return 1
        contract = load_agent_contract()
        if contract.get("stateEndpoint") != "/api/session/state":
            print("FAIL: agent contract was not loaded")
            return 1
        action_response = enqueue_session_action({"type": "noop"})
        if not action_response.get("ok") or not action_response.get("action", {}).get("id"):
            print("FAIL: session action queue is not working")
            return 1
        profile = merge_profile_with_state(
            {
                "title": "Smoke Map",
                "project": "YOUR_EE_PROJECT",
                "favoriteDatasets": ["COPERNICUS/S2_SR_HARMONIZED"],
                "customBasemaps": [
                    {
                        "id": "custom-smoke",
                        "name": "Smoke XYZ",
                        "type": "xyz",
                        "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        "maxZoom": 19,
                    }
                ],
                "defaultBasemap": "custom-smoke",
                "center": [39.9, 116.4],
                "zoom": 10,
                "basemap": "custom-smoke",
                "measurements": [{"id": "m1", "start": [0, 0], "end": [0, 1], "lengthMeters": 1}],
                "tasks": [{"id": "t1", "title": "Drive export", "status": "READY", "folder": "EasyGEE"}],
                "sessionReason": "favorites",
            }
        )
        if profile.get("favoriteDatasets") != ["COPERNICUS/S2_SR_HARMONIZED"]:
            print("FAIL: profile favorites were not persisted")
            return 1
        if profile.get("defaultBasemap") != "custom-smoke" or not profile.get("customBasemaps"):
            print("FAIL: custom basemaps were not persisted")
            return 1
        projects = profile.get("projects") if isinstance(profile.get("projects"), dict) else {}
        if not any(isinstance(entry, dict) and entry.get("tasks") for entry in projects.values()):
            print("FAIL: profile tasks were not persisted")
            return 1
        if not any(isinstance(entry, dict) and entry.get("view", {}).get("basemap") == "custom-smoke" for entry in projects.values()):
            print("FAIL: active basemap was not persisted per project")
            return 1
        payload = session_state_payload()
        if not isinstance(payload.get("profile"), dict):
            print("FAIL: session state does not include profile")
            return 1
    print("serve_map_preview smoke passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path, help="HTML file or directory to serve. If omitted, creates a placeholder page.")
    parser.add_argument("--root", type=Path, help="Directory for the generated placeholder page.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="Bind port. Default: choose a free port.")
    parser.add_argument("--title", default="EasyGEE Preview", help="Title for generated placeholder pages.")
    parser.add_argument("--profile", type=Path, help="Persistent Map Console profile JSON path. Defaults to local app data.")
    parser.add_argument("--plan", action="store_true", help="Print the preview plan and exit without starting a server.")
    parser.add_argument("--json", action="store_true", help="Print the preview plan as JSON. Implies --plan.")
    parser.add_argument("--smoke", action="store_true", help="Run offline self-checks.")
    args = parser.parse_args()

    configure_profile_path(args.profile)

    if args.smoke:
        return smoke()

    plan = build_plan(args.target, args.host, args.port, args.title, args.root)
    if args.json:
        print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))
        return 0
    if args.plan:
        print_plan(plan)
        return 0
    serve(plan, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
