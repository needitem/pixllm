from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.tools.codebase import (
    CodeToolService,
    _query_score_tokens,
    extract_symbol_query_candidates,
)
from backend.app.services.tools.query_strategy import prioritize_usage_matches


SOURCE_EXTENSIONS = {".cs", ".xaml"}
EXCLUDED_DIRS = {"bin", "obj", "packages", ".git", ".vs", ".vscode"}


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    style: str
    query: str
    answer: str
    expected_paths: Sequence[str]


@dataclass
class Hit:
    path: Path
    line_no: int
    text: str
    score: float


CASES: List[EvalCase] = [
    EvalCase(
        case_id="startup_db_natural",
        style="natural_korean",
        query="앱 시작 시 DB 연결 실패하면 어떻게 처리되나?",
        answer="MainWindow 생성자에서 InitDefaultData를 호출하고, DBConnectManager.Instance.CheckConnectDB()가 false면 오류 메시지를 띄운 뒤 창을 닫는다. 성공하면 VmMainWindow를 만들어 DataContext에 연결한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\MainWindow.xaml.cs"],
    ),
    EvalCase(
        case_id="startup_db_anchored",
        style="symbol_anchored",
        query="InitDefaultData에서 DB 연결 실패 시 어떻게 처리되나?",
        answer="InitDefaultData는 DBConnectManager.Instance.CheckConnectDB()가 false면 WinMessageBoxError.ShowDialog(...)를 호출하고 MainWindow를 닫는다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\MainWindow.xaml.cs"],
    ),
    EvalCase(
        case_id="workorder_path_natural",
        style="natural_korean",
        query="워크오더 JSON 파일은 어디 경로에 생성되나?",
        answer="ConfigManager.WorkOrderPath는 ROOT_FILE_PATH/MATR_Data/DataFiles/Output/workorder를 가리키고, WorkOrderMaker.JSON_PATH가 이를 사용한다. WriteWorkOrder가 그 위치에 파일을 쓰고 CommonService.ConvertPath로 서버 경로로 바꿔 반환한다.",
        expected_paths=[
            r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\ConfigManager.cs",
            r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WorkOrderMaker.cs",
        ],
    ),
    EvalCase(
        case_id="workorder_path_anchored",
        style="symbol_anchored",
        query="ConfigManager.WorkOrderPath와 WorkOrderMaker.JSON_PATH는 어디를 가리키나?",
        answer="ConfigManager.WorkOrderPath는 ROOT_FILE_PATH/MATR_Data/DataFiles/Output/workorder이고 WorkOrderMaker.JSON_PATH가 그 값을 그대로 사용한다.",
        expected_paths=[
            r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\ConfigManager.cs",
            r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WorkOrderMaker.cs",
        ],
    ),
    EvalCase(
        case_id="change_detect_send_natural",
        style="natural_korean",
        query="변화탐지 작업을 JSON으로 만들고 서버에 보내는 흐름은?",
        answer="WorkOrderMaker.WriteJsonChangeDetect가 ProcessChangeDetectTask를 호출하고, 내부에서 BuildChangeDetectJson으로 JSON을 만든 뒤 WriteWorkOrder로 파일을 저장하고 TCPService.Instance.SendWorkOrder로 서버에 전송해 requestId를 반환한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WorkOrderMaker.cs"],
    ),
    EvalCase(
        case_id="change_detect_send_anchored",
        style="symbol_anchored",
        query="WriteJsonChangeDetect와 ProcessChangeDetectTask의 전송 흐름은?",
        answer="WriteJsonChangeDetect는 ProcessChangeDetectTask를 거쳐 BuildChangeDetectJson, WriteWorkOrder, TCPService.Instance.SendWorkOrder 순으로 처리한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\WorkOrderMaker.cs"],
    ),
    EvalCase(
        case_id="tcp_connect_natural",
        style="natural_korean",
        query="TCPService는 서버 연결을 어떻게 시도하고 유지하나?",
        answer="ConnectionManager.Connect가 이미 연결된 상태를 확인한 뒤 ConnectWithRetry로 10초 간격 재시도를 반복한다. AttemptConnection에서 소켓 keepalive를 설정하고, Connect 후 PerformHandshake를 거쳐 listener와 app ping timer를 시작한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\TCPService.cs"],
    ),
    EvalCase(
        case_id="tcp_connect_anchored",
        style="symbol_anchored",
        query="ConnectWithRetry, AttemptConnection, PerformHandshake는 어떻게 이어지나?",
        answer="ConnectWithRetry가 AttemptConnection을 반복 호출하고, AttemptConnection이 keepalive 설정, socket connect, stream 획득, PerformHandshake, listener 시작, StartAppPingTimer까지 수행한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\TCPService.cs"],
    ),
    EvalCase(
        case_id="fallback_natural",
        style="natural_korean",
        query="task result가 안 오면 언제 DB fallback을 요청하나?",
        answer="EvaluatePendingTaskResultFallbacks는 LastPingRemainingTaskCount가 0이고 pending work order가 남아 있으며, 각 요청의 전송 시각이 TASKRESULT_DB_FALLBACK_TIMEOUT(120초)을 넘었을 때 DB fallback 이벤트를 올린다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\TCPService.cs"],
    ),
    EvalCase(
        case_id="fallback_anchored",
        style="symbol_anchored",
        query="EvaluatePendingTaskResultFallbacks와 TASKRESULT_DB_FALLBACK_TIMEOUT은 어떻게 동작하나?",
        answer="EvaluatePendingTaskResultFallbacks는 남은 작업 수가 0일 때만 pending request를 돌며, 전송 후 120초를 넘은 requestId에 대해 PendingTaskResultDbFallbackRequested를 발생시킨다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\TCPService.cs"],
    ),
    EvalCase(
        case_id="convert_path_natural",
        style="natural_korean",
        query="CommonService.ConvertPath는 로컬 경로와 서버 경로를 어떻게 바꾸나?",
        answer="isLocalMode가 false면 LocalHome 기준 Windows 경로를 ServerHome 기준 Linux 경로로 바꾸고, true면 ServerHome 기준 경로를 다시 LocalHome 기준 Windows 경로로 되돌린다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\CommonService.cs"],
    ),
    EvalCase(
        case_id="convert_path_anchored",
        style="symbol_anchored",
        query="CommonService.ConvertPath(filePath, isLocalMode)는 어떤 변환을 하나?",
        answer="ConvertPath는 기본적으로 local home prefix를 server home prefix로 치환하고, isLocalMode=true일 때는 server home prefix를 local home prefix로 바꾸며 슬래시도 Windows 형식으로 정리한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Common\CommonService.cs"],
    ),
    EvalCase(
        case_id="hetero_view_natural",
        style="natural_korean",
        query="이종 정합 화면을 열 때 strID가 비어 있으면 어떻게 동작하나?",
        answer="ImageMatchingMgr.DisplayView에서 imageType이 Heterogeneous이고 strID가 비어 있으면 WinImageMatching을 열고 SelectHeterogeneousTab()을 호출한 뒤 VmMain으로 창을 표시한다. strID가 있으면 DisplayViewHeterogeneous로 분기한다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Mgrs\ImageMatching\ImageMatchingMgr.cs"],
    ),
    EvalCase(
        case_id="hetero_view_anchored",
        style="symbol_anchored",
        query="ImageMatchingMgr.DisplayView에서 Heterogeneous + empty strID는 어떻게 처리되나?",
        answer="Heterogeneous 모드에서 strID가 비어 있으면 WinImageMatching을 만든 뒤 SelectHeterogeneousTab()을 호출하고 VmMain을 바인딩해 보여준다.",
        expected_paths=[r"D:\Pixoneer_Source\MATR_Source\src\MATR\MATR\Mgrs\ImageMatching\ImageMatchingMgr.cs"],
    ),
]


