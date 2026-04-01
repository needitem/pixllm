# PIXLLM Desktop App Plan

> 상태: 이 문서는 현재 구현 위에서의 다음 단계 계획을 정리합니다. 현재 앱은 이미 동작 중이며, 아래 계획은 그 위에 무엇을 더 정리할지에 대한 것입니다.

## 1. 현재 기준 베이스라인

현재 데스크톱 앱은 이미 아래를 제공합니다.

- workspace 선택
- settings 관리
- session 생성/재개/저장
- 로컬 agent 스트리밍 대화
- tool / terminal / question 이벤트 표시
- backend runs 조회
- run detail의 tasks / approvals / artifacts 확인

현재 UI의 실제 중심은 `desktop/src/renderer/App.svelte` 하나와 preload bridge입니다.

## 2. 현재 없는 것

현재 앱에 없는 것:

- team monitor
- remote bridge panel
- MCP/open-world surface
- 별도 multi-agent orchestration UI

즉 과거 문서처럼 "세션 + 태스크 + 팀 + 브리지"가 모두 구현된 상태는 아닙니다.

## 3. 목표 방향

앱의 방향은 여전히 `단순 채팅창`보다 `실행 과정을 볼 수 있는 데스크톱 콘솔`에 가깝습니다.

다만 현재 기준에서 우선순위는 아래 순서가 맞습니다.

1. 단일 로컬 에이전트 경로를 더 단단하게 만들기
2. session / run / approval / artifact 화면을 정리하기
3. 모놀리식 renderer를 기능 단위로 분리하기
4. 필요가 입증될 때만 team/remote를 다시 검토하기

## 4. 단기 계획

### Phase 1: 현재 경로 정리

- `App.svelte`를 session, timeline, run inspector, approvals 뷰로 분리
- 로컬 tool/terminal 이벤트 표현 개선
- session resume / run snapshot UX 정리
- grounding 실패, tool denial, task failure 표시 개선

### Phase 2: 실행 결과 보기 강화

- artifact viewer 개선
- terminal capture 전용 뷰 정리
- run detail의 tasks / approvals / artifacts 연결 강화
- local trace 요약 보기 추가

### Phase 3: 선택적 확장

- 장시간 작업 재개 UX 보강
- background task 제어 개선
- team/remote 필요성이 제품적으로 입증되면 그때 별도 계획 수립

## 5. 명시적 비범위

현재 계획에서 제외하는 것:

- MCP/open-world integration
- plugin registry surface
- remote bridge를 전제로 한 UI 설계
- 구현되지 않은 multi-agent 패널을 현재 기능처럼 문서화하는 일

## 6. 성공 기준

- 사용자가 현재 세션에서 어떤 tool과 task가 실행됐는지 쉽게 따라갈 수 있어야 합니다.
- runs 화면에서 approvals, tasks, artifacts를 바로 검토할 수 있어야 합니다.
- session 저장/재개와 local trace가 일관되게 보여야 합니다.
- 현재 없는 team/bridge 개념이 UI 문서의 기본 전제가 아니어야 합니다.
