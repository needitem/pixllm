# 01-overview

이 폴더는 PIXLLM의 새 운영 모델을 설명합니다.

이제 PIXLLM은 기존의 `백엔드 중심 RAG 채팅` 개념이 아니라, 다음 축으로 이해해야 합니다.

- `desktop-first` 실행면
- `session / turn / task` 중심 런타임
- `tool-first` 근거 수집
- `bridge / remote worker` 확장
- `plugin / skill / command` 기반 기능 조합
- `team execution` 기반 병렬 작업

모델 축은 유지합니다.

- 모델 서빙: [../02-design/LLM서빙_상세_설계.md](../02-design/LLM서빙_상세_설계.md)
- 임베딩: [../02-design/임베딩_상세_설계.md](../02-design/임베딩_상세_설계.md)

문서:

- [시스템_상세_아키텍처_설계.md](./시스템_상세_아키텍처_설계.md)

권장 읽기 순서:

1. [시스템_상세_아키텍처_설계.md](./시스템_상세_아키텍처_설계.md)
2. [../02-design/desktop_layered_tool_loop_architecture.md](../02-design/desktop_layered_tool_loop_architecture.md)
3. [../02-design/에이전트_상세_설계.md](../02-design/에이전트_상세_설계.md)
4. [../02-design/API_인터페이스_설계.md](../02-design/API_인터페이스_설계.md)

주의:

- `01-overview`와 `02-design`은 현재 코드 설명보다 목표 운영 개념과 목표 설계를 우선합니다.
- 모델 관련 설정과 실제 서빙 값은 기존 백엔드 설정 파일을 그대로 기준으로 봅니다.
