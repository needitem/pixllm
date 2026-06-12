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
- 환각(hallucination) 방지: 사용자가 특정 API 이름을 물었는데 도구 관찰
  결과에 그 식별자가 전혀 없으면, LLM에게 답을 맡기지 않고
  `_not_observed_api_answer`가 "관측되지 않았다"는 정해진 답변을
  한국어/영어로 직접 반환한다. (LLM이 존재하지 않는 API를 지어내는 것을 차단)

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
MODEL_OBSERVATION_CHARS = 12000
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


def _api_request_tokens(prompt: str) -> List[str]:
    """사용자 프롬프트에서 '특정 API를 묻는' 식별자 토큰을 추출한다.

    환각 방지 가드의 1단계. 두 가지 패턴을 인식한다:
    1. 백틱으로 감싼 식별자: `GetPixelValue` 같은 표기
    2. "XXX API" 패턴: "GetPixelValue API 사용법" 같은 표기 (대소문자 무시)

    반환값: 등장 순서를 유지한 중복 없는 토큰 리스트.
    토큰이 하나도 없으면 가드는 작동하지 않는다(일반 질문으로 간주).
    """
    tokens: List[str] = []
    # 패턴 1: 백틱 식별자 `Foo`
    for token in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", prompt):
        if token not in tokens:
            tokens.append(token)
    # 패턴 2: "Foo API" 형태 (API 단어 바로 앞의 식별자)
    for token in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+API(?=$|[^A-Za-z0-9_])", prompt, flags=re.IGNORECASE):
        if token not in tokens:
            tokens.append(token)
    return tokens


def _observed_identifier_keys(observations: List[Dict[str, Any]]) -> set:
    """관찰 결과에서 '실제로 관측된' 식별자 키 집합을 만든다.

    환각 방지 가드의 2단계. _source_facts_for_model(final=True)로 압축한
    사실에서 다음을 수집해 _identifier_key로 정규화한다:
    - api_signatures의 symbol을 '.'으로 분리한 각 조각
      (예: "NXImage.GetPixel" → "nximage", "getpixel")
    - 시그니처 문자열에서 여는 괄호 앞의 메서드 이름
    - type_relations에 등장하는 타입 이름들

    반환값: 정규화된 식별자 키의 set. _identifier_is_observed에서
    사용자가 물어본 토큰과 대조하는 데 쓰인다.
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


def _identifier_is_observed(token: str, observed_keys: set) -> bool:
    """질문된 토큰이 관측된 식별자 키 집합에 존재하는지 판정한다.

    완전 일치뿐 아니라 한쪽이 다른 쪽의 접미사인 경우도 매치로 인정한다
    (예: 사용자가 "GetPixel"만 쓰고 관측 키는 "nximagegetpixel"인 경우).
    """
    token_key = _identifier_key(token)
    if not token_key:
        return False
    return any(key == token_key or key.endswith(token_key) or token_key.endswith(key) for key in observed_keys)


def _not_observed_api_answer(prompt: str, observations: List[Dict[str, Any]]) -> str:
    """환각 방지 가드의 최종 단계: '관측되지 않은 API' 정형 답변을 생성한다.

    동작 흐름:
    1. 프롬프트에서 API 토큰을 추출 (_api_request_tokens)
       — 토큰이 없으면 일반 질문이므로 가드 미적용("" 반환)
    2. 관찰 결과의 식별자 키와 대조 (_observed_identifier_keys)
       — 하나라도 관측됐으면 정상 흐름이므로 가드 미적용("" 반환)
    3. 질문된 API가 전부 미관측이면, LLM 호출 없이 "관측되지 않았다"는
       고정 답변을 반환한다. 프롬프트에 한글이 있으면 한국어로,
       아니면 영어로 답한다.

    반환값: 빈 문자열("")이면 가드 미발동(정상 흐름 계속),
    비어 있지 않으면 그 자체가 최종 답변이 되어 LLM의 답변 생성을 차단한다.
    이 함수가 이 파일의 핵심 환각 방지 장치다.
    """
    tokens = _api_request_tokens(prompt)
    # 특정 API를 묻는 질문이 아니면 가드를 적용하지 않음
    if not tokens:
        return ""
    observed_keys = _observed_identifier_keys(observations)
    # 질문된 토큰 중 하나라도 관측됐으면 정상적으로 LLM이 답하게 함
    if any(_identifier_is_observed(token, observed_keys) for token in tokens):
        return ""
    name = tokens[0]
    # 프롬프트 언어(한글 포함 여부)에 맞춰 고정 답변을 선택
    if re.search(r"[가-힣]", prompt):
        return (
            f"`{name}` API는 현재 소스에서 관측된 API 시그니처에 없습니다.\n\n"
            "따라서 실제 소스 기준 사용법이나 ref/out 변환 예제 코드는 제공할 수 없습니다."
        )
    return (
        f"`{name}` was not found in the observed source API signatures.\n\n"
        "I cannot provide source-grounded usage or ref/out conversion code for it."
    )


def _build_system_prompt() -> str:
    """에이전트의 시스템 프롬프트를 구성한다.

    핵심 지시 사항:
    - source_facts.api_signatures를 '관측된 API 전부'로 취급할 것
    - 이름이 지목된 API 질문은 관측된 시그니처에서만 답하고,
      없으면 '관측되지 않음'이라고 말할 것 (다른 API로 대체 금지)
    - 코드 예제는 소스 바인딩 문법이 아닌 C# 문법으로 작성할 것
    - ref/out 파라미터는 관측된 C# 타입으로 지역 변수를 선언/초기화할 것
    - 사용자의 언어로 자연스럽게 답할 것
    """
    return "\n".join(
        [
            "You are the PIXLLM backend source agent.",
            "Use source_search for discovery and source_read for exact source spans or declarations when concrete code evidence is needed.",
            "Treat source_facts.api_signatures as the observed API set.",
            "For named-API questions, answer from matching observed signatures only; if none match, say it was not observed and do not substitute unrelated APIs or code.",
            "For SDK/API calls in code, use observed Pixoneer/NXDL signatures; ordinary C# language/runtime syntax is allowed.",
            "For C# answers, emit C# syntax instead of source binding syntax.",
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
    "source_search": "Discover candidate symbols/files plus recommended source_read targets.",
    "source_read": "Inspect exact Source/ spans or indexed symbol targets.",
    "source_type_graph": "Return compact type/member graph and signatures.",
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


def _build_messages(prompt: str, observations: List[Dict[str, Any]], *, final: bool = False) -> List[Dict[str, str]]:
    """LLM에 보낼 chat 메시지 배열을 구성한다.

    기본 구조: [system 프롬프트, user 질문]. 관찰이 있으면 세 번째 user
    메시지로 압축된 관찰(_observations_for_model)과 지시문을 덧붙인다.

    파라미터:
    - final: True면 "이 사실들로 지금 답하라(추가 도구 사용 금지)"는 지시,
      False면 "필요하면 도구를 더 쓰고, 아니면 source_facts만으로 답하라"는 지시.
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
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": bool(enable_thinking)},
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
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


