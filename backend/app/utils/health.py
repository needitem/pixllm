def aggregate_status(components: dict) -> str:
    healthy_states = {"ok", "disabled"}
    return "ok" if all(v.get("status") in healthy_states for v in components.values()) else "degraded"
