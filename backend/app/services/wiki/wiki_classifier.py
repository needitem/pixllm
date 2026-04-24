import json
from urllib import request

from ... import config


WORKFLOW_FAMILY_CLASSIFIER_PREFIX = "\n".join(
    [
        "You are a strict workflow family classifier for a technical engine wiki.",
        "Do not answer the user question.",
        'Return JSON only with this shape: {"primary_family":"workflow_family_id","secondary_families":["workflow_family_id"],"confidence":"low|medium|high"}',
        "Allowed family values are the workflow-family ids in the available family catalog, or empty string.",
        "Choose one primary_family and 0 to 2 secondary_families when needed.",
        "Use empty primary_family only when the question is clearly unrelated to engine APIs. If the question is about an engine API family, do not leave primary_family empty.",
        "Primary evidence should come from the provided family catalog, including titles, summaries, aliases, and workflow-family ids.",
        "Use secondary_families only when the query genuinely spans multiple families.",
        "Do not include explanations or extra fields.",
    ]
)


def _normalize_base_url(value: str) -> str:
    return str(value or "").strip().rstrip("/")


def _to_string(value) -> str:
    return str(value or "").strip()


def _catalog_family_id(item) -> str:
    if not isinstance(item, dict):
        return ""
    return _to_string(item.get("family") or item.get("workflow_family"))


def _catalog_allowed_families(family_catalog) -> list[str]:
    families: list[str] = []
    seen = set()
    for item in family_catalog or []:
        family = _catalog_family_id(item)
        if not family or family in seen:
            continue
        seen.add(family)
        families.append(family)
    return families


def _normalize_family(value: str, allowed_families) -> str:
    normalized = _to_string(value)
    allowed = set(allowed_families or [])
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
    allowed_families = _catalog_allowed_families(family_catalog)
    if not allowed_families:
        return "\n".join([WORKFLOW_FAMILY_CLASSIFIER_PREFIX, "", "No workflow family catalog is available. Return empty primary_family."])
    for item in family_catalog or []:
        if not isinstance(item, dict):
            continue
        family = _normalize_family(_catalog_family_id(item), allowed_families)
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
    allowed_families = _catalog_allowed_families(family_catalog)
    parsed = _post_json_completion(_family_catalog_prompt(family_catalog), query)
    if not parsed and allowed_families:
        parsed = _post_json_completion(WORKFLOW_FAMILY_CLASSIFIER_PREFIX, query)
    primary_family = _normalize_family(parsed.get("primary_family") or parsed.get("primaryFamily"), allowed_families)
    secondary_families = [
        family
        for family in [_normalize_family(item, allowed_families) for item in (parsed.get("secondary_families") or parsed.get("secondaryFamilies") or [])]
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
