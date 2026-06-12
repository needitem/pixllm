"""C++/CLI 헤더 파일을 파싱해서 "메서드 인덱스"를 생성하는 모듈.

Pixoneer NXDL SDK는 C++/CLI(.NET managed C++)로 작성되어 있다. 이 모듈은
원본 소스 트리(raw_root)를 정규식 기반으로 파싱해서, `public ref class`
타입의 public 멤버(메서드/프로퍼티/생성자) 선언을 추출하고 레코드 리스트를
만든다. 이 인덱스는 service.py가 `.runtime/methods_index.json`으로 저장하며,
이후 모든 심볼 검색(코드 검색/읽기/타입 그래프 API)의 기반 데이터가 된다.

전체 흐름 (진입점: build_methods_index_from_raw_source):
    1. `_index_cpp_implementations()` — 모든 .cpp 파일을 훑어
       `Class::Method(` 패턴이 나오는 위치를 (클래스명, 메서드명) ->
       [파일경로, 줄번호] 매핑으로 미리 인덱싱한다.
    2. `_extract_header_method_records()` — 모든 .h 파일을 줄 단위
       스테이트 머신으로 파싱한다. 블록 주석(/* */) 제거, `///` XML
       문서주석 수집, 접근지정자(public/protected/private) 추적, 중괄호
       깊이 기반 namespace/class 스택 관리를 수행하면서 public 구역의
       멤버 선언만 골라낸다.
    3. `_build_record()` — 선언문 하나를 레코드 dict로 변환한다.
       1번에서 만든 구현 인덱스를 이용해 헤더 선언과 .cpp 구현 위치를
       짝지어 source_refs에 담고, XML 문서주석(`<summary>`, `<param>`,
       `<returns>`)을 구조화해서 doc 필드에 넣는다.
    4. 최종 레코드들을 qualified_symbol 기준으로 정렬해 반환한다.

각 레코드에는 정규화된 타입/심볼 이름(qualified_type, qualified_symbol),
선언문 원문(declaration), 선언/구현 위치(source_refs), 구조화된 문서주석
(doc), 그리고 LLM에게 보여줄 마크다운 요약(text)이 포함된다.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# XML/HTML 태그(<summary>, <para> 등)를 통째로 매칭하는 정규식.
# 문서주석 텍스트에서 태그를 제거하고 순수 텍스트만 남길 때 사용한다.
_SUMMARY_TAG_RE = re.compile(r"<[^>]+>")
# `namespace Pixoneer { ...` 같은 네임스페이스 선언 줄을 매칭한다.
# 그룹 1 = 네임스페이스 이름.
_NAMESPACE_DECL_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)\b")
# C++/CLI의 managed 클래스 선언(`public ref class XImage ...`)을 매칭한다.
# public ref class만 인덱싱 대상이며, 그룹 1 = 클래스 이름.
_CLASS_DECL_RE = re.compile(r"^\s*public\s+ref\s+class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
# 접근지정자 한 줄(`public:`, `protected:`, `private:`)을 매칭한다.
# 줄 끝의 // 주석은 허용. 그룹 1 = 접근지정자 이름.
_ACCESS_RE = re.compile(r"^\s*(public|protected|private)\s*:\s*(?://.*)?$")
# 생성자/소멸자 선언을 매칭하는 정규식 "템플릿".
# {name} 자리에 클래스 이름을 채워 컴파일한다(소멸자 `~Name`도 포함).
# suffix는 `override`, `abstract`, `= 0`(순수 가상) 같은 뒷부분 키워드.
_CTOR_RE_TEMPLATE = r"^(?P<name>{name}|~{name})\s*\((?P<args>.*)\)\s*(?P<suffix>(?:\s+[A-Za-z_][A-Za-z0-9_]*)*(?:\s*=\s*0)?)\s*;\s*$"
# 일반 메서드 선언을 매칭한다. prefix = 반환 타입 및 수식어(virtual 등),
# name = 메서드 이름, args = 괄호 안 인자 목록, suffix = override/= 0 등.
# 세미콜론으로 끝나는 "선언"만 매칭한다(본문 있는 정의는 제외).
_METHOD_RE = re.compile(
    r"^(?P<prefix>.+?)\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<args>.*)\)\s*(?P<suffix>(?:\s+[A-Za-z_][A-Za-z0-9_]*)*(?:\s*=\s*0)?)\s*;\s*$"
)
# C++/CLI property 선언(`property int Width { ... }` 또는 `property int Width;`)을
# 매칭한다. type = 프로퍼티 타입, name = 프로퍼티 이름, rest = 본문 또는 세미콜론.
_PROPERTY_RE = re.compile(
    r"^property\s+(?P<type>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<rest>\{.*\};?|;)\s*$"
)
# .cpp 파일에서 `Class::Method(` 형태의 구현부 시작 위치를 찾는 정규식.
# 소멸자 구현(`Class::~Class(`)도 매칭하기 위해 method 쪽에 `~?` 허용.
_IMPLEMENTATION_RE = re.compile(
    r"(?P<class>[A-Za-z_][A-Za-z0-9_]*)::(?P<method>~?[A-Za-z_][A-Za-z0-9_]*)\s*\("
)
# 이 접두사로 시작하는 선언문은 메서드 인덱싱 대상에서 제외한다.
# (property는 _should_skip_statement에서 먼저 별도 처리되어 통과된다.
#  event/delegate/enum/literal/typedef/using은 메서드가 아니므로 스킵.)
_SKIP_DECLARATION_PREFIXES = (
    "property ",
    "event ",
    "delegate ",
    "enum class ",
    "literal ",
    "typedef ",
    "using ",
)
# 소스 파일 디코딩 시도 순서. NXDL 소스에 한국어 주석이 섞여 있어
# utf-8 실패 시 한국어 레거시 인코딩(cp949, euc-kr)을 차례로 시도한다.
_RAW_SOURCE_ENCODINGS = ("utf-8", "cp949", "euc-kr")


def _read_source_text(path: Path) -> str:
    """소스 파일을 읽어 문자열로 디코딩한다.

    한국어 주석이 포함된 소스가 많아 utf-8 -> cp949 -> euc-kr 순서로
    디코딩을 시도하고, 전부 실패하면 utf-8 + errors="replace"로
    깨진 문자를 치환해서라도 반환한다(파싱이 중단되지 않도록).

    파라미터:
        path: 읽을 소스 파일 경로.
    반환값:
        디코딩된 파일 전체 내용 문자열.
    """
    data = path.read_bytes()
    # 우선순위 인코딩을 차례로 시도한다.
    for encoding in _RAW_SOURCE_ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    # 모든 인코딩이 실패하면 깨진 바이트를 치환 문자로 대체해서 반환.
    return data.decode("utf-8", errors="replace")


def _source_path(raw_root: Path, file_path: Path) -> str:
    """절대 파일 경로를 인덱스에 저장할 표준 상대 경로 문자열로 변환한다.

    raw_root 기준 상대 경로 앞에 "Source/" 접두사를 붙인 POSIX 형식
    경로(예: "Source/NXDL/XImage.h")를 반환한다. 레코드의 doc_path와
    source_refs.path에 일관된 형식으로 쓰인다.
    """
    return f"Source/{file_path.relative_to(raw_root).as_posix()}"


def _clean_summary(lines: Sequence[str]) -> str:
    """`///` 문서주석 줄들에서 태그를 제거하고 한 줄 요약 텍스트를 만든다.

    `<summary>` 블록 파싱(_doc_comment)이 실패했을 때의 폴백(fallback)으로,
    `///`로 시작하는 줄만 골라 XML 태그를 전부 벗겨내고 공백을 정규화한 뒤
    공백 한 칸으로 이어붙인 문자열을 반환한다.

    파라미터:
        lines: 선언 직전에 수집된 원본 주석 줄들.
    반환값:
        태그가 제거된 평문 요약 문자열(없으면 빈 문자열).
    """
    cleaned: List[str] = []
    for raw in lines:
        text = str(raw or "").strip()
        # /// 로 시작하지 않는 줄은 문서주석이 아니므로 무시.
        if not text.startswith("///"):
            continue
        # "///" 접두사 제거 후 XML 태그를 공백으로 치환.
        text = text[3:].strip()
        text = _SUMMARY_TAG_RE.sub(" ", text)
        # 연속 공백을 하나로 정규화.
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cleaned.append(text)
    return " ".join(cleaned).strip()


def _clean_doc_text(value: str) -> str:
    """문서주석 텍스트 조각에서 XML 태그를 제거하고 공백을 정규화한다.

    `<summary>`/`<returns>`/`<param>` 블록 내부 텍스트를 사람이 읽을 수
    있는 한 줄 평문으로 다듬을 때 공통으로 사용하는 헬퍼.
    """
    text = str(value or "")
    text = _SUMMARY_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _doc_lines(lines: Sequence[str]) -> List[str]:
    """주석 줄들에서 `///` 접두사만 벗겨낸 "본문 줄" 리스트를 만든다.

    XML 태그 구조(<summary>...</summary> 등)는 그대로 보존한 채
    접두사만 제거하므로, 이후 _extract_tag_blocks / _extract_inline_tags가
    태그 단위로 파싱할 수 있는 입력이 된다.
    """
    cleaned: List[str] = []
    for raw in lines:
        text = str(raw or "").strip()
        if text.startswith("///"):
            text = text[3:].strip()
        cleaned.append(text)
    return cleaned


def _extract_tag_blocks(lines: Sequence[str], tag: str) -> List[str]:
    """여러 줄에 걸칠 수 있는 XML 태그 블록의 내용을 모두 추출한다.

    예: tag="summary"이면 `<summary> ... </summary>` 사이의 텍스트를
    (여는 태그와 닫는 태그가 서로 다른 줄에 있어도) 찾아서 반환한다.
    한 줄에 블록이 여러 개 있거나, 블록이 줄 중간에서 열리고 닫히는
    경우까지 처리하기 위해 줄 안에서 while 루프로 반복 스캔한다.

    파라미터:
        lines: `///` 접두사가 제거된 문서주석 본문 줄들(_doc_lines 결과).
        tag: 추출할 태그 이름(예: "summary", "returns").
    반환값:
        각 블록 내부 텍스트의 리스트(빈 블록은 제외).
    """
    blocks: List[str] = []
    # in_block: 현재 여는 태그는 만났지만 닫는 태그는 아직 못 만난 상태인지.
    in_block = False
    # buffer: 블록이 여러 줄에 걸칠 때 내용을 누적하는 버퍼.
    buffer: List[str] = []
    open_re = re.compile(rf"<{tag}\b[^>]*>", re.IGNORECASE)
    close_re = re.compile(rf"</{tag}>", re.IGNORECASE)
    for line in lines:
        text = str(line or "")
        # 한 줄 안에 태그가 여러 번 나올 수 있으므로 남은 텍스트가
        # 없어질 때까지 반복해서 스캔한다.
        while text:
            if not in_block:
                # 블록 밖: 여는 태그를 찾는다. 없으면 이 줄은 끝.
                open_match = open_re.search(text)
                if not open_match:
                    break
                # 여는 태그 이후 부분부터 블록 내용으로 취급.
                text = text[open_match.end() :]
                in_block = True
            # 블록 안: 같은 (남은) 텍스트에서 닫는 태그를 찾는다.
            close_match = close_re.search(text)
            if close_match:
                # 닫는 태그 앞까지가 블록 내용 — 버퍼에 모아 하나의 블록으로 확정.
                buffer.append(text[: close_match.start()])
                block = "\n".join(buffer).strip()
                if block:
                    blocks.append(block)
                buffer = []
                # 닫는 태그 뒤의 나머지 텍스트로 계속 스캔(같은 줄에 또 블록이 있을 수 있음).
                text = text[close_match.end() :]
                in_block = False
            else:
                # 닫는 태그가 이 줄에 없음 — 줄 전체를 버퍼에 쌓고 다음 줄로.
                buffer.append(text)
                break
    return blocks


def _extract_inline_tags(lines: Sequence[str], tag: str) -> List[Dict[str, str]]:
    """한 줄 안에서 열리고 닫히는 인라인 XML 태그들을 구조화해서 추출한다.

    주 용도는 `<param name="x">설명</param>` 파싱. 태그의 name 속성
    (큰따옴표/작은따옴표 모두 지원)과 내부 텍스트를 뽑아
    {"name": ..., "description": ...} dict 리스트로 반환한다.
    (_extract_tag_blocks와 달리 여러 줄에 걸친 태그는 처리하지 않는다.)

    파라미터:
        lines: `///` 접두사가 제거된 문서주석 본문 줄들.
        tag: 추출할 태그 이름(예: "param").
    반환값:
        name/description을 담은 dict 리스트(둘 다 비어 있으면 제외).
    """
    pattern = re.compile(rf"<{tag}\b([^>]*)>(.*?)</{tag}>", re.IGNORECASE)
    name_pattern = re.compile(r'name\s*=\s*"([^"]+)"|name\s*=\s*\'([^\']+)\'', re.IGNORECASE)
    items: List[Dict[str, str]] = []
    for line in lines:
        # 한 줄에 태그가 여러 개 있어도 finditer로 전부 수집.
        for match in pattern.finditer(str(line or "")):
            attrs = str(match.group(1) or "")
            # 속성 문자열에서 name="..." 또는 name='...' 값을 추출.
            name_match = name_pattern.search(attrs)
            name = ""
            if name_match:
                name = str(name_match.group(1) or name_match.group(2) or "").strip()
            text = _clean_doc_text(match.group(2) or "")
            if name or text:
                item = {"description": text}
                if name:
                    item["name"] = name
                items.append(item)
    return items


def _doc_comment(lines: Sequence[str]) -> Dict[str, Any]:
    """`///` XML 문서주석 줄 묶음을 구조화된 dict로 변환한다.

    `<summary>` 블록 -> "summary", `<param name="...">` 태그 ->
    "parameters" 리스트, `<returns>` 블록 -> "returns" 키로 정리한다.
    `<summary>` 태그가 아예 없는 주석이면 _clean_summary로 전체 텍스트를
    요약으로 사용하는 폴백을 적용한다.

    파라미터:
        lines: 선언 직전에 수집된 원본 `///` 주석 줄들.
    반환값:
        {"summary": str, ["parameters": [...]], ["returns": str]} 형태의 dict.
        (parameters/returns는 내용이 있을 때만 포함된다.)
    """
    # /// 접두사를 벗겨 태그 파싱이 가능한 본문 줄로 만든다.
    cleaned_lines = _doc_lines(lines)
    summary_blocks = [_clean_doc_text(block) for block in _extract_tag_blocks(cleaned_lines, "summary")]
    return_blocks = [_clean_doc_text(block) for block in _extract_tag_blocks(cleaned_lines, "returns")]

    summary = " ".join(block for block in summary_blocks if block).strip()
    # <summary> 블록이 없으면 주석 전체 텍스트를 요약으로 사용(폴백).
    if not summary:
        summary = _clean_summary(lines)
    doc: Dict[str, Any] = {"summary": summary}
    params = _extract_inline_tags(cleaned_lines, "param")
    if params:
        doc["parameters"] = params
    returns = " ".join(block for block in return_blocks if block).strip()
    if returns:
        doc["returns"] = returns
    return doc


def _index_cpp_implementations(raw_root: Path) -> Dict[Tuple[str, str], List[Dict[str, str]]]:
    """소스 트리의 모든 .cpp 파일에서 메서드 구현 위치를 미리 인덱싱한다.

    각 줄에서 `Class::Method(` 패턴(_IMPLEMENTATION_RE)을 찾아
    (클래스명, 메서드명) -> [{"path": 상대경로, "line_range": "N-N"}, ...]
    매핑을 만든다. 이후 _build_record가 헤더 선언과 구현 위치를 짝지을 때
    이 인덱스를 조회한다. 줄 단위 정규식 매칭이므로 호출부도 일부 섞일 수
    있지만, 보통 구현부 시작 줄이 먼저/함께 잡힌다.

    파라미터:
        raw_root: 원본 소스 트리 루트 디렉터리.
    반환값:
        (클래스명, 메서드명) 키 -> 구현 위치 dict 리스트.
    """
    index: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    # 결과가 결정적(deterministic)이도록 파일을 정렬 순서로 순회.
    for cpp_path in sorted(raw_root.rglob("*.cpp")):
        try:
            lines = _read_source_text(cpp_path).splitlines()
        except Exception:
            # 읽기 실패한 파일은 건너뛴다(전체 인덱싱은 계속).
            continue
        source_path = _source_path(raw_root, cpp_path)
        for line_number, line in enumerate(lines, 1):
            match = _IMPLEMENTATION_RE.search(line)
            if not match:
                continue
            key = (str(match.group("class") or "").strip(), str(match.group("method") or "").strip())
            if not key[0] or not key[1]:
                continue
            # 같은 키의 구현 후보를 발견 순서대로 누적한다.
            index.setdefault(key, []).append(
                {
                    "path": source_path,
                    "line_range": f"{line_number}-{line_number}",
                }
            )
    return index


def _should_skip_statement(statement: str) -> bool:
    """선언문이 메서드 인덱싱 대상에서 제외돼야 하는지 판정한다.

    제외(True) 조건:
        - 빈 문자열
        - 접근지정자 줄(private:/protected:/internal:)이 섞여 들어온 경우
        - 괄호가 없거나 세미콜론으로 끝나지 않는 줄(메서드 선언이 아님)
        - event/delegate/enum class/literal/typedef/using 선언
        - operator 오버로드(연산자는 인덱싱하지 않음)
    단, property 선언은 괄호가 없어도 인덱싱 대상이므로 가장 먼저
    False를 반환해 통과시킨다.

    파라미터:
        statement: 공백이 정규화된 선언문 한 줄.
    반환값:
        스킵해야 하면 True, 인덱싱 후보면 False.
    """
    lowered = str(statement or "").strip().lower()
    if not lowered:
        return True
    # 접근지정자 줄이 선언문으로 잘못 모인 경우 제외.
    if lowered.startswith(("private:", "protected:", "internal:")):
        return True
    # property는 괄호/세미콜론 검사 전에 먼저 통과시킨다.
    if lowered.startswith("property "):
        return False
    # 괄호가 없거나 ';'로 끝나지 않으면 메서드 선언이 아니다.
    if "(" not in lowered or not lowered.endswith(";"):
        return True
    # event/delegate/typedef 등 메서드가 아닌 선언 제외.
    if any(lowered.startswith(prefix) for prefix in _SKIP_DECLARATION_PREFIXES):
        return True
    # 연산자 오버로드는 인덱싱하지 않는다.
    if "operator" in lowered:
        return True
    return False


def _build_record(
    *,
    raw_root: Path,
    header_path: Path,
    declaration_line: int,
    namespace_parts: Sequence[str],
    class_name: str,
    statement: str,
    summary_lines: Sequence[str],
    impl_index: Dict[Tuple[str, str], List[Dict[str, str]]],
) -> Optional[Dict[str, Any]]:
    """헤더에서 추출한 선언문 하나를 메서드 인덱스 레코드 dict로 변환한다.

    처리 순서:
        1. 공백을 정규화하고 _should_skip_statement로 제외 대상 필터링.
        2. 멤버 이름 추출 — property -> 생성자/소멸자 -> 일반 메서드
           순서로 정규식 매칭을 시도한다(어느 것도 안 맞으면 None 반환).
        3. 네임스페이스.클래스.멤버 형태의 정규화된 심볼 이름 생성.
        4. impl_index에서 (클래스, 멤버) 키로 .cpp 구현 위치를 찾아
           최대 6개까지 source_refs에 연결(첫 항목은 항상 헤더 선언 위치).
        5. XML 문서주석을 구조화(doc)하고, LLM 검색 결과로 보여줄
           마크다운 text 필드(이름/설명/선언 위치/구현 위치)를 생성.

    파라미터:
        raw_root: 소스 트리 루트(상대 경로 계산용).
        header_path: 선언이 들어 있는 헤더 파일 경로.
        declaration_line: 선언이 시작되는 줄 번호(1부터).
        namespace_parts: 선언을 감싸는 네임스페이스 이름들(바깥->안 순서).
        class_name: 선언이 속한 클래스 이름.
        statement: 여러 줄을 합쳐 만든 선언문 전체 문자열.
        summary_lines: 선언 직전에 수집된 `///` 문서주석 줄들.
        impl_index: _index_cpp_implementations가 만든 구현 위치 인덱스.
    반환값:
        인덱스 레코드 dict, 또는 인덱싱 대상이 아니면 None.
    """
    # 여러 줄 선언을 합치며 생긴 연속 공백을 한 칸으로 정규화.
    normalized_statement = re.sub(r"\s+", " ", statement).strip()
    if _should_skip_statement(normalized_statement):
        return None

    member_name = ""
    declaration_text = normalized_statement
    # 1순위: property 선언 매칭.
    property_match = _PROPERTY_RE.match(normalized_statement)
    if property_match:
        member_name = str(property_match.group("name") or "").strip()
    else:
        # 2순위: 클래스 이름을 채워 만든 생성자/소멸자 정규식 매칭.
        ctor_re = re.compile(_CTOR_RE_TEMPLATE.format(name=re.escape(class_name)))
        ctor_match = ctor_re.match(normalized_statement)
        if ctor_match:
            member_name = str(ctor_match.group("name") or "").strip()
        else:
            # 3순위: 일반 메서드 선언 매칭. 실패하면 레코드 생성 포기.
            method_match = _METHOD_RE.match(normalized_statement)
            if not method_match:
                return None
            member_name = str(method_match.group("name") or "").strip()
    if not member_name:
        return None

    # "Namespace.Class" / "Namespace.Class.Member" 형태의 정규화 심볼 생성.
    qualified_type = ".".join([*namespace_parts, class_name])
    qualified_symbol = f"{qualified_type}.{member_name}"
    header_source = _source_path(raw_root, header_path)
    # XML 문서주석을 summary/parameters/returns로 구조화.
    doc = _doc_comment(summary_lines)
    description = str(doc.get("summary") or "").strip()
    # source_refs 첫 항목은 항상 헤더의 선언 위치.
    source_refs = [
        {
            "path": header_source,
            "line_range": f"{declaration_line}-{declaration_line}",
        }
    ]
    # 구현 인덱스에서 (클래스, 멤버) 키로 .cpp 구현 위치를 찾아
    # 최대 6개까지만 연결한다(과도한 후보 나열 방지).
    for item in impl_index.get((class_name, member_name), [])[:6]:
        source_refs.append(item)

    # LLM 검색 결과로 노출할 마크다운 텍스트 조립:
    # 멤버 이름 헤딩 + 설명 + 선언 위치 + 구현 위치 목록.
    text_lines = [f"## {member_name}"]
    if description:
        text_lines.append(f"- Description: {description}")
    text_lines.append(f"- Declaration: `{header_source}:{declaration_line}`")
    # source_refs[0]은 선언 위치이므로 그 뒤가 구현 위치들.
    impl_refs = [item for item in source_refs[1:]]
    if impl_refs:
        impl_text = ", ".join(f"`{item['path']}:{item['line_range'].split('-', 1)[0]}`" for item in impl_refs)
        text_lines.append(f"- Implementation: {impl_text}")

    return {
        "qualified_type": qualified_type,
        "type_name": class_name,
        "member_name": member_name,
        "qualified_symbol": qualified_symbol,
        "doc_path": header_source,
        "heading_path": f"{qualified_type} Methods > {member_name}",
        "text": "\n".join(text_lines),
        "source_refs": source_refs,
        "declaration": declaration_text,
        "doc": doc,
        "owner": {
            "namespace": ".".join(namespace_parts),
            "qualified_type": qualified_type,
            "type_name": class_name,
        },
    }


def _extract_header_method_records(
    *,
    raw_root: Path,
    header_path: Path,
    impl_index: Dict[Tuple[str, str], List[Dict[str, str]]],
) -> List[Dict[str, Any]]:
    """헤더 파일 하나를 줄 단위 스테이트 머신으로 파싱해 레코드들을 추출한다.

    이 모듈의 핵심 파서. 각 줄을 순회하면서 다음 상태를 유지/갱신한다:
        - in_block_comment: /* */ 블록 주석 내부 여부(주석 내용은 무시).
        - pending_summary: 선언 직전까지 모은 `///` 문서주석 줄들.
        - namespace_stack / class_stack: 현재 위치를 감싸는 네임스페이스와
          클래스의 스택. 각 항목은 자신이 열린 중괄호 깊이를 기억하고,
          중괄호가 그 깊이 아래로 닫히면 pop된다.
        - pending: "namespace/class 선언은 봤지만 아직 여는 중괄호 `{`를
          만나지 못한" 대기열. `{`를 만나는 순간 해당 깊이로 스택에 push.
        - class_stack 항목의 "access": 현재 접근지정자 구역. `public:`
          구역의 멤버만 인덱싱 대상이다(ref class 기본값은 private).
        - statement_lines: 여러 줄에 걸친 선언을 모으는 버퍼. `(`가 있는
          줄에서 수집을 시작하고 `;`를 만나면 flush_statement()로
          _build_record를 호출해 레코드를 만든다.
        - brace_depth: 파일 전체의 현재 중괄호 깊이.

    파라미터:
        raw_root: 소스 트리 루트(상대 경로 계산용).
        header_path: 파싱할 .h 파일 경로.
        impl_index: .cpp 구현 위치 인덱스(_build_record에 전달).
    반환값:
        이 헤더에서 추출한 메서드 인덱스 레코드 리스트.
    """
    try:
        lines = _read_source_text(header_path).splitlines()
    except Exception:
        # 읽을 수 없는 파일은 빈 결과로 건너뛴다.
        return []

    records: List[Dict[str, Any]] = []
    # (네임스페이스 이름, 열린 중괄호 깊이) 스택.
    namespace_stack: List[Tuple[str, int]] = []
    # 클래스 정보(name/depth/access/summary) dict의 스택. 중첩 클래스 대응.
    class_stack: List[Dict[str, Any]] = []
    # 선언은 봤지만 아직 '{'를 만나지 못한 namespace/class 대기열.
    # 각 항목: (종류, 이름, 클래스 문서주석 줄들).
    pending: List[Tuple[str, str, List[str]]] = []
    # 다음 선언에 붙일 후보로 모으는 중인 `///` 문서주석 줄들.
    pending_summary: List[str] = []
    # 파일 전체의 현재 중괄호 깊이.
    brace_depth = 0
    # 여러 줄에 걸친 선언문을 모으는 버퍼와, 그 선언의 문서주석/시작 줄.
    statement_lines: List[str] = []
    statement_summary: List[str] = []
    statement_start_line = 0
    # /* */ 블록 주석 내부 여부.
    in_block_comment = False

    def current_namespace() -> List[str]:
        """현재 위치를 감싸는 네임스페이스 이름 리스트(바깥->안)를 반환한다."""
        return [item[0] for item in namespace_stack]

    def current_class() -> Optional[Dict[str, Any]]:
        """현재 위치를 가장 안쪽에서 감싸는 클래스 정보를 반환한다(없으면 None)."""
        return class_stack[-1] if class_stack else None

    def flush_statement() -> None:
        """버퍼에 모인 선언문을 레코드로 확정하고 버퍼를 비운다.

        현재 클래스의 접근지정자 구역이 public일 때만 _build_record를
        호출하며, 성공하면 records에 추가한다. 어떤 경우든 선언 버퍼
        (statement_lines / statement_summary / statement_start_line)는
        초기화된다.
        """
        nonlocal statement_lines, statement_summary, statement_start_line
        if not statement_lines:
            return
        active_class = current_class()
        # public 구역의 멤버만 인덱싱 대상이다.
        if active_class and active_class.get("access") == "public":
            record = _build_record(
                raw_root=raw_root,
                header_path=header_path,
                declaration_line=statement_start_line or 1,
                namespace_parts=current_namespace(),
                class_name=str(active_class.get("name") or "").strip(),
                statement=" ".join(statement_lines),
                summary_lines=statement_summary,
                impl_index=impl_index,
            )
            if record:
                records.append(record)
        # 다음 선언 수집을 위해 버퍼 초기화.
        statement_lines = []
        statement_summary = []
        statement_start_line = 0

    for line_number, raw_line in enumerate(lines, 1):
        # --- 단계 1: /* */ 블록 주석 제거 ---
        if in_block_comment:
            # 블록 주석이 이 줄에서 닫히지 않으면 줄 전체를 건너뛴다.
            if "*/" not in raw_line:
                continue
            # 닫힌 위치 이후의 코드만 남기고 주석 상태 해제.
            raw_line = raw_line.split("*/", 1)[1]
            in_block_comment = False
        if "/*" in raw_line:
            before, after = raw_line.split("/*", 1)
            if "*/" in after:
                # 한 줄 안에서 열리고 닫히는 블록 주석 — 주석 부분만 제거.
                raw_line = before + after.split("*/", 1)[1]
            else:
                # 이 줄에서 열렸지만 닫히지 않음 — 앞부분만 남기고 주석 상태 진입.
                raw_line = before
                in_block_comment = True
        stripped = str(raw_line or "").strip()

        # --- 단계 2: `///` 문서주석 수집 ---
        # 문서주석 줄은 pending_summary에 쌓아 두고 다음 선언에 붙인다.
        if stripped.startswith("///"):
            pending_summary.append(stripped)
            continue

        active_class = current_class()
        # --- 단계 3: 접근지정자(public:/protected:/private:) 추적 ---
        access_match = _ACCESS_RE.match(stripped)
        if access_match and active_class:
            active_class["access"] = str(access_match.group(1) or "private").lower()
            # 접근지정자 줄을 만나면 모아둔 문서주석은 무효화.
            pending_summary = []
            continue

        # --- 단계 4: 네임스페이스/클래스 선언 감지 ---
        # 아직 '{'를 만나지 않았으므로 pending 대기열에 넣어 두고,
        # 아래 중괄호 스캔에서 '{'를 만날 때 실제 스택에 push한다.
        namespace_match = _NAMESPACE_DECL_RE.match(stripped)
        if namespace_match:
            pending.append(("namespace", str(namespace_match.group(1) or "").strip(), []))

        class_match = _CLASS_DECL_RE.match(stripped)
        if class_match:
            # 클래스 선언 직전의 문서주석은 클래스 설명으로 함께 보관.
            pending.append(("class", str(class_match.group(1) or "").strip(), list(pending_summary)))
            pending_summary = []

        # --- 단계 5: public 구역에서 멤버 선언 수집 ---
        if active_class and active_class.get("access") == "public":
            if statement_lines:
                # 이미 선언을 수집 중 — 이어지는 줄을 버퍼에 추가하고,
                # ';'를 만나면 선언이 끝난 것이므로 flush.
                statement_lines.append(stripped)
                if ";" in stripped:
                    flush_statement()
            else:
                # 새 선언 시작 후보: '('가 있고, // 주석이나
                # [attribute] 줄이 아닌 경우에만 수집을 시작한다.
                if "(" in stripped and not stripped.startswith("//") and not stripped.startswith("["):
                    statement_lines = [stripped]
                    # 직전까지 모은 문서주석을 이 선언의 것으로 확정.
                    statement_summary = list(pending_summary)
                    statement_start_line = line_number
                    pending_summary = []
                    # 한 줄로 끝나는 선언이면 즉시 flush.
                    if ";" in stripped:
                        flush_statement()
        elif stripped and not stripped.startswith("//") and not stripped.startswith("["):
            # public 구역 밖에서 일반 코드 줄을 만나면, 모아둔 문서주석은
            # 더 이상 다음 선언의 것이 아니므로 버린다.
            pending_summary = []

        # --- 단계 6: 중괄호 깊이 추적 및 namespace/class 스택 push/pop ---
        local_depth = brace_depth
        for char in raw_line:
            if char == "{":
                local_depth += 1
                # '{'를 만나면 대기 중이던 namespace/class를
                # 현재 깊이와 함께 스택에 push한다.
                if pending:
                    kind, name, summary_lines = pending.pop(0)
                    if kind == "namespace" and name:
                        namespace_stack.append((name, local_depth))
                    elif kind == "class" and name:
                        class_stack.append(
                            {
                                "name": name,
                                "depth": local_depth,
                                # ref class 멤버의 기본 접근 수준은 private.
                                "access": "private",
                                "summary": summary_lines,
                            }
                        )
            elif char == "}":
                local_depth -= 1
                # 닫힌 깊이보다 더 깊은 곳에서 열린 클래스/네임스페이스는
                # 스코프가 끝난 것이므로 스택에서 pop한다.
                while class_stack and int(class_stack[-1].get("depth") or 0) > local_depth:
                    class_stack.pop()
                while namespace_stack and namespace_stack[-1][1] > local_depth:
                    namespace_stack.pop()
        brace_depth = local_depth

    # 파일 끝에 도달 — 버퍼에 남은 선언이 있으면 마지막으로 flush.
    flush_statement()
    return records


def build_methods_index_from_raw_source(raw_root: Path) -> List[Dict[str, Any]]:
    """원본 소스 트리 전체에서 메서드 인덱스를 빌드한다(모듈의 진입점).

    동작:
        1. raw_root가 존재하는 디렉터리인지 확인(아니면 빈 리스트 반환).
        2. 모든 .cpp 파일을 스캔해 `Class::Method` 구현 위치 인덱스 생성.
        3. 모든 .h 파일을 파싱해 public ref class의 public 멤버 레코드 추출.
        4. qualified_symbol(및 heading_path) 기준으로 정렬해 반환.

    반환된 리스트는 service.py가 `.runtime/methods_index.json`으로
    직렬화해 저장하고, 심볼 검색 API의 기반 데이터로 사용한다.

    파라미터:
        raw_root: NXDL SDK 원본 소스 트리의 루트 디렉터리 경로.
    반환값:
        정렬된 메서드 인덱스 레코드(dict) 리스트.
    """
    root = Path(raw_root)
    if not root.exists() or not root.is_dir():
        return []

    # 1단계: .cpp 구현 위치 인덱스를 먼저 만들어 둔다.
    impl_index = _index_cpp_implementations(root)
    records: List[Dict[str, Any]] = []
    # 2단계: 헤더를 정렬 순서로 순회하며 레코드를 누적한다.
    for header_path in sorted(root.rglob("*.h")):
        records.extend(
            _extract_header_method_records(
                raw_root=root,
                header_path=header_path,
                impl_index=impl_index,
            )
        )

    # 3단계: 심볼 이름 기준으로 정렬해 결정적인 출력 순서를 보장한다.
    records.sort(
        key=lambda item: (
            str(item.get("qualified_symbol") or ""),
            str(item.get("heading_path") or ""),
        )
    )
    return records
