from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.chat.evidence import build_evidence_gate


def _result(*, score: float, source_file: str, text: str, line_start: int | None = 1, line_end: int | None = 4) -> dict:
    return {
        "combined_score": score,
        "payload": {
            "source_file": source_file,
            "file_path": source_file,
            "text": text,
            "line_start": line_start,
            "line_end": line_end,
        },
    }


def test_single_strong_anchor_is_sufficient() -> None:
    gate = build_evidence_gate(
        results=[
            _result(
                score=0.55,
                source_file="/repo/src/foo.py",
                text="def run(payload):\n    return FooBarManager(payload).run()",
            )
        ],
        sources=[],
    )

    assert gate["passed"] is True
    assert gate["anchor_count"] == 1
    assert gate["best_anchor_score"] >= 0.55


def test_many_weak_hits_do_not_pass_without_a_strong_anchor() -> None:
    gate = build_evidence_gate(
        results=[
            _result(
                score=0.12,
                source_file=f"/repo/src/file_{idx}.py",
                text=f"FooBarManager mention {idx}",
            )
            for idx in range(8)
        ],
        sources=[],
    )

    assert gate["passed"] is False
    assert gate["score"] < gate["threshold"]


def test_document_anchor_without_line_numbers_still_counts() -> None:
    gate = build_evidence_gate(
        results=[
            {
                "combined_score": 0.48,
                "payload": {
                    "file_path": "/docs/sdk.md",
                    "source_file": "/docs/sdk.md",
                    "document_id": "sdk",
                    "section_path": "API > FooBarManager",
                    "text": "FooBarManager.run(payload) starts processing immediately.",
                    "line_start": None,
                    "line_end": None,
                },
            }
        ],
        sources=[],
    )

    assert gate["passed"] is True
    assert gate["anchor_count"] == 1
