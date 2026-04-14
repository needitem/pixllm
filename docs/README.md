# PIXLLM Docs

기준일: 2026-04-06

이 문서 묶음은 현재 저장소의 실제 구현을 기준으로 정리한다. 현재 PIXLLM의 기본 경로는 더 이상 `LocalAgentEngine`, `LocalAgentRuntime`, `desktop/src/main/core/*` 구조가 아니다.

현재 기준축은 아래와 같다.

- `desktop`이 유일한 agent loop를 가진다.
- `backend`는 evidence, runs, approvals, health, LLM/proxy surface를 제공하는 보조 평면이다.
- desktop 메인 런타임은 `QueryEngine.cjs`, `ToolRuntime.cjs`, `StreamingToolExecutor.cjs`, `processUserInput.cjs`, `QwenAdapter.cjs`, `tools/*` 구조를 따른다.
- Qwen textual tool protocol이 현재 기본 경로다.
  - assistant -> `<tool_call>...</tool_call>`
  - user/tool result -> `<tool_response>...</tool_response>`
- 회사 엔진 소스나 내부 문서는 `company_reference_search`로 backend evidence를 읽기 전용으로 참조한다.
- 한국어 입력은 하드코딩된 용어 사전으로 처리하지 않는다. `processUserInput`가 `languageProfile`과 `symbolHints`를 만든다.
- MCP/open-world, remote bridge, team worker는 현재 기본 경로가 아니다.

먼저 읽을 문서:

1. `01-overview/시스템_상세_아키텍처_설계.md`
2. `02-design/desktop_layered_tool_loop_architecture.md`
3. `02-design/Qwen_출력_적응_설계.md`
4. `02-design/API_인터페이스_설계.md`
5. `02-design/에이전트_상세_설계.md`
6. `05-reference/claude-code-vs-pixllm-20260401.md`

디렉터리 요약:

- `01-overview`: 현재 제품 구조와 실행 경로 개요
- `02-design`: desktop loop, Qwen adapter, tool/runtime, UI, backend evidence 설계
- `05-reference`: 비교 문서와 참고 자료

주의:

- 오래된 계획 문서에는 미래 기능이나 과거 구조 설명이 일부 남을 수 있다.
- 현재 동작과 구현 근거가 더 중요할 때는 `desktop/src/main/`과 `backend/app/` 코드를 우선 본다.
- `tool_choice=required` 같은 과거 stopgap은 현재 기본 설계가 아니다. 현재 기본 설계는 Qwen adapter, tolerant parser, `nextSpeakerCheck`, request shaping 계층이다.