def iter_source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if any(part.lower() in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def collect_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="cp949", errors="ignore").splitlines()


def build_hits(service: CodeToolService, root: Path, query: str, limit: int = 20) -> List[Hit]:
    query_tokens = _query_score_tokens(query)
    symbol_candidates = extract_symbol_query_candidates(query, max_candidates=2)
    hits_by_key: Dict[tuple[str, int], Hit] = {}

    def add_hit(path: Path, line_no: int, text: str, score: float) -> None:
        key = (str(path), line_no)
        current = hits_by_key.get(key)
        if current is None or score > current.score:
            hits_by_key[key] = Hit(path=path, line_no=line_no, text=text.strip(), score=score)

    for path in iter_source_files(root):
        lines = collect_lines(path)
        path_lower = path.as_posix().lower()
        for idx, line in enumerate(lines, 1):
            lowered = line.lower()
            if query_tokens and not any(token in lowered or token in path_lower for token in query_tokens):
                continue
            score = service._score_line(line, file_path=path, query_text=query, hit_kind="search")
            if score > 0:
                add_hit(path, idx, line, score)

        for symbol in symbol_candidates:
            for pattern_kind, pattern in service._definition_patterns(symbol):
                compiled = re.compile(pattern, flags=re.IGNORECASE)
                for idx, line in enumerate(lines, 1):
                    if not compiled.search(line):
                        continue
                    score = service._definition_score(line, symbol, path, pattern_kind)
                    if score > 0:
                        add_hit(path, idx, line, score)

    hits = sorted(hits_by_key.values(), key=lambda item: item.score, reverse=True)
    return hits[:limit]


