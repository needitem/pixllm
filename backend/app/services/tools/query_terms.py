import re
from typing import Dict, Iterable, List, Sequence, Tuple

from ... import wiki_config

_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")
_ASCII_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_HANGUL_WORD_RE = re.compile(r"[가-힣]{2,}")
_IDENTIFIER_PART_RE = re.compile(r"[A-Z]+[0-9]*(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+[0-9]*")
_MEMBER_ACCESS_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*(?:\.|::|->)\s*([A-Za-z_][A-Za-z0-9_]*)")
_BACKTICK_CONTENT_RE = re.compile(r"`([^`]+)`")
_QUERY_STOPWORDS = {
    "about",
    "after",
    "along",
    "and",
    "are",
    "does",
    "for",
    "from",
    "help",
    "how",
    "into",
    "show",
    "that",
    "the",
    "this",
    "using",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
}
_QUERY_FILLER_TOKENS = {
    "the",
    "and",
    "with",
    "from",
    "show",
    "where",
    "what",
    "how",
}
_IDENTIFIER_STRUCTURE_SCORE_DEFAULTS = {
    "multi_part_unit": 2,
    "multi_part_cap": 6,
    "underscore_bonus": 2,
    "digit_bonus": 1,
    "long_identifier_threshold": 12,
    "long_identifier_bonus": 1,
}
_SYMBOL_QUERY_CANDIDATE_SCORE_DEFAULTS = {
    "filler_penalty": 4,
    "structure_multiplier": 3,
}
_QUERY_TERM_EXTRACTION_DEFAULTS = {
    "score_ngram_max": 3,
    "score_ngram_min_compact": 6,
    "compound_symbol_min_parts": 2,
    "compound_symbol_min_compact": 8,
    "explicit_symbol_bonus": 18,
    "member_symbol_bonus": 30,
    "ngram_symbol_bonus": 4,
}


