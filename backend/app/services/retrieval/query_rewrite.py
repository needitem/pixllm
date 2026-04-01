import re
from dataclasses import dataclass
from typing import List


_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")
_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")


@dataclass(frozen=True)
class QueryCandidate:
    query: str
    strategy: str
    reason: str
    is_original: bool = False


@dataclass(frozen=True)
class QueryRewritePlan:
    original_query: str
    candidates: List[QueryCandidate]


def _normalize_spaces(text: str) -> str:
    return _SPACE_RE.sub(" ", str(text or "")).strip()


def _punctuation_normalize(text: str) -> str:
    cleaned = _PUNCT_RE.sub(" ", str(text or ""))
    return _normalize_spaces(cleaned).lower()


def _identifier_expand(text: str) -> str:
    expanded = str(text or "").replace("_", " ").replace("-", " ")
    expanded = _CAMEL_RE.sub(r"\1 \2", expanded)
    return _normalize_spaces(expanded).lower()


def build_query_rewrite(query: str, max_candidates: int = 3) -> QueryRewritePlan:
    original = _normalize_spaces(query)
    limit = max(1, int(max_candidates or 1))
    candidates: List[QueryCandidate] = [
        QueryCandidate(
            query=original,
            strategy="original",
            reason="preserve_user_input",
            is_original=True,
        )
    ]
    seen = {original}

    rewrites = [
        ("punctuation_normalize", "normalize_punctuation", _punctuation_normalize(original)),
        ("identifier_expand", "expand_identifier_tokens", _identifier_expand(original)),
    ]
    for strategy, reason, candidate_query in rewrites:
        if len(candidates) >= limit:
            break
        if not candidate_query or candidate_query in seen:
            continue
        seen.add(candidate_query)
        candidates.append(
            QueryCandidate(
                query=candidate_query,
                strategy=strategy,
                reason=reason,
                is_original=False,
            )
        )

    return QueryRewritePlan(original_query=original, candidates=candidates)
