# 02-design

이 폴더는 PIXLLM의 목표 설계를 담습니다.

기준이 되는 운영 개념은 참고 소스의 `QueryEngine`, `tools`, `tasks`, `bridge`, `swarm/team`, `plugin/skill` 구조입니다. 따라서 이 폴더 문서는 기존 `intent + backend RAG` 설명보다 `session kernel + tool loop + task orchestration` 설계를 우선합니다.

권장 시작점:

- [desktop_layered_tool_loop_architecture.md](./desktop_layered_tool_loop_architecture.md)
- [에이전트_상세_설계.md](./에이전트_상세_설계.md)
- [API_인터페이스_설계.md](./API_인터페이스_설계.md)
- [데스크톱_UI_상세_설계.md](./데스크톱_UI_상세_설계.md)

모델 관련 문서는 유지합니다.

- [LLM서빙_상세_설계.md](./LLM서빙_상세_설계.md)
- [임베딩_상세_설계.md](./임베딩_상세_설계.md)

읽을 때의 원칙:

- 이 폴더의 다수 문서는 `현재 구현 설명`이 아니라 `목표 구조와 마이그레이션 기준`입니다.
- 코드와 문서가 다르면, 모델 관련 값은 현재 코드/설정을 따르고, 운영 개념은 이 문서 방향으로 맞춥니다.
- `intent_routing_minimal.md`는 더 이상 광범위한 intent taxonomy 문서가 아니라 최소 라우터 설계 문서입니다.
