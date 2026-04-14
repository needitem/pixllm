# Minimal Intent Routing

기준일: 2026-04-06

목적: 현재 PIXLLM이 요청을 어떤 축으로 분기하는지 설명한다.

## Summary

현재 PIXLLM은 복잡한 multi-route planner가 없다. 대신 `processUserInput`, `QueryEngine`, `ToolRuntime`이 아래 세 가지를 결정한다.

- 어떤 evidence plane을 우선 쓸지
- 어떤 tool을 이번 turn에 활성화할지
- 바로 답할지, tool loop를 돌릴지, 사용자에게 다시 물을지, model을 한 턴 더 이어갈지

즉 현재 routing은 `team_run`, `remote_run`, `MCP route` 같은 라우터가 아니라 `single local loop 안의 진입 규칙`에 가깝다.

## 1. 현재 결과 상태

현재 요청은 보통 아래 중 하나로 귀결된다.

- `answer_from_context`
- `tool_loop`
- `user_question`
- `continue_model_turn`

설명:

- `answer_from_context`: 이미 충분한 transcript/context가 있어서 추가 tool 없이 답하는 경우
- `tool_loop`: 기본 경로. 파일 탐색, 읽기, 수정, build, backend evidence 수집 포함
- `user_question`: 경로나 요구사항이 모호해서 추가 확인이 필요한 경우
- `continue_model_turn`: prose-only 응답이지만 model이 다음 turn을 이어가야 하는 경우

## 2. 라우팅 입력

현재 구현이 보는 신호:

- explicit path
- selected file
- change intent
- execution intent
- analysis/compare intent
- `languageProfile`
- `/reference`, `/workspace`, `/hybrid`, `/exec`, `/change`, `/analysis`, `/config` directive
- 기존 trace/file cache가 충분한지
- backend reference evidence가 필요한지

## 3. evidence mode 결정

`processUserInput`는 아래 세 모드 중 하나를 정한다.

- `workspace`: 현재 workspace code를 우선 본다.
- `reference`: backend company reference evidence를 우선 본다.
- `hybrid`: workspace와 backend evidence를 같이 본다.

결정 기준:

- `/reference`, `/workspace`, `/hybrid` directive
- 회사 엔진/내부 문서 언급 여부
- compare 성격 여부
- workspace 존재 여부

## 4. 한국어와 mixed prompt 적응

현재 한국어 적응은 별도 hardcoded glossary가 아니다.

흐름:

1. `processUserInput`가 `languageProfile`을 만든다.
2. 현재 request context는 `symbolHints` 중심의 최소 힌트만 유지한다.
3. parser recovery용 search rewrite 필드는 제거됐다.

즉 routing은 언어별 하드코딩이 아니라 `minimal intent routing + symbol hint extraction` 구조다.

## 5. tool scope 결정

현재는 request context에서 초기 tool scope를 만든다.

- ambiguous short prompt은 별도 질문 툴 없이 최소 scope로 시작
- todo 성격이면 `todo_*`
- runtime task 성격이면 `terminal_capture`, `task_*`
- workspace 분석 성격이면 discovery/read 계열 활성화
- reference 성격이면 `company_reference_search` 우선 활성화
- change 성격이면 mutation tool은 보통 후속 turn이나 grounded context 이후 활성화
- execution 성격이면 build/shell/task tool을 조건부 활성화

이후 `ToolRuntime.activeToolNames()`가 turn과 trace 상태를 보고 활성 집합을 더 넓힌다.

## 6. continuation 결정

현재 prose-only 응답은 무조건 final이 아니다.

- assistant가 tool call 없이 prose만 냈더라도
- `nextSpeakerCheck`가 `model`을 반환하면
- `Please continue.` meta message를 넣고 다음 turn으로 넘긴다.

이 흐름은 heavy finalization rule보다 약하지만, Qwen이 search/read를 이어가야 하는 상황을 살려주는 현재 routing의 일부다.

## 7. 현재 없는 routing

현재 없는 것:

- team routing
- remote routing
- bridge session routing
- MCP/open-world routing
- plugin/skill host routing

따라서 현재 문맥에서 "intent routing"은 거대한 오케스트레이터가 아니라 `tool loop 진입과 continuation을 위한 최소 분기`다.
