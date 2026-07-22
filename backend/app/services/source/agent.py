"""PIXLLM 백엔드 소스 에이전트 — `POST /api/v1/source/answer` 엔드포인트의 본체.

이 모듈은 ReAct 스타일 tool-calling 루프를 구현한다:

1. vLLM(OpenAI 호환 chat/completions API) 모델에게 소스 탐색 도구 목록
   (search / read / type_graph / usages 등)을 함께 전달하여 호출한다.
2. 모델이 tool_calls를 반환하면, 해당 도구를 service.py의 함수로 실행하고
   그 결과를 관찰(observation) 리스트에 누적한다.
3. 누적된 관찰을 "source_facts"라는 압축 페이로드로 변환해 다시 모델에
   넣어주고, 모델이 도구 호출 없이 텍스트만 반환하면 그것이 최종 답이 된다.

핵심 설계 포인트:

- 컨텍스트 예산 관리: 상단 상수들(MAX_OBSERVATIONS_FOR_MODEL,
  MODEL_OBSERVATION_CHARS 등)로 모델에 넣을 관찰 데이터의 개수/글자수를
  제한하고, `_observations_for_model`이 다단계 축소 전략으로 예산을 맞춘다.
- 환각(hallucination) 방지: 최종 답변을 낸 뒤 `_validate_generated_code`가
  코드 블록의 'SDK 타입 변수.메서드(' 호출을 관측된 시그니처와 대조해,
  관측되지 않은 호출(존재하지 않는 API)을 경고로 표기한다. (LLM 재호출 없음)

진입점: `answer_source_question()`
"""

import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from ... import config
from ...envelopes import ApiError
from ...logging_config import get_logger
from . import service as source_service
from ._common import (
    clip as _clip,
    json_for_model as _json_for_model,
    normalized_token as _identifier_key,
    safe_int as _safe_int,
    to_text as _to_text,
)


# 소스 에이전트(LLM 호출/도구 실행) 로깅용 'pixllm.agent' 로거
logger = get_logger("agent")


# ---------------------------------------------------------------------------
# 모델 컨텍스트 예산 상수
# 모델 프롬프트에 넣을 관찰(observation) 데이터의 양을 제한하기 위한 값들.
# vLLM 컨텍스트 윈도우 초과를 막고 토큰 비용을 줄이는 역할을 한다.
# ---------------------------------------------------------------------------

# 모델에 전달할 최근 관찰의 최대 개수 (오래된 관찰은 버림)
MAX_OBSERVATIONS_FOR_MODEL = 8
# 한 스텝에서 모델이 요청한 tool_calls 중 실제로 실행할 최대 개수
MAX_TOOL_CALLS_PER_STEP = 4
# 모델에 넣는 관찰 JSON 직렬화 문자열의 최대 글자수 예산
MODEL_OBSERVATION_CHARS = config.MODEL_OBSERVATION_CHARS
# source_facts에 포함할 API 시그니처(api_signatures)의 최대 개수
MAX_API_SIGNATURES_FOR_MODEL = 64
# source_facts에 포함할 이벤트 선언(event_declarations)의 최대 개수
MAX_EVENT_DECLARATIONS_FOR_MODEL = 12
# source_facts에 포함할 타입 관계(type_relations)의 최대 개수
MAX_TYPE_RELATIONS_FOR_MODEL = 32
# source_facts에 포함할 추천 읽기 대상(read_targets)의 최대 개수
MAX_READ_TARGETS_FOR_MODEL = 12
# source_facts에 포함할 소스 코드 조각(source_spans)의 최대 개수
MAX_SOURCE_SPANS_FOR_MODEL = 12
# 소스 코드 조각 하나(content)의 최대 글자수
SOURCE_SPAN_CONTENT_CHARS = 2200


def _normalize_tool_args(params: Any) -> Dict[str, Any]:
    """LLM이 반환한 도구 인자를 dict로 정규화한다.

    OpenAI function-calling 응답의 arguments는 보통 JSON 문자열이지만,
    모델에 따라 dict 그대로 오거나 JSON이 아닌 평문이 올 수도 있다.
    - dict면 그대로 반환
    - JSON 문자열이면 파싱해서 반환
    - JSON 파싱에 실패한 문자열이면 {"pattern": 원문}으로 감싸서 반환
      (검색 도구가 그대로 쿼리로 쓸 수 있게 하는 관대한 처리)
    - 그 외에는 빈 dict
    """
    if isinstance(params, dict):
        return params
    if isinstance(params, str):
        try:
            parsed = json.loads(params) if params.strip() else {}
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {"pattern": params}
    return {}


def _ensure_model_server(value: str) -> str:
    """vLLM 서버 base URL을 정규화해 항상 '/v1'로 끝나는 형태로 만든다.

    인자가 비어 있으면 config.LLM_BASE_URL로 폴백하고, 그것도 없으면
    ApiError(LLM_BASE_URL_MISSING)를 던진다. 끝의 '/'는 제거한 뒤
    '/v1' 접미사가 없으면 붙여준다.
    """
    base = _to_text(value).rstrip("/") or _to_text(config.LLM_BASE_URL).rstrip("/")
    if not base:
        raise ApiError("LLM_BASE_URL_MISSING", "llm_base_url is required for source answer")
    return base if base.endswith("/v1") else f"{base}/v1"


def _minimum_observation_for_model(item: Dict[str, Any]) -> Dict[str, Any]:
    """관찰 항목 하나를 '최소 필드'만 남긴 축소판으로 변환한다.

    _observations_for_model의 축소 전략 중 한 단계로, source_facts 압축으로도
    글자 예산을 못 맞출 때 사용된다. 화이트리스트 방식으로:
    - 스칼라 메타 필드(ok/query/path/symbol/kind/schemas/error)는 그대로 유지
    - 리스트 필드는 종류별로 정해진 상한 개수까지만 잘라서 유지
    - content/context는 글자수 제한(_clip)을 걸어 유지

    반환값: {"tool", "input", "observation(축소본)"} 형태의 dict.
    observation이 dict가 아니면 원본을 그대로 반환한다.
    """
    observation = item.get("observation") if isinstance(item, dict) else None
    if not isinstance(observation, dict):
        return item

    reduced: Dict[str, Any] = {}
    # 1단계: 작고 중요한 스칼라 필드는 그대로 복사
    for key in ("ok", "query", "path", "symbol", "kind", "schemas", "error"):
        if key in observation:
            reduced[key] = observation[key]
    # 2단계: 리스트 필드는 (필드명, 최대 개수) 표에 따라 앞쪽 N개만 유지
    for key, limit in (
        ("declarations", 2),
        ("types", 8),
        ("assignability", 16),
        ("operations", 32),
        ("paths", 1),
        ("results", 12),
        ("matches", 12),
        ("items", 12),
        ("candidates", 12),
        ("type_members", 16),
        ("files", 12),
        ("event_declarations", 12),
        ("recommended_reads", 8),
        ("read_targets", 16),
        ("source_spans", 12),
        ("type_relations", 24),
        ("csharp_ref_constraints", 8),
    ):
        value = observation.get(key)
        if isinstance(value, list):
            reduced[key] = value[:limit]
    # 3단계: 본문 텍스트 필드는 글자수 제한을 걸어 유지
    if "content" in observation:
        reduced["content"] = _clip(observation.get("content"), 6000)
    if "context" in observation:
        reduced["context"] = _clip(observation.get("context"), 2000)
    return {
        "tool": item.get("tool"),
        "input": item.get("input"),
        "observation": reduced,
    }


