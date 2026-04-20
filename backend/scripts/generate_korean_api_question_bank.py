import json
import math
import re
from collections import defaultdict
from pathlib import Path

from app.services.wiki.methods_index import build_methods_index_from_raw_source


SOURCE_ROOT = Path(r"C:\Users\p22418\Documents\Amaranth10\Source\Source")
OUTPUT_DIR = Path(r"D:\Pixoneer_Source\PIX_RAG_Source\.tmp\korean-api-question-bank")
QUESTION_LIMIT = 1000


VERB_TRANSLATIONS = {
    "Add": "추가",
    "Append": "추가",
    "Attach": "붙이기",
    "Begin": "시작",
    "Calc": "계산",
    "Calculate": "계산",
    "Capture": "캡처",
    "Change": "변경",
    "Check": "확인",
    "Clear": "초기화",
    "Clone": "복제",
    "Close": "닫기",
    "Convert": "변환",
    "Create": "생성",
    "Decode": "디코드",
    "Delete": "삭제",
    "Destory": "삭제",
    "Destroy": "삭제",
    "Disable": "비활성화",
    "Draw": "그리기",
    "Edit": "편집",
    "Enable": "활성화",
    "Encode": "인코드",
    "Export": "내보내기",
    "Find": "찾기",
    "Fit": "맞추기",
    "Gen": "생성",
    "Get": "가져오기",
    "Hit": "히트테스트",
    "Initialize": "초기화",
    "Invalidate": "갱신",
    "Is": "확인",
    "Load": "로드",
    "Lock": "잠그기",
    "Merge": "병합",
    "Move": "이동",
    "New": "생성",
    "Open": "열기",
    "Pause": "일시정지",
    "Play": "재생",
    "Print": "출력",
    "Read": "읽기",
    "Register": "등록",
    "Remove": "제거",
    "Render": "렌더링",
    "Reset": "초기화",
    "Resume": "재개",
    "Rotate": "회전",
    "Save": "저장",
    "Select": "선택",
    "Set": "설정",
    "Show": "표시",
    "Start": "시작",
    "Stop": "중지",
    "Transform": "변환",
    "Unlock": "잠금해제",
    "Update": "업데이트",
    "Use": "사용",
    "Write": "쓰기",
    "Zoom": "확대축소",
}


def split_identifier_parts(value: str):
    text = str(value or "").strip()
    if not text:
        return []
    return re.findall(r"[A-Z]+(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+|\d+", text)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def module_name_from_record(record: dict) -> str:
    source_refs = record.get("source_refs") if isinstance(record.get("source_refs"), list) else []
    for source_ref in source_refs:
        path = str(source_ref.get("path") or "").strip()
        if path.startswith("Source/"):
            parts = path.split("/")
            if len(parts) >= 2:
                return parts[1]
    doc_path = str(record.get("doc_path") or "").strip()
    if doc_path.startswith("Source/"):
        parts = doc_path.split("/")
        if len(parts) >= 2:
            return parts[1]
    return ""


def classify_record(record: dict) -> str:
    member = str(record.get("member_name") or "").strip()
    type_name = str(record.get("type_name") or "").strip()
    declaration = str(record.get("declaration") or "").strip()
    if not member:
        return "unknown"
    if member == type_name or member == f"~{type_name}":
        return "constructor"
    if declaration.lower().startswith("property "):
        return "property"
    return "method"


def member_core_phrase(record: dict) -> str:
    member = str(record.get("member_name") or "").strip()
    parts = split_identifier_parts(member)
    if not parts:
        return member
    verb = parts[0]
    rest = " ".join(parts[1:]).strip()
    action = VERB_TRANSLATIONS.get(verb, "")
    if action and rest:
        return f"{rest} {action}"
    if action:
        return action
    return " ".join(parts)


