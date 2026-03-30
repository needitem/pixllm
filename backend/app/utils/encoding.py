from pathlib import Path
from typing import Sequence

TEXT_ENCODING_FALLBACKS = ("utf-8", "euc-kr", "cp949", "cp1252", "latin-1")
TEXT_ENCODING_FALLBACKS_LATIN_FIRST = ("utf-8", "euc-kr", "cp949", "latin-1", "cp1252")


def decode_bytes(raw: bytes, encodings: Sequence[str] = TEXT_ENCODING_FALLBACKS) -> str:
    for enc in encodings:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def read_text_with_fallback(path: Path, encodings: Sequence[str] = TEXT_ENCODING_FALLBACKS) -> str:
    for enc in encodings:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return path.read_text(encoding="utf-8", errors="replace")
