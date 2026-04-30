import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_SUMMARY_TAG_RE = re.compile(r"<[^>]+>")
_NAMESPACE_DECL_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_CLASS_DECL_RE = re.compile(r"^\s*public\s+ref\s+class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_ACCESS_RE = re.compile(r"^\s*(public|protected|private)\s*:\s*(?://.*)?$")
_CTOR_RE_TEMPLATE = r"^(?P<name>{name}|~{name})\s*\((?P<args>.*)\)\s*(?P<suffix>(?:\s+[A-Za-z_][A-Za-z0-9_]*)*(?:\s*=\s*0)?)\s*;\s*$"
_METHOD_RE = re.compile(
    r"^(?P<prefix>.+?)\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<args>.*)\)\s*(?P<suffix>(?:\s+[A-Za-z_][A-Za-z0-9_]*)*(?:\s*=\s*0)?)\s*;\s*$"
)
_PROPERTY_RE = re.compile(
    r"^property\s+(?P<type>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<rest>\{.*\};?|;)\s*$"
)
_IMPLEMENTATION_RE = re.compile(
    r"(?P<class>[A-Za-z_][A-Za-z0-9_]*)::(?P<method>~?[A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_SKIP_DECLARATION_PREFIXES = (
    "property ",
    "event ",
    "delegate ",
    "enum class ",
    "literal ",
    "typedef ",
    "using ",
)
_RAW_SOURCE_ENCODINGS = ("utf-8", "cp949", "euc-kr")


def _read_source_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in _RAW_SOURCE_ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _source_path(raw_root: Path, file_path: Path) -> str:
    return f"Source/{file_path.relative_to(raw_root).as_posix()}"


def _clean_summary(lines: Sequence[str]) -> str:
    cleaned: List[str] = []
    for raw in lines:
        text = str(raw or "").strip()
        if not text.startswith("///"):
            continue
        text = text[3:].strip()
        text = _SUMMARY_TAG_RE.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cleaned.append(text)
    return " ".join(cleaned).strip()


def _clean_doc_text(value: str) -> str:
    text = str(value or "")
    text = _SUMMARY_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _doc_lines(lines: Sequence[str]) -> List[str]:
    cleaned: List[str] = []
    for raw in lines:
        text = str(raw or "").strip()
        if text.startswith("///"):
            text = text[3:].strip()
        cleaned.append(text)
    return cleaned


def _extract_tag_blocks(lines: Sequence[str], tag: str) -> List[str]:
    blocks: List[str] = []
    in_block = False
    buffer: List[str] = []
    open_re = re.compile(rf"<{tag}\b[^>]*>", re.IGNORECASE)
    close_re = re.compile(rf"</{tag}>", re.IGNORECASE)
    for line in lines:
        text = str(line or "")
        while text:
            if not in_block:
                open_match = open_re.search(text)
                if not open_match:
                    break
                text = text[open_match.end() :]
                in_block = True
            close_match = close_re.search(text)
            if close_match:
                buffer.append(text[: close_match.start()])
                block = "\n".join(buffer).strip()
                if block:
                    blocks.append(block)
                buffer = []
                text = text[close_match.end() :]
                in_block = False
            else:
                buffer.append(text)
                break
    return blocks


def _extract_inline_tags(lines: Sequence[str], tag: str) -> List[Dict[str, str]]:
    pattern = re.compile(rf"<{tag}\b([^>]*)>(.*?)</{tag}>", re.IGNORECASE)
    name_pattern = re.compile(r'name\s*=\s*"([^"]+)"|name\s*=\s*\'([^\']+)\'', re.IGNORECASE)
    items: List[Dict[str, str]] = []
    for line in lines:
        for match in pattern.finditer(str(line or "")):
            attrs = str(match.group(1) or "")
            name_match = name_pattern.search(attrs)
            name = ""
            if name_match:
                name = str(name_match.group(1) or name_match.group(2) or "").strip()
            text = _clean_doc_text(match.group(2) or "")
            if name or text:
                item = {"description": text}
                if name:
                    item["name"] = name
                items.append(item)
    return items


def _doc_comment(lines: Sequence[str]) -> Dict[str, Any]:
    cleaned_lines = _doc_lines(lines)
    summary_blocks = [_clean_doc_text(block) for block in _extract_tag_blocks(cleaned_lines, "summary")]
    return_blocks = [_clean_doc_text(block) for block in _extract_tag_blocks(cleaned_lines, "returns")]

    summary = " ".join(block for block in summary_blocks if block).strip()
    if not summary:
        summary = _clean_summary(lines)
    doc: Dict[str, Any] = {"summary": summary}
    params = _extract_inline_tags(cleaned_lines, "param")
    if params:
        doc["parameters"] = params
    returns = " ".join(block for block in return_blocks if block).strip()
    if returns:
        doc["returns"] = returns
    return doc


def _index_cpp_implementations(raw_root: Path) -> Dict[Tuple[str, str], List[Dict[str, str]]]:
    index: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    for cpp_path in sorted(raw_root.rglob("*.cpp")):
        try:
            lines = _read_source_text(cpp_path).splitlines()
        except Exception:
            continue
        source_path = _source_path(raw_root, cpp_path)
        for line_number, line in enumerate(lines, 1):
            match = _IMPLEMENTATION_RE.search(line)
            if not match:
                continue
            key = (str(match.group("class") or "").strip(), str(match.group("method") or "").strip())
            if not key[0] or not key[1]:
                continue
            index.setdefault(key, []).append(
                {
                    "path": source_path,
                    "line_range": f"{line_number}-{line_number}",
                }
            )
    return index


def _should_skip_statement(statement: str) -> bool:
    lowered = str(statement or "").strip().lower()
    if not lowered:
        return True
    if lowered.startswith(("private:", "protected:", "internal:")):
        return True
    if lowered.startswith("property "):
        return False
    if "(" not in lowered or not lowered.endswith(";"):
        return True
    if any(lowered.startswith(prefix) for prefix in _SKIP_DECLARATION_PREFIXES):
        return True
    if "operator" in lowered:
        return True
    return False


def _build_record(
    *,
    raw_root: Path,
    header_path: Path,
    declaration_line: int,
    namespace_parts: Sequence[str],
    class_name: str,
    statement: str,
    summary_lines: Sequence[str],
    impl_index: Dict[Tuple[str, str], List[Dict[str, str]]],
) -> Optional[Dict[str, Any]]:
    normalized_statement = re.sub(r"\s+", " ", statement).strip()
    if _should_skip_statement(normalized_statement):
        return None

    member_name = ""
    declaration_text = normalized_statement
    property_match = _PROPERTY_RE.match(normalized_statement)
    if property_match:
        member_name = str(property_match.group("name") or "").strip()
    else:
        ctor_re = re.compile(_CTOR_RE_TEMPLATE.format(name=re.escape(class_name)))
        ctor_match = ctor_re.match(normalized_statement)
        if ctor_match:
            member_name = str(ctor_match.group("name") or "").strip()
        else:
            method_match = _METHOD_RE.match(normalized_statement)
            if not method_match:
                return None
            member_name = str(method_match.group("name") or "").strip()
    if not member_name:
        return None

    qualified_type = ".".join([*namespace_parts, class_name])
    qualified_symbol = f"{qualified_type}.{member_name}"
    header_source = _source_path(raw_root, header_path)
    doc = _doc_comment(summary_lines)
    description = str(doc.get("summary") or "").strip()
    source_refs = [
        {
            "path": header_source,
            "line_range": f"{declaration_line}-{declaration_line}",
        }
    ]
    for item in impl_index.get((class_name, member_name), [])[:6]:
        source_refs.append(item)

    text_lines = [f"## {member_name}"]
    if description:
        text_lines.append(f"- Description: {description}")
    text_lines.append(f"- Declaration: `{header_source}:{declaration_line}`")
    impl_refs = [item for item in source_refs[1:]]
    if impl_refs:
        impl_text = ", ".join(f"`{item['path']}:{item['line_range'].split('-', 1)[0]}`" for item in impl_refs)
        text_lines.append(f"- Implementation: {impl_text}")

    return {
        "qualified_type": qualified_type,
        "type_name": class_name,
        "member_name": member_name,
        "qualified_symbol": qualified_symbol,
        "doc_path": header_source,
        "heading_path": f"{qualified_type} Methods > {member_name}",
        "text": "\n".join(text_lines),
        "source_refs": source_refs,
        "declaration": declaration_text,
        "doc": doc,
        "owner": {
            "namespace": ".".join(namespace_parts),
            "qualified_type": qualified_type,
            "type_name": class_name,
        },
    }


def _extract_header_method_records(
    *,
    raw_root: Path,
    header_path: Path,
    impl_index: Dict[Tuple[str, str], List[Dict[str, str]]],
) -> List[Dict[str, Any]]:
    try:
        lines = _read_source_text(header_path).splitlines()
    except Exception:
        return []

    records: List[Dict[str, Any]] = []
    namespace_stack: List[Tuple[str, int]] = []
    class_stack: List[Dict[str, Any]] = []
    pending: List[Tuple[str, str, List[str]]] = []
    pending_summary: List[str] = []
    brace_depth = 0
    statement_lines: List[str] = []
    statement_summary: List[str] = []
    statement_start_line = 0
    in_block_comment = False

    def current_namespace() -> List[str]:
        return [item[0] for item in namespace_stack]

    def current_class() -> Optional[Dict[str, Any]]:
        return class_stack[-1] if class_stack else None

    def flush_statement() -> None:
        nonlocal statement_lines, statement_summary, statement_start_line
        if not statement_lines:
            return
        active_class = current_class()
        if active_class and active_class.get("access") == "public":
            record = _build_record(
                raw_root=raw_root,
                header_path=header_path,
                declaration_line=statement_start_line or 1,
                namespace_parts=current_namespace(),
                class_name=str(active_class.get("name") or "").strip(),
                statement=" ".join(statement_lines),
                summary_lines=statement_summary,
                impl_index=impl_index,
            )
            if record:
                records.append(record)
        statement_lines = []
        statement_summary = []
        statement_start_line = 0

    for line_number, raw_line in enumerate(lines, 1):
        if in_block_comment:
            if "*/" not in raw_line:
                continue
            raw_line = raw_line.split("*/", 1)[1]
            in_block_comment = False
        if "/*" in raw_line:
            before, after = raw_line.split("/*", 1)
            if "*/" in after:
                raw_line = before + after.split("*/", 1)[1]
            else:
                raw_line = before
                in_block_comment = True
        stripped = str(raw_line or "").strip()

        if stripped.startswith("///"):
            pending_summary.append(stripped)
            continue

        active_class = current_class()
        access_match = _ACCESS_RE.match(stripped)
        if access_match and active_class:
            active_class["access"] = str(access_match.group(1) or "private").lower()
            pending_summary = []
            continue

        namespace_match = _NAMESPACE_DECL_RE.match(stripped)
        if namespace_match:
            pending.append(("namespace", str(namespace_match.group(1) or "").strip(), []))

        class_match = _CLASS_DECL_RE.match(stripped)
        if class_match:
            pending.append(("class", str(class_match.group(1) or "").strip(), list(pending_summary)))
            pending_summary = []

        if active_class and active_class.get("access") == "public":
            if statement_lines:
                statement_lines.append(stripped)
                if ";" in stripped:
                    flush_statement()
            else:
                if "(" in stripped and not stripped.startswith("//") and not stripped.startswith("["):
                    statement_lines = [stripped]
                    statement_summary = list(pending_summary)
                    statement_start_line = line_number
                    pending_summary = []
                    if ";" in stripped:
                        flush_statement()
        elif stripped and not stripped.startswith("//") and not stripped.startswith("["):
            pending_summary = []

        local_depth = brace_depth
        for char in raw_line:
            if char == "{":
                local_depth += 1
                if pending:
                    kind, name, summary_lines = pending.pop(0)
                    if kind == "namespace" and name:
                        namespace_stack.append((name, local_depth))
                    elif kind == "class" and name:
                        class_stack.append(
                            {
                                "name": name,
                                "depth": local_depth,
                                "access": "private",
                                "summary": summary_lines,
                            }
                        )
            elif char == "}":
                local_depth -= 1
                while class_stack and int(class_stack[-1].get("depth") or 0) > local_depth:
                    class_stack.pop()
                while namespace_stack and namespace_stack[-1][1] > local_depth:
                    namespace_stack.pop()
        brace_depth = local_depth

    flush_statement()
    return records


def build_methods_index_from_raw_source(raw_root: Path) -> List[Dict[str, Any]]:
    root = Path(raw_root)
    if not root.exists() or not root.is_dir():
        return []

    impl_index = _index_cpp_implementations(root)
    records: List[Dict[str, Any]] = []
    for header_path in sorted(root.rglob("*.h")):
        records.extend(
            _extract_header_method_records(
                raw_root=root,
                header_path=header_path,
                impl_index=impl_index,
            )
        )

    records.sort(
        key=lambda item: (
            str(item.get("qualified_symbol") or ""),
            str(item.get("heading_path") or ""),
        )
    )
    return records
