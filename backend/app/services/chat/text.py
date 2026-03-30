from ... import config


def _is_control_message(content: str) -> bool:
    lowered = content.strip().lower()
    for prefix in config.CHAT_CONTROL_MESSAGE_PREFIXES:
        if lowered.startswith(str(prefix or "").strip().lower()):
            return True
    for marker in config.CHAT_CONTROL_MESSAGE_CONTAINS:
        if str(marker or "").strip().lower() in lowered:
            return True
    return False


def sanitize_user_message(content: str) -> str:
    text = (content or "").strip()
    if not text:
        return ""

    if _is_control_message(text) and "---" in text:
        text = text.split("---", 1)[1].strip()

    if "[Pasted" in text:
        text = text.split("[Pasted", 1)[0].strip()

    # Desktop may append a large inline workspace overlay block after the
    # original user prompt. Keep the prompt itself for routing/planning and rely
    # on structured attachments for the actual overlay evidence.
    for marker in ("[Workspace Overlay Policy]", "[Local Workspace Context]"):
        if marker in text:
            text = text.split(marker, 1)[0].strip()
            break

    cleaned_lines = []
    for line in text.splitlines():
        l = line.strip()
        lowered = l.lower()
        if not l:
            continue
        if l in ("assistant", "user"):
            continue
        if lowered.startswith("analyze the") or lowered.startswith("final polish") or lowered.startswith("draft:"):
            continue
        if lowered.startswith("self-correction") or lowered.startswith("final output"):
            continue
        if "</think>" in lowered or "<think>" in lowered:
            continue
        cleaned_lines.append(l)

    return "\n".join(cleaned_lines).strip()

