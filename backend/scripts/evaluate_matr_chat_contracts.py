#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


MATR_ROOT = Path(r"D:\Pixoneer_Source\MATR_Source\src\MATR")
DEFAULT_API_BASE = "http://192.168.2.238:8000/api/v1"
DEFAULT_TOKEN = "pixllm-desktop-local"
DEFAULT_MODEL = "qwen3.5-27b"
BAD_PHRASES = [
    "inaccessible",
    "upload",
    "tree",
    "ls ",
    "cannot inspect",
    "can't inspect",
    "direct access",
]


@dataclass(frozen=True)
class SpanSpec:
    path: Path
    start_line: int
    end_line: int
    symbol: str = ""
    tool: str = "read_symbol_span"


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    category: str
    question: str
    selected_file: Path
    spans: List[SpanSpec]
    expected_contract: str
    expected_tokens: List[str]
    expected_header: str = ""
    workspace_graph: Dict[str, Any] = field(default_factory=dict)
    changed_paths: List[str] = field(default_factory=list)


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "cp949", "euc-kr"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def line_slice(path: Path, start_line: int, end_line: int) -> str:
    lines = read_text(path).splitlines()
    start_index = max(start_line - 1, 0)
    end_index = min(end_line, len(lines))
    return "\n".join(lines[start_index:end_index]).strip()