def _source_facts_for_model(observations: List[Dict[str, Any]], *, final: bool = False) -> Dict[str, Any]:
    """여러 도구 관찰 결과를 모델용 압축 페이로드(source_facts)로 변환한다.

    원본 관찰 JSON을 그대로 모델에 넣으면 너무 크므로, 답변에 실제로 필요한
    사실(fact)만 종류별로 중복 제거하며 추출한다:
    - api_signatures: 관측된 C# API 시그니처 (candidates / type_members에서 수집)
    - source_spans: 실제 소스 코드 조각 (source_spans 및 source_read 결과의 content)
    - event_declarations: 이벤트 선언
    - type_relations: 타입 간 관계(상속/참조 등)
    - csharp_ref_constraints: ref/out 파라미터 타입 제약
    - read_targets: 다음에 읽어볼 만한 대상 (recommended_reads + read_targets)

    파라미터:
    - observations: {"tool", "input", "observation"} 형식의 관찰 리스트
    - final: True이면 "최종 답변용" 모드. 시그니처에서 타입 상세 필드를 빼고
      summary도 exact_identifier 매치일 때만 남기는 등 더 공격적으로 줄이며,
      read_targets는 아예 제외하고(더 읽을 필요가 없으므로) source_spans도
      api_signatures가 있으면 2개로 제한한다.

    반환값: 종류별 리스트를 담은 dict. 비어 있는 종류는 키 자체를 생략한다.
    """
    api_signatures: List[Dict[str, Any]] = []
    source_spans: List[Dict[str, Any]] = []
    event_declarations: List[Dict[str, Any]] = []
    type_relations: List[Any] = []
    ref_constraints: List[Dict[str, Any]] = []
    read_targets: List[Dict[str, Any]] = []
    # 중복 제거용 집합들 (종류별 고유 키 추적)
    seen_api = set()
    seen_signature = set()
    seen_span = set()
    seen_event = set()
    seen_target = set()

    def append_api(item: Dict[str, Any]) -> None:
        """API 후보 하나를 (symbol, signature) 키로 중복 제거하며 api_signatures에 추가.

        final=True면 symbol/signature/enum_literals 중심의 최소 페이로드만 남기고,
        아니면 return_type, parameter_types, ref/out 타입, summary까지 포함한다.
        빈 값("", [], {}, None) 필드는 제거해 토큰을 아낀다.
        """
        signature = _to_text(item.get("csharp_signature"))
        symbol = _to_text(item.get("symbol"))
        # 시그니처가 없는 후보는 사실로 쓸 수 없으므로 건너뜀
        if not signature:
            return
        key = (symbol, signature)
        if key in seen_api:
            return
        seen_api.add(key)
        # 시그니처 자체도 기록해 두어 append_span에서 중복 표기를 피함
        seen_signature.add(signature)
        if final:
            # 최종 답변용: 최소 필드만 (summary는 정확한 식별자 매치일 때만)
            payload = {
                "symbol": symbol,
                "signature": signature,
                "enum_literals": item.get("enum_literals") or {},
            }
            if _to_text(item.get("reason")) == "exact_identifier":
                payload["summary"] = _to_text(item.get("summary"))
            api_signatures.append({key: value for key, value in payload.items() if value not in ("", [], {}, None)})
            return
        # 탐색 중간 단계용: 타입 정보를 풍부하게 포함 (모델이 후속 판단에 활용)
        payload = {
            "symbol": symbol,
            "signature": signature,
            "return_type": item.get("return_type"),
            "parameter_types": item.get("parameter_types") or [],
            "ref_parameter_types": item.get("ref_parameter_types") or [],
            "out_parameter_types": item.get("out_parameter_types") or [],
            "enum_literals": item.get("enum_literals") or {},
            "summary": _to_text(item.get("summary")),
        }
        api_signatures.append({key: value for key, value in payload.items() if value not in ("", [], {}, None)})

    def append_span(item: Dict[str, Any]) -> None:
        """소스 코드 조각을 (path, line_range, symbol) 키로 중복 제거하며 추가.

        content는 SOURCE_SPAN_CONTENT_CHARS 글자로 잘라 넣는다.
        이미 api_signatures에 들어간 시그니처는 다시 싣지 않는다.
        """
        path = _to_text(item.get("path"))
        line_range = _to_text(item.get("line_range"))
        content = _to_text(item.get("content"))
        signature = _to_text(item.get("csharp_signature"))
        # 경로도 내용도 없으면 의미 있는 코드 조각이 아님
        if not path and not content:
            return
        key = (path, line_range, _to_text(item.get("symbol")))
        if key in seen_span:
            return
        seen_span.add(key)
        payload = {
            "symbol": _to_text(item.get("symbol")),
            "path": path,
            "line_range": line_range,
            "content": _clip(content, SOURCE_SPAN_CONTENT_CHARS),
        }
        # api_signatures에 이미 있는 시그니처는 중복 수록하지 않음
        if signature and signature not in seen_signature:
            payload["signature"] = signature
        source_spans.append(payload)

    def append_target(item: Dict[str, Any]) -> None:
        """읽기 대상(read target)을 JSON 직렬화 문자열 키로 중복 제거하며 추가."""
        key = _json_for_model(item)
        if key in seen_target:
            return
        seen_target.add(key)
        read_targets.append(item)

    def append_event(item: Dict[str, Any]) -> None:
        """이벤트 선언을 (path, line_range, name) 키로 중복 제거하며 추가."""
        path = _to_text(item.get("path"))
        line_range = _to_text(item.get("line_range"))
        name = _to_text(item.get("name"))
        # 경로도 이름도 없는 선언은 무의미
        if not path and not name:
            return
        key = (path, line_range, name)
        if key in seen_event:
            return
        seen_event.add(key)
        event_declarations.append(item)

    # 모든 관찰을 순회하며 종류별 사실을 수집한다
    for item in observations:
        observation = item.get("observation") if isinstance(item, dict) else None
        if not isinstance(observation, dict):
            continue
        # 검색 결과 후보(candidates)와 타입 멤버(type_members) → API 시그니처
        for candidate in observation.get("candidates") if isinstance(observation.get("candidates"), list) else []:
            if isinstance(candidate, dict):
                append_api(candidate)
        for candidate in observation.get("type_members") if isinstance(observation.get("type_members"), list) else []:
            if isinstance(candidate, dict):
                append_api(candidate)
        # 소스 코드 조각
        for span in observation.get("source_spans") if isinstance(observation.get("source_spans"), list) else []:
            if isinstance(span, dict):
                append_span(span)
        # 이벤트 선언
        for event in observation.get("event_declarations") if isinstance(observation.get("event_declarations"), list) else []:
            if isinstance(event, dict):
                append_event(event)
        # 추천 읽기 대상 두 종류(recommended_reads, read_targets)를 하나로 합침
        for target in observation.get("recommended_reads") if isinstance(observation.get("recommended_reads"), list) else []:
            if isinstance(target, dict):
                append_target(target)
        for target in observation.get("read_targets") if isinstance(observation.get("read_targets"), list) else []:
            if isinstance(target, dict):
                append_target(target)
        # 타입 관계 / ref 제약은 단순 값 비교로 중복 제거
        for relation in observation.get("type_relations") if isinstance(observation.get("type_relations"), list) else []:
            if relation not in type_relations:
                type_relations.append(relation)
        for constraint in observation.get("csharp_ref_constraints") if isinstance(observation.get("csharp_ref_constraints"), list) else []:
            if isinstance(constraint, dict) and constraint not in ref_constraints:
                ref_constraints.append(constraint)
        # source_read 결과(파일 본문)도 코드 조각으로 취급해 source_spans에 합류
        if observation.get("kind") == "source_file" or observation.get("content"):
            append_span(
                {
                    "symbol": observation.get("symbol"),
                    "csharp_signature": observation.get("csharp_signature"),
                    "path": observation.get("path"),
                    "line_range": observation.get("line_range"),
                    "content": observation.get("content"),
                }
            )

    # 종류별 상한을 적용해 최종 facts dict를 구성 (빈 종류는 생략)
    facts: Dict[str, Any] = {}
    if api_signatures:
        facts["api_signatures"] = api_signatures[:MAX_API_SIGNATURES_FOR_MODEL]
    if ref_constraints:
        facts["csharp_ref_constraints"] = ref_constraints[:16]
    if type_relations:
        facts["type_relations"] = type_relations[:MAX_TYPE_RELATIONS_FOR_MODEL]
    if event_declarations:
        facts["event_declarations"] = event_declarations[:MAX_EVENT_DECLARATIONS_FOR_MODEL]
    # read_targets는 "다음에 읽을 것" 안내이므로 최종 답변(final)에는 불필요
    if read_targets and not final:
        facts["read_targets"] = read_targets[:MAX_READ_TARGETS_FOR_MODEL]
    if source_spans:
        # 최종 답변 시 시그니처가 이미 충분하면 코드 조각은 2개로 강하게 축소
        facts["source_spans"] = (
            source_spans[:2]
            if final and api_signatures
            else source_spans[:MAX_SOURCE_SPANS_FOR_MODEL]
        )
    return facts


