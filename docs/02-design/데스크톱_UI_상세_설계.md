# 데스크톱 UI 상세 설계

> 목적: 현재 PIXLLM 데스크톱 UI가 실제로 어떤 화면과 상태를 다루는지 정리

## 1. 현재 UI 목표

현재 데스크톱 UI의 목표는 두 가지입니다.

- 로컬 에이전트 대화와 실행 흔적을 같은 화면에서 보여주기
- backend runs의 task / approval / artifact를 별도 조회면에서 확인하게 하기

즉 현재 UI는 "실행 콘솔을 지향"하지만, 과거 문서처럼 team/bridge 패널까지 구현된 상태는 아닙니다.

## 2. 현재 화면 구조

현재 renderer는 크게 두 모드로 나뉩니다.

- `main` 뷰
- `runs` 뷰

### Main 뷰

- 설정 및 workspace 컨트롤
- session rail
- 대화 타임라인
- 입력 composer
- agent stream 상태 표시

### Runs 뷰

- recent runs 목록
- 선택한 run의 summary
- approvals 탭
- tasks 탭
- artifacts 탭

## 3. 현재 실제로 보이는 이벤트

로컬 agent 스트림에서 UI가 다루는 주요 이벤트는 아래입니다.

- `request_start`
- `session_restored`
- `status`
- `model`
- `tool_use`
- `tool_result`
- `transition`
- `tool_batch_start`
- `tool_batch_end`
- `terminal`
- `user_question`
- `brief`
- `token`
- `done`
- `cancelled`
- `error`

즉 현재 타임라인은 message-only가 아니라 tool / terminal / question 이벤트도 함께 다룹니다.

## 4. 현재 상태 모델

현재 UI가 직접 유지하는 핵심 상태는 아래 범주입니다.

- settings
- workspace path
- sessions 목록
- 선택된 session과 conversation
- stream request 상태
- runs 목록
- 선택된 run detail
- run approvals / artifacts / tasks

과거 문서의 `team_members`, `bridge_connections` 같은 상태는 현재 UI 기본 상태가 아닙니다.

## 5. 현재 컴포넌트 현실

현재 구현은 아직 feature-split 구조가 아닙니다.

실질적인 UI 중심은 아래 파일들입니다.

- `desktop/src/renderer/App.svelte`
- `desktop/src/renderer/lib/api.ts`
- `desktop/src/renderer/lib/bridge.ts`
- `desktop/src/renderer/lib/store.ts`

즉 문서에서 `TeamMonitor`, `BridgeStatus` 같은 독립 컴포넌트를 현재 구성요소처럼 설명하는 것은 맞지 않습니다.

## 6. 현재 UX의 강점

- session 저장과 재개가 됩니다.
- 로컬 agent의 stream 이벤트가 즉시 보입니다.
- backend run approvals와 artifacts를 따로 점검할 수 있습니다.
- tool result와 terminal 결과가 대화 흐름과 분리되지 않습니다.

## 7. 현재 UX의 한계

- `App.svelte`에 상태와 화면 로직이 많이 모여 있습니다.
- local trace / tool batch / terminal capture 시각화가 더 정돈될 필요가 있습니다.
- runs 뷰와 main 뷰 사이의 연결이 아직 느슨합니다.
- artifact viewer와 diff/terminal 전용 뷰는 더 다듬을 여지가 큽니다.

## 8. 다음 리팩터링 방향

현재 UI 문서가 가리켜야 할 다음 단계는 아래입니다.

1. session rail, timeline, composer, run inspector로 화면 분리
2. tool / terminal / user question 이벤트 row를 컴포넌트화
3. approvals / artifacts / tasks 탭 정리
4. local trace와 run snapshot을 더 명확히 연결

현재 PIXLLM 데스크톱 UI는 `팀/브리지 대시보드`가 아니라 `로컬 세션 타임라인 + run inspector`로 설명하는 것이 정확합니다.
