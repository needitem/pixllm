# PIXLLM 전체 구현 체크리스트

> 현재 기준: 웹 프런트엔드 제거, 데스크톱 UI 기준

## 백엔드 / 데이터

- [x] FastAPI API 운영
- [x] Qdrant / Redis / MinIO 연결
- [x] vLLM 연동
- [x] import / run / pipeline 기본 경로 유지

## UI

- [x] `desktop/`를 유일한 UI로 유지
- [x] 웹 `frontend/` 제거
- [x] 데스크톱에서 chat / run / workspace 기본 흐름 제공

## 남은 구조 정리

- [ ] `backend/app/routers/imports.py` 레거시 분기 축소
- [ ] `backend/app/services/execution/runs.py` record 생성 중복 축소
- [ ] 문서 전체에서 역사적 `frontend` 언급이 남았는지 추가 점검
