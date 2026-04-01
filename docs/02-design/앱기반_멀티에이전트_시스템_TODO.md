# 앱기반 멀티 에이전트 시스템 TODO

> 상태: 현재 코드와 제품 방향을 반영해 backlog를 다시 정리한 문서입니다. 지금 우선순위는 멀티 에이전트가 아니라 단일 로컬 런타임 완성도입니다.

## 1. 이미 현재 코드에 들어간 것

- desktop가 실제 주 실행면입니다
- session 생성, 저장, 재개가 됩니다
- `LocalAgentEngine`과 `LocalAgentRuntime`이 분리돼 있습니다
- request context 추출이 있습니다
- 중앙 local tool policy가 있습니다
- grounded final answer 검사와 read-before-edit 규칙이 있습니다
- background task runtime과 terminal capture가 있습니다
- backend `/api/v1/runs` 조회 및 approval/action UI가 있습니다

## 2. 단일 로컬 런타임에서 아직 남은 것

- streaming 중 즉시 tool execution
- interrupt 시 transcript 복구 정교화
- local trace, terminal capture, run snapshot의 공통 표현 정리
- renderer의 `App.svelte` 기능 분리
- artifact / diff / terminal viewer 보강
- local path와 backend run path의 역할 문서화 정리

## 3. backend 운영 표면에서 남은 것

- run detail과 local session의 연결 강화
- approval/action 결과를 main session UI에도 더 명확히 반영
- run task / artifact 데이터의 표준 shape 정리
- health / runs / approvals 문서와 UI를 더 맞추기

## 4. 선택적 미래 과제

아래는 현재 코드의 기본 경로가 아니라, 필요성이 생길 때만 다시 검토할 항목입니다.

- team execution
- remote execution
- bridge-connected worker
- isolated worktree orchestration

즉 현재 backlog에서 이 항목들은 1순위가 아닙니다.

## 5. 명시적 비범위

현재 방향에서 제외하는 것:

- MCP/open-world tool integration
- plugin registry / plugin trust 설계
- skill execution plane을 로컬 에이전트 기본 경로로 넣는 일

## 6. 완료 기준

이 문서의 가까운 완료 기준은 아래입니다.

- 대부분의 기술 질문이 안정적으로 local `tool_loop`에서 처리된다
- 파일 수정과 실행 요청이 grounding 규칙 안에서 일관되게 동작한다
- session / run / approval / artifact 흐름이 UI와 문서에서 서로 맞는다
- 현재 없는 team/remote/MCP 개념이 핵심 설계 문서의 기본 전제가 아니다
