# PIXLLM Docs

기준일: 2026-04-01

이 문서 묶음은 현재 저장소의 실제 구현을 기준으로 정리한다. 예전 문서에 남아 있던 `local_agent_*`, `desktop/src/main/core/*`, `LocalAgentRuntime` 기준 설명은 더 이상 현재 구조가 아니다.

현재 기준축은 아래와 같다.

- `desktop`이 유일한 agent loop를 가진다.
- `backend`는 evidence, runs, approvals, health, LLM endpoint를 제공하는 보조 평면이다.
- desktop 메인 런타임은 `QueryEngine.cjs`, `ToolRuntime.cjs`, `StreamingToolExecutor.cjs`, `processUserInput.cjs`, `tools/*` 구조를 따른다.
- 회사 엔진 소스나 내부 문서는 `company_reference_search`로 backend evidence를 읽기 전용으로 참조한다.
- MCP/open-world, remote bridge, team worker는 현재 기본 경로가 아니다.

먼저 읽을 문서:

1. `01-overview/시스템_상세_아키텍처_설계.md`
2. `02-design/desktop_layered_tool_loop_architecture.md`
3. `02-design/API_인터페이스_설계.md`
4. `02-design/에이전트_상세_설계.md`
5. `05-reference/claude-code-vs-pixllm-20260401.md`

디렉터리 요약:

- `01-overview`: 현재 제품 구조와 실행 경로 개요
- `02-design`: desktop loop, tool/runtime, UI, backend evidence 설계
- `03-test`: 수동 검증 기록
- `05-reference`: 비교 문서와 참고 자료

주의:

- 오래된 계획 문서에는 미래 기능이나 과거 구조 설명이 일부 남을 수 있다.
- 현재 동작과 구현 근거가 더 중요할 때는 `desktop/src/main/`과 `backend/app/` 코드를 우선 본다.
