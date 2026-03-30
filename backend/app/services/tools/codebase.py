import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ... import config, rag_config
from ...utils.encoding import TEXT_ENCODING_FALLBACKS, decode_bytes
from ...utils.file_indexing import language_from_name
from .query_terms import compact_token as _compact_token
from .query_terms import extract_query_terms as _extract_query_terms
from .query_terms import extract_query_score_tokens as _query_score_tokens
from .query_terms import extract_symbol_query_candidates
_DEFINITION_SCORE_DEFAULTS = {
    "type_declaration": 8.5,
    "function_declaration": 8.0,
    "callable_signature": 5.5,
    "fallback": 4.0,
    "type_keyword_bonus": 2.5,
    "modifier_bonus": 1.5,
    "new_expression_penalty": 4.0,
    "member_call_penalty": 4.5,
    "assignment_penalty": 1.0,
    "brace_bonus": 0.5,
    "stem_bonus": 1.5,
    "long_line_threshold": 220,
    "long_line_penalty": 0.5,
}
_SEARCH_HIT_SCORE_DEFAULTS = {
    "base": 1.0,
    "query_exact_hit": 2.0,
    "query_token_hit": 0.75,
    "path_token_hit": 0.5,
    "call_bonus": 0.2,
    "declaration_bonus": 0.3,
    "symbol_definition_bonus": 1.2,
    "token_hit_cap": 4,
    "path_hit_cap": 3,
    "long_line_threshold": 160,
    "long_line_penalty": 0.1,
}


def _strip_companion_suffixes(stem: str) -> str:
    normalized = str(stem or "").strip()
    lowered = normalized.lower()
    for suffix in (".generated", ".gen", ".g.i", ".g"):
        if lowered.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            lowered = normalized.lower()
    return normalized

@dataclass
class CodeHit:
    path: Path
    root: Path
    line: int
    text: str
    score: float
    kind: str = "search"


