# PIXLLM Desktop App Plan

## 목표

PIXLLM 데스크톱 앱을 `백엔드 채팅창`이 아니라 `세션 실행 콘솔`로 재설계합니다.

핵심 방향:

- 앱이 주 실행면입니다.
- 사용자는 `세션`, `태스크`, `아티팩트`, `승인`, `팀 실행`을 앱 안에서 다룹니다.
- 백엔드는 모델/데이터/제어 평면으로 남고, 앱은 작업 오케스트레이션의 표면이 됩니다.

## 제품 개념

앱은 아래 다섯 화면군을 중심으로 구성합니다.

- 세션 목록과 재개
- 중앙 작업 스트림
- 우측 컨텍스트/아티팩트 패널
- 하단 터미널/로그 패널
- 승인/팀 상태 패널

## 핵심 사용자 흐름

1. 사용자가 워크스페이스를 선택합니다.
2. 새 세션을 열거나 기존 세션을 재개합니다.
3. 질문, 편집 요청, 리뷰 요청, 빌드/테스트 요청을 보냅니다.
4. 앱은 실행 과정을 메시지뿐 아니라 tool/task 이벤트로 보여줍니다.
5. 필요하면 사용자는 approval inbox에서 승인하거나 거절합니다.
6. 결과는 최종 답변과 함께 diff, 로그, 테스트 결과, 계획서를 아티팩트로 확인합니다.

## 화면 구성

### 1. Session Rail

- 세션 목록
- 최근 워크스페이스
- 즐겨찾기된 프로젝트
- 실행 중 task 배지

### 2. Main Timeline

- 사용자 메시지
- assistant 응답
- tool start/result 이벤트
- task 진행률
- approval 요청과 처리 결과
- verification 요약

### 3. Context Panel

- 현재 파일과 심볼
- 수집된 evidence bundle
- source references
- 모델/실행 모드

### 4. Artifact Panel

- diff viewer
- build/test 결과
- 계획서
- 리뷰 findings
- 명령 결과 로그

### 5. Team and Bridge Panel

- 병렬 worker 상태
- 파일 ownership
- remote session 상태
- reconnect / stop 제어

## 단계별 계획

### Phase 1

- 세션 생성/재개
- 스트리밍 타임라인
- artifact viewer
- approval inbox

### Phase 2

- task retry/resume
- patch apply/reject UX
- structured terminal panel
- verification result panel

### Phase 3

- team execution 시각화
- remote bridge session monitor
- automation/inbox surface

## 비목표

- 순수 채팅 UX로 회귀하지 않습니다.
- 웹 프런트엔드를 별도 제품 표면으로 되살리지 않습니다.
- 모든 작업을 중앙 서버가 먼저 판단하는 구조로 되돌리지 않습니다.

## 성공 기준

- 사용자가 "무슨 작업이 실행됐는지"를 답변 밖에서도 추적할 수 있어야 합니다.
- 장시간 실행과 파일 변경 결과를 아티팩트로 검토할 수 있어야 합니다.
- 세션 단위로 재개, retry, review가 가능해야 합니다.
