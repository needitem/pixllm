#!/usr/bin/env python3
"""
Evaluate deployed runtime intent classification at scale.

Designed to run inside the running `pixllm-agent` container so it uses:
- current `classify_intent_hybrid()` logic
- current orchestration policy/rules
- current embedding model + vLLM client from app state
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import csv
import json
import os
import random
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

if "/app" not in sys.path:
    sys.path.insert(0, "/app")

from app import config
from app.deps import close_state, init_state, state
from app.services.chat.intent import classify_intent_hybrid


@dataclass
class EvalRow:
    index: int
    category: str
    expected: str
    predicted: str
    source: str
    question: str
    rule_hit_count: int
    matched_intents: List[str]
    correct_labeled: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remote runtime intent classifier evaluator")
    parser.add_argument("--seed", type=int, default=20260226, help="Random seed")
    parser.add_argument("--in-rule", type=int, default=7000, help="In-rule labeled sample count")
    parser.add_argument("--non-tech", type=int, default=700, help="Out-of-rule non-technical sample count")
    parser.add_argument("--tech-oos", type=int, default=700, help="Out-of-rule technical sample count")
    parser.add_argument("--english-oos", type=int, default=900, help="Out-of-rule English sample count")
    parser.add_argument("--typo-oos", type=int, default=400, help="Out-of-rule typo sample count")
    parser.add_argument("--mixed", type=int, default=300, help="Mixed-intent conflict sample count")
    parser.add_argument("--model", type=str, default="", help="Classifier model override")
    parser.add_argument("--disable-llm", action="store_true", help="Disable LLM fallback during evaluation")
    parser.add_argument("--api-url", type=str, default="http://127.0.0.1:8000/api/v1/chat", help="Deployed chat API URL")
    parser.add_argument("--api-spot-check", type=int, default=20, help="Number of API spot-check samples")
    parser.add_argument("--progress-every", type=int, default=500, help="Progress print interval")
    parser.add_argument("--dataset-only", action="store_true", help="Only build dataset and exit")
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("/tmp/intent_remote_eval_runtime_10000.md"),
        help="Markdown report path",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("/tmp/intent_remote_eval_runtime_10000.csv"),
        help="CSV output path",
    )
    return parser.parse_args()


def build_rules(policy) -> Tuple[Dict[str, List[str]], Dict[str, List[re.Pattern]]]:
    keyword_map: Dict[str, List[str]] = {}
    pattern_map: Dict[str, List[re.Pattern]] = {}
    for intent in policy.intents:
        intent_id = str(intent.get("id") or "").strip()
        if not intent_id:
            continue
        kws = [str(k).strip() for k in (intent.get("keywords") or []) if str(k).strip()]
        keyword_map[intent_id] = kws

        compiled: List[re.Pattern] = []
        for raw in (intent.get("patterns") or []):
            token = str(raw).strip()
            if not token:
                continue
            try:
                compiled.append(re.compile(token, flags=re.IGNORECASE))
            except re.error:
                continue
        pattern_map[intent_id] = compiled
    return keyword_map, pattern_map


def matched_intents(text: str, keyword_map: Dict[str, List[str]], pattern_map: Dict[str, List[re.Pattern]]) -> List[str]:
    lowered = text.lower()
    hits: List[str] = []
    for intent_id in keyword_map:
        matched = False
        for kw in keyword_map.get(intent_id, []):
            if kw.lower() in lowered:
                matched = True
                break
        if not matched:
            for pat in pattern_map.get(intent_id, []):
                if pat.search(text):
                    matched = True
                    break
        if matched:
            hits.append(intent_id)
    return sorted(hits)


def unique_keywords(keyword_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    owners: Dict[str, List[str]] = defaultdict(list)
    for intent_id, kws in keyword_map.items():
        for kw in kws:
            owners[kw.lower()].append(intent_id)

    out: Dict[str, List[str]] = {}
    for intent_id, kws in keyword_map.items():
        uniq = [kw for kw in kws if len(owners[kw.lower()]) == 1]
        out[intent_id] = uniq if uniq else list(kws)
    return out


def mutate_token(token: str, rng: random.Random) -> str:
    if len(token) < 2:
        return token + "x"
    idx = rng.randrange(len(token))
    alphabet = "abcdefghijklmnopqrstuvwxyz가나다라마바사아자차카타파하"
    repl = rng.choice(alphabet)
    return token[:idx] + repl + token[idx + 1 :]


def collect_unique(
    *,
    target: int,
    make_query,
    accept,
    global_seen: Set[str],
) -> List[str]:
    out: List[str] = []
    local_seen: Set[str] = set()
    attempts = 0
    max_attempts = max(1000, target * 500)

    while len(out) < target and attempts < max_attempts:
        attempts += 1
        q = str(make_query() or "").strip()
        key = q.lower()
        if not q or key in local_seen or key in global_seen:
            continue
        if not accept(q):
            continue
        local_seen.add(key)
        global_seen.add(key)
        out.append(q)

    if len(out) < target:
        raise RuntimeError(f"Failed to build enough unique samples. target={target}, got={len(out)}")
    return out


def build_dataset(
    *,
    policy,
    seed: int,
    in_rule_count: int,
    non_tech_count: int,
    tech_oos_count: int,
    english_oos_count: int,
    typo_oos_count: int,
    mixed_count: int,
) -> List[Tuple[str, str, str]]:
    """
    Returns tuples: (category, expected_intent, question)
    expected_intent is empty for unlabeled categories.
    """
    rng = random.Random(seed)
    keyword_map, pattern_map = build_rules(policy)
    uniq_map = unique_keywords(keyword_map)
    global_seen: Set[str] = set()
    dataset: List[Tuple[str, str, str]] = []

    components = [
        "검색 서비스",
        "업로드 파이프라인",
        "문서 인덱싱",
        "채팅 라우팅",
        "의도 분류기",
        "벡터 검색",
        "리랭킹 로직",
    ]
    domains = ["백엔드", "API", "배치", "운영", "배포", "품질"]
    contexts = [
        "온보딩 중이라",
        "운영 이슈 대응 중이라",
        "릴리즈 전에",
        "긴급 장애 대응 상황이라",
        "신규 기능 검토 단계라",
        "코드 정리 작업 중이라",
        "리뷰 준비 중이라",
        "문서 정리 단계라",
    ]
    output_styles = [
        "핵심만 짧게",
        "실무 순서로",
        "체크리스트 형태로",
        "우선순위 포함해서",
        "바로 실행 가능한 형태로",
        "초보도 이해되게",
        "요약 중심으로",
        "한눈에 보이게",
    ]
    constraints = [
        "10분 안에 파악할 수 있게",
        "팀 공유용으로",
        "내가 바로 적용할 수 있게",
        "회의 전에 빠르게 볼 수 있게",
        "리스크 먼저 보이게",
        "작업 순서가 드러나게",
        "핵심 용어만 남겨서",
        "불필요한 설명 빼고",
    ]
    oos_contexts = [
        "개인 메모 용도라",
        "팀 잡담 중이라",
        "가벼운 참고용이라",
        "여유 시간에",
        "취미 계획 세우는 중이라",
        "일상 기록 차원이라",
        "빠른 참고가 필요해서",
        "간단히 결정하려고",
    ]
    oos_styles = [
        "짧게",
        "한 줄 위주로",
        "부담 없이",
        "핵심 단어만",
        "길지 않게",
        "편한 말투로",
        "간단하게",
        "빠르게",
    ]
    oos_constraints = [
        "3개만",
        "5개만",
        "중복 없이",
        "지금 바로",
        "오늘 안에",
        "시간 적게 들게",
        "간단한 형태로",
        "가볍게",
    ]

    in_rule_templates = [
        "{kw} 관련해서 {component} 쪽을 먼저 어떻게 보면 좋을까? {ctx} {style}.",
        "이번 이슈는 {kw} 쪽인데 {domain} 관점에서 핵심만 정리해줘. {constraint}.",
        "{component} 작업 중이야. {kw} 기준으로 바로 시작할 순서 알려줘. {ctx}.",
        "{kw} 요청이 들어왔어. 지금 바로 확인해야 할 포인트가 뭐야? {style}.",
        "{domain} 기준으로 {kw} 처리할 때 체크할 항목만 짧게 알려줘. {constraint}.",
        "{component}에서 {kw} 하려면 어디부터 손대는 게 맞아? {ctx} {constraint}.",
    ]

    non_tech_topics = [
        "점심 메뉴",
        "주말 산책 코스",
        "출장 준비물",
        "커피 취향",
        "운동 루틴",
        "취미 아이디어",
        "휴가 계획",
        "영화 목록",
        "간식 리스트",
        "책 고르기",
    ]
    non_tech_templates = [
        "{topic} 후보를 골라줘. {constraint}.",
        "{topic} 아이템을 제안해줘. {style}.",
        "오늘 {topic} 관련 선택지를 줘. {constraint}.",
        "{topic} 목록을 부탁해. {ctx} {style}.",
    ]

    tech_oos_templates = [
        "{component} 쪽에서 지표 변동이 커. 로그 후보를 알려줘. {constraint}.",
        "배포 뒤 {component} 신호가 불안정해. 관찰 포인트를 알려줘. {style}.",
        "{domain} 운영 중 {component} 알람이 자주 떠. 먼저 볼 항목만 줘. {constraint}.",
        "최근 {component} 지연이 간헐적으로 보여. 진단 시작 지점을 알려줘. {style}.",
        "{component} 처리량이 들쭉날쭉해. 추적할 지표 이름을 제안해줘. {constraint}.",
    ]

    english_oos_templates = [
        "Need a brief on {component} health signals for production checks, {ctx_en}.",
        "Share a short list of logs to inspect for noisy behavior in {component}, {style_en}.",
        "Give me immediate triage pointers for unstable latency around {component}, {constraint_en}.",
        "I need quick observability hints for {component} after deployment, {style_en}.",
        "List first investigation clues for intermittent slowness in {component}, {constraint_en}.",
    ]

    mixed_templates = [
        "{kw1}도 필요하고 {kw2}도 같이 필요해. {ctx} 둘 다 챙겨줘.",
        "{kw1} 기준으로 보되 결과물은 {kw2}까지 같이 부탁해. {style}.",
        "{kw1}이랑 {kw2}를 한 번에 처리해야 해. {constraint}.",
        "요청이 섞였어. {kw1}도 하고 {kw2}도 해야 해. {ctx}.",
    ]

    intents_with_kw = [iid for iid, kws in uniq_map.items() if iid != "general" and kws]
    if not intents_with_kw:
        raise RuntimeError("No keyword-based intents found.")

    # In-rule labeled set (rule hits exactly one expected intent for clean labeling)
    in_rule_rows: List[Tuple[str, str, str]] = []
    attempts = 0
    max_attempts = max(10000, in_rule_count * 2000)
    while len(in_rule_rows) < in_rule_count and attempts < max_attempts:
        attempts += 1
        intent_id = rng.choice(intents_with_kw)
        kws = uniq_map.get(intent_id) or keyword_map.get(intent_id) or []
        if not kws:
            continue
        q = rng.choice(in_rule_templates).format(
            kw=rng.choice(kws),
            component=rng.choice(components),
            domain=rng.choice(domains),
            ctx=rng.choice(contexts),
            style=rng.choice(output_styles),
            constraint=rng.choice(constraints),
        )
        key = q.lower()
        if key in global_seen:
            continue
        hits = matched_intents(q, keyword_map, pattern_map)
        if intent_id not in hits:
            continue
        if len(hits) > 5:
            continue
        global_seen.add(key)
        in_rule_rows.append(("in_rule", intent_id, q))

    if len(in_rule_rows) < in_rule_count:
        raise RuntimeError(f"Failed to build enough in_rule samples. target={in_rule_count}, got={len(in_rule_rows)}")
    dataset.extend(in_rule_rows)

    non_tech = collect_unique(
        target=non_tech_count,
        make_query=lambda: rng.choice(non_tech_templates).format(
            topic=rng.choice(non_tech_topics),
            ctx=rng.choice(oos_contexts),
            style=rng.choice(oos_styles),
            constraint=rng.choice(oos_constraints),
        ),
        accept=lambda q: len(matched_intents(q, keyword_map, pattern_map)) == 0,
        global_seen=global_seen,
    )
    dataset.extend(("non_tech", "", q) for q in non_tech)

    tech_oos = collect_unique(
        target=tech_oos_count,
        make_query=lambda: rng.choice(tech_oos_templates).format(
            component=rng.choice(components),
            domain=rng.choice(domains),
            style=rng.choice(oos_styles),
            constraint=rng.choice(oos_constraints),
        ),
        accept=lambda q: len(matched_intents(q, keyword_map, pattern_map)) == 0,
        global_seen=global_seen,
    )
    dataset.extend(("tech_oos", "", q) for q in tech_oos)

    english_oos = collect_unique(
        target=english_oos_count,
        make_query=lambda: rng.choice(english_oos_templates).format(
            component=rng.choice(components),
            ctx_en=rng.choice(
                [
                    "we are close to release",
                    "this is for incident response",
                    "our team is rotating ownership",
                    "I have only fifteen minutes",
                    "this is for a handoff note",
                    "we just shipped a new build",
                ]
            ),
            style_en=rng.choice(
                [
                    "keep it practical",
                    "prioritize quick wins",
                    "focus on failure signals",
                    "avoid deep theory",
                    "use short bullet points",
                    "make it concise",
                ]
            ),
            constraint_en=rng.choice(
                [
                    "with risk-first ordering",
                    "for a small team",
                    "for production support",
                    "with minimal context",
                    "with immediate actions",
                    "for immediate triage",
                ]
            ),
        ),
        accept=lambda q: len(matched_intents(q, keyword_map, pattern_map)) == 0,
        global_seen=global_seen,
    )
    dataset.extend(("english_oos", "", q) for q in english_oos)

    typo_pool = [kw for iid, kws in uniq_map.items() if iid != "general" for kw in kws]
    if not typo_pool:
        typo_pool = [kw for kws in keyword_map.values() for kw in kws]
    typo_templates = [
        "{component} 쪽에서 {kw_typo} 관련 내용을 먼저 보고 싶어. {ctx} {style}.",
        "{kw_typo} 이슈 같은데 진단 시작점을 잡고 싶어. {constraint}.",
        "{domain} 관점에서 {kw_typo} 쪽 확인 포인트를 알려줘. {ctx}.",
    ]
    typo_oos = collect_unique(
        target=typo_oos_count,
        make_query=lambda: rng.choice(typo_templates).format(
            kw_typo=mutate_token(rng.choice(typo_pool), rng),
            component=rng.choice(components),
            domain=rng.choice(domains),
            ctx=rng.choice(oos_contexts),
            style=rng.choice(oos_styles),
            constraint=rng.choice(oos_constraints),
        ),
        accept=lambda q: len(matched_intents(q, keyword_map, pattern_map)) == 0,
        global_seen=global_seen,
    )
    dataset.extend(("typo_oos", "", q) for q in typo_oos)

    intent_ids_with_kw = [iid for iid, kws in keyword_map.items() if iid != "general" and kws]
    mixed = collect_unique(
        target=mixed_count,
        make_query=lambda: (
            lambda pair: rng.choice(mixed_templates).format(
                kw1=rng.choice(keyword_map[pair[0]]),
                kw2=rng.choice(keyword_map[pair[1]]),
                ctx=rng.choice(contexts),
                style=rng.choice(output_styles),
                constraint=rng.choice(constraints),
            )
        )(tuple(rng.sample(intent_ids_with_kw, 2))),
        accept=lambda q: len(matched_intents(q, keyword_map, pattern_map)) >= 2,
        global_seen=global_seen,
    )
    dataset.extend(("mixed_conflict", "", q) for q in mixed)

    rng.shuffle(dataset)
    return dataset


def classify_rows(
    *,
    dataset: Sequence[Tuple[str, str, str]],
    policy,
    model_name: str,
    llm_enabled: bool,
    progress_every: int,
) -> List[EvalRow]:
    rows: List[EvalRow] = []
    keyword_map, pattern_map = build_rules(policy)
    llm_client = state.vllm_client if llm_enabled else None
    model = model_name or config.VLLM_MODEL
    started = time.time()
    with open(os.devnull, "w", encoding="utf-8", errors="ignore") as devnull:
        for idx, (category, expected, question) in enumerate(dataset, start=1):
            with contextlib.redirect_stderr(devnull), contextlib.redirect_stdout(devnull):
                result = classify_intent_hybrid(
                    policy=policy,
                    message=question,
                    model_name=model,
                    llm_client=llm_client,
                )
            predicted = str(result.get("intent") or "").strip() or "general"
            source = str(result.get("source") or "").strip() or "unknown"
            hits = matched_intents(question, keyword_map, pattern_map)
            correct_labeled = int(bool(expected) and predicted == expected)
            rows.append(
                EvalRow(
                    index=idx,
                    category=category,
                    expected=expected,
                    predicted=predicted,
                    source=source,
                    question=question,
                    rule_hit_count=len(hits),
                    matched_intents=hits,
                    correct_labeled=correct_labeled,
                )
            )
            if progress_every > 0 and (idx % progress_every == 0):
                elapsed = time.time() - started
                print(f"[progress] {idx}/{len(dataset)} elapsed={elapsed:.1f}s")
    return rows


def _post_json(url: str, payload: Dict[str, str], timeout: int = 90) -> Tuple[bool, str, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
        parsed = json.loads(body)
        d = parsed.get("data") or {}
        return True, str(d.get("intent_id") or ""), str(d.get("intent_source") or "")
    except Exception:
        return False, "", ""


def run_api_spot_check(rows: Sequence[EvalRow], api_url: str, sample_count: int, seed: int) -> Dict[str, int]:
    if sample_count <= 0 or not rows:
        return {"checked": 0, "api_ok": 0, "api_match": 0, "api_mismatch": 0, "api_error": 0}

    rng = random.Random(seed + 17)
    picks = list(rows)
    rng.shuffle(picks)
    picks = picks[: min(sample_count, len(picks))]

    checked = 0
    ok = 0
    match = 0
    mismatch = 0
    errors = 0
    for row in picks:
        checked += 1
        success, api_intent, _api_source = _post_json(api_url, {"message": row.question})
        if not success:
            errors += 1
            continue
        ok += 1
        if (api_intent or "general") == row.predicted:
            match += 1
        else:
            mismatch += 1
    return {"checked": checked, "api_ok": ok, "api_match": match, "api_mismatch": mismatch, "api_error": errors}


def summarize(rows: Sequence[EvalRow]) -> Dict[str, object]:
    labeled = [r for r in rows if r.expected]
    labeled_correct = sum(r.correct_labeled for r in labeled)
    labeled_total = len(labeled)
    labeled_acc = (labeled_correct / labeled_total) if labeled_total else 0.0

    by_source = Counter(r.source for r in rows)
    by_category: Dict[str, List[EvalRow]] = defaultdict(list)
    for row in rows:
        by_category[row.category].append(row)

    category_summary: List[Tuple[str, int, str, float, float]] = []
    for category in sorted(by_category.keys()):
        block = by_category[category]
        pred_counter = Counter(r.predicted for r in block)
        top_pred, top_count = pred_counter.most_common(1)[0] if pred_counter else ("", 0)
        general_ratio = (pred_counter.get("general", 0) / len(block)) if block else 0.0
        category_summary.append((category, len(block), top_pred, (top_count / len(block)) if block else 0.0, general_ratio))

    confusions = Counter(
        (r.expected, r.predicted) for r in labeled if r.expected and r.predicted != r.expected
    )

    return {
        "total": len(rows),
        "labeled_total": labeled_total,
        "labeled_correct": labeled_correct,
        "labeled_accuracy": labeled_acc,
        "by_source": by_source,
        "category_summary": category_summary,
        "confusions": confusions,
    }


def write_csv(rows: Sequence[EvalRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "index",
                "category",
                "expected",
                "predicted",
                "source",
                "rule_hit_count",
                "matched_intents",
                "correct_labeled",
                "question",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.index,
                    r.category,
                    r.expected,
                    r.predicted,
                    r.source,
                    r.rule_hit_count,
                    ",".join(r.matched_intents),
                    r.correct_labeled,
                    r.question,
                ]
            )


def write_markdown(
    *,
    rows: Sequence[EvalRow],
    summary: Dict[str, object],
    output_path: Path,
    seed: int,
    llm_enabled: bool,
    model_name: str,
    elapsed_sec: float,
    spot: Dict[str, int],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    by_source: Counter = summary["by_source"]  # type: ignore[assignment]
    category_summary: List[Tuple[str, int, str, float, float]] = summary["category_summary"]  # type: ignore[assignment]
    confusions: Counter = summary["confusions"]  # type: ignore[assignment]

    total = int(summary["total"])
    labeled_total = int(summary["labeled_total"])
    labeled_correct = int(summary["labeled_correct"])
    labeled_acc = float(summary["labeled_accuracy"])

    lines: List[str] = []
    lines.append("# Remote Intent Classification Report (Deployed Runtime)")
    lines.append("")
    lines.append(f"- Generated at (UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Total questions: {total}")
    lines.append(f"- Seed: {seed}")
    lines.append(f"- Evaluated function: `classify_intent_hybrid()`")
    lines.append(f"- LLM fallback enabled: `{llm_enabled}`")
    lines.append(f"- Model: `{model_name or config.VLLM_MODEL}`")
    lines.append("- Dataset style: human-like prompts (no bracket-prefix, no synthetic batch suffix)")
    lines.append("- Execution: `root@192.168.2.238` / container `pixllm-agent`")
    lines.append(f"- Elapsed seconds: {elapsed_sec:.2f}")
    lines.append("")
    lines.append("## Labeled Accuracy (in_rule only)")
    lines.append("")
    lines.append(f"- Labeled samples: **{labeled_total}**")
    lines.append(f"- Correct: **{labeled_correct}**")
    lines.append(f"- Accuracy: **{labeled_acc:.4%}**")
    lines.append("")
    lines.append("## Source Distribution")
    lines.append("")
    lines.append("| source | count | ratio |")
    lines.append("|---|---:|---:|")
    for source, count in by_source.most_common():
        lines.append(f"| `{source}` | {count} | {(count / total if total else 0.0):.2%} |")
    lines.append("")
    lines.append("## Category Summary")
    lines.append("")
    lines.append("| category | samples | top_pred | top_ratio | general_ratio |")
    lines.append("|---|---:|---|---:|---:|")
    for category, size, top_pred, top_ratio, general_ratio in category_summary:
        lines.append(f"| `{category}` | {size} | `{top_pred}` | {top_ratio:.2%} | {general_ratio:.2%} |")
    lines.append("")
    lines.append("## Top Confusions (labeled only)")
    lines.append("")
    if confusions:
        lines.append("| expected | predicted | count |")
        lines.append("|---|---|---:|")
        for (expected, predicted), count in confusions.most_common(20):
            lines.append(f"| `{expected}` | `{predicted}` | {count} |")
    else:
        lines.append("- No labeled confusions.")
    lines.append("")
    lines.append("## API Spot Check")
    lines.append("")
    lines.append(f"- Checked samples: **{spot.get('checked', 0)}**")
    lines.append(f"- API successful responses: **{spot.get('api_ok', 0)}**")
    lines.append(f"- API match with local classifier prediction: **{spot.get('api_match', 0)}**")
    lines.append(f"- API mismatch: **{spot.get('api_mismatch', 0)}**")
    lines.append(f"- API errors: **{spot.get('api_error', 0)}**")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `in_rule` samples are generated to include the expected intent signal (some can also match additional rules).")
    lines.append("- OOS categories are generated to avoid current keyword/pattern rule matches.")
    lines.append("- Raw rows are saved as CSV alongside this report.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    seed = int(args.seed)
    total_target = (
        int(args.in_rule)
        + int(args.non_tech)
        + int(args.tech_oos)
        + int(args.english_oos)
        + int(args.typo_oos)
        + int(args.mixed)
    )
    print(f"[start] target_total={total_target}")

    started = time.time()
    asyncio.run(init_state())
    try:
        policy = state.orchestration_policy
        if policy is None:
            raise RuntimeError("orchestration policy unavailable")

        dataset = build_dataset(
            policy=policy,
            seed=seed,
            in_rule_count=int(args.in_rule),
            non_tech_count=int(args.non_tech),
            tech_oos_count=int(args.tech_oos),
            english_oos_count=int(args.english_oos),
            typo_oos_count=int(args.typo_oos),
            mixed_count=int(args.mixed),
        )
        print(f"[dataset] built={len(dataset)}")

        if bool(args.dataset_only):
            print("[dataset-only] skip classification")
            elapsed = time.time() - started
            print(f"samples={len(dataset)}")
            print(f"elapsed_sec={elapsed:.2f}")
            return 0
        else:
            rows = classify_rows(
                dataset=dataset,
                policy=policy,
                model_name=str(args.model or "").strip(),
                llm_enabled=not bool(args.disable_llm),
                progress_every=max(0, int(args.progress_every)),
            )
            print(f"[classify] rows={len(rows)}")

            summary = summarize(rows)
            spot = run_api_spot_check(
                rows=rows,
                api_url=str(args.api_url),
                sample_count=max(0, int(args.api_spot_check)),
                seed=seed,
            )

            write_csv(rows, Path(args.output_csv))
            write_markdown(
                rows=rows,
                summary=summary,
                output_path=Path(args.output_md),
                seed=seed,
                llm_enabled=not bool(args.disable_llm),
                model_name=str(args.model or "").strip(),
                elapsed_sec=time.time() - started,
                spot=spot,
            )
    finally:
        try:
            asyncio.run(close_state())
        except Exception:
            pass

    elapsed = time.time() - started
    print(f"samples={total_target}")
    print(f"elapsed_sec={elapsed:.2f}")
    print(f"report={args.output_md}")
    print(f"csv={args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