def _observed_identifier_keys(observations: List[Dict[str, Any]]) -> set:
    """관찰 결과에서 '실제로 관측된' 식별자 키 집합을 만든다.

    _source_facts_for_model(final=True)로 압축한 사실에서 다음을 수집해
    _identifier_key로 정규화한다:
    - api_signatures의 symbol을 '.'으로 분리한 각 조각
      (예: "NXImage.GetPixel" → "nximage", "getpixel")
    - 시그니처 문자열에서 여는 괄호 앞의 메서드 이름
    - type_relations에 등장하는 타입 이름들

    반환값: 정규화된 식별자 키의 set. 사후 검증 가드(_unverified_sdk_calls)에서
    생성 코드의 SDK 호출이 관측되었는지 대조하는 데 쓰인다.
    """
    facts = _source_facts_for_model(observations, final=True)
    keys = set()
    for item in facts.get("api_signatures") if isinstance(facts.get("api_signatures"), list) else []:
        if not isinstance(item, dict):
            continue
        # symbol의 네임스페이스/타입/멤버 각 조각을 모두 키로 등록
        for part in _to_text(item.get("symbol")).split("."):
            key = _identifier_key(part)
            if key:
                keys.add(key)
        # 시그니처에서 메서드 이름(괄호 직전 식별자)도 키로 등록
        signature = _to_text(item.get("signature") or item.get("csharp_signature"))
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
        if match:
            keys.add(_identifier_key(match.group(1)))
    # 타입 관계에 등장하는 타입 이름들도 관측된 식별자로 인정
    for item in facts.get("type_relations") if isinstance(facts.get("type_relations"), list) else []:
        values = item.values() if isinstance(item, dict) else item if isinstance(item, list) else []
        for value in values:
            key = _identifier_key(value)
            if key:
                keys.add(key)
    return keys


# ---------------------------------------------------------------------------
# 환각 방지 가드 (post-hoc): 생성된 코드의 SDK 호출을 관측 시그니처와 대조
#
# 작업형 프롬프트("tif 로드해서 보여줘")는 지목된 API가 없어도 모델이 코드 본문에
# 존재하지 않는 메서드(예: NXImageLayer.Load)를 지어낼 수 있다. 이 가드는 최종
# 답변의 코드 블록에서 'SDK 타입 변수.메서드(' 호출을 뽑아 관측된 식별자와
# 대조하고, 미관측 호출을 경고로 표기한다. LLM을 재호출하지 않는다.
# ---------------------------------------------------------------------------

# 이 가드를 끄고 싶을 때 False로.
VALIDATE_GENERATED_CODE = True
# System.Object 공통 메서드 — SDK 수신자에 붙어도 환각으로 보지 않음
_UNIVERSAL_MEMBER_KEYS = {"tostring", "equals", "gethashcode", "gettype"}
# 코드 펜스(``` ... ```) 블록 추출용
_CODE_BLOCK_RE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)
# "Type varName =" / "Type varName;" 형태의 지역 변수 선언 (수신자 타입 추적용)
_VAR_DECL_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s+([a-z_][A-Za-z0-9_]*)\s*[=;)]")
# "receiver.Member(" 형태의 메서드 호출
_MEMBER_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# 주석 제거용 — 모델이 "쓰지 말라"고 주석 처리한 코드를 환각으로 오탐하지 않기 위함
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")


def _strip_code_comments(code: str) -> str:
    """C#/C 스타일 주석(// ..., /* ... */)을 제거한다.

    모델이 미관측 API를 주석으로 남기며 "확인되지 않음"이라 밝히는 경우가 있는데,
    그 주석 줄까지 호출로 오탐하지 않도록 검증 전에 주석을 걷어낸다.
    """
    return _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub(" ", code))


def _looks_like_sdk_type(name: str, observed_keys: set) -> bool:
    """이름이 Pixoneer SDK 타입인지 판별한다.

    - 관측된 식별자 집합에 있으면(=검색으로 실제 확인됨) SDK 타입으로 인정
    - 아니면 명명 규칙(NX*/X* + 뒤에 대문자/숫자)으로 판별. 표준 .NET 타입
      (Color, ArrayList, Console 등)은 이 규칙에 걸리지 않는다.
    """
    if _identifier_key(name) in observed_keys:
        return True
    return bool(re.match(r"^(NX|X)[A-Z0-9]", name))


def _extract_code_blocks(answer: str) -> List[str]:
    """답변 텍스트에서 코드 펜스 블록들의 본문만 뽑아 반환한다."""
    return _CODE_BLOCK_RE.findall(_to_text(answer))


def _sdk_variable_types(code: str, observed_keys: set) -> Dict[str, str]:
    """코드에서 'SDK 타입 지역 변수'의 (변수명 → 타입명) 맵을 만든다.

    'NXImageLayer imageLayer = ...' 같은 선언을 잡아, 타입이 SDK 타입일 때만
    등록한다. 이후 그 변수에 붙은 메서드 호출을 SDK 호출로 간주해 검증한다.
    """
    mapping: Dict[str, str] = {}
    for type_name, var_name in _VAR_DECL_RE.findall(code):
        if _looks_like_sdk_type(type_name, observed_keys):
            mapping[var_name] = type_name
    return mapping


def _unverified_sdk_calls(
    answer: str, observations: List[Dict[str, Any]], *, strip_comments: bool = True
) -> List[Dict[str, str]]:
    """생성 답변의 코드에서 '관측되지 않은 SDK 메서드 호출'을 수집한다.

    검사 대상:
    - SDK 타입으로 선언된 변수에 대한 `변수.Member(` 호출
    - `SdkType.Member(` 형태의 정적/타입 멤버 호출 (SdkType이 SDK 명명/관측)

    각 호출의 Member가 관측된 식별자에 없으면 (type, member)로 수집한다.
    타입 존재 자체는 검사하지 않는다(부분 검색으로 인한 오탐 방지).

    strip_comments:
    - True(기본): 주석을 걷어내고 검사 → 사용자에게 보일 '경고' 판정용
      (모델이 정직하게 주석 처리한 호출은 경고하지 않음).
    - False: 주석까지 포함해 검사 → '재탐색 트리거'용. 모델이 API를 못 찾아
      주석으로 남긴 능력 갭도 포착해, 그 능력을 소스에서 다시 찾게 한다.

    반환: [{"type": <타입명>, "member": <멤버명>, "call": "<타입>.<멤버>(...)"}] (중복 제거)
    """
    observed_keys = _observed_identifier_keys(observations)
    found: List[Dict[str, str]] = []
    seen: set = set()
    for raw_code in _extract_code_blocks(answer):
        code = _strip_code_comments(raw_code) if strip_comments else raw_code
        var_types = _sdk_variable_types(code, observed_keys)
        for receiver, member in _MEMBER_CALL_RE.findall(code):
            member_key = _identifier_key(member)
            if not member_key or member_key in _UNIVERSAL_MEMBER_KEYS:
                continue
            # 수신자 타입 결정: SDK 변수이거나, 수신자 자체가 SDK 타입명(정적 호출)
            type_name = var_types.get(receiver)
            if type_name is None:
                if receiver[:1].isupper() and _looks_like_sdk_type(receiver, observed_keys):
                    type_name = receiver
                else:
                    continue
            # 멤버가 관측되었으면 정상
            if member_key in observed_keys:
                continue
            dedup_key = (_identifier_key(type_name), member_key)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            found.append({"type": type_name, "member": member, "call": f"{type_name}.{member}(...)"})
    return found


