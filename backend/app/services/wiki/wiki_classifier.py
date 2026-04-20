import json
from urllib import request

from ... import config


WORKFLOW_FAMILY_CLASSIFIER_PREFIX = "\n".join(
    [
        "You are a strict workflow family classifier for a technical engine wiki.",
        "Do not answer the user question.",
        'Return JSON only with this shape: {"primary_family":"api_imageview","secondary_families":["api_raster"],"confidence":"low|medium|high"}',
        "Allowed family values: api_imageview, api_raster, api_coordinate, api_videoview, api_milmapview, api_planetview, api_vector, api_editor, api_scene_editor, api_sensor_model, api_dfs, api_uspaceview, api_core, or empty string.",
        "Choose one primary_family and 0 to 2 secondary_families when needed.",
        "Use empty primary_family only when the question is clearly unrelated to engine APIs. If the question is about an engine API family, do not leave primary_family empty.",
        "Family glossary:",
        "- api_imageview: ImageView hosting, layer add/remove, background map, zoom, refresh, screen/world conversion, pixel read.",
        "- api_raster: raster file load, XRasterIO, XDM bands, composite assembly, grayscale/RGB display, stretch/cut, raster enhancement.",
        "- api_coordinate: spatial reference, EPSG/WKT/Proj4, UTM/MGRS/GEOREF, coordinate-code conversion, point transforms between SRs.",
        "- api_videoview: video open/playback, channel bind/reset, KLV, frame capture, video fusion, video layer wiring.",
        "- api_milmapview: MilmapView scale/center/render/display operations.",
        "- api_planetview: PlanetView camera/render/dataset display, PBI group registration tied to view usage.",
        "- api_vector: vector file load, SHP overlay, vector object properties, bounds, vector hit test, vector object geometry.",
        "- api_editor: edit/selection/group/ungroup/undo/redo/canvas/edit interactions on displayed objects.",
        "- api_scene_editor: scene file create/open/save, scene object IO, scene object selection lifecycle.",
        "- api_sensor_model: image-to-ground, ground-to-image, projection, sensor geometry, world/image mapping from sensor model.",
        "- api_dfs: DFS provider/export/PBI/PBE pipeline, export progress, export cancel, provider group inputs.",
        "- api_uspaceview: UspaceView render layers, camera/region/world interaction.",
        "- api_core: license validation, config path, thread progress/helper utilities.",
        "Decision rules:",
        "- Prefer api_sensor_model for image<->ground or image<->geo projection, and api_coordinate for coordinate-code/SR conversion.",
        "- Prefer api_dfs for provider/export/pbi/pbe pipeline questions, and api_planetview for camera/render/dataset display questions.",
        "- Prefer api_editor for edit/selection/group/undo/redo questions, and api_scene_editor for scene object IO/scene file questions.",
        "- Prefer api_videoview for video channel/playback/klv/fusion questions, even when the view is embedded in ImageView/MilmapView/PlanetView.",
        "- Prefer api_vector for SHP/vector overlay and vector object/property questions, even when ImageView is also mentioned.",
        "- If the query explicitly says ImageView and asks about comp-link manager retrieval or composite 1/2 front/back settings, prefer api_imageview rather than api_raster.",
        "- If the query explicitly says ImageView and also says 비디오 레이어, 채널 연결, 채널 해제, 초기 프레임 크기, KLV, or 프레임 캡처, prefer api_videoview.",
        "- If the query explicitly says 편집 화면, Canvas, Component, To Front, To Rear, To Frontmost, or To Rearmost, prefer api_editor unless scene file/object is explicit.",
        "- Prefer api_sensor_model for 영상 중심점의 지도 좌표 and image-center map-coordinate questions.",
        "- Prefer api_uspaceview for bare 공간 좌표 -> world 좌표 / 화면 좌표 conversion questions.",
        "- Prefer api_dfs when DFS/provider group is named together with XDMCompManager or export progress/cancel.",
        "- If the query explicitly says MilmapView or PlanetView, prefer that view family for its shader, render-layer, capture, and camera options.",
        "- Prefer api_coordinate for generic 좌표변환, 좌표 한 점 변환, and 두 좌표계 사이 변환 when image/ground projection words are absent.",
        "- Prefer api_core for license/config/progress helper questions.",
        "Do not include explanations or extra fields.",
        "Examples:",
        '{"primary_family":"api_core","secondary_families":[],"confidence":"high"} // 현재 라이선스가 유효한지 확인하는 방법 알려줘',
        '{"primary_family":"api_core","secondary_families":[],"confidence":"high"} // 엔진 설정 경로를 바꾸고 초기화하는 방법 알려줘',
        '{"primary_family":"api_videoview","secondary_families":[],"confidence":"high"} // Mpeg2TS 동영상 파일을 로드해서 화면에 도시하는 방법 알려줘',
        '{"primary_family":"api_sensor_model","secondary_families":["api_coordinate"],"confidence":"high"} // 지리 좌표를 영상 좌표로 변환하는 방법 알려줘',
        '{"primary_family":"api_dfs","secondary_families":[],"confidence":"high"} // DFS export 진행률을 확인하는 방법 알려줘',
        '{"primary_family":"api_scene_editor","secondary_families":[],"confidence":"high"} // scene 파일을 새로 만드는 방법 알려줘',
        '{"primary_family":"api_vector","secondary_families":["api_imageview"],"confidence":"high"} // ImageView 위에 shp를 overlay 하는 방법 알려줘',
        '{"primary_family":"api_videoview","secondary_families":["api_imageview"],"confidence":"high"} // ImageView 비디오 레이어에 채널 연결하는 방법 알려줘',
        '{"primary_family":"api_videoview","secondary_families":["api_imageview"],"confidence":"high"} // ImageView 비디오 레이어 초기 프레임 크기 설정 방법 알려줘',
        '{"primary_family":"api_imageview","secondary_families":["api_raster"],"confidence":"high"} // 합성 1 Front 설정하는 방법 알려줘',
        '{"primary_family":"api_editor","secondary_families":[],"confidence":"high"} // 편집 화면에서 To Front 변경하는 방법 알려줘',
        '{"primary_family":"api_editor","secondary_families":[],"confidence":"high"} // 편집 화면에서 Component 사용하는 방법 알려줘',
        '{"primary_family":"api_coordinate","secondary_families":[],"confidence":"high"} // 좌표 한 점 변환하는 방법 알려줘',
        '{"primary_family":"api_milmapview","secondary_families":[],"confidence":"high"} // MilmapView에서 Shader Code CBS 사용하는 방법 알려줘',
        '{"primary_family":"api_planetview","secondary_families":[],"confidence":"high"} // PlanetView에서 Shader Code Average 사용하는 방법 알려줘',
        '{"primary_family":"api_sensor_model","secondary_families":["api_coordinate"],"confidence":"high"} // 영상 중심점의 지도 좌표를 얻는 방법 알려줘',
        '{"primary_family":"api_uspaceview","secondary_families":["api_coordinate"],"confidence":"high"} // 공간 좌표를 world 좌표로 바꾸는 방법 알려줘',
        '{"primary_family":"api_uspaceview","secondary_families":["api_coordinate"],"confidence":"high"} // 공간 좌표를 화면 좌표로 바꾸는 방법 알려줘',
        '{"primary_family":"api_dfs","secondary_families":[],"confidence":"high"} // XDMCompManager를 DFS provider group에 추가하는 방법 알려줘',
    ]
)


