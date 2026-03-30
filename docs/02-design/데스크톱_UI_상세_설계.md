# 데스크톱 UI 상세 설계

> 목적: 현재 Electron + Svelte 기반 UI 구조를 정리

## 현재 역할

- 워크스페이스 선택
- 로컬 파일/grep/svn 상태 확인
- run 목록 및 상세 조회
- approval / cancel / resume
- 스트리밍 chat

## 현재 구조

```text
desktop/src/
  main/
  renderer/
    App.svelte
    lib/
      api.ts
      bridge.ts
      store.ts
```

## 설계 원칙

- 백엔드 API가 실행 상태의 기준 진실 소스다.
- 데스크톱은 로컬 워크스페이스와 브리지 호출을 통해 보조 컨텍스트를 제공한다.
- 기존 웹 `frontend/`는 제거되었고, UI는 데스크톱 하나만 유지한다.
