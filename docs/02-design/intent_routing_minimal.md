# Minimal Intent Routing

> 목적: 현재 PIXLLM 로컬 에이전트가 실제로 어떤 수준의 라우팅을 하는지 설명

## Summary

현재 PIXLLM에는 별도의 다중 실행면 라우터가 없습니다.

실제 동작은 `desktop/src/main/core/local_request_context.cjs`가 요청 신호를 정리하고, `LocalAgentEngine`이 하나의 로컬 tool loop 안에서 답변과 도구 호출을 반복하는 구조입니다.

즉 이 문서에서 말하는 "routing"은 `team_run`, `remote_run` 같은 표면 분기가 아니라, 현재 턴을 `즉시 답변`, `로컬 도구 탐색`, `사용자 보충 질문` 중 어느 형태로 흘릴지 결정하는 얇은 게이트입니다.

## 1. 현재 기준의 라우팅 결과

현재 코드에서 의미 있는 결과는 아래 네 가지입니다.

- `answer_from_context`
- `tool_loop`
- `user_question`
- `run_snapshot_attach`

설명:

- `answer_from_context`: 세션 안의 기존 근거와 이미 수집된 trace만으로 답할 수 있을 때입니다.
- `tool_loop`: 기본값입니다. 파일 탐색, 검색, 읽기, 편집, 셸, 빌드 같은 로컬 도구를 사용합니다.
- `user_question`: 경로, 의도, 확인이 부족할 때 `ask_user_question`과 `user_question` stream 이벤트로 사용자 입력을 더 받습니다.
- `run_snapshot_attach`: backend의 `/api/v1/runs` 데이터는 UI에서 별도 조회/첨부되지만, 로컬 에이전트가 실행 표면으로 분기하는 것은 아닙니다.

## 2. 실제 결정 지점

현재 구현에서 라우팅은 독립 classifier가 아니라 아래 조합으로 결정됩니다.

- `createRunRequestContext`
- 시스템 프롬프트의 grounding 규칙
- `LocalAgentRuntime`의 grounded path 계산
- `local_tool_policy`의 permission gate

흐름은 아래와 같습니다.

1. 사용자 입력에서 explicit path, selected file, 변경/실행/분석 의도를 추출합니다.
2. 엔진이 시스템 프롬프트에 이 컨텍스트를 실어 모델 턴을 시작합니다.
3. 모델이 도구 없이 답하면 `answer_from_context`에 가깝게 종료됩니다.
4. 모델이 도구를 요청하면 `tool_loop`로 진행합니다.
5. 입력이 부족하거나 확인이 필요하면 `user_question` 이벤트를 보냅니다.
6. tool policy가 막으면 같은 턴 안에서 다른 전략으로 재시도합니다.

## 3. 현재 사용하는 입력 신호

현재 코드가 실제로 보는 신호는 아래 수준입니다.

- 사용자가 명시적으로 파일 경로를 언급했는가
- UI에서 선택된 파일이 있는가
- 분석 요청인가
- 수정 요청인가
- 실행, 빌드, 테스트 요청인가
- 이미 trace나 file cache에 grounding된 파일이 있는가
- 수정 전에 해당 파일을 읽었는가

즉 문장 taxonomy보다 `경로`, `실행 의도`, `이미 확보된 근거`가 더 중요합니다.

## 4. 현재 하지 않는 것

현재 로컬 경로에는 아래가 없습니다.

- `team_run`
- `remote_run`
- bridge session routing
- MCP/open-world routing
- plugin/skill 실행면 선택

이 개념들은 현재 코드 기준 "실행 중인 기능"이 아니라 과거 설계 또는 장기 확장 아이디어입니다.

## 5. 예시

- `이 함수가 어디서 호출되는지 찾아줘` -> `tool_loop`
- `이 파일 두 개만 기준으로 차이 설명해줘` -> `answer_from_context` 또는 짧은 `tool_loop`
- `이 버그 고치고 테스트 돌려줘` -> `tool_loop`
- `어느 파일을 고쳐야 할지 모르겠어, 먼저 찾자` -> `tool_loop`
- `이 설정 바꿔도 되는지 먼저 확인해줘` -> `user_question` 또는 read-first `tool_loop`

## 6. 설계 원칙

- 기본 경로는 하나의 로컬 tool loop입니다.
- 별도 "큰 intent 분류기"보다 request context와 tool policy를 신뢰합니다.
- 불충분한 근거는 route 확장이 아니라 `더 읽기`, `더 찾기`, `질문 되묻기`로 해결합니다.
- backend runs는 운영/검토 표면이지, 로컬 채팅 루프의 라우팅 결과가 아닙니다.

현재 PIXLLM의 minimal router는 `질문의 종류 이름`을 맞추는 컴포넌트가 아니라, `로컬 도구 루프를 바로 돌릴지`, `바로 답할지`, `질문을 되돌릴지`를 정하는 얇은 문맥 계층으로 보는 것이 맞습니다.
