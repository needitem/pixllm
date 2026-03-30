#!/usr/bin/env python3
"""
Evaluate intent classification quality using an external labeled CSV dataset.

This script does not generate synthetic samples.
Provide your own CSV with at least:
  - question/message/query column
  - expected intent label column
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import openai

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import config
from app.core.orchestration import OrchestrationPolicy
from app.services.chat.intent import classify_intent_hybrid


@dataclass
class EvalInputRow:
    index: int
    expected: str
    question: str


@dataclass
class EvalRow:
    index: int
    expected: str
    predicted: str
    correct: bool
    question: str
    source: str
    confidence: float
    failure_reason: str
    llm_error: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intent classifier evaluator (external CSV only)")
    parser.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Path to labeled CSV. Required columns: question/message/query + expected/label/intent",
    )
    parser.add_argument(
        "--classifier",
        choices=["hybrid"],
        default="hybrid",
        help="Classifier path to evaluate (LLM-only; default: hybrid)",
    )
    parser.add_argument(
        "--disable-llm",
        action="store_true",
        help="Disable LLM calls (expect fail-closed behavior)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="",
        help="Model name override for hybrid classifier",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("docs/07-status/03-tested/backend-reports/intent_classifier_eval.md"),
        help="Markdown report output path",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("docs/07-status/03-tested/backend-reports/intent_classifier_eval.csv"),
        help="Raw result CSV output path",
    )
    return parser.parse_args()


def _find_column(header: Sequence[str], candidates: Sequence[str]) -> Optional[str]:
    lowered = {str(col).strip().lower(): col for col in header}
    for cand in candidates:
        key = str(cand).strip().lower()
        if key in lowered:
            return lowered[key]
    return None


def load_dataset(path: Path) -> List[EvalInputRow]:
    if not path.exists():
        raise FileNotFoundError(f"input csv not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("input csv must include header row")

        question_col = _find_column(
            reader.fieldnames,
            ["question", "message", "query", "prompt", "text"],
        )
        expected_col = _find_column(
            reader.fieldnames,
            ["expected", "expected_intent", "label", "intent", "intent_id"],
        )

        if not question_col or not expected_col:
            raise ValueError(
                "input csv must contain question column (question/message/query/prompt/text) "
                "and expected label column (expected/expected_intent/label/intent/intent_id)"
            )

        rows: List[EvalInputRow] = []
        for idx, row in enumerate(reader, start=1):
            question = str(row.get(question_col) or "").strip()
            expected = str(row.get(expected_col) or "").strip()
            if not question or not expected:
                continue
            rows.append(EvalInputRow(index=idx, expected=expected, question=question))

    if not rows:
        raise ValueError("input csv has no valid rows (non-empty question + expected)")
    return rows


def _build_llm_client(enabled: bool) -> Optional[openai.OpenAI]:
    if not enabled:
        return None
    try:
        return openai.OpenAI(base_url=f"{config.VLLM_URL}/v1", api_key="EMPTY")
    except Exception:
        return None


def _predict_intent(
    *,
    policy: OrchestrationPolicy,
    question: str,
    model_name: str,
    llm_client: Optional[openai.OpenAI],
) -> Tuple[str, Dict[str, object]]:
    result = classify_intent_hybrid(
        policy=policy,
        message=question,
        model_name=model_name or config.VLLM_MODEL,
        llm_client=llm_client,
    )

    intent = str(result.get("intent") or "").strip()
    source = str(result.get("source") or "").strip()
    if intent:
        predicted = intent
    elif source == "intent_classification_failed":
        predicted = "intent_classification_failed"
    else:
        predicted = "general"

    return predicted, result


def evaluate(
    policy: OrchestrationPolicy,
    dataset: Sequence[EvalInputRow],
    model_name: str,
    llm_client: Optional[openai.OpenAI],
) -> List[EvalRow]:
    rows: List[EvalRow] = []
    for item in dataset:
        predicted, meta = _predict_intent(
            policy=policy,
            question=item.question,
            model_name=model_name,
            llm_client=llm_client,
        )
        rows.append(
            EvalRow(
                index=item.index,
                expected=item.expected,
                predicted=predicted,
                correct=(predicted == item.expected),
                question=item.question,
                source=str(meta.get("source") or ""),
                confidence=float(meta.get("confidence") or 0.0),
                failure_reason=str(meta.get("failure_reason") or ""),
                llm_error=str(meta.get("llm_error") or ""),
            )
        )
    return rows


def write_csv(rows: Sequence[EvalRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "index",
                "expected",
                "predicted",
                "correct",
                "source",
                "confidence",
                "failure_reason",
                "llm_error",
                "question",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.index,
                    row.expected,
                    row.predicted,
                    int(row.correct),
                    row.source,
                    f"{row.confidence:.6f}",
                    row.failure_reason,
                    row.llm_error,
                    row.question,
                ]
            )


def _summarize(rows: Sequence[EvalRow]) -> Dict[str, object]:
    by_intent: Dict[str, Dict[str, int]] = defaultdict(lambda: {"samples": 0, "correct": 0})
    confusion: Dict[str, Counter] = defaultdict(Counter)
    source_counter: Counter = Counter()
    failure_counter: Counter = Counter()
    errors: List[EvalRow] = []

    for row in rows:
        by_intent[row.expected]["samples"] += 1
        source_counter[row.source] += 1
        if row.failure_reason:
            failure_counter[row.failure_reason] += 1
        if row.correct:
            by_intent[row.expected]["correct"] += 1
        else:
            errors.append(row)
            confusion[row.expected][row.predicted] += 1

    total = len(rows)
    correct = sum(1 for r in rows if r.correct)
    overall = (correct / total) if total else 0.0

    macro_parts: List[float] = []
    per_intent_rows: List[Tuple[str, int, int, float]] = []
    for intent_id in sorted(by_intent.keys()):
        s = by_intent[intent_id]["samples"]
        c = by_intent[intent_id]["correct"]
        acc = (c / s) if s else 0.0
        macro_parts.append(acc)
        per_intent_rows.append((intent_id, s, c, acc))
    macro = (sum(macro_parts) / len(macro_parts)) if macro_parts else 0.0

    confusion_pairs: List[Tuple[str, str, int]] = []
    for expected, pred_counter in confusion.items():
        for predicted, count in pred_counter.items():
            confusion_pairs.append((expected, predicted, count))
    confusion_pairs.sort(key=lambda x: x[2], reverse=True)

    return {
        "total": total,
        "correct": correct,
        "overall_accuracy": overall,
        "macro_accuracy": macro,
        "per_intent": per_intent_rows,
        "errors": errors,
        "confusion_pairs": confusion_pairs,
        "source_counter": source_counter,
        "failure_counter": failure_counter,
    }


def write_markdown(
    rows: Sequence[EvalRow],
    summary: Dict[str, object],
    output_path: Path,
    input_csv: Path,
    classifier: str,
    llm_enabled: bool,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = int(summary["total"])
    correct = int(summary["correct"])
    overall = float(summary["overall_accuracy"])
    macro = float(summary["macro_accuracy"])
    per_intent = list(summary["per_intent"])
    confusion_pairs = list(summary["confusion_pairs"])
    errors: List[EvalRow] = list(summary["errors"])
    source_counter: Counter = summary["source_counter"]  # type: ignore[assignment]
    failure_counter: Counter = summary["failure_counter"]  # type: ignore[assignment]

    lines: List[str] = []
    lines.append("# Intent Classifier Evaluation Report")
    lines.append("")
    lines.append(f"- Generated at: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Input CSV: `{input_csv}`")
    lines.append(f"- Classifier mode: `{classifier}`")
    lines.append("- Evaluated function: `classify_intent_hybrid()` (LLM-only)")
    lines.append(f"- LLM enabled: `{llm_enabled}`")
    lines.append(f"- Total samples: {total}")
    lines.append("")

    lines.append("## Overall")
    lines.append("")
    lines.append(f"- Accuracy: **{overall:.4%}** ({correct}/{total})")
    lines.append(f"- Macro average accuracy: **{macro:.4%}**")
    lines.append(f"- Misclassified: **{len(errors)}**")
    lines.append("")

    lines.append("## Source Distribution")
    lines.append("")
    lines.append("| source | count | ratio |")
    lines.append("|---|---:|---:|")
    for src, count in source_counter.most_common():
        ratio = (count / total) if total else 0.0
        lines.append(f"| `{src}` | {count} | {ratio:.2%} |")
    lines.append("")

    lines.append("## Failure Reason Distribution")
    lines.append("")
    if failure_counter:
        lines.append("| failure_reason | count | ratio |")
        lines.append("|---|---:|---:|")
        for reason, count in failure_counter.most_common():
            ratio = (count / total) if total else 0.0
            lines.append(f"| `{reason}` | {count} | {ratio:.2%} |")
    else:
        lines.append("- No classification failures.")
    lines.append("")

    lines.append("## Per Intent Accuracy")
    lines.append("")
    lines.append("| expected intent | samples | correct | accuracy |")
    lines.append("|---|---:|---:|---:|")
    for intent_id, samples, good, acc in per_intent:
        lines.append(f"| `{intent_id}` | {samples} | {good} | {acc:.2%} |")
    lines.append("")

    lines.append("## Top Confusions")
    lines.append("")
    if confusion_pairs:
        lines.append("| expected | predicted | count |")
        lines.append("|---|---|---:|")
        for expected, predicted, count in confusion_pairs[:30]:
            lines.append(f"| `{expected}` | `{predicted}` | {count} |")
    else:
        lines.append("- No confusion pairs (no misclassifications).")
    lines.append("")

    lines.append("## Misclassified Samples")
    lines.append("")
    if errors:
        lines.append("| # | expected | predicted | source | failure_reason | question |")
        lines.append("|---:|---|---|---|---|---|")
        for row in errors[:200]:
            q = row.question.replace("|", "\\|")
            lines.append(
                f"| {row.index} | `{row.expected}` | `{row.predicted}` | `{row.source}` | `{row.failure_reason or '-'}` | {q} |"
            )
    else:
        lines.append("- No misclassified samples.")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This report uses only external labeled CSV input.")
    lines.append("- Runtime routing is LLM-only and fail-closed on classification failure.")
    lines.append("- Raw rows are saved as CSV alongside this report.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    policy = OrchestrationPolicy()

    dataset = load_dataset(args.input_csv)
    classifier = str(args.classifier or "hybrid").strip().lower()
    llm_enabled = classifier == "hybrid" and not bool(args.disable_llm)
    llm_client = _build_llm_client(llm_enabled)

    rows = evaluate(
        policy=policy,
        dataset=dataset,
        model_name=str(args.model or "").strip(),
        llm_client=llm_client,
    )
    summary = _summarize(rows)

    write_csv(rows, args.output_csv)
    write_markdown(
        rows=rows,
        summary=summary,
        output_path=args.output_md,
        input_csv=args.input_csv,
        classifier=classifier,
        llm_enabled=llm_client is not None,
    )

    print(f"samples={len(rows)}")
    print(f"accuracy={float(summary['overall_accuracy']):.6f}")
    print(f"report={args.output_md}")
    print(f"csv={args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
