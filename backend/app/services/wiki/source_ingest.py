import json
import time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Sequence

from .methods_index import METHODS_INDEX_RELATIVE_PATH

SOURCE_MANIFEST_RELATIVE_PATH = ".runtime/source_manifest.json"
_SOURCE_EXTENSIONS = {".h", ".hpp", ".cpp", ".cxx", ".cc", ".cs"}
_SKIP_MODULE_NAMES = {"vc143", "__pycache__"}
_GENERATED_BLOCK_START = "<!-- GENERATED:RUNTIME_STATUS:START -->"
_GENERATED_BLOCK_END = "<!-- GENERATED:RUNTIME_STATUS:END -->"


def source_manifest_file_for_root(root: Path) -> Path:
    return root / PurePosixPath(SOURCE_MANIFEST_RELATIVE_PATH).as_posix()


def load_source_manifest_for_root(root: Path) -> Dict[str, Any]:
    path = source_manifest_file_for_root(root)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_source_manifest_from_raw_source(
    raw_root: Path,
    methods_index: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    root = Path(raw_root)
    modules: List[Dict[str, Any]] = []
    if not root.exists() or not root.is_dir():
        return {"generated_at": "", "raw_root": root.as_posix(), "modules": modules}

    method_records_by_module: Dict[str, List[Dict[str, Any]]] = {}
    for record in methods_index or []:
        source_refs = record.get("source_refs") if isinstance(record.get("source_refs"), list) else []
        if not source_refs:
            continue
        first_path = str(source_refs[0].get("path") or "").strip()
        if not first_path.startswith("Source/"):
            continue
        parts = first_path.split("/")
        if len(parts) < 2:
            continue
        method_records_by_module.setdefault(parts[1], []).append(record)

    for module_dir in sorted(child for child in root.iterdir() if child.is_dir() and child.name not in _SKIP_MODULE_NAMES):
        source_files = [
            file_path
            for file_path in sorted(module_dir.rglob("*"))
            if file_path.is_file() and file_path.suffix.lower() in _SOURCE_EXTENSIONS
        ]
        if not source_files:
            continue

        method_records = method_records_by_module.get(module_dir.name, [])
        unique_types = sorted(
            {
                str(record.get("qualified_type") or "").strip()
                for record in method_records
                if str(record.get("qualified_type") or "").strip()
            }
        )
        updated_ts = max(file_path.stat().st_mtime for file_path in source_files)
        modules.append(
            {
                "module": module_dir.name,
                "relative_path": module_dir.relative_to(root).as_posix(),
                "file_count": len(source_files),
                "header_count": sum(1 for file_path in source_files if file_path.suffix.lower() in {".h", ".hpp"}),
                "implementation_count": sum(1 for file_path in source_files if file_path.suffix.lower() in {".cpp", ".cxx", ".cc", ".cs"}),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(updated_ts)),
                "source_paths": [f"Source/{file_path.relative_to(root).as_posix()}" for file_path in source_files],
                "type_count": len(unique_types),
                "method_count": len(method_records),
                "sample_types": unique_types[:12],
                "sample_symbols": [
                    str(record.get("qualified_symbol") or "").strip()
                    for record in method_records[:12]
                    if str(record.get("qualified_symbol") or "").strip()
                ],
            }
        )

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_root": root.as_posix(),
        "methods_index_path": METHODS_INDEX_RELATIVE_PATH,
        "module_count": len(modules),
        "modules": modules,
    }


def source_page_path_for_module(module_name: str) -> str:
    return f"pages/sources/{str(module_name or '').strip().lower()}.md"


def render_source_page(module_entry: Dict[str, Any], *, raw_root_text: str) -> str:
    module = str(module_entry.get("module") or "").strip()
    source_paths = [str(item or "").strip() for item in module_entry.get("source_paths") or [] if str(item or "").strip()]
    sample_types = [str(item or "").strip() for item in module_entry.get("sample_types") or [] if str(item or "").strip()]
    sample_symbols = [str(item or "").strip() for item in module_entry.get("sample_symbols") or [] if str(item or "").strip()]
    lines = [
        "---",
        f"title: Source Module | {module}",
        f"description: Auto-generated summary for raw source module `{module}`.",
        "tags:",
        "  - source",
        "  - generated",
        f"  - {module.lower()}",
        "sources:",
        "  - pages/sources/raw-source-root.md",
        "---",
        "",
        f"# Source Module | {module}",
        "",
        "## Overview",
        f"- Raw source root: `{raw_root_text}`",
        f"- Module path: `Source/{module}`",
        f"- File count: `{module_entry.get('file_count')}`",
        f"- Header count: `{module_entry.get('header_count')}`",
        f"- Implementation count: `{module_entry.get('implementation_count')}`",
        f"- Type count: `{module_entry.get('type_count')}`",
        f"- Method count: `{module_entry.get('method_count')}`",
        f"- Last source update: `{module_entry.get('updated_at')}`",
    ]
    if sample_types:
        lines.extend(["", "## Sample Types"])
        lines.extend([f"- `{item}`" for item in sample_types])
    if sample_symbols:
        lines.extend(["", "## Sample Symbols"])
        lines.extend([f"- `{item}`" for item in sample_symbols])
    if source_paths:
        lines.extend(["", "## Source Files"])
        lines.extend([f"- `{item}`" for item in source_paths[:40]])
        if len(source_paths) > 40:
            lines.append(f"- ... `{len(source_paths) - 40}` more")
    return "\n".join(lines) + "\n"


def build_workflow_runtime_status_block(
    *,
    linked_modules: Iterable[str],
    resolved_required_count: int,
    total_required_count: int,
    missing_required_symbols: Sequence[str],
    source_manifest_generated_at: str,
) -> str:
    modules = [str(item or "").strip() for item in linked_modules if str(item or "").strip()]
    missing = [str(item or "").strip() for item in missing_required_symbols if str(item or "").strip()]
    lines = [
        _GENERATED_BLOCK_START,
        "## Runtime Ingest Status",
        f"- Auto-generated from raw source ingest at `{source_manifest_generated_at}`.",
        f"- Resolved required symbols: `{resolved_required_count}/{total_required_count}`",
    ]
    if modules:
        lines.append("- Linked modules:")
        lines.extend([f"  - `{module}`" for module in modules[:12]])
    if missing:
        lines.append("- Missing required symbols:")
        lines.extend([f"  - `{symbol}`" for symbol in missing[:16]])
    else:
        lines.append("- Missing required symbols: `0`")
    lines.append(_GENERATED_BLOCK_END)
    return "\n".join(lines)


def upsert_workflow_runtime_status(content: str, block: str) -> str:
    text = str(content or "")
    start = text.find(_GENERATED_BLOCK_START)
    end = text.find(_GENERATED_BLOCK_END)
    replacement = f"{block}\n"
    if start >= 0 and end > start:
        end += len(_GENERATED_BLOCK_END)
        updated = text[:start].rstrip() + "\n\n" + replacement + text[end:].lstrip("\n")
        return updated

    marker = "## Required Facts"
    index = text.find(marker)
    if index >= 0:
        prefix = text[:index].rstrip()
        suffix = text[index:].lstrip("\n")
        return f"{prefix}\n\n{replacement}\n{suffix}"
    return f"{text.rstrip()}\n\n{replacement}"
