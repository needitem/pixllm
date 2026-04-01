# 앱기반 멀티 에이전트 시스템 TODO

> 목적: PIXLLM을 `세션 커널 + 도구/태스크 + 팀/브리지` 구조로 옮기기 위한 구현 체크리스트

## 0. 개념 전환

- [ ] `conversation-only` 모델을 `session / turn / task / artifact` 모델로 교체
- [ ] `intent-heavy` 설명을 `minimal routing + tool loop`로 교체
- [ ] 데스크톱을 단순 채팅 클라이언트가 아니라 주 실행면으로 고정

## 1. Session Kernel

- [ ] 세션 생성, 재개, 종료 수명주기 정의
- [ ] turn 실행 상태 머신 정의
- [ ] 공통 context builder 구현
- [ ] minimal router 구현
- [ ] final response에 verification 구조 포함

## 2. Tool Plane

- [ ] 파일 읽기/검색/편집 도구 정비
- [ ] 셸/빌드/테스트 도구를 task 승격 가능한 구조로 정비
- [ ] MCP, plugin, skill 도구를 공통 registry에 편입
- [ ] tool result를 표준 evidence schema로 저장

## 3. Task Plane

- [ ] `local_shell`, `local_agent`, `remote_agent`, `verification` task 정의
- [ ] task retry/resume/cancel 상태 전이 정의
- [ ] artifact 저장 구조 정의
- [ ] approval-required task 계약 정의

## 4. Team Plane

- [ ] 병렬 worker 생성 기준 정의
- [ ] 파일 ownership 규칙 정의
- [ ] worker 산출물을 artifact와 evidence로 재통합
- [ ] team status를 UI와 control plane에 모두 노출

## 5. Bridge Plane

- [ ] remote environment 등록 API 정의
- [ ] work polling/ack/stop 계약 구현
- [ ] 세션 재연결과 heartbeat 지원
- [ ] worktree 또는 isolated workspace 전략 확정

## 6. Desktop UI

- [ ] session rail
- [ ] timeline stream
- [ ] artifact viewer
- [ ] approval inbox
- [ ] team monitor
- [ ] bridge status panel

## 7. Security and Policy

- [ ] permission mode 정의
- [ ] 위험 명령 승인 흐름 구현
- [ ] plugin trust 정책 정의
- [ ] remote token과 secret 저장 정책 정의

## 8. Observability

- [ ] session/turn/task/tool correlation id 통일
- [ ] structured event logging 구현
- [ ] bridge/task/approval 대시보드 정의
- [ ] 모델 usage/cost 추적 연결

## 9. Model Plane

- [ ] 기존 LLM 서빙 문서 유지
- [ ] 기존 임베딩 문서 유지
- [ ] 모델 변경 없이 오케스트레이션만 교체하는 원칙 고정

## 10. 완료 기준

- [ ] 기술 질문 대부분이 `tool_loop` 경로로 안정 동작
- [ ] 파일 변경 요청이 `task + approval + artifact + verification`으로 표현됨
- [ ] 병렬 실행과 원격 실행이 세션 안에서 추적 가능
- [ ] UI가 답변뿐 아니라 실행 흐름을 일관되게 보여줌