def build_cases() -> List[EvalCase]:
    hetero = MATR_ROOT / "MATR" / "ViewModels" / "UserControls" / "ImageMatching" / "Vm_ImageMatching_Heterogeneous.cs"
    peer = MATR_ROOT / "MATR" / "ViewModels" / "UserControls" / "ImageMatching" / "Vm_ImageMatching_Peer.cs"
    mgr = MATR_ROOT / "MATR" / "Mgrs" / "ImageMatching" / "ImageMatchingMgr.cs"
    warping = MATR_ROOT / "MATR" / "Common" / "WarpingService.cs"

    return [
        EvalCase(
            case_id="flow_select_matching",
            category="flow",
            question="영상 정합 화면에서 항목을 고르면 어떤 순서로 로드되는지 흐름을 정리해줘.",
            selected_file=hetero,
            spans=[
                SpanSpec(hetero, 299, 335, "SelectMatchingData"),
                SpanSpec(hetero, 3186, 3205, "LoadReferenceImage"),
                SpanSpec(hetero, 3207, 3218, "LoadTargetImage"),
                SpanSpec(hetero, 3220, 3228, "HandleInitialState"),
            ],
            expected_contract="code_flow_explanation",
            expected_tokens=["SelectMatchingData", "LoadTargetImage", "LoadReferenceImage"],
            workspace_graph={
                "target_symbol": "SelectMatchingData",
                "focus_file": str(hetero),
                "core_files": [str(hetero)],
                "graph_state": {
                    "chain": [
                        {"relation": "anchor", "symbol": "SelectMatchingData", "path": str(hetero), "covered": True, "discovered": True, "search_completed": True},
                        {"relation": "callee", "symbol": "HandleInitialState", "path": str(hetero), "covered": True, "discovered": True, "search_completed": True},
                        {"relation": "callee", "symbol": "LoadTargetImage", "path": str(hetero), "covered": True, "discovered": True, "search_completed": True},
                        {"relation": "callee", "symbol": "LoadReferenceImage", "path": str(hetero), "covered": True, "discovered": True, "search_completed": True},
                    ],
                    "frontiers": [
                        {"relation": "callee", "symbol": "IsTargerAndRefernceImageUsed", "path": str(hetero), "covered": False, "discovered": True, "search_completed": False}
                    ],
                },
            },
        ),
        EvalCase(
            case_id="state_select_matching",
            category="state_change",
            question="SelectMatchingData가 실행되면 어떤 상태값과 UI 표시가 같이 바뀌는지 정리해줘.",
            selected_file=hetero,
            spans=[
                SpanSpec(hetero, 299, 335, "SelectMatchingData"),
                SpanSpec(hetero, 3409, 3428, "ResultViewInit"),
            ],
            expected_contract="code_read",
            expected_tokens=["TImagePath", "RImagePath", "VisibilityResultImageView", "LastResultReferenceImagePath"],
            expected_header="## Code Read",
            workspace_graph={"target_symbol": "SelectMatchingData", "focus_file": str(hetero), "core_files": [str(hetero)]},
        ),
        EvalCase(
            case_id="read_display_view",
            category="read",
            question="ImageMatchingMgr.DisplayView가 imageType에 따라 어떤 뷰 분기로 이어지는지 설명해줘.",
            selected_file=mgr,
            spans=[
                SpanSpec(mgr, 59, 89, "DisplayView"),
                SpanSpec(mgr, 92, 180, "DisplayViewPeer"),
                SpanSpec(mgr, 182, 274, "DisplayViewHeterogeneous"),
            ],
            expected_contract="code_read",
            expected_tokens=["DisplayView", "DisplayViewPeer", "DisplayViewHeterogeneous", "_windowManager.ShowWindow"],
            expected_header="## Code Read",
            workspace_graph={"target_symbol": "DisplayView", "focus_file": str(mgr), "core_files": [str(mgr)]},
        ),
        EvalCase(
            case_id="compare_select_matching",
            category="compare",
            question="VmImageMatchingHeterogeneous.SelectMatchingData와 VmImageMatchingPeer.SelectMatchingData 차이를 비교해줘.",
            selected_file=hetero,
            spans=[
                SpanSpec(hetero, 299, 335, "VmImageMatchingHeterogeneous.SelectMatchingData"),
                SpanSpec(peer, 216, 296, "VmImageMatchingPeer.SelectMatchingData"),
            ],
            expected_contract="code_compare",
            expected_tokens=["VmImageMatchingHeterogeneous.SelectMatchingData", "VmImageMatchingPeer.SelectMatchingData"],
            expected_header="## Code Comparison",
            workspace_graph={"focus_file": str(hetero), "core_files": [str(hetero), str(peer)]},
        ),
        EvalCase(
            case_id="failure_warping_parse",
            category="failure_analysis",
            question="WarpingService.ProcessWarpingAsync에서 registrationResult 파싱이 실패하면 이후 처리와 산출물이 어떻게 달라지는지 분석해줘.",
            selected_file=warping,
            spans=[
                SpanSpec(warping, 21, 162, "ProcessWarpingAsync"),
                SpanSpec(warping, 219, 317, "ParseRegistrationResult"),
            ],
            expected_contract="failure_analysis",
            expected_tokens=["ProcessWarpingAsync", "ParseRegistrationResult", "transformInfo", "return result"],
            expected_header="## Failure Analysis",
            workspace_graph={"target_symbol": "ProcessWarpingAsync", "focus_file": str(warping), "core_files": [str(warping)]},
        ),
        EvalCase(
            case_id="review_warping",
            category="review",
            question="WarpingService.ProcessWarpingAsync 구현을 코드 리뷰해줘. 버그, 누락된 방어 로직, 테스트 공백 중심으로.",
            selected_file=warping,
            spans=[
                SpanSpec(warping, 21, 162, "ProcessWarpingAsync"),
                SpanSpec(warping, 219, 317, "ParseRegistrationResult"),
                SpanSpec(warping, 588, 680, "SaveWarpedDetectionResultToDBAsync"),
            ],
            expected_contract="code_review",
            expected_tokens=["ProcessWarpingAsync", "WarpingService.cs"],
            expected_header="## Code Review",
            workspace_graph={"target_symbol": "ProcessWarpingAsync", "focus_file": str(warping), "core_files": [str(warping)]},
            changed_paths=[str(warping)],
        ),
    ]


def build_overlay(case: EvalCase) -> Dict[str, Any]:
    selected_text = read_text(case.selected_file)[:6000]
    local_trace: List[Dict[str, Any]] = []
    for span in case.spans:
        local_trace.append(
            {
                "tool": span.tool,
                "symbol": span.symbol,
                "observation": {
                    "path": str(span.path),
                    "lineRange": f"{span.start_line}-{span.end_line}",
                    "content": line_slice(span.path, span.start_line, span.end_line),
                    "symbol": span.symbol,
                },
            }
        )

    metadata: Dict[str, Any] = {
        "workspace_path": str(MATR_ROOT),
        "selected_file_path": str(case.selected_file),
        "selected_file_content": selected_text,
        "workspace_change_paths": list(case.changed_paths),
        "local_summary": f"Collected grounded {case.category} evidence from MATR local workspace overlay.",
        "local_context_text": "Local overlay built from selected file content plus grounded symbol spans.",
        "local_trace": local_trace,
        "workspace_graph": dict(case.workspace_graph),
        "question": case.question,
    }
    return {
        "kind": "local_workspace_overlay",
        "name": "MATR",
        "path": str(MATR_ROOT),
        "content_type": "application/json",
        "metadata": metadata,
    }