class CodeToolService:
    def __init__(
        self,
        roots: List[str],
        max_results: int = 8,
        context_lines: int = 8,
        max_file_bytes: int = 1_500_000,
    ):
        self.configured_roots = [Path(r) for r in roots if r.strip()]
        self.max_results = max(1, max_results)
        self.context_lines = max(2, context_lines)
        self.max_file_bytes = max(100_000, max_file_bytes)
        self.rg_bin = shutil.which("rg")

    def status(self) -> Dict:
        existing = [str(p) for p in self.configured_roots if p.exists() and p.is_dir()]
        missing = [str(p) for p in self.configured_roots if not p.exists() or not p.is_dir()]
        version = ""
        if self.rg_bin:
            try:
                version = subprocess.check_output([self.rg_bin, "--version"], text=True, timeout=2).splitlines()[0].strip()
            except Exception:
                version = "unavailable"
        return {
            "enabled": config.CODE_TOOL_ENABLED,
            "rg_available": bool(self.rg_bin),
            "rg_version": version,
            "roots_configured": [str(p) for p in self.configured_roots],
            "roots_available": existing,
            "roots_missing": missing,
            "max_results": self.max_results,
            "context_lines": self.context_lines,
            "max_file_bytes": self.max_file_bytes,
        }

    def search(
        self,
        query: str,
        top_k: int = 8,
        repo_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
    ) -> Tuple[List[Dict], float]:
        started = time.perf_counter()
        if not self.rg_bin:
            return [], 0.0

        search_paths = self._resolve_search_paths(repo_filter)
        if not search_paths:
            return [], 0.0

        pattern = self._build_pattern(query)
        if not pattern:
            return [], 0.0

        definition_hits = self._find_symbol_definition_hits(
            query=query,
            search_paths=search_paths,
            max_hits=max(top_k * 4, 24),
        )
        hits = self._grep(pattern, search_paths, max_hits=max(top_k * 8, 60), query_text=query)
        hits = self._filter_hits(
            self._merge_hits(definition_hits, hits),
            language_filter=language_filter,
        )

        ranked = hits[: max(top_k * 3, self.max_results)]
        results: List[Dict] = []
        for idx, hit in enumerate(ranked):
            payload = self._build_payload(hit, repo_filter)
            if not payload:
                continue
            results.append(
                {
                    "id": f"code:{payload['file_path']}:{payload['line_start']}",
                    "payload": payload,
                    "dense_score": 0.0,
                    "sparse_score": hit.score,
                    "combined_score": max(0.01, hit.score - idx * 0.01),
                }
            )
            if len(results) >= min(top_k, self.max_results):
                break

        elapsed_ms = (time.perf_counter() - started) * 1000
        return results, elapsed_ms

    def find_symbol(
        self,
        symbol: str,
        top_k: int = 8,
        repo_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        path_filter: Optional[str] = None,
    ) -> Tuple[List[Dict], float]:
        started = time.perf_counter()
        if not self.rg_bin:
            return [], 0.0

        search_paths = self._resolve_search_paths(repo_filter)
        if not search_paths:
            return [], 0.0

        normalized_symbol = str(symbol or "").strip()
        if not normalized_symbol:
            return [], 0.0

        hits = self._collect_definition_hits(
            symbol=normalized_symbol,
            search_paths=search_paths,
            max_hits=max(top_k * 6, 24),
        )
        hits = self._filter_hits(hits, language_filter=language_filter, path_filter=path_filter)

        results: List[Dict] = []
        for idx, hit in enumerate(hits[: min(max(top_k, 1), self.max_results)]):
            payload = self._build_payload(hit, repo_filter)
            if not payload:
                continue
            payload["match_kind"] = "symbol_definition"
            payload["symbol"] = normalized_symbol
            results.append(
                {
                    "id": f"symbol:{normalized_symbol}:{payload['file_path']}:{payload['line_start']}",
                    "payload": payload,
                    "dense_score": 0.0,
                    "sparse_score": hit.score,
                    "combined_score": max(0.01, hit.score - idx * 0.01),
                }
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        return results, elapsed_ms

    def _resolve_search_paths(self, repo_filter: Optional[str]) -> List[Tuple[Path, Path]]:
        roots = [p for p in self.configured_roots if p.exists() and p.is_dir()]
        if not roots:
            return []

        paths: List[Tuple[Path, Path]] = []
        repo_name = (repo_filter or "").strip()
        if repo_name:
            for root in roots:
                candidate = root / repo_name
                if candidate.exists() and candidate.is_dir():
                    paths.append((root, candidate))
            return paths

        for root in roots:
            paths.append((root, root))
        return paths

    def _build_pattern(self, query: str) -> str:
        text = (query or "").strip()
        if not text:
            return ""
        tokens: List[str] = []
        tokens.extend(_extract_query_terms(text, limit=8))
        tokens.extend(extract_symbol_query_candidates(text, max_candidates=3))

        unique_tokens: List[str] = []
        seen = set()
        for token in tokens:
            candidate = str(token or "").strip()
            compact = _compact_token(candidate)
            if len(compact) < 2 or compact in seen:
                continue
            seen.add(compact)
            unique_tokens.append(candidate)

        escaped = [re.escape(token) for token in sorted(unique_tokens, key=lambda value: (-len(value), value.lower()))[:6]]
        if not escaped:
            return ""
        return "|".join(escaped)

    def _definition_patterns(self, symbol: str) -> List[Tuple[str, str]]:
        escaped = re.escape(str(symbol or "").strip())
        if not escaped:
            return []
        return [
            ("type_declaration", rf"\b(?:class|struct|interface|enum|record|typedef|using)\s+{escaped}\b"),
            ("function_declaration", rf"\b(?:def|function)\s+{escaped}\s*\("),
            ("callable_signature", rf"\b{escaped}\s*\("),
        ]

    def _find_symbol_definition_hits(
        self,
        query: str,
        search_paths: List[Tuple[Path, Path]],
        max_hits: int,
    ) -> List[CodeHit]:
        merged: List[CodeHit] = []
        for symbol in extract_symbol_query_candidates(query, max_candidates=2):
            merged = self._merge_hits(
                merged,
                self._collect_definition_hits(symbol=symbol, search_paths=search_paths, max_hits=max_hits),
            )
            if len(merged) >= max_hits:
                break
        return merged

    def _collect_definition_hits(
        self,
        symbol: str,
        search_paths: List[Tuple[Path, Path]],
        max_hits: int,
    ) -> List[CodeHit]:
        seen = set()
        hits: List[CodeHit] = []
        for pattern_kind, pattern in self._definition_patterns(symbol):
            pattern_hits = self._grep(
                pattern,
                search_paths,
                max_hits=max_hits,
                hit_kind="symbol_definition",
                query_text=symbol,
            )
            for hit in pattern_hits:
                key = (str(hit.path), hit.line)
                if key in seen:
                    continue
                score = self._definition_score(hit.text, symbol, hit.path, pattern_kind)
                if score <= 0.0:
                    continue
                seen.add(key)
                hits.append(
                    CodeHit(
                        path=hit.path,
                        root=hit.root,
                        line=hit.line,
                        text=hit.text,
                        score=score,
                        kind="symbol_definition",
                    )
                )
                if len(hits) >= max_hits:
                    break
            if len(hits) >= max_hits:
                break
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits

    def _definition_score(self, text: str, symbol: str, path: Path, pattern_kind: str) -> float:
        weights = rag_config.heuristics_weights("code_definition_score", _DEFINITION_SCORE_DEFAULTS)
        lowered = str(text or "").strip().lower()
        symbol_lower = str(symbol or "").strip().lower()
        score = {
            "type_declaration": float(weights["type_declaration"]),
            "function_declaration": float(weights["function_declaration"]),
            "callable_signature": float(weights["callable_signature"]),
        }.get(pattern_kind, float(weights["fallback"]))

        if any(keyword in lowered for keyword in ("class ", "struct ", "interface ", "enum ", "record ")):
            score += float(weights["type_keyword_bonus"])
        if any(keyword in lowered for keyword in ("public ", "private ", "protected ", "internal ", "static ", "virtual ", "override ", "async ")):
            score += float(weights["modifier_bonus"])
        if f"new {symbol_lower}" in lowered:
            score -= float(weights["new_expression_penalty"])
        if f".{symbol_lower}(" in lowered or f"->{symbol_lower}(" in lowered:
            score -= float(weights["member_call_penalty"])
        if "=" in lowered and f"{symbol_lower}(" not in lowered:
            score -= float(weights["assignment_penalty"])
        if "{" in lowered:
            score += float(weights["brace_bonus"])
        stem = _strip_companion_suffixes(path.stem).lower()
        if symbol_lower == stem or symbol_lower in stem:
            score += float(weights["stem_bonus"])
        if len(lowered) > int(weights["long_line_threshold"]):
            score -= float(weights["long_line_penalty"])
        return score

    def _merge_hits(self, primary: List[CodeHit], secondary: List[CodeHit]) -> List[CodeHit]:
        by_key: Dict[Tuple[str, int], CodeHit] = {}
        for hit in [*(primary or []), *(secondary or [])]:
            key = (str(hit.path), int(hit.line))
            existing = by_key.get(key)
            if existing is None or hit.score > existing.score:
                by_key[key] = hit
        return sorted(by_key.values(), key=lambda item: item.score, reverse=True)

    def _filter_hits(
        self,
        hits: List[CodeHit],
        language_filter: Optional[str] = None,
        path_filter: Optional[str] = None,
    ) -> List[CodeHit]:
        filtered = list(hits or [])
        if language_filter:
            needle = language_filter.strip().lower()
            filtered = [h for h in filtered if language_from_name(h.path.name).lower().startswith(needle)]
        if path_filter:
            needle = path_filter.strip().replace("\\", "/").lower()
            filtered = [h for h in filtered if needle in h.path.as_posix().lower()]
        return filtered

    def _grep(
        self,
        pattern: str,
        search_paths: List[Tuple[Path, Path]],
        max_hits: int = 80,
        hit_kind: str = "search",
        query_text: str = "",
    ) -> List[CodeHit]:
        cmd = [
            self.rg_bin,
            "--line-number",
            "--no-heading",
            "--color",
            "never",
            "--smart-case",
            "--max-columns",
            "220",
            "--max-columns-preview",
            pattern,
        ]
        for g in config.CODE_SEARCH_EXCLUDE_GLOBS:
            cmd.extend(["-g", g])
        cmd.extend([str(p) for _, p in search_paths])

        try:
            raw_out = subprocess.check_output(
                cmd,
                timeout=max(2, config.CODE_SEARCH_TIMEOUT_SEC),
                stderr=subprocess.DEVNULL,
            )
            out = raw_out.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as exc:
            # rg returns 1 when no match.
            if exc.returncode == 1:
                return []
            return []
        except Exception:
            return []

        root_by_path: List[Tuple[Path, Path]] = search_paths
        hits: List[CodeHit] = []
        seen = set()
        for raw in out.splitlines():
            parsed = self._parse_rg_line(raw)
            if not parsed:
                continue
            file_path, line_no, text = parsed
            if len(text.strip()) == 0:
                continue
            key = (str(file_path), line_no)
            if key in seen:
                continue
            seen.add(key)

            root = self._match_root(file_path, root_by_path)
            score = self._score_line(text, file_path=file_path, query_text=query_text, hit_kind=hit_kind)
            hits.append(CodeHit(path=file_path, root=root, line=line_no, text=text, score=score, kind=hit_kind))
            if len(hits) >= max_hits:
                break

        hits.sort(key=lambda x: x.score, reverse=True)
        return hits

    def _match_root(self, file_path: Path, roots: List[Tuple[Path, Path]]) -> Path:
        for root, scope in roots:
            try:
                file_path.relative_to(scope)
                return root
            except Exception:
                continue
        return roots[0][0]

    def _parse_rg_line(self, raw: str) -> Optional[Tuple[Path, int, str]]:
        # format: /path/to/file:123:matched line...
        parts = raw.split(":", 2)
        if len(parts) != 3:
            return None
        p, line_s, text = parts
        if not line_s.isdigit():
            return None
        path = Path(p)
        if not path.exists() or not path.is_file():
            return None
        return path, int(line_s), text

    def _score_line(
        self,
        text: str,
        *,
        file_path: Optional[Path] = None,
        query_text: str = "",
        hit_kind: str = "search",
    ) -> float:
        weights = rag_config.heuristics_weights("search_hit_score", _SEARCH_HIT_SCORE_DEFAULTS)
        t = (text or "").strip()
        lowered = t.lower()
        path_lower = file_path.as_posix().lower() if file_path is not None else ""
        query_tokens = _query_score_tokens(query_text)
        exact_hits = 0
        token_hits = 0
        path_hits = 0
        for token in query_tokens:
            if re.search(rf"\b{re.escape(token)}\b", lowered):
                exact_hits += 1
            elif token in lowered:
                token_hits += 1
            if len(token) >= 3 and token in path_lower:
                path_hits += 1

        score = float(weights["base"])
        score += min(exact_hits, int(weights["token_hit_cap"])) * float(weights["query_exact_hit"])
        score += min(token_hits, int(weights["token_hit_cap"])) * float(weights["query_token_hit"])
        score += min(path_hits, int(weights["path_hit_cap"])) * float(weights["path_token_hit"])
        if "(" in t and ")" in t:
            score += float(weights["call_bonus"])
        if "class " in t or "def " in t or "function " in t:
            score += float(weights["declaration_bonus"])
        if hit_kind == "symbol_definition":
            score += float(weights["symbol_definition_bonus"])
        if len(t) > int(weights["long_line_threshold"]):
            score -= float(weights["long_line_penalty"])
        return score

    def _read_window(self, path: Path, line_no: int) -> Tuple[str, int, int]:
        try:
            if path.stat().st_size > self.max_file_bytes:
                return "(file too large: skipped)", line_no, line_no
        except Exception:
            return "", line_no, line_no

        raw = path.read_bytes()
        text = self._decode(raw)
        lines = text.splitlines()
        if not lines:
            return "", line_no, line_no

        start = max(1, line_no - self.context_lines)
        end = min(len(lines), line_no + self.context_lines)
        snippet_lines = []
        for ln in range(start, end + 1):
            prefix = ">>" if ln == line_no else "  "
            snippet_lines.append(f"{prefix} {ln:5d}: {lines[ln - 1]}")
        return "\n".join(snippet_lines), start, end

    def _decode(self, raw: bytes) -> str:
        return decode_bytes(raw, TEXT_ENCODING_FALLBACKS)

    def _infer_project(self, path: Path, root: Path, explicit_repo: Optional[str]) -> str:
        if explicit_repo and explicit_repo.strip():
            return explicit_repo.strip()
        try:
            rel = path.relative_to(root)
            if rel.parts:
                return rel.parts[0]
        except Exception:
            pass
        return root.name or "workspace"

    def _build_payload(self, hit: CodeHit, repo_filter: Optional[str]) -> Optional[Dict]:
        snippet, line_start, line_end = self._read_window(hit.path, hit.line)
        if not snippet:
            return None

        project = self._infer_project(hit.path, hit.root, repo_filter)
        return {
            "file_path": str(hit.path),
            "source_file": str(hit.path),
            "language": language_from_name(hit.path.name),
            "project": project,
            "module": project,
            "text": snippet,
            "type": "code_reference",
            "source_kind": "code_tool",
            "match_kind": hit.kind,
            "line_start": line_start,
            "line_end": line_end,
        }