def _validate_generated_code(
    answer: str, observations: List[Dict[str, Any]], *, prompt: str = ""
) -> Tuple[str, List[Dict[str, str]]]:
    """최종 답변의 코드 SDK 호출을 검증하고, 미관측 호출이 있으면 경고를 덧붙인다.

    반환: (경고가 추가된 답변, 미관측 호출 목록). 미관측이 없으면 원문 그대로.
    """
    if not VALIDATE_GENERATED_CODE:
        return answer, []
    unverified = _unverified_sdk_calls(answer, observations)
    if not unverified:
        return answer, []
    lines = "\n".join(f"- `{item['call']}`" for item in unverified)
    if re.search(r"[가-힣]", _to_text(prompt) or _to_text(answer)):
        notice = (
            "\n\n---\n"
            "⚠️ **소스 검증 경고** — 아래 호출은 관측된 소스 API 시그니처에서 확인되지 "
            "않았습니다(실제로 존재하지 않거나 이번 검색에서 관측되지 않음):\n"
            f"{lines}\n"
            "해당 멤버가 실제 소스에 있는지 확인한 뒤 사용하세요."
        )
    else:
        notice = (
            "\n\n---\n"
            "⚠️ **Source validation warning** — the following calls were not found in the "
            "observed source API signatures (either they do not exist or were not observed "
            "by this search):\n"
            f"{lines}\n"
            "Verify these members against the actual source before use."
        )
    return answer + notice, unverified


def _build_system_prompt() -> str:
    """에이전트의 시스템 프롬프트를 구성한다.

    핵심 지시 사항:
    - source_facts.api_signatures를 '관측된 API 전부'로 취급할 것
    - 이름이 지목된 API 질문은 관측된 시그니처에서만 답하고,
      없으면 '관측되지 않음'이라고 말할 것 (다른 API로 대체 금지)
    - 코드 예제는 소스 바인딩 문법이 아닌 C# 문법으로 작성할 것
    - UI 코드는 기본 WPF: 사용자가 다른 프레임워크를 명시하지 않으면 XAML 마크업과
      code-behind(.xaml.cs)를 각각 별도 코드 블록으로 분리해 작성할 것 (WinForms 금지)
    - ref/out 파라미터는 관측된 C# 타입으로 지역 변수를 선언/초기화할 것
    - 사용자의 언어로 자연스럽게 답할 것
    """
    return "\n".join(
        [
            "You are the PIXLLM backend source agent.",
            "Use source_search for discovery and source_read for exact source spans or declarations when concrete code evidence is needed.",
            "Tool routing: when the question names a specific class, method, or property (e.g. 'NXImageView', 'what members/signature does X have'), call source_search FIRST to obtain its declaration and C# signature, then source_read for exact spans. Use source_type_graph ONLY for relationships between types (inheritance, referenced/assignable types, call graph) — never as the primary way to list a named symbol's members. Do not answer a named-symbol question from a source_type_graph result alone; if you have not called source_search for that symbol, call it before answering.",
            "Treat source_facts.api_signatures as the observed API set.",
            "For named-API questions, answer from matching observed signatures only; if none match, say it was not observed and do not substitute unrelated APIs or code.",
            "For SDK/API calls in code, use observed Pixoneer/NXDL signatures; ordinary C# language/runtime syntax is allowed.",
            "Never invent SDK members. Every method/property you call on a Pixoneer/NXDL (NX*/X*) type MUST appear verbatim in the observed api_signatures. If the operation the user asked for (e.g. loading a file into a layer) has no matching observed API, DO NOT fabricate a plausible-looking call such as `.Load(...)` or `.LoadImage(...)`; instead state that the API for that operation was not observed in the source, and show only the steps you can ground. If a needed member is missing, prefer calling source_search again with a different query before giving up.",
            "For C# answers, emit C# syntax instead of source binding syntax.",
            "UI code default: unless the user explicitly asks for another framework (e.g. WinForms), write WPF. Emit TWO separate code blocks — a ```xaml block for the markup and a ```csharp block for the code-behind (.xaml.cs) — never merge them and never use WinForms 'this.Controls.Add'. The code-behind uses observed Pixoneer/NXDL signatures for SDK calls.",
            "For ref/out parameters, declare and initialize local variables with the observed C# parameter type before the call.",
            "If a derived object is passed to a ref base-type parameter, first assign it to a variable of that base type.",
            "Answer naturally in the user's language.",
        ]
    )


class _TraceRecorder:
    """도구 호출 이력을 기록하는 디버깅/감사용 추적기.

    에이전트 루프 동안 실행된 모든 도구 호출(도구 이름, 입력, 성공 여부,
    요약, 전체 관찰 결과)을 순서대로 self.items에 쌓는다.
    이 리스트는 최종 응답의 "trace" 필드로 그대로 반환되어,
    에이전트가 어떤 경로로 답에 도달했는지 사후 분석할 수 있게 한다.
    """

    def __init__(self) -> None:
        """빈 추적 리스트로 초기화한다."""
        self.items: List[Dict[str, Any]] = []

    def append(self, tool: str, arguments: Dict[str, Any], result: Dict[str, Any], phase: str = "tool") -> None:
        """도구 호출 한 건을 기록한다.

        파라미터:
        - tool: 실행된 도구 이름
        - arguments: 도구에 전달된 인자
        - result: 도구 실행 결과 (observation으로 통째 저장)
        - phase: 호출 단계 라벨 (기본 "tool")

        summary에는 path/pattern/query/total/error 등 한눈에 볼 수 있는
        요약 필드를 따로 뽑아 둔다.
        """
        self.items.append(
            {
                "phase": phase,
                "tool": tool,
                "input": arguments,
                "ok": result.get("ok", True) is not False,
                "summary": {
                    "path": _to_text(result.get("path")),
                    "pattern": _to_text(result.get("pattern")),
                    "query": _to_text(result.get("query")),
                    "total": result.get("total"),
                    "error": _to_text(result.get("error")),
                },
                "observation": result,
            }
        )


# ---------------------------------------------------------------------------
# 도구 정의 (OpenAI function-calling 스펙)
# LLM에게 전달되는 소스 탐색 도구 목록. 각 항목의 name이 _execute_tool의
# 디스패치 키가 되고, 실제 구현은 service.py의 함수들이다.
# ---------------------------------------------------------------------------
TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "source_overview",
            "description": "Return source root, file count, top-level modules, and index status.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_ls",
            "description": "List source directories/files under RAW_SOURCE_ROOT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Optional Source/... directory"},
                    "depth": {"type": "integer", "description": "Directory recursion depth"},
                    "limit": {"type": "integer", "description": "Maximum returned entries"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_glob",
            "description": "Find source files by glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern relative to Source/"},
                    "limit": {"type": "integer", "description": "Maximum returned files"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_search",
            "description": "Find candidate symbols, files, source_spans, and recommended_reads suitable for source_read.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural-language/API search query"},
                    "limit": {"type": "integer", "description": "Maximum returned items"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_read",
            "description": "Inspect exact source evidence from Source/... spans or .runtime symbol paths returned by source_search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Source/... path or .runtime/methods_index.json#Symbol"},
                    "start_line": {"type": "integer", "description": "Optional start line"},
                    "end_line": {"type": "integer", "description": "Optional end line"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_type_graph",
            "description": "Build a type/member graph from declarations, referenced types, inheritance, and C# signatures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Workflow, API, or type terms"},
                    "limit": {"type": "integer", "description": "Maximum returned types"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_usages",
            "description": "Find real non-comment source usages for a type, method, or call pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Type, method, or call pattern"},
                    "limit": {"type": "integer", "description": "Maximum returned usages"},
                },
                "required": ["query"],
            },
        },
    },
]

