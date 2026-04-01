# 01-overview

이 폴더는 PIXLLM의 현재 운영 구조를 설명합니다.

현재 구현에서 가장 중요한 축은 `desktop-first local agent runtime`입니다.

- 단일 로컬 에이전트가 한 턴을 반복 처리합니다
- request context를 먼저 만들고 그 위에서 tool loop를 돌립니다
- tool 입력 검증, 경로 정책, grounded answer check가 로컬 런타임에 들어 있습니다
- backend는 모델/health/runs/approval 같은 별도 서비스 역할을 맡습니다

현재 구현 기준으로 먼저 읽을 문서:

1. `시스템_상세_아키텍처_설계.md`
2. `../02-design/desktop_layered_tool_loop_architecture.md`
3. `../02-design/API_인터페이스_설계.md`
4. `../05-reference/claude-code-vs-pixllm-20260401.md`

주의:

- 예전 문서에 있던 `team`, `remote`, `plugin/skill`, `MCP`는 현재 desktop local agent 경로의 기본 기능이 아닙니다.
- 현재 코드를 설명할 때는 `desktop/src/main/core/local_agent_engine.cjs`, `local_agent_runtime.cjs`, `local_tools.cjs`를 기준으로 봅니다.
