import html
import io
import re

from ...utils.encoding import TEXT_ENCODING_FALLBACKS, decode_bytes
from ...utils.file_indexing import chunk_text

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

def strip_html(text: str) -> str:
    out = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    out = re.sub(r"(?is)<!--.*?-->", " ", out)
    out = re.sub(r"(?is)<[^>]+>", " ", out)
    out = html.unescape(out)
    return re.sub(r"\s+", " ", out).strip()


def normalize_document_text(text: str) -> str:
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in raw.split("\n")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_pdf_pages(raw: bytes) -> list[str]:
    if PdfReader is None:
        raise RuntimeError("PDF 처리 라이브러리(pypdf)를 찾을 수 없습니다.")

    reader = PdfReader(io.BytesIO(raw))
    page_texts: list[str] = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")
    return page_texts


def extract_pdf_text(raw: bytes) -> str:
    return "\n".join(extract_pdf_pages(raw))


def extract_document_text(filename: str, raw: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        return extract_pdf_text(raw)

    text = decode_bytes(raw, TEXT_ENCODING_FALLBACKS)
    if suffix in {"html", "htm"}:
        return strip_html(text)
    return text


def chunk_document_sections(text: str) -> list[dict]:
    normalized = normalize_document_text(text)
    if not normalized:
        return []

    sections: list[dict] = []
    current_heading = "root"
    current_lines: list[str] = []

    def flush_section():
        if not current_lines:
            return
        body = "\n".join(current_lines).strip()
        if not body:
            return
        for part in chunk_text(body):
            sections.append({"text": part, "heading_path": current_heading})

    for line in normalized.splitlines():
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", line)
        if match:
            flush_section()
            current_lines = []
            current_heading = match.group(2).strip() or "section"
            continue
        current_lines.append(line)

    flush_section()
    return sections


def extract_document_sections(filename: str, raw: bytes) -> list[dict]:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        page_texts = extract_pdf_pages(raw)
        total_pages = len(page_texts)
        sections: list[dict] = []
        for page_idx, page_text in enumerate(page_texts, start=1):
            normalized_page = normalize_document_text(page_text)
            if not normalized_page:
                continue
            for part in chunk_text(normalized_page):
                sections.append(
                    {
                        "text": part,
                        "heading_path": f"page:{page_idx}",
                        "page_number": page_idx,
                        "total_pages": total_pages,
                    }
                )
        return sections

    text = extract_document_text(filename, raw)
    sections = chunk_document_sections(text)
    for section in sections:
        section.setdefault("page_number", None)
        section.setdefault("total_pages", None)
    return sections