# 기본으로 항상 개방하는 핵심 도구 (검색/읽기/타입그래프/사용처)
PRIMARY_TOOL_NAMES = ("source_search", "source_read", "source_type_graph", "source_usages")
# 탐색 범위가 넓은 보조 도구 (전체 개요/디렉터리 목록/글롭) — 조건부 개방
BROAD_TOOL_NAMES = ("source_overview", "source_ls", "source_glob")
# 프롬프트가 "파일 목록/구조" 류의 광역 질문인지 판별하는 키워드 정규식
# (영문 + 한국어 키워드 모두 매치)
BROAD_SOURCE_PROMPT_RE = re.compile(
    r"(overview|module|directory|folder|glob|list|ls|tree|파일|목록|폴더|디렉|구조|모듈|전체|경로)",
    re.IGNORECASE,
)
# 토큰 절약을 위한 도구별 축약 설명 (compact 도구 정의에 사용)
COMPACT_TOOL_DESCRIPTIONS = {
    "source_overview": "Source root, counts, modules, index status.",
    "source_ls": "List Source/ paths.",
    "source_glob": "Find Source/ files by glob.",
    "source_search": (
        "PRIMARY lookup for a named class/method/property: returns its declaration, "
        "C# signature, and source_read targets. Call this FIRST whenever the question "
        "names a symbol or asks what members/signature/parameters it has."
    ),
    "source_read": "Inspect exact Source/ spans or indexed symbol targets.",
    "source_type_graph": (
        "Relationships BETWEEN types only: inheritance, referenced/assignable types, "
        "call graph. NOT for listing a single named symbol's members/signature "
        "(use source_search for that)."
    ),
    "source_usages": "Find real source usages.",
}
# 도구 이름 → 원본(풀) 도구 정의 매핑
TOOL_DEFINITIONS_BY_NAME = {
    _to_text(item.get("function", {}).get("name")): item
    for item in TOOL_DEFINITIONS
    if isinstance(item.get("function"), dict) and _to_text(item.get("function", {}).get("name"))
}


def _compact_parameters(schema: Any) -> Dict[str, Any]:
    """도구 파라미터 JSONSchema를 축약해 토큰을 절약한다.

    각 프로퍼티에서 type/enum/items만 남기고 description 등 부가 정보를
    제거한다. required 목록은 실제 존재하는 프로퍼티만 남긴다.
    schema가 dict가 아니면 빈 object 스키마를 반환한다.
    """
    if not isinstance(schema, dict):
        return {"type": "object", "properties": {}, "required": []}
    properties: Dict[str, Any] = {}
    raw_properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    for name, definition in raw_properties.items():
        if not isinstance(definition, dict):
            continue
        compact: Dict[str, Any] = {}
        # description 등은 버리고 스키마 핵심 키만 유지
        for key in ("type", "enum", "items"):
            if key in definition:
                compact[key] = definition[key]
        properties[_to_text(name)] = compact or {"type": "string"}
    required = [
        _to_text(item)
        for item in (schema.get("required") if isinstance(schema.get("required"), list) else [])
        if _to_text(item) in properties
    ]
    return {"type": "object", "properties": properties, "required": required}


def _compact_tool_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    """원본 도구 정의 하나를 축약(compact) 버전으로 변환한다.

    설명은 COMPACT_TOOL_DESCRIPTIONS의 짧은 문구로 교체하고,
    파라미터 스키마는 _compact_parameters로 줄인다.
    매 LLM 호출마다 도구 정의가 프롬프트에 포함되므로 토큰 절약 효과가 크다.
    """
    function = definition.get("function") if isinstance(definition, dict) else {}
    function = function if isinstance(function, dict) else {}
    name = _to_text(function.get("name"))
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": COMPACT_TOOL_DESCRIPTIONS.get(name, _to_text(function.get("description"))),
            "parameters": _compact_parameters(function.get("parameters")),
        },
    }


# 도구 이름 → 축약 도구 정의 매핑 (실제로 모델에 전달되는 것은 이 버전)
COMPACT_TOOL_DEFINITIONS_BY_NAME = {
    name: _compact_tool_definition(definition)
    for name, definition in TOOL_DEFINITIONS_BY_NAME.items()
}


def _prompt_needs_broad_source_tools(prompt: str) -> bool:
    """프롬프트가 파일 목록/디렉터리 구조 등 광역 탐색 질문인지 판별한다.

    BROAD_SOURCE_PROMPT_RE 키워드(목록/폴더/구조/overview 등)가 있으면 True.
    True이면 _tool_definitions_for_step이 BROAD 도구까지 개방한다.
    """
    return bool(BROAD_SOURCE_PROMPT_RE.search(_to_text(prompt)))


def _needs_broad_tool_fallback(observations: List[Dict[str, Any]]) -> bool:
    """직전 search 결과가 빈손이어서 광역 도구로 폴백해야 하는지 판단한다.

    최근 2개의 관찰 중 source_search 호출을 검사하여:
    - 검색 자체가 실패했거나(ok=False)
    - candidates / source_spans / read_targets가 전혀 없으면
    True를 반환한다. 검색이 막혔을 때 ls/glob/overview로 우회 경로를 열어준다.
    """
    for item in observations[-2:]:
        if _to_text(item.get("tool")) != "source_search":
            continue
        observation = item.get("observation") if isinstance(item, dict) else {}
        observation = observation if isinstance(observation, dict) else {}
        # 검색 실패 → 폴백 필요
        if observation.get("ok") is False:
            return True
        # 후보/코드 조각/읽기 대상이 모두 비어 있음 → 폴백 필요
        has_candidates = bool(observation.get("candidates") or observation.get("source_spans") or observation.get("read_targets"))
        if not has_candidates:
            return True
    return False


