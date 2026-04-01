# PIXLLM Desktop App Plan

상태: 2026-04-01 현재 구현 기준 후속 정리 계획

## 1. 현재 baseline

현재 desktop 앱은 아래 축을 이미 갖고 있다.

- workspace 선택
- settings 관리
- session 생성, 복구, 저장
- local agent stream 표시
- tool, terminal, user question, transition 이벤트 표시
- backend runs 조회
- run detail의 tasks, approvals, artifacts 표시

현재 기본 구조는 `App.svelte + preload bridge + QueryEngine runtime`이다.

## 2. 현재 없는 것

- team monitor
- remote bridge panel
- MCP/open-world surface
- multi-agent orchestration UI

이 항목들은 현재 기능처럼 문서화하지 않는다.

## 3. 우선순위

1. local agent timeline과 tool/result 표시를 더 읽기 쉽게 정리
2. runs inspector와 local trace의 관계를 더 명확히 표현
3. approvals, tasks, artifacts 화면을 현재 backend API 기준으로 정리
4. background task 제어 UX 개선

## 4. 문서상 원칙

- desktop은 single-agent console로 설명한다.
- backend는 evidence/control plane으로 설명한다.
- 아직 없는 team/remote/MCP UI를 기본 전제로 적지 않는다.