def _normalize_base_url(value: str) -> str:
    return str(value or "").strip().rstrip("/")


def _to_string(value) -> str:
    return str(value or "").strip()


def _normalize_family(value: str) -> str:
    normalized = _to_string(value)
    allowed = {
        "api_imageview",
        "api_raster",
        "api_coordinate",
        "api_videoview",
        "api_milmapview",
        "api_planetview",
        "api_vector",
        "api_editor",
        "api_scene_editor",
        "api_sensor_model",
        "api_dfs",
        "api_uspaceview",
        "api_core",
    }
    return normalized if normalized in allowed else ""


def _post_json_completion(prompt: str, query: str) -> dict:
    base_url = _normalize_base_url(config.WORKFLOW_CLASSIFIER_URL)
    model = _to_string(config.WORKFLOW_CLASSIFIER_MODEL)
    if not base_url or not model or not _to_string(query):
        return {}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": _to_string(query)},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    payload = json.dumps(body).encode("utf-8")
    req = request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = _to_string((((data.get("choices") or [{}])[0]).get("message") or {}).get("content"))
        return json.loads(text) if text else {}
    except Exception:
        return {}


def _family_catalog_prompt(family_catalog) -> str:
    lines = [WORKFLOW_FAMILY_CLASSIFIER_PREFIX, "", "Available families:"]
    for item in family_catalog or []:
        if not isinstance(item, dict):
            continue
        family = _normalize_family(item.get("family") or item.get("workflow_family"))
        if not family:
            continue
        title = _to_string(item.get("title"))
        summary = _to_string(item.get("summary"))[:120]
        aliases = [str(value or "").strip() for value in (item.get("aliases") if isinstance(item.get("aliases"), list) else []) if str(value or "").strip()]
        alias_text = ", ".join(aliases[:3])
        lines.append(f"- {family}: {title}")
        if summary:
            lines.append(f"  summary: {summary}")
        if alias_text:
            lines.append(f"  aliases: {alias_text}")
    return "\n".join(lines)


def classify_workflow_family(query: str, family_catalog=None) -> dict:
    if not config.WORKFLOW_CLASSIFIER_URL or not config.WORKFLOW_CLASSIFIER_MODEL or not _to_string(query):
        return {"primary_family": "", "secondary_families": [], "confidence": ""}
    parsed = _post_json_completion(_family_catalog_prompt(family_catalog), query)
    if not parsed:
        parsed = _post_json_completion(WORKFLOW_FAMILY_CLASSIFIER_PREFIX, query)
    primary_family = _normalize_family(parsed.get("primary_family") or parsed.get("primaryFamily"))
    secondary_families = [
        family
        for family in [_normalize_family(item) for item in (parsed.get("secondary_families") or parsed.get("secondaryFamilies") or [])]
        if family
    ][:2]
    if not primary_family and secondary_families:
        primary_family = secondary_families[0]
        secondary_families = secondary_families[1:]
    return {
        "primary_family": primary_family,
        "secondary_families": secondary_families,
        "confidence": _to_string(parsed.get("confidence")).lower(),
    }
__all__ = ["classify_workflow_family"]
