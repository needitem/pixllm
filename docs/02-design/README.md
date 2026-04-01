# 02-design

이 섹션은 현재 구현의 설계 의도와 다음 리팩토링 방향을 정리한다.

현재 기준으로 먼저 읽을 문서:

- `desktop_layered_tool_loop_architecture.md`
- `API_인터페이스_설계.md`
- `에이전트_상세_설계.md`
- `intent_routing_minimal.md`

현재 핵심 설계 요약:

- desktop이 유일한 agent loop를 가진다.
- `QueryEngine -> processUserInput -> ToolRuntime -> tools/*`가 기본 실행축이다.
- backend는 evidence, runs, approvals, health, LLM endpoint를 제공한다.
- `company_reference_search`가 backend knowledge/code evidence를 desktop loop에 연결한다.
- tool policy는 중앙 gate와 tool별 hook을 같이 사용한다.
- 현재 streaming tool execution은 "스트리밍 중 선실행 + turn 종료 시 claim/recovery" 수준이다.

주의:

- 과거 `LocalAgentEngine`, `LocalAgentRuntime`, `desktop/src/main/core/*` 기준 설명은 현재 구조가 아니다.
- 미래 계획 문서는 현재 기능처럼 읽히지 않도록 구분해서 봐야 한다.
