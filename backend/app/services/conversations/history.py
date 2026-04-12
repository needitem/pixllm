from typing import Dict, List, Tuple


def normalize_chat_messages(messages) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for message in list(messages or []):
        role = str(getattr(message, "role", "") or "").strip()
        content = str(getattr(message, "content", "") or "")
        if not role:
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def _message_signature(message: Dict[str, str]) -> Tuple[str, str]:
    return (
        str((message or {}).get("role") or "").strip().lower(),
        str((message or {}).get("content") or ""),
    )


def merge_conversation_messages(
    stored_messages: List[Dict[str, str]],
    request_messages: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    if not stored_messages:
        return list(request_messages or [])
    if not request_messages:
        return list(stored_messages or [])

    stored = list(stored_messages or [])
    incoming = list(request_messages or [])
    max_overlap = min(len(stored), len(incoming))
    overlap = 0
    for size in range(max_overlap, 0, -1):
        if [_message_signature(item) for item in stored[-size:]] == [
            _message_signature(item) for item in incoming[:size]
        ]:
            overlap = size
            break
    return [*stored, *incoming[overlap:]]
