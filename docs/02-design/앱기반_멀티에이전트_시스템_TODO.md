# 앱기반 멀티에이전트 시스템 TODO

상태: 현재 코드를 반영한 backlog 재정리

이 문서의 우선순위는 멀티에이전트가 아니라 `single local runtime의 완성도`다.

## 1. 이미 들어간 것

- desktop이 실제 주 실행면이다.
- session 생성, 저장, 복구가 된다.
- `QueryEngine`과 `ToolRuntime` 중심 구조가 들어갔다.
- request context 추출이 들어갔다.
- 중앙 tool policy가 들어갔다.
- grounded final answer, read-before-edit, stale-read 방어가 들어갔다.
- background task runtime과 terminal capture가 있다.
- backend `/api/v1/runs` 조회와 approval UI가 있다.
- backend evidence를 `company_reference_search`로 읽을 수 있다.

## 2. single local runtime에서 더 해야 할 것

- same-stream tool result reinjection
- interrupt/transcript recovery 추가 강화
- local trace, terminal capture, run snapshot의 공통 vocabulary 정리
- renderer `App.svelte` 책임 분리
- artifact / diff / terminal viewer 보강
- local path와 backend reference path 역할 문서화 강화

## 3. backend 보조 표면에서 더 할 것

- run detail과 local session 연결 강화
- approval/action 결과를 main session UI에 더 명확히 반영
- run task / artifact shape 정리
- health / runs / approvals 문서와 UI 정합성 유지

## 4. 선택적 미래 과제

현재 기본 경로가 아닌 항목:

- team execution
- remote execution
- bridge-connected worker
- isolated worktree orchestration

즉 이 항목들은 1순위 backlog가 아니다.

## 5. 명시적 비범위

- MCP/open-world tool integration
- plugin registry / plugin trust 설계
- skill execution plane을 local agent 기본 경로로 두는 것
