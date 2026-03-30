# PIXLLM 앱기반 멀티에이전트 시스템 전체 체크리스트

> 현재 기준: 앱 기반 UI는 `desktop/` 하나만 유지

## 앱 기준 확인

- [x] Electron + Svelte 데스크톱 UI 사용
- [x] 백엔드 API와 스트리밍 chat 연동
- [x] 워크스페이스 선택 / run 조회 / 로컬 도구 루프 제공
- [x] 레거시 웹 `frontend/` 제거

## 후속 정리

- [ ] 백엔드 import 레거시 경로 축소
- [ ] execution run 상태 기록 중복 축소
- [ ] 문서와 배포 스크립트에서 웹 UI 가정 제거 여부 재점검