def compact_token(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def split_identifier_parts(value: str) -> List[str]:
    return [part for part in _IDENTIFIER_PART_RE.findall(str(value or "")) if part]


def identifier_structure_score(token: str) -> int:
    weights = wiki_config.heuristics_weights("identifier_structure_score", _IDENTIFIER_STRUCTURE_SCORE_DEFAULTS)
    raw = str(token or "").strip()
    parts = split_identifier_parts(raw)
    score = 0
    if len(parts) > 1:
        score += min(int(weights["multi_part_cap"]), len(parts) * int(weights["multi_part_unit"]))
    if "_" in raw:
        score += int(weights["underscore_bonus"])
    if any(ch.isdigit() for ch in raw):
        score += int(weights["digit_bonus"])
    if len(raw) >= int(weights["long_identifier_threshold"]):
        score += int(weights["long_identifier_bonus"])
    return score


def _unique_preserving_order(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        token = str(value or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _query_term_config() -> Dict[str, int]:
    return wiki_config.heuristics_weights("query_term_extraction", _QUERY_TERM_EXTRACTION_DEFAULTS)
def _title_compound(words: Sequence[str]) -> str:
    return "".join(word[:1].upper() + word[1:] for word in words if word)


def _ascii_query_words(query: str) -> List[str]:
    words: List[str] = []
    for token in _ASCII_WORD_RE.findall(str(query or "")):
        parts = split_identifier_parts(token) or [token]
        for part in parts:
            lowered = str(part or "").strip().lower()
            if len(lowered) < 2 or lowered in _QUERY_STOPWORDS:
                continue
            words.append(lowered)
    return words


def _native_query_words(query: str) -> List[str]:
    return _unique_preserving_order(_HANGUL_WORD_RE.findall(str(query or "")))


def _query_ngram_compacts(words: Sequence[str], max_n: int, min_compact_length: int) -> List[str]:
    compacts: List[str] = []
    bounded_max_n = max(2, int(max_n or 2))
    for n in range(2, bounded_max_n + 1):
        for idx in range(0, max(0, len(words) - n + 1)):
            window = words[idx : idx + n]
            compact = "".join(window)
            if len(compact) >= max(2, int(min_compact_length or 2)):
                compacts.append(compact)
    return _unique_preserving_order(compacts)


def extract_query_terms(query: str, limit: int = 8) -> List[str]:
    config = _query_term_config()
    explicit = _IDENTIFIER_RE.findall(str(query or ""))
    terms: List[str] = list(explicit)

    ascii_words = _ascii_query_words(query)
    terms.extend(_native_query_words(query))
    for compact in _query_ngram_compacts(
        ascii_words,
        max_n=int(config["score_ngram_max"]),
        min_compact_length=int(config["score_ngram_min_compact"]),
    ):
        terms.append(compact)
    return _unique_preserving_order(terms)[: max(1, int(limit or 1))]


def extract_query_compacts(query: str, limit: int = 12) -> List[str]:
    config = _query_term_config()
    identifier_tokens: List[str] = []
    identifier_part_tokens: List[str] = []
    for token in _IDENTIFIER_RE.findall(str(query or "")):
        compact = compact_token(token)
        if compact:
            identifier_tokens.append(compact)
        identifier_part_tokens.extend(compact_token(part) for part in split_identifier_parts(token))

    ascii_words = _ascii_query_words(query)
    native_words = _native_query_words(query)
    ngram_tokens = _query_ngram_compacts(
        ascii_words,
        max_n=int(config["score_ngram_max"]),
        min_compact_length=int(config["score_ngram_min_compact"]),
    )

    tokens: List[str] = []
    tokens.extend(identifier_tokens)
    tokens.extend(ascii_words)
    tokens.extend(native_words)
    tokens.extend(ngram_tokens)
    tokens.extend(identifier_part_tokens)

    filtered = [
        token
        for token in _unique_preserving_order(tokens)
        if len(compact_token(token)) >= 2 and compact_token(token) not in _QUERY_STOPWORDS
    ]
    return filtered[: max(1, int(limit or 1))]


def extract_query_score_tokens(query: str, limit: int = 6) -> List[str]:
    return extract_query_compacts(query, limit=limit)


def _looks_like_explicit_symbol_token(token: str) -> bool:
    raw = str(token or "").strip()
    if not raw:
        return False
    if "_" in raw:
        return True
    if any(ch.isdigit() for ch in raw):
        return True
    if any(ch.isupper() for ch in raw[1:]):
        return True
    return len(split_identifier_parts(raw)) > 1


def _iter_backtick_identifier_tokens(query: str) -> List[str]:
    tokens: List[str] = []
    for content in _BACKTICK_CONTENT_RE.findall(str(query or "")):
        for token in _IDENTIFIER_RE.findall(str(content or "")):
            normalized = str(token or "").strip()
            if normalized:
                tokens.append(normalized)
    return _unique_preserving_order(tokens)


def _iter_symbol_candidate_pool(query: str) -> List[Tuple[str, str]]:
    candidates: List[Tuple[str, str]] = []
    member_tokens = _MEMBER_ACCESS_RE.findall(str(query or ""))
    for token in member_tokens:
        candidates.append(("member", token))
    for token in _iter_backtick_identifier_tokens(query):
        candidates.append(("backtick", token))
    explicit_tokens = [
        token
        for token in _IDENTIFIER_RE.findall(str(query or ""))
        if _looks_like_explicit_symbol_token(token)
    ]
    for token in explicit_tokens:
        candidates.append(("explicit", token))
    return candidates


def extract_symbol_query_candidates(query: str, max_candidates: int = 3) -> List[str]:
    weights = wiki_config.heuristics_weights("symbol_query_candidate_score", _SYMBOL_QUERY_CANDIDATE_SCORE_DEFAULTS)
    config = _query_term_config()
    scored: List[Tuple[int, str]] = []

    for source, token in _iter_symbol_candidate_pool(query):
        compact = compact_token(token)
        structure = identifier_structure_score(token)
        if source == "explicit" and str(token).isupper() and len(compact) <= 4 and structure <= 0:
            continue
        lowered = token.lower()
        score = len(token)
        if lowered in _QUERY_FILLER_TOKENS:
            score -= int(weights["filler_penalty"])
        score += structure * int(weights["structure_multiplier"])
        if source == "explicit":
            score += int(config["explicit_symbol_bonus"])
        elif source == "member":
            score += int(config["member_symbol_bonus"])
        elif source == "backtick":
            score += int(config["explicit_symbol_bonus"])
        scored.append((score, token))

    ordered: List[str] = []
    seen = set()
    for _, token in sorted(scored, key=lambda item: (-item[0], -len(item[1]), item[1].lower())):
        compact = compact_token(token)
        if not compact or compact in seen:
            continue
        seen.add(compact)
        ordered.append(token)
        if len(ordered) >= max(1, int(max_candidates or 1)):
            break
    return ordered
