# PIXLLM Docs

PIXLLM 문서는 두 축으로 나뉩니다.

- `01-overview`: 새 운영 모델의 큰 구조
- `02-design`: 세부 설계와 구현 방향
- `03-test`: 검증 기록
- `05-reference`: 비교 자료와 모델 참고 문서

이제 `01`, `02` 문서는 기존 `백엔드 중심 RAG 채팅` 개념이 아니라, Claude Code 계열 소스 구조를 참고한 `세션 커널 + 도구 루프 + 태스크/브리지 + 플러그인/스킬 + 팀 실행` 개념을 기준으로 읽어야 합니다.

모델 축은 기존 방침을 유지합니다.

- [02-design/LLM서빙_상세_설계.md](./02-design/LLM서빙_상세_설계.md)
- [02-design/임베딩_상세_설계.md](./02-design/임베딩_상세_설계.md)

추천 시작 순서:

1. [01-overview/시스템_상세_아키텍처_설계.md](./01-overview/시스템_상세_아키텍처_설계.md)
2. [02-design/desktop_layered_tool_loop_architecture.md](./02-design/desktop_layered_tool_loop_architecture.md)
3. [02-design/에이전트_상세_설계.md](./02-design/에이전트_상세_설계.md)
4. [02-design/API_인터페이스_설계.md](./02-design/API_인터페이스_설계.md)

참고:

- `01`, `02` 문서는 현재 구현 설명보다 목표 운영 개념과 목표 설계를 우선한다.
- 실제 모델/서빙 설정은 여전히 `backend/app/config.py`, `backend/.profiles/rag_config.yaml`, `backend/docker-compose.yml`을 기준으로 본다.