def rank_case_hits(service: CodeToolService, root: Path, case: EvalCase, limit: int = 8) -> List[Hit]:
    hits = build_hits(service, root, case.query, limit=max(20, limit * 3))
    preferred = extract_symbol_query_candidates(case.query, max_candidates=1)
    matches = [
        {"path": str(hit.path), "line_range": f"{hit.line_no}-{hit.line_no}", "match": hit.text, "base_score": hit.score}
        for hit in hits
    ]
    ranked = prioritize_usage_matches(
        matches,
        query_text=case.query,
        preferred_symbol=(preferred[0] if preferred else ""),
    )
    score_by_key = {(str(hit.path), hit.line_no): hit.score for hit in hits}
    ranked_hits: List[Hit] = []
    for row in ranked:
        path = Path(str(row.get("path") or ""))
        start = int(str(row.get("line_range") or "1-1").split("-", 1)[0])
        ranked_hits.append(
            Hit(
                path=path,
                line_no=start,
                text=str(row.get("match") or ""),
                score=score_by_key.get((str(path), start), 0.0),
            )
        )
    return ranked_hits[:limit]


def top_unique_paths(hits: Sequence[Hit], limit: int = 3) -> List[str]:
    seen = set()
    paths: List[str] = []
    for hit in hits:
        value = str(hit.path)
        if value in seen:
            continue
        seen.add(value)
        paths.append(value)
        if len(paths) >= limit:
            break
    return paths


def evaluate_case(service: CodeToolService, root: Path, case: EvalCase) -> Dict[str, object]:
    ranked_hits = rank_case_hits(service, root, case, limit=8)
    top_paths = top_unique_paths(ranked_hits, limit=3)
    expected = set(case.expected_paths)
    top1 = top_paths[:1]
    return {
        "case_id": case.case_id,
        "style": case.style,
        "query": case.query,
        "answer": case.answer,
        "expected_paths": list(case.expected_paths),
        "top_paths": top_paths,
        "top_hit": ranked_hits[0].text if ranked_hits else "",
        "hit_top1": any(path in expected for path in top1),
        "hit_top3": any(path in expected for path in top_paths),
    }


def print_report(results: Sequence[Dict[str, object]]) -> None:
    total = len(results)
    top1 = sum(1 for row in results if row["hit_top1"])
    top3 = sum(1 for row in results if row["hit_top3"])
    print(f"Overall: top1={top1}/{total}, top3={top3}/{total}")

    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in results:
        grouped[str(row["style"])].append(row)

    for style, rows in grouped.items():
        style_top1 = sum(1 for row in rows if row["hit_top1"])
        style_top3 = sum(1 for row in rows if row["hit_top3"])
        print(f"{style}: top1={style_top1}/{len(rows)}, top3={style_top3}/{len(rows)}")

    print()
    for row in results:
        print(f"[{row['case_id']}] {row['query']}")
        print(f"  answer: {row['answer']}")
        print(f"  expected: {', '.join(row['expected_paths'])}")
        print(f"  top_paths: {', '.join(row['top_paths']) if row['top_paths'] else '(none)'}")
        print(f"  hit_top1={row['hit_top1']} hit_top3={row['hit_top3']}")
        if row["top_hit"]:
            print(f"  top_hit_line: {row['top_hit']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=r"D:\Pixoneer_Source\MATR_Source\src\MATR",
        help="Path to MATR source root",
    )
    args = parser.parse_args()

    root = Path(args.root)
    service = CodeToolService([], max_results=8)
    results = [evaluate_case(service, root, case) for case in CASES]
    print_report(results)


if __name__ == "__main__":
    main()
