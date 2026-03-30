# 01-overview

현재 구현된 PIXLLM의 큰 구조와 운영 토폴로지를 정리한 문서 모음입니다.

## 문서

- [시스템_상세_아키텍처_설계.md](./시스템_상세_아키텍처_설계.md)

## 읽기 가이드

- 현재 구현 상태를 가장 빠르게 확인하려면 [PIXLLM_전체_구현_체크리스트.md](../PIXLLM_전체_구현_체크리스트.md)를 먼저 봅니다.
- 실제 설정값은 `backend/app/config.py`, `backend/.profiles/rag_config.yaml`, `backend/docker-compose.yml`를 우선 기준으로 봅니다.
- 이 폴더 문서는 구현 코드의 세부 함수 설명보다 "현재 시스템이 어떤 구조로 돌아가는가"에 집중합니다.
