# 01-overview

이 섹션은 현재 PIXLLM의 실제 동작 구조를 설명한다.

현재 시스템은 `desktop-first single agent loop` 구조다.

- Electron renderer가 UI를 담당한다.
- preload IPC가 renderer와 main process를 연결한다.
- Electron main에서 `QueryEngine` 기반 로컬 agent loop를 실행한다.
- backend는 runs, approvals, evidence, health, LLM endpoint를 제공한다.
- desktop이 최종 응답 주체이고, backend는 두 번째 agent가 아니다.

먼저 읽을 문서:

1. `시스템_상세_아키텍처_설계.md`
2. `../02-design/desktop_layered_tool_loop_architecture.md`
3. `../02-design/API_인터페이스_설계.md`
4. `../05-reference/claude-code-vs-pixllm-20260401.md`

범위 밖:

- MCP/open-world 기본 통합
- remote bridge session
- multi-agent 기본 경로