def build_payload(case: EvalCase, model: str) -> Dict[str, Any]:
    return {
        "message": case.question,
        "model": model,
        "workspace_id": str(MATR_ROOT),
        "task_type": "workspace_overlay",
        "goal": "Use the local workspace as the primary code graph. Consult server baseline only when local evidence is insufficient.",
        "tool_scope": ["local_workspace_overlay", "server_code_baseline"],
        "attachments": [build_overlay(case)],
        "top_k": 20,
        "use_reranker": False,
    }


def post_json(url: str, token: str, payload: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_post_json(url: str, token: str, payload: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
    try:
        return post_json(url, token, payload, timeout_sec)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return {"ok": False, "error": {"type": "http", "status": exc.code, "body": body}}
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return {"ok": False, "error": {"type": "network", "message": str(exc)}}


def answer_excerpt(answer: str, limit_lines: int = 18) -> str:
    lines = str(answer or "").splitlines()
    trimmed = "\n".join(lines[:limit_lines]).strip()
    if len(lines) > limit_lines:
        trimmed += "\n..."
    return trimmed


def contains_bad_phrase(answer: str) -> bool:
    lowered = str(answer or "").lower()
    return any(phrase in lowered for phrase in BAD_PHRASES)


def token_hits(answer: str, expected_tokens: List[str]) -> List[str]:
    lowered = str(answer or "").lower()
    return [token for token in expected_tokens if token.lower() in lowered]


def evaluate_case(case: EvalCase, verify_data: Dict[str, Any], chat_data: Dict[str, Any]) -> Dict[str, Any]:
    verify_payload = dict((verify_data or {}).get("data") or {})
    chat_payload = dict((chat_data or {}).get("data") or {})
    answer = str(chat_payload.get("answer") or "")
    observed_contract = str(((verify_payload.get("question_contract") or {}).get("kind")) or "")
    observed_header = answer.splitlines()[0].strip() if answer.strip() else ""
    hits = token_hits(answer, case.expected_tokens)
    bad_phrase = contains_bad_phrase(answer)
    contract_ok = observed_contract == case.expected_contract
    header_ok = True if not case.expected_header else observed_header == case.expected_header
    token_ok = len(hits) >= max(1, min(2, len(case.expected_tokens)))
    overall = "satisfactory"
    if not contract_ok or not header_ok or bad_phrase:
        overall = "needs_attention"
    elif not token_ok:
        overall = "mixed"

    trace_items = list(((build_overlay(case).get("metadata") or {}).get("local_trace")) or [])
    trace_symbols = [str(item.get("symbol") or "") for item in trace_items if str(item.get("symbol") or "").strip()]

    return {
        "case": case,
        "verify": verify_payload,
        "chat": chat_payload,
        "observed_contract": observed_contract,
        "observed_response_type": str(verify_payload.get("response_type") or ""),
        "observed_planned_response_type": str(verify_payload.get("planned_response_type") or ""),
        "observed_answer_style": str(verify_payload.get("answer_style") or ""),
        "observed_header": observed_header,
        "trace_symbols": trace_symbols,
        "token_hits": hits,
        "bad_phrase": bad_phrase,
        "contract_ok": contract_ok,
        "header_ok": header_ok,
        "token_ok": token_ok,
        "overall": overall,
        "answer_excerpt": answer_excerpt(answer),
    }


def render_report(results: List[Dict[str, Any]], api_base: str, model: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(results)
    satisfactory = sum(1 for item in results if item["overall"] == "satisfactory")
    mixed = sum(1 for item in results if item["overall"] == "mixed")
    needs_attention = sum(1 for item in results if item["overall"] == "needs_attention")

    lines = [
        "# MATR Multi-Question Chat Evaluation",
        "",
        f"- Generated: `{timestamp}`",
        f"- API: `{api_base}`",
        f"- Model: `{model}`",
        f"- Workspace: `{MATR_ROOT}`",
        "",
        "## Summary",
        "",
        "| Case | Category | Expected Contract | Observed Contract | Header | Overall |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        case: EvalCase = item["case"]
        lines.append(
            f"| `{case.case_id}` | `{case.category}` | `{case.expected_contract}` | `{item['observed_contract'] or '-'}` | `{item['observed_header'] or '-'}` | `{item['overall']}` |"
        )
    lines.extend(
        [
            "",
            f"- Satisfactory: `{satisfactory}/{total}`",
            f"- Mixed: `{mixed}/{total}`",
            f"- Needs attention: `{needs_attention}/{total}`",
            "",
            "## Detailed Results",
            "",
        ]
    )

    for item in results:
        case: EvalCase = item["case"]
        verify = item["verify"]
        lines.extend(
            [
                f"### {case.case_id}",
                "",
                f"- Category: `{case.category}`",
                f"- Question: {case.question}",
                f"- Selected file: `{case.selected_file}`",
                f"- Expected contract: `{case.expected_contract}`",
                f"- Observed contract: `{item['observed_contract'] or '-'}`",
                f"- Planned response type: `{item['observed_planned_response_type'] or '-'}`",
                f"- Response type: `{item['observed_response_type'] or '-'}`",
                f"- Answer style: `{item['observed_answer_style'] or '-'}`",
                f"- Trace symbols: {', '.join(f'`{symbol}`' for symbol in item['trace_symbols']) if item['trace_symbols'] else '-'}",
                f"- Token hits: {', '.join(f'`{token}`' for token in item['token_hits']) if item['token_hits'] else '-'}",
                f"- Overall: `{item['overall']}`",
                "",
                "Observed thinking flow:",
                f"1. Verify classified the question as `{item['observed_contract'] or '-'}` with `{item['observed_response_type'] or '-'}` lane.",
                f"2. The overlay grounded the answer on `{case.selected_file.name}` plus {len(case.spans)} explicit span read(s).",
                f"3. The response came back with header `{item['observed_header'] or '-'}`.",
                "",
                "Response excerpt:",
                "",
                "```text",
                item["answer_excerpt"] or "(empty)",
                "```",
                "",
            ]
        )
        if verify:
            lines.extend(
                [
                    "Verify payload excerpt:",
                    "",
                    "```json",
                    json.dumps(
                        {
                            "planned_response_type": verify.get("planned_response_type"),
                            "response_type": verify.get("response_type"),
                            "answer_style": verify.get("answer_style"),
                            "question_contract": verify.get("question_contract"),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )[:2000],
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate deployed chat behavior against MATR overlay questions.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--token", default=DEFAULT_TOKEN)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-sec", type=int, default=240)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/03-test/matr-multi-question-chat-report-20260331.md"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = build_cases()
    results: List[Dict[str, Any]] = []
    verify_url = f"{args.api_base.rstrip('/')}/chat/intent/verify"
    chat_url = f"{args.api_base.rstrip('/')}/chat"

    for case in cases:
        payload = build_payload(case, args.model)
        verify = safe_post_json(verify_url, args.token, payload, args.timeout_sec)
        chat = safe_post_json(chat_url, args.token, payload, args.timeout_sec)
        if not verify.get("ok"):
            results.append(
                {
                    "case": case,
                    "verify": {},
                    "chat": {},
                    "observed_contract": "",
                    "observed_response_type": "",
                    "observed_planned_response_type": "",
                    "observed_answer_style": "",
                    "observed_header": "",
                    "trace_symbols": [span.symbol for span in case.spans if span.symbol],
                    "token_hits": [],
                    "bad_phrase": False,
                    "contract_ok": False,
                    "header_ok": False,
                    "token_ok": False,
                    "overall": "needs_attention",
                    "answer_excerpt": f"verify failed: {json.dumps(verify.get('error') or {}, ensure_ascii=False)}",
                }
            )
            continue
        if not chat.get("ok"):
            results.append(
                {
                    "case": case,
                    "verify": dict(verify.get("data") or {}),
                    "chat": {},
                    "observed_contract": str(((verify.get("data") or {}).get("question_contract") or {}).get("kind") or ""),
                    "observed_response_type": str((verify.get("data") or {}).get("response_type") or ""),
                    "observed_planned_response_type": str((verify.get("data") or {}).get("planned_response_type") or ""),
                    "observed_answer_style": str((verify.get("data") or {}).get("answer_style") or ""),
                    "observed_header": "",
                    "trace_symbols": [span.symbol for span in case.spans if span.symbol],
                    "token_hits": [],
                    "bad_phrase": False,
                    "contract_ok": False,
                    "header_ok": False,
                    "token_ok": False,
                    "overall": "needs_attention",
                    "answer_excerpt": f"chat failed: {json.dumps(chat.get('error') or {}, ensure_ascii=False)}",
                }
            )
            continue
        results.append(evaluate_case(case, verify, chat))

    report = render_report(results, args.api_base, args.model)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parents[2] / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