def build_question_templates(record: dict):
    type_name = str(record.get("type_name") or "").strip()
    member = str(record.get("member_name") or "").strip()
    symbol = str(record.get("qualified_symbol") or "").strip()
    kind = classify_record(record)
    core_phrase = member_core_phrase(record)

    if kind == "constructor":
        return [
            f"{type_name} 객체는 어떻게 생성해?",
            f"{type_name} 인스턴스 만드는 방법 알려줘",
            f"{type_name} 생성자 사용법 알려줘",
            f"{type_name} 초기화는 어떻게 해?",
        ]

    if kind == "property":
        return [
            f"{type_name}의 {member} 값은 어떻게 확인해?",
            f"{type_name}.{member} 속성은 어떻게 써?",
            f"{type_name}에서 {member} 설정하는 방법 알려줘",
            f"{symbol} 사용법 알려줘",
        ]

    questions = [
        f"{type_name}에서 {core_phrase} 하는 방법 알려줘",
        f"{type_name}.{member} 사용법 알려줘",
        f"{symbol}는 어떻게 써?",
        f"{type_name}에서 {member} 호출 예시 보여줘",
    ]

    lowered = member.lower()
    if lowered.startswith("load"):
        questions.extend([
            f"{type_name}로 파일 로드하는 방법 알려줘",
            f"{type_name}의 {member}로 데이터를 여는 방법 알려줘",
        ])
    if lowered.startswith("save"):
        questions.extend([
            f"{type_name}로 결과 저장하는 방법 알려줘",
            f"{type_name}의 {member} 사용 예시 보여줘",
        ])
    if lowered.startswith("get"):
        questions.extend([
            f"{type_name}에서 {core_phrase} 하는 방법 알려줘",
            f"{type_name}.{member}로 값을 읽는 방법 알려줘",
        ])
    if lowered.startswith("set"):
        questions.extend([
            f"{type_name}에서 {core_phrase} 하는 방법 알려줘",
            f"{type_name}.{member}로 설정값 바꾸는 예시 보여줘",
        ])
    if lowered.startswith("add"):
        questions.extend([
            f"{type_name}에 항목 추가하는 방법 알려줘",
            f"{type_name}.{member}로 레이어나 객체 붙이는 방법 알려줘",
        ])
    if lowered.startswith("remove"):
        questions.extend([
            f"{type_name}에서 항목 제거하는 방법 알려줘",
            f"{type_name}.{member}로 삭제하는 예시 보여줘",
        ])
    if lowered.startswith("transform"):
        questions.extend([
            f"{type_name}로 좌표 변환하는 방법 알려줘",
            f"{type_name}.{member} 호출 방법 알려줘",
        ])
    if lowered.startswith("zoom"):
        questions.extend([
            f"{type_name}에서 화면에 맞게 확대축소하는 방법 알려줘",
            f"{type_name}.{member}로 뷰 맞추는 방법 알려줘",
        ])
    if lowered.startswith("enable") or lowered.startswith("disable"):
        questions.extend([
            f"{type_name}에서 기능 {core_phrase} 하는 방법 알려줘",
            f"{type_name}.{member}로 옵션 켜고 끄는 방법 알려줘",
        ])
    return questions


def record_priority(record: dict):
    module_name = module_name_from_record(record)
    kind = classify_record(record)
    member = str(record.get("member_name") or "").strip()
    kind_rank = {"method": 0, "property": 1, "constructor": 2}.get(kind, 3)
    member_rank = 0 if not member.startswith("~") else 1
    return (module_name.lower(), kind_rank, member_rank, str(record.get("qualified_symbol") or "").lower())


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records = build_methods_index_from_raw_source(SOURCE_ROOT)
    sorted_records = sorted(records, key=record_priority)

    module_buckets = defaultdict(list)
    for record in sorted_records:
        module_name = module_name_from_record(record) or "unknown"
        module_buckets[module_name].append(record)

    ordered_records = []
    bucket_positions = {key: 0 for key in module_buckets}
    bucket_keys = sorted(module_buckets.keys())
    while len(ordered_records) < len(sorted_records):
        progress = False
        for key in bucket_keys:
            pos = bucket_positions[key]
            bucket = module_buckets[key]
            if pos >= len(bucket):
                continue
            ordered_records.append(bucket[pos])
            bucket_positions[key] += 1
            progress = True
        if not progress:
            break

    questions = []
    seen = set()
    for record in ordered_records:
        module_name = module_name_from_record(record)
        symbol = str(record.get("qualified_symbol") or "").strip()
        declaration = clean_text(record.get("declaration") or "")
        for query in build_question_templates(record):
            normalized_query = clean_text(query)
            if not normalized_query:
                continue
            key = f"{symbol.lower()}::{normalized_query.lower()}"
            if key in seen:
                continue
            seen.add(key)
            questions.append(
                {
                    "id": len(questions) + 1,
                    "module": module_name,
                    "typeName": str(record.get("type_name") or "").strip(),
                    "memberName": str(record.get("member_name") or "").strip(),
                    "qualifiedSymbol": symbol,
                    "declaration": declaration,
                    "docPath": str(record.get("doc_path") or "").strip(),
                    "query": normalized_query,
                }
            )
            if len(questions) >= QUESTION_LIMIT:
                break
        if len(questions) >= QUESTION_LIMIT:
            break

    txt_path = OUTPUT_DIR / "questions-1000.txt"
    json_path = OUTPUT_DIR / "questions-1000.json"
    meta_path = OUTPUT_DIR / "meta.json"

    txt_path.write_text("\n".join(item["query"] for item in questions) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path.write_text(
        json.dumps(
            {
                "sourceRoot": str(SOURCE_ROOT),
                "recordCount": len(records),
                "questionCount": len(questions),
                "moduleCount": len(module_buckets),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"questionCount": len(questions), "txtPath": str(txt_path), "jsonPath": str(json_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
