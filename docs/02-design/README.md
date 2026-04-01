# 02-design

이 폴더는 현재 구현 설명과 향후 설계 방향을 함께 담습니다.

현재 코드 기준으로 먼저 봐야 하는 문서:

- `desktop_layered_tool_loop_architecture.md`
- `API_인터페이스_설계.md`
- `에이전트_상세_설계.md`

현재 구현 기준 핵심 요약:

- desktop local agent가 실제 주 실행 경로입니다
- `LocalAgentRuntime`이 request context, tool policy, grounding을 묶습니다
- 도구 실행은 로컬 registry 기반이며, MCP/open-world는 현재 경로에 없습니다
- backend의 `/api/v1/runs` 계열은 운영 표면이지 로컬 채팅 루프 자체는 아닙니다

주의:

- 이 폴더의 일부 문서는 장기 설계를 포함합니다
- 현재 동작 여부가 중요할 때는 `desktop/src/main/core/`와 `backend/app/routers/` 코드를 우선합니다
