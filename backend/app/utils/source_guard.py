import re
from typing import Iterable, List


_SOURCE_FILE_EXTENSIONS = {
    "c",
    "cc",
    "cjs",
    "cpp",
    "cxx",
    "cs",
    "css",
    "go",
    "h",
    "hpp",
    "htm",
    "html",
    "java",
    "js",
    "json",
    "md",
    "mjs",
    "pdf",
    "py",
    "rs",
    "rst",
    "ts",
    "tsx",
    "txt",
    "svelte",
    "xml",
    "xaml",
    "yaml",
    "yml",
}


def normalize_source_path(path: str) -> str:
    return str(path or "").strip().replace("\\", "/").lower()


def extract_answer_file_mentions(answer: str) -> List[str]:
    text = str(answer or "")
    if not text:
        return []

    mentions: List[str] = []
    token_pattern = r"(?:[A-Za-z]:)?[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8}(?::\d+)?"
    for match in re.finditer(token_pattern, text):
        token = match.group(0).strip().strip("`\"'()[]{}<>,;:")
        if not token or token.startswith(("http://", "https://")):
            continue
        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?", token):
            continue
        if re.fullmatch(r"v?\d+(?:\.\d+){1,3}", token.lower()):
            continue
        token_base = token.split(":", 1)[0]
        if "." not in token_base:
            continue
        extension = token_base.rsplit(".", 1)[-1].lower()
        if extension not in _SOURCE_FILE_EXTENSIONS:
            continue
        mentions.append(token)

    dedup: List[str] = []
    seen = set()
    for mention in mentions:
        key = mention.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(mention)
    return dedup


def is_grounded_source(mention: str, allowed_paths: Iterable[str]) -> bool:
    candidate = normalize_source_path(mention).split(":", 1)[0]
    if not candidate:
        return True
    allowed = {normalize_source_path(item) for item in list(allowed_paths or []) if str(item or "").strip()}
    if candidate in allowed:
        return True
    return any(path.endswith(f"/{candidate}") or candidate.endswith(f"/{path}") for path in allowed)


def find_ungrounded_source_mentions(answer: str, allowed_paths: Iterable[str]) -> List[str]:
    return [
        mention
        for mention in extract_answer_file_mentions(answer)
        if not is_grounded_source(mention, allowed_paths)
    ]
