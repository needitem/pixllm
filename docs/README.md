# PIXLLM Docs

기준일: 2026-04-01

이 폴더 문서는 현재 구현과 목표 설계를 함께 다룹니다. 다만 현재 코드를 설명할 때는 아래 문서를 우선 기준으로 봅니다.

- `01-overview/시스템_상세_아키텍처_설계.md`
- `02-design/desktop_layered_tool_loop_architecture.md`
- `02-design/API_인터페이스_설계.md`
- `02-design/에이전트_상세_설계.md`
- `05-reference/claude-code-vs-pixllm-20260401.md`

현재 구현의 핵심은 `desktop` 로컬 에이전트 경로입니다.

- Renderer -> preload IPC -> Electron main -> `local_agent_service.cjs`
- `LocalAgentEngine`가 턴 루프를 관리
- `LocalAgentRuntime`이 request context, tool policy, grounding, tool batch 실행을 담당
- `createLocalToolCollection`이 실제 로컬 도구 registry
- `workspace.cjs`가 파일/검색/셸/빌드 실행을 담당
- 백엔드의 `/api/v1/runs`와 approval API는 별도 운영 표면이며, 현재 로컬 채팅 루프의 중심은 아닙니다

현재 로컬 에이전트 경로에서 아직 구현되지 않은 항목도 명시적으로 구분해서 봐야 합니다.

- MCP/open-world tool integration
- team worker / remote bridge 실행
- streaming 중 즉시 tool execution
- desktop local loop와 backend tool runtime의 단일화

폴더 구조:

- `01-overview`: 현재 구현 기준의 큰 구조와 운영 개념
- `02-design`: 구현 세부와 향후 설계 방향
- `03-test`: 검증 기록
- `05-reference`: 비교 분석과 참고 자료

주의:

- 일부 `02-design` 문서는 여전히 계획 성격이 남아 있습니다.
- 현재 동작 여부는 항상 `desktop/src/main/`과 `backend/app/routers/` 코드를 우선합니다.