def _tool_definitions_for_step(prompt: str, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """이번 스텝에서 모델에게 개방할 도구 정의 목록을 결정한다.

    기본 정책: 핵심 도구(PRIMARY_TOOL_NAMES: search/read/type_graph/usages)만
    개방해 모델의 선택지를 좁히고 토큰을 아낀다.

    단, 다음 중 하나면 광역 도구(BROAD_TOOL_NAMES: overview/ls/glob)까지 개방:
    - 첫 스텝(아직 관찰이 없음)
    - 프롬프트가 파일 목록/구조성 질문 (_prompt_needs_broad_source_tools)
    - 직전 search가 빈손이라 우회가 필요 (_needs_broad_tool_fallback)

    반환값: 모델에 전달할 compact 도구 정의 리스트.
    """
    names = list(PRIMARY_TOOL_NAMES)
    if not observations or _prompt_needs_broad_source_tools(prompt) or _needs_broad_tool_fallback(observations):
        names = [*BROAD_TOOL_NAMES, *PRIMARY_TOOL_NAMES]
    return [
        COMPACT_TOOL_DEFINITIONS_BY_NAME[name]
        for name in names
        if name in COMPACT_TOOL_DEFINITIONS_BY_NAME
    ]


def _search_query_with_prompt(raw_query: str, prompt: str) -> str:
    """도구 쿼리가 비어 있으면 사용자 프롬프트 전문을 쿼리로 대신 사용한다.

    모델이 가끔 query를 빈 값으로 도구를 호출하는데, 그 경우에도
    의미 있는 검색이 되도록 하는 안전장치.
    """
    query = _to_text(raw_query)
    return query or _to_text(prompt)


def _execute_tool(name: str, arguments: Dict[str, Any], trace: _TraceRecorder, *, prompt: str = "") -> Dict[str, Any]:
    """도구 이름을 service.py의 실제 구현 함수로 디스패치하여 실행한다.

    LLM이 요청한 (도구 이름, 인자) 한 건을 받아:
    - 인자를 _safe_int 등으로 안전하게 정규화하고
    - 쿼리형 도구(search/type_graph/usages)는 빈 쿼리를 사용자 프롬프트로
      대체(_search_query_with_prompt)하며, 보정된 쿼리를 arguments에 다시
      기록해 추적/관찰에 남긴다
    - 알 수 없는 도구 이름이면 {"ok": False, "error": "unknown_tool"} 반환

    모든 실행 결과는 trace에 기록된다.

    파라미터:
    - name: 도구 이름 (TOOL_DEFINITIONS의 function.name)
    - arguments: 정규화된 도구 인자 dict (이 함수가 일부 보정함)
    - trace: 호출 이력 기록기
    - prompt: 빈 쿼리 폴백에 쓸 사용자 프롬프트

    반환값: 도구 실행 결과 dict (관찰 데이터).
    """
    if name == "source_overview":
        # 소스 루트/파일 수/모듈/인덱스 상태 개요
        result = source_service.get_context()
    elif name == "source_ls":
        # 디렉터리 목록 (path 또는 pattern 인자 모두 허용)
        result = source_service.list_source(
            _to_text(arguments.get("path") or arguments.get("pattern")),
            depth=_safe_int(arguments.get("depth"), 1, 0, 8),
            limit=_safe_int(arguments.get("limit"), 80, 1, 300),
        )
    elif name == "source_glob":
        # 글롭 패턴 파일 검색 (패턴이 없으면 전체 매칭 "**/*")
        result = source_service.glob_source(
            _to_text(arguments.get("pattern")) or "**/*",
            limit=_safe_int(arguments.get("limit"), 80, 1, 300),
        )
    elif name == "source_search":
        # 심볼/파일/코드조각 통합 검색 — 빈 쿼리는 사용자 프롬프트로 대체
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        query = _search_query_with_prompt(raw_query, prompt)
        arguments["query"] = query
        result = source_service.find_source(
            query,
            limit=max(12, _safe_int(arguments.get("limit"), 12, 1, 40)),
        )
    elif name == "source_read":
        # 정확한 소스 범위/심볼 읽기 — 결과가 비면 not_found 오류로 표준화
        result = source_service.read_source(
            _to_text(arguments.get("path") or arguments.get("pattern")),
            start_line=arguments.get("start_line"),
            end_line=arguments.get("end_line"),
        )
        if not result:
            result = {"ok": False, "error": "source_path_not_found", "path": _to_text(arguments.get("path"))}
    elif name == "source_type_graph":
        # 타입/멤버 그래프 조회 — 빈 쿼리는 사용자 프롬프트로 대체
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        query = _search_query_with_prompt(raw_query, prompt)
        arguments["query"] = query
        result = source_service.type_graph(
            query,
            limit=max(12, _safe_int(arguments.get("limit"), 12, 1, 20)),
        )
    elif name == "source_usages":
        # 실제 사용처(usage) 검색 — 빈 쿼리는 사용자 프롬프트로 대체
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        query = _search_query_with_prompt(raw_query, prompt)
        arguments["query"] = query
        result = source_service.source_usages(
            query,
            limit=_safe_int(arguments.get("limit"), 12, 1, 50),
        )
    else:
        # 정의되지 않은 도구 이름 — 오류 관찰로 응답
        result = {"ok": False, "error": "unknown_tool", "tool": name}

    # 성공/실패와 무관하게 모든 호출을 추적에 기록
    trace.append(name, arguments, result)
    return result


def _observations_for_model(observations: List[Dict[str, Any]], *, final: bool = False) -> str:
    """관찰 리스트를 MODEL_OBSERVATION_CHARS 글자 예산 안의 JSON 문자열로 만든다.

    글자 예산을 맞추기 위한 다단계 축소 전략:
    1. 최근 MAX_OBSERVATIONS_FOR_MODEL개만 선택
    2. source_facts 압축본을 우선 시도 — 예산 내면 그대로 사용.
       초과하면 큰 리스트(source_spans → read_targets → type_relations →
       api_signatures) 순서로 절반씩 잘라가며 재시도
    3. source_facts가 비면 원본 관찰 JSON을 시도
    4. 그래도 초과하면 _minimum_observation_for_model로 필드 단위 축소
    5. 그래도 초과하면 리스트 필드를 4개씩으로 더 자르고 schemas 제거
    6. 최후의 수단: 가장 오래된 관찰부터 하나씩 버리며 예산을 맞춤

    파라미터:
    - final: source_facts 압축 시 최종 답변용 공격적 축소 모드 사용 여부

    반환값: 모델 프롬프트에 그대로 삽입할 JSON 문자열 (관찰이 없으면 "[]").
    """
    # 1단계: 최근 N개만 선택
    selected = observations[-MAX_OBSERVATIONS_FOR_MODEL:]
    if not selected:
        return "[]"

    # 2단계: source_facts 압축본 우선 시도
    source_facts = _source_facts_for_model(selected, final=final)
    if source_facts:
        payload = {"source_facts": source_facts}
        text = _json_for_model(payload)
        if len(text) <= MODEL_OBSERVATION_CHARS:
            return text
        # 예산 초과 시 부피가 큰 리스트부터 절반씩 줄이며 재시도
        for key in ("source_spans", "read_targets", "type_relations", "api_signatures"):
            value = source_facts.get(key)
            if isinstance(value, list):
                source_facts[key] = value[: max(4, len(value) // 2)]
            text = _json_for_model(payload)
            if len(text) <= MODEL_OBSERVATION_CHARS:
                return text

    # 3단계: 압축할 사실이 없으면 원본 관찰 JSON 시도
    text = _json_for_model(selected)
    if len(text) <= MODEL_OBSERVATION_CHARS:
        return text

    # 4단계: 관찰별로 최소 필드만 남기는 축소판으로 변환
    reduced = [_minimum_observation_for_model(item) for item in selected]
    text = _json_for_model(reduced)
    if len(text) <= MODEL_OBSERVATION_CHARS:
        return text

    # 5단계: 리스트 필드를 4개씩으로 추가 절단하고 schemas 필드 제거
    for item in reduced:
        observation = item.get("observation") if isinstance(item, dict) else None
        if not isinstance(observation, dict):
            continue
        for key in ("operations", "results", "matches", "items", "types", "assignability", "declarations", "paths"):
            value = observation.get(key)
            if isinstance(value, list):
                observation[key] = value[:4]
        observation.pop("schemas", None)

    # 6단계(최후): 가장 오래된 관찰부터 하나씩 버리며 예산을 맞춤
    text = _json_for_model(reduced)
    while len(text) > MODEL_OBSERVATION_CHARS and len(reduced) > 1:
        reduced = reduced[1:]
        text = _json_for_model(reduced)
    return text


def _build_messages(
    prompt: str,
    observations: List[Dict[str, Any]],
    *,
    final: bool = False,
    correction: str = "",
) -> List[Dict[str, str]]:
    """LLM에 보낼 chat 메시지 배열을 구성한다.

    기본 구조: [system 프롬프트, user 질문]. 관찰이 있으면 세 번째 user
    메시지로 압축된 관찰(_observations_for_model)과 지시문을 덧붙인다.

    파라미터:
    - final: True면 "이 사실들로 지금 답하라(추가 도구 사용 금지)"는 지시,
      False면 "필요하면 도구를 더 쓰고, 아니면 source_facts만으로 답하라"는 지시.
    - correction: 비어 있지 않으면 교정 지시문을 마지막 user 메시지로 덧붙인다
      (사후 검증에서 미관측 호출이 나왔을 때의 재생성 경로에서 사용).
    """
    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": prompt},
    ]
    if observations:
        # 단계(중간 탐색 vs 최종 답변)에 따라 지시문을 다르게 구성
        task = (
            "Answer the user now from these source facts. Ground SDK/API calls in source_facts.api_signatures "
            "and follow source_facts.csharp_ref_constraints."
            if final
            else "Use more tools if needed; otherwise answer the user from source_facts only."
        )
        messages.append(
            {
                "role": "user",
                "content": f"Source observations so far:\n{_observations_for_model(observations, final=final)}\n\n{task}",
            }
        )
    if correction:
        messages.append({"role": "user", "content": correction})
    return messages


def _chat_completion_response(
    *,
    model_cfg: Dict[str, Any],
    messages: List[Dict[str, Any]],
    max_tokens: int,
    enable_thinking: bool = False,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """vLLM 서버의 /chat/completions 엔드포인트를 urllib로 직접 호출한다.

    파라미터:
    - model_cfg: {"model": 모델명, "model_server": '/v1'까지의 base URL}
    - messages: chat 메시지 배열
    - max_tokens: 응답 토큰 상한
    - enable_thinking: Qwen 계열 모델의 사고(thinking) 모드 토글
      (chat_template_kwargs로 전달; 다른 모델에서는 무시될 수 있음)
    - tools: 함께 전달할 도구 정의. 주어지면 tool_choice="auto"로 설정해
      모델이 도구 호출 여부를 스스로 결정하게 한다.

    재현성/결정성을 위해 temperature=0으로 고정한다.
    HTTP 오류는 ApiError(LLM_HTTP_ERROR, 502)로 변환해 던진다.

    반환값: OpenAI 호환 응답 JSON dict.
    """
    endpoint = f"{_to_text(model_cfg.get('model_server')).rstrip('/')}/chat/completions"
    payload: Dict[str, Any] = {
        "model": model_cfg["model"],
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "top_k": config.LLM_TOP_K,
        "chat_template_kwargs": {"enable_thinking": bool(enable_thinking)},
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {config.LLM_API_KEY}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.LLM_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        # ApiError로 감싸기 전에 실패한 엔드포인트와 응답 본문을 남겨 LLM 서버 장애를 추적한다
        logger.error("LLM request failed (%s) at %s: %s", exc.code, endpoint, detail or repr(exc))
        raise ApiError("LLM_HTTP_ERROR", detail or repr(exc), status_code=502) from exc


def _response_usage(response: Dict[str, Any]) -> Dict[str, int]:
    """LLM 응답의 usage 블록에서 토큰 사용량을 안전하게 추출한다.

    필드가 없거나 형식이 이상해도 0으로 기본 처리하여
    항상 {prompt_tokens, completion_tokens, total_tokens} dict를 반환한다.
    """
    usage = response.get("usage") if isinstance(response, dict) else {}
    usage = usage if isinstance(usage, dict) else {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def _add_response_usage(total: Dict[str, int], response: Dict[str, Any]) -> None:
    """응답 한 건의 토큰 사용량을 누적 합계 dict(total)에 더한다. (in-place 수정)"""
    usage = _response_usage(response)
    for key, value in usage.items():
        total[key] = int(total.get(key) or 0) + value


def _choice_message(response: Dict[str, Any]) -> Dict[str, Any]:
    """OpenAI 호환 응답에서 choices[0].message를 안전하게 꺼낸다.

    구조가 어긋나 있으면 빈 dict를 반환해 호출 측의 방어 코드를 단순화한다.
    """
    choices = response.get("choices") if isinstance(response, dict) else []
    if not choices or not isinstance(choices[0], dict):
        return {}
    message = choices[0].get("message")
    return message if isinstance(message, dict) else {}


def _extract_tool_calls(message: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """LLM 응답 메시지에서 도구 호출 요청을 (이름, 인자) 튜플 리스트로 추출한다.

    두 가지 포맷을 모두 지원한다:
    - 신형 tool_calls 배열 (MAX_TOOL_CALLS_PER_STEP개까지만 수용)
    - 구형 단일 function_call 필드 (레거시 모델 호환)

    인자는 _normalize_tool_args로 dict로 정규화한다.
    빈 리스트가 반환되면 "도구 호출 없음 = 모델이 최종 답을 냈음"을 의미한다.
    """
    calls: List[Tuple[str, Dict[str, Any]]] = []
    tool_calls = message.get("tool_calls") if isinstance(message, dict) else None
    if isinstance(tool_calls, list):
        # 한 스텝의 도구 호출 수를 상한으로 제한
        for call in tool_calls[:MAX_TOOL_CALLS_PER_STEP]:
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = _to_text(function.get("name"))
            arguments = _normalize_tool_args(function.get("arguments"))
            if name:
                calls.append((name, arguments))
    # 구형 단일 function_call 포맷 호환 처리
    function_call = message.get("function_call") if isinstance(message, dict) else None
    if isinstance(function_call, dict):
        name = _to_text(function_call.get("name"))
        arguments = _normalize_tool_args(function_call.get("arguments"))
        if name:
            calls.append((name, arguments))
    return calls


def _message_answer(message: Dict[str, Any]) -> str:
    """LLM 응답 메시지의 content를 평문 텍스트로 변환한다.

    content가 멀티파트 리스트(예: [{"text": ...}, ...])인 경우 각 조각의
    text를 줄바꿈으로 합치고, 문자열이면 그대로 정리해 반환한다.
    """
    content = message.get("content") if isinstance(message, dict) else ""
    if isinstance(content, list):
        return "\n".join(_to_text(item.get("text") if isinstance(item, dict) else item) for item in content).strip()
    return _to_text(content)


def _final_answer(
    *,
    prompt: str,
    observations: List[Dict[str, Any]],
    model_cfg: Dict[str, Any],
    max_tokens: int,
    enable_thinking: bool = False,
) -> Tuple[str, Dict[str, int]]:
    """도구 없이(tools=None) 최종 답변만 강제로 1회 생성한다.

    에이전트 루프가 max_llm_calls를 다 쓰고도 텍스트 답을 내지 못했을 때
    호출되는 마무리 경로. final=True 메시지("지금 답하라")로 모델을 호출한다.

    반환값: (답변 텍스트, 이번 호출의 토큰 사용량) 튜플.
    """
    response = _chat_completion_response(
        model_cfg=model_cfg,
        messages=_build_messages(prompt, observations, final=True),
        max_tokens=max_tokens,
        enable_thinking=enable_thinking,
        tools=None,
    )
    return _message_answer(_choice_message(response)), _response_usage(response)


# ---------------------------------------------------------------------------
# 능력 재탐색 루프 (structural): 사후 검증에서 미관측 SDK 호출이 나오면,
# 그 능력(operation)을 소스 전체에서 다시 검색해 관찰을 보강하고, 모델에게
# 교정 답변을 1회 재생성시킨다. 리트리벌을 '엔티티 중심'에서 '능력 중심'으로
# 확장해, 지목된 클래스에 없는 기능(예: 로드가 파생/합성 레이어에 있는 경우)을
# 찾아내게 한다.
# ---------------------------------------------------------------------------

# 이 재탐색 루프를 끄고 싶을 때 False로.
RESEARCH_UNVERIFIED_CALLS = True
# 재탐색에서 추가로 실행할 도구 호출(검색/타입그래프)의 상한
MAX_RESEARCH_TOOL_CALLS = 6


def _research_missing_capabilities(
    unverified: List[Dict[str, str]],
    observations: List[Dict[str, Any]],
    trace: "_TraceRecorder",
    *,
    prompt: str,
) -> int:
    """미관측 호출이 가리키는 '능력'을 소스 전체에서 재탐색해 관찰을 보강한다.

    각 미관측 (Type, Member)에 대해:
    - source_search(Member): 그 연산이 실제로 존재하는 타입을 소스 전역에서 찾음
    - source_type_graph(Type): 그 타입의 파생/관련 타입(능력을 실제로 구현할 수도
      있는 서브클래스 등)을 발견
    실행 결과는 observations/trace에 그대로 누적된다 (LLM 토큰 소모 없음).

    반환값: 실제로 실행한 추가 도구 호출 수.
    """
    queries: List[Tuple[str, str]] = []  # (tool_name, query)
    seen: set = set()

    def add(tool_name: str, query: str) -> None:
        query = _to_text(query)
        key = (tool_name, query.lower())
        if query and key not in seen:
            seen.add(key)
            queries.append((tool_name, query))

    for item in unverified:
        member = _to_text(item.get("member"))
        type_name = _to_text(item.get("type"))
        add("source_search", member)
        add("source_search", f"{type_name} {member}")
        add("source_type_graph", type_name)
    # 사용자 질문 자체로도 한 번 더 검색해 연산 맥락(로드/열기 등)을 넓게 훑는다
    add("source_search", prompt)

    executed = 0
    for tool_name, query in queries[:MAX_RESEARCH_TOOL_CALLS]:
        observation = _execute_tool(tool_name, {"query": query}, trace, prompt=prompt)
        observations.append({"tool": tool_name, "input": {"query": query}, "observation": observation})
        executed += 1
    return executed


def _correction_directive(unverified: List[Dict[str, str]]) -> str:
    """교정 재생성에 쓸 지시문을 만든다.

    초안에서 미관측으로 표기된 호출 목록과, 새로 보강된 source_facts를 근거로
    '관측된 API만' 다시 쓰라는 지시를 담는다.
    """
    calls = ", ".join(f"`{item['call']}`" for item in unverified)
    return (
        "Your previous draft used these calls that are NOT in the observed source API and may not exist: "
        f"{calls}. Additional source facts were just added above from a targeted search. "
        "Rewrite the answer using ONLY observed APIs from source_facts.api_signatures: "
        "if a real API for that operation now appears (possibly on a related or derived type, "
        "e.g. a concrete layer subclass), use it; if none exists in the observed facts, "
        "explicitly state that the operation has no observed source API and omit the fabricated call. "
        "Keep the same overall format (WPF: separate xaml and code-behind blocks unless the user asked otherwise)."
    )


def answer_source_question(
    *,
    prompt: str,
    model: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    max_tokens: int = config.DEFAULT_MAX_TOKENS,
    max_llm_calls: int = config.DEFAULT_MAX_LLM_CALLS,
    enable_thinking: bool = False,
) -> Dict[str, Any]:
    """소스 질문에 답하는 에이전트의 메인 진입점 (POST /api/v1/source/answer).

    동작 흐름 (ReAct 스타일 루프, 최대 max_llm_calls회):
    1. 모델 호출 — 이번 스텝에 맞는 도구 목록(_tool_definitions_for_step)과
       지금까지의 관찰(source_facts 압축본)을 함께 전달
    2. 응답에 tool_calls가 있으면 → _execute_tool로 실행해 관찰을 누적하고
       다음 스텝으로; tool_calls가 없으면 → 그 응답 텍스트가 최종 답
    3. 사후 검증(_unverified_sdk_calls)에서 미관측 SDK 호출이 나오면,
       _research_missing_capabilities로 그 능력을 소스 전역에서 재탐색해 관찰을
       보강하고 교정 답변을 1회 재생성한다(_correction_directive). 미관측 호출을
       더 줄인 경우에만 교정본을 채택한다.
    4. 남은 미관측 호출은 _validate_generated_code가 경고로 표기한다.

    루프가 끝나도 답이 없으면 _final_answer로 도구 없이 강제 1회 더 호출해
    답을 받아낸다. 그래도 답이 비면 ApiError(LLM_EMPTY_ANSWER, 502)를 던진다.

    파라미터:
    - prompt: 사용자 질문 (필수; 비어 있으면 EMPTY_PROMPT 오류)
    - model: 사용할 모델명 (없으면 빈 문자열로 전달 — vLLM은 서버에 모델이
      하나만 떠 있으면 이름 없이도 그 모델로 응답한다)
    - llm_base_url: vLLM 서버 주소 (없으면 config.LLM_BASE_URL)
    - session_id: 응답에 그대로 되돌려줄 세션 식별자
    - max_tokens: 한 번의 LLM 응답 토큰 상한 (256~16384로 클램프)
    - max_llm_calls: 루프 내 LLM 호출 횟수 상한 (1~40으로 클램프)
    - enable_thinking: Qwen 계열 사고 모드 토글

    반환값: 다음 키를 담은 dict
    - answer: 최종 답변 텍스트
    - session_id / model / llm_base_url: 요청 컨텍스트 echo
    - trace: _TraceRecorder가 기록한 전체 도구 호출 이력 (디버깅용)
    - summary: 한 줄 요약
    - usage: 도구 호출 수, LLM 호출 수, 누적 토큰 사용량(usage_totals)
    """
    normalized_prompt = _to_text(prompt)
    if not normalized_prompt:
        raise ApiError("EMPTY_PROMPT", "prompt is required")

    # 도구 호출 추적기와 모델 설정 준비
    trace = _TraceRecorder()
    completion_token_budget = _safe_int(max_tokens, 4096, 256, 16384)
    model_cfg = {
        "model": _to_text(model),
        "model_server": _ensure_model_server(llm_base_url or ""),
    }

    observations: List[Dict[str, Any]] = []
    completion_calls = 0
    final_answer = ""
    max_steps = _safe_int(max_llm_calls, 12, 1, 40)
    # 전체 루프의 토큰 사용량 누적 합계
    usage_totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # 답변 처리 시작을 기록 (모델/서버/프롬프트 길이/최대 스텝)
    logger.info(
        "source answer start: model=%s server=%s prompt_chars=%d max_steps=%d",
        model_cfg["model"],
        model_cfg["model_server"],
        len(normalized_prompt),
        max_steps,
    )

    # === 메인 에이전트 루프 ===
    for _ in range(max_steps):
        # (1) 모델 호출 — 관찰이 하나라도 있으면 final=True 메시지로
        #     "가능하면 지금 답하라"고 유도하되 도구는 계속 개방해 둔다
        response = _chat_completion_response(
            model_cfg=model_cfg,
            messages=_build_messages(normalized_prompt, observations, final=bool(observations)),
            max_tokens=completion_token_budget,
            enable_thinking=enable_thinking,
            tools=_tool_definitions_for_step(normalized_prompt, observations),
        )
        _add_response_usage(usage_totals, response)
        completion_calls += 1
        message = _choice_message(response)
        tool_calls = _extract_tool_calls(message)
        # (2-a) 도구 호출이 없으면 모델이 최종 답을 낸 것
        if not tool_calls:
            final_answer = _message_answer(message)
            break
        # (2-b) 도구 호출이 있으면 순서대로 실행하여 관찰을 누적
        for tool_name, arguments in tool_calls:
            observation = _execute_tool(tool_name, arguments, trace, prompt=normalized_prompt)
            observations.append({"tool": tool_name, "input": arguments, "observation": observation})

    # === 루프 종료 후 마무리 ===
    if not final_answer:
        # 도구 없이 강제로 최종 답변을 1회 더 요청
        final_answer, final_usage = _final_answer(
            prompt=normalized_prompt,
            observations=observations,
            model_cfg=model_cfg,
            max_tokens=completion_token_budget,
            enable_thinking=enable_thinking,
        )
        for key, value in final_usage.items():
            usage_totals[key] = int(usage_totals.get(key) or 0) + value
        completion_calls += 1
    # 그래도 답이 비어 있으면 서버 오류로 처리
    if not final_answer:
        logger.error("source answer produced no result after %d completion calls", completion_calls)
        raise ApiError("LLM_EMPTY_ANSWER", "backend source agent did not produce an answer", status_code=502)

    # 능력 재탐색 피드백 루프: 재탐색 트리거는 '주석 포함'으로 능력 갭을 감지한다
    # (모델이 API를 못 찾아 주석으로 남긴 경우까지 포함). 갭이 있으면 그 능력을
    # 소스 전역에서 다시 검색해 관찰을 보강하고, 교정 답변을 1회 재생성한다.
    gaps = _unverified_sdk_calls(final_answer, observations, strip_comments=False)
    if gaps and RESEARCH_UNVERIFIED_CALLS:
        logger.info(
            "capability gap: %d unresolved call(s): %s — researching",
            len(gaps),
            ", ".join(item["call"] for item in gaps),
        )
        researched = _research_missing_capabilities(gaps, observations, trace, prompt=normalized_prompt)
        if researched:
            response = _chat_completion_response(
                model_cfg=model_cfg,
                messages=_build_messages(
                    normalized_prompt,
                    observations,
                    final=True,
                    correction=_correction_directive(gaps),
                ),
                max_tokens=completion_token_budget,
                enable_thinking=enable_thinking,
                tools=None,
            )
            _add_response_usage(usage_totals, response)
            completion_calls += 1
            corrected_answer = _message_answer(_choice_message(response))
            if corrected_answer:
                corrected_gaps = _unverified_sdk_calls(corrected_answer, observations, strip_comments=False)
                # 교정본이 능력 갭(주석 포함)을 더 줄였을 때만 채택
                if len(corrected_gaps) < len(gaps):
                    logger.info("correction reduced capability gaps %d → %d", len(gaps), len(corrected_gaps))
                    final_answer = corrected_answer

    # 최종 사후 검증: 남은 '활성(비주석)' 미관측 호출만 경고로 표기한다 (LLM 재호출 없음).
    final_answer, unverified_calls = _validate_generated_code(
        final_answer, observations, prompt=normalized_prompt
    )

    # 정상 완료: 도구 호출 수/모델 호출 수/총 토큰을 한 줄로 기록
    logger.info(
        "source answer done: tool_calls=%d completion_calls=%d total_tokens=%d",
        len(trace.items),
        completion_calls,
        usage_totals["total_tokens"],
    )
    return {
        "answer": final_answer,
        "session_id": _to_text(session_id),
        "model": model_cfg["model"],
        "llm_base_url": model_cfg["model_server"],
        "trace": trace.items,
        "summary": f"Completed by backend source agent with {len(trace.items)} source tool observations.",
        "validation": {"unverified_calls": unverified_calls},
        "usage": {
            "tool_calls": len(trace.items),
            "completion_calls": completion_calls,
            "prompt_tokens": usage_totals["prompt_tokens"],
            "completion_tokens": usage_totals["completion_tokens"],
            "total_tokens": usage_totals["total_tokens"],
        },
    }
