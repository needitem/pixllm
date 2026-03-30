from typing import Dict, List, Optional


def apply_module_filter(results: List[Dict], module_filter: Optional[str]) -> List[Dict]:
    if not module_filter:
        return results
    filtered = []
    for r in results:
        payload = r.get("payload", {}) if isinstance(r, dict) else {}
        module = payload.get("module") or ""
        if module.startswith(module_filter):
            filtered.append(r)
    return filtered
