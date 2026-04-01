import logging
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from ..retrieval.query_rewrite import build_query_rewrite
from ...core.policy import SecurityPolicy
from .access import register_code_search, register_listed_files
from .codebase import extract_symbol_query_candidates
from .support import clamp_int, decode_file, is_safe_regex, is_subpath, parse_query_or_regex


logger = logging.getLogger(__name__)


def iter_code_query_variants(query: str, max_candidates: int = 4) -> List[Dict[str, Any]]:
    variants: List[Dict[str, Any]] = []
    seen = set()
    for candidate in build_query_rewrite(query, max_candidates=max_candidates).candidates:
        variant_query = str(candidate.query or "").strip()
        if not variant_query or variant_query in seen:
            continue
        seen.add(variant_query)
        variants.append(
            {
                "query": variant_query,
                "strategy": str(candidate.strategy or "original"),
                "reason": str(candidate.reason or ""),
                "is_original": bool(candidate.is_original),
            }
        )
    if not variants:
        variants.append(
            {
                "query": str(query or "").strip(),
                "strategy": "original",
                "reason": "preserve_user_input",
                "is_original": True,
            }
        )
    return variants


def dedupe_code_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for row in rows:
        key = (
            str(row.get("path") or ""),
            str(row.get("line_range") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def iter_code_roots(code_tools) -> List[Path]:
    return [Path(root) for root in getattr(code_tools, "configured_roots", []) if Path(root).exists()]


def normalize_repo_glob(glob: str) -> Tuple[str, bool]:
    raw = str(glob or "**/*").strip().replace("\\", "/") or "**/*"
    if re.match(r"^[A-Za-z]:", raw) or raw.startswith("/"):
        return raw, False
    parts = PurePosixPath(raw).parts
    if any(part in {"..", ""} for part in parts):
        return raw, False
    return raw, True


def resolve_code_root(code_tools, module_name: str) -> Optional[Path]:
    name = (module_name or "").strip().strip("/")
    if not name:
        return None

    for root in getattr(code_tools, "configured_roots", []):
        candidate = Path(root) / name
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def resolve_path_root(code_tools, path_value: str) -> Optional[tuple[Path, Path, str]]:
    raw = str(path_value or "").strip()
    if not raw:
        return None

    roots = [Path(root) for root in getattr(code_tools, "configured_roots", []) if Path(root).exists()]
    candidate_path = Path(raw)

    if candidate_path.is_absolute():
        resolved = candidate_path.resolve()
        for root in roots:
            try:
                rel = resolved.relative_to(root).as_posix()
                if resolved.exists() and resolved.is_file():
                    return root, resolved, rel
            except Exception:
                continue
        return None

    normalized_rel = raw.replace("\\", "/")
    for root in roots:
        resolved = (root / normalized_rel).resolve()
        if resolved.exists() and resolved.is_file() and is_subpath(resolved, root):
            try:
                rel = resolved.relative_to(root).as_posix()
            except Exception:
                rel = normalized_rel
            return root, resolved, rel
    return None


def relativize_code_path(code_tools, path_value: str) -> str:
    raw = str(path_value or "").strip()
    if not raw:
        return ""
    candidate_path = Path(raw)
    if not candidate_path.is_absolute():
        return raw.replace("\\", "/")

    resolved = candidate_path.resolve()
    for root in [Path(root) for root in getattr(code_tools, "configured_roots", []) if Path(root).exists()]:
        try:
            return resolved.relative_to(root).as_posix()
        except Exception:
            continue
    return candidate_path.name


def code_tool_results_to_rows(
    results: Sequence[Dict[str, Any]],
    code_tools,
    path_filter: Optional[str],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    filter_norm = (path_filter or "").strip().replace("\\", "/")

    for item in results or []:
        payload = item.get("payload", {}) if isinstance(item, dict) else {}
        file_path = payload.get("source_file") or payload.get("file_path") or ""
        path_str = str(file_path).replace("\\", "/")
        if Path(path_str).is_absolute():
            path_str = relativize_code_path(code_tools, path_str)
        if filter_norm and filter_norm not in path_str:
            continue

        line_start = payload.get("line_start") or 1
        line_end = payload.get("line_end") or line_start
        row: Dict[str, Any] = {"path": path_str, "line_range": f"{line_start}-{line_end}", "match": payload.get("text", "")}
        if payload.get("match_kind"):
            row["match_kind"] = payload.get("match_kind")
        if payload.get("symbol"):
            row["symbol"] = payload.get("symbol")
        rows.append(row)

    return rows


async def register_code_rows(
    redis,
    session_id: Optional[str],
    rows: Sequence[Dict[str, Any]],
) -> None:
    await register_code_search(redis, session_id, rows)


def run_rg(code_tools, pattern: str, roots: Sequence[Path], path_filter: Optional[str], limit: int, rg_logger) -> List[Dict[str, Any]]:
    if not getattr(code_tools, "rg_bin", None):
        return []

    try:
        rows: List[Dict[str, Any]] = []
        filter_norm = (path_filter or "").strip().replace("\\", "/")
        max_rows = clamp_int(limit, 1, 100)

        for search_root in roots:
            cmd = [
                code_tools.rg_bin,
                "--line-number",
                "--no-heading",
                "--color",
                "never",
                "--smart-case",
                pattern,
            ]
            for g in config.CODE_SEARCH_EXCLUDE_GLOBS:
                cmd.extend(["-g", g])
            cmd.append(str(search_root))

            try:
                raw_out = subprocess.check_output(
                    cmd,
                    timeout=max(2, config.CODE_SEARCH_TIMEOUT_SEC),
                    stderr=subprocess.DEVNULL,
                )
                out = raw_out.decode("utf-8", errors="replace")
            except subprocess.CalledProcessError as exc:
                if exc.returncode == 1:
                    continue
                rg_logger.warning("rg exited with non-match error", extra={"return_code": exc.returncode})
                continue
            except Exception as exc:
                rg_logger.warning("rg execution failed", extra={"error": str(exc)[:240]})
                continue

            for raw in out.splitlines():
                parts = raw.split(":", 2)
                if len(parts) != 3:
                    continue
                p, line_s, text = parts
                if not line_s.isdigit():
                    continue
                abs_path = Path(p)
                if not abs_path.exists() or not abs_path.is_file():
                    continue

                rel_path = relativize_code_path(code_tools, str(abs_path))
                if filter_norm and filter_norm not in rel_path:
                    continue

                line_no = int(line_s)
                rows.append(
                    {
                        "path": rel_path,
                        "line_range": f"{line_no}-{line_no}",
                        "match": text,
                    }
                )
                if len(rows) >= max_rows:
                    return rows
    except Exception as exc:
        rg_logger.warning("rg multi-root execution failed", extra={"error": str(exc)[:240]})
        return []

    return rows


def run_symbol_lookup(
    code_tools,
    *,
    symbol: str,
    limit: int,
    language_filter: Optional[str],
    path_filter: Optional[str],
) -> Tuple[List[Dict[str, Any]], float] | None:
    finder = getattr(code_tools, "find_symbol", None)
    if not callable(finder):
        return None

    try:
        result = finder(
            symbol=symbol,
            top_k=limit,
            repo_filter=None,
            language_filter=language_filter,
            path_filter=path_filter,
        )
    except Exception:
        return None

    if not (isinstance(result, tuple) and len(result) == 2):
        return None

    rows, elapsed_ms = result
    if not isinstance(rows, list):
        return None
    return rows, float(elapsed_ms or 0.0)


async def list_repo_files(
    redis, code_tools, glob: str, limit: int, session_id: Optional[str] = None
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"files": [], "truncated": False, "reason": gate["reason"]}
    if code_tools is None:
        return {"files": [], "truncated": False, "reason": "code_tools_unavailable"}

    pattern, is_safe_pattern = normalize_repo_glob(glob)
    if not is_safe_pattern:
        return {"files": [], "truncated": False, "reason": "invalid_glob"}
    max_items = clamp_int(limit, 1, 500)
    files = []
    truncated = False

    search_roots = iter_code_roots(code_tools)
    for root in search_roots:
        try:
            candidates = root.glob(pattern)
        except Exception:
            return {"files": [], "truncated": False, "reason": "invalid_glob"}

        for file_path in candidates:
            if file_path.is_dir():
                continue
            try:
                resolved_path = file_path.resolve()
            except Exception:
                continue
            if not is_subpath(resolved_path, root.resolve()):
                continue
            rel = relativize_code_path(code_tools, str(file_path))
            files.append({"path": rel, "size_bytes": file_path.stat().st_size, "language": "text"})
            if len(files) >= max_items:
                truncated = True
                break
        if truncated:
            break

    await register_listed_files(redis, session_id, files)
    return {"files": files, "truncated": truncated}


def read_code_lines(
    code_tools,
    path: str,
    start_line: int,
    end_line: int,
    max_line_span: int = 500,
    max_chars: int = 12000,
) -> Dict[str, Any]:
    resolved = resolve_path_root(code_tools, path)
    if resolved is None:
        return {"path": path, "found": False, "reason": "path_not_found"}
    repo_root, target, normalized_path = resolved

    line_start = max(1, int(start_line))
    line_end = max(line_start, int(end_line))
    line_end = min(line_end, line_start + clamp_int(max_line_span, 1, 500))

    lines = decode_file(target.read_bytes()).splitlines()
    if not lines:
        return {"path": normalized_path, "found": True, "line_range": f"{line_start}-{line_start}", "content": "", "truncated": False}

    bounded_end = min(len(lines), line_end)
    window = lines[line_start - 1 : bounded_end]
    content = "\n".join(window)
    truncated_chars = False
    if len(content) > clamp_int(max_chars, 500, 12000):
        content = content[: clamp_int(max_chars, 500, 12000)]
        truncated_chars = True

    return {
        "path": normalized_path,
        "found": True,
        "line_range": f"{line_start}-{bounded_end}",
        "content": content,
        "truncated": truncated_chars or bounded_end < line_end,
    }


async def search_code(
    redis,
    code_tools,
    query_or_regex: str,
    path_filter: Optional[str],
    limit: int,
    session_id: Optional[str] = None,
    logger=None,
) -> Dict[str, Any]:
    active_logger = logger or globals()["logger"]
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"matches": [], "reason": gate["reason"]}

    q, is_regex = parse_query_or_regex(query_or_regex)
    q = q.strip()
    if not q:
        return {"matches": [], "reason": "empty_query", "is_regex": is_regex}
    if code_tools is None:
        return {
            "query": q,
            "is_regex": is_regex,
            "matches": [],
            "truncated": False,
            "reason": "code_tools_unavailable",
        }

    max_rows = clamp_int(limit, 1, 100)
    search_roots = iter_code_roots(code_tools)
    if is_regex:
        if not is_safe_regex(q):
            return {"query": q, "is_regex": True, "matches": [], "truncated": False, "reason": "unsafe_regex"}
        rows = run_rg(code_tools, q, search_roots, path_filter, max_rows, active_logger)
        await register_code_rows(redis, session_id, rows)
        return {"query": q, "is_regex": True, "matches": rows, "truncated": len(rows) >= max_rows, "scope": "all"}

    rows: List[Dict[str, Any]] = []
    variant_log: List[Dict[str, Any]] = []
    symbol_lookup_log: List[Dict[str, Any]] = []
    min_variant_hits = min(max_rows, 3)
    for symbol in extract_symbol_query_candidates(q, max_candidates=2):
        symbol_lookup = run_symbol_lookup(
            code_tools,
            symbol=symbol,
            limit=min(max_rows, 4),
            language_filter=None,
            path_filter=path_filter,
        )
        if symbol_lookup is None:
            continue
        symbol_results, _ = symbol_lookup
        symbol_rows = code_tool_results_to_rows(symbol_results, code_tools, path_filter)
        if not symbol_rows:
            continue
        symbol_lookup_log.append({"symbol": symbol, "match_count": len(symbol_rows)})
        rows = dedupe_code_rows([*rows, *symbol_rows])[:max_rows]
        if len(rows) >= max_rows:
            break

    for candidate in iter_code_query_variants(q):
        results, _ = code_tools.search(query=candidate["query"], top_k=max_rows, repo_filter=None)
        variant_rows = code_tool_results_to_rows(results, code_tools, path_filter)[:max_rows]
        variant_log.append(
            {
                "query": candidate["query"],
                "strategy": candidate["strategy"],
                "reason": candidate["reason"],
                "match_count": len(variant_rows),
            }
        )
        rows = dedupe_code_rows([*rows, *variant_rows])
        if len(rows) >= max_rows:
            break
        if rows and (len(rows) >= min_variant_hits or not candidate["is_original"]):
            break

    rows = rows[:max_rows]
    await register_code_rows(redis, session_id, rows)
    response = {
        "query": q,
        "is_regex": False,
        "matches": rows,
        "truncated": len(rows) >= max_rows,
        "scope": "all",
    }
    if symbol_lookup_log:
        response["symbol_lookups"] = symbol_lookup_log
    if len(variant_log) > 1:
        response["query_variants"] = variant_log
    return response


async def find_symbol(
    redis,
    code_tools,
    symbol: str,
    limit: int,
    session_id: Optional[str] = None,
    language_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"symbol": symbol, "matches": [], "reason": gate["reason"]}

    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return {"symbol": normalized_symbol, "matches": [], "reason": "empty_symbol"}

    symbol_lookup = run_symbol_lookup(
        code_tools,
        symbol=normalized_symbol,
        limit=clamp_int(limit, 1, 50),
        language_filter=language_filter,
        path_filter=path_filter,
    )
    if symbol_lookup is None:
        return {"symbol": normalized_symbol, "matches": [], "reason": "symbol_lookup_unavailable"}

    results, _ = symbol_lookup
    rows = code_tool_results_to_rows(results, code_tools, path_filter)
    rows = dedupe_code_rows(rows)[: clamp_int(limit, 1, 50)]
    await register_code_rows(redis, session_id, rows)
    return {"symbol": normalized_symbol, "matches": rows, "truncated": len(rows) >= clamp_int(limit, 1, 50)}