def answer_source_question(
    *,
    prompt: str,
    model: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    max_tokens: int = 4096,
    max_llm_calls: int = 12,
    enable_thinking: bool = False,
) -> Dict[str, Any]:
    """소스 질문에 답하는 에이전트의 메인 진입점 (POST /api/v1/source/answer).

    동작 흐름 (ReAct 스타일 루프, 최대 max_llm_calls회):
    1. 모델 호출 — 이번 스텝에 맞는 도구 목록(_tool_definitions_for_step)과
       지금까지의 관찰(source_facts 압축본)을 함께 전달
    2. 응답에 tool_calls가 있으면 → _execute_tool로 실행해 관찰을 누적하고
       다음 스텝으로; tool_calls가 없으면 → 그 응답 텍스트가 최종 답
    3. 매 스텝마다 환각 가드(_not_observed_api_answer)를 체크 —
       질문된 API가 관측 결과에 없다고 판정되면 즉시 고정 답변으로 종료

    루프가 끝나도 답이 없으면: 환각 가드를 한 번 더 확인한 뒤,
    _final_answer로 도구 없이 강제 1회 더 호출해 답을 받아낸다.
    그래도 답이 비면 ApiError(LLM_EMPTY_ANSWER, 502)를 던진다.

    파라미터:
    - prompt: 사용자 질문 (필수; 비어 있으면 EMPTY_PROMPT 오류)
    - model: 사용할 모델명 (없으면 config.DEFAULT_MODEL)
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
        "model": _to_text(model) or config.DEFAULT_MODEL,
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
        # (2-a) 도구 호출이 없으면 모델이 답을 낸 것 — 단, 환각 가드가
        #       발동하면 모델 답변 대신 "관측되지 않음" 고정 답변을 채택
        if not tool_calls:
            final_answer = _not_observed_api_answer(normalized_prompt, observations) or _message_answer(message)
            break
        # (2-b) 도구 호출이 있으면 순서대로 실행하여 관찰을 누적
        for tool_name, arguments in tool_calls:
            observation = _execute_tool(tool_name, arguments, trace, prompt=normalized_prompt)
            observations.append({"tool": tool_name, "input": arguments, "observation": observation})
        # (3) 매 스텝 환각 가드 체크 — 질문된 API가 미관측으로 확정되면
        #     더 탐색하지 않고 즉시 고정 답변으로 종료
        final_answer = _not_observed_api_answer(normalized_prompt, observations)
        if final_answer:
            break

    # === 루프 종료 후 마무리 ===
    if not final_answer:
        # 환각 가드를 마지막으로 한 번 더 확인
        final_answer = _not_observed_api_answer(normalized_prompt, observations)
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
        "usage": {
            "tool_calls": len(trace.items),
            "completion_calls": completion_calls,
            "prompt_tokens": usage_totals["prompt_tokens"],
            "completion_tokens": usage_totals["completion_tokens"],
            "total_tokens": usage_totals["total_tokens"],
        },
    }
