# 앱기반 멀티 에이전트 시스템 TODO

> 목적: 현재 PIXLLM을 `웹 RAG 채팅` 수준에서 `Codex / Claude Code` 류의 앱기반 멀티 에이전트 시스템 수준으로 끌어올리기 위해, 큰 줄기별 구현 TODO를 정리한다.
>
> 기준:
> - 주 실행면은 `앱 + 로컬 런타임`
> - 중앙 서버는 `LLM / 정책 / 지식 / 로그 / 동기화 API`
> - 웹은 사용하지 않는다.
> - 사용자 기능은 앱 내부 화면으로 제공한다.
> - 실제 코딩 작업은 `로컬 workspace` 기준

---

## 0. 현재 상태 요약

- [x] 중앙 API / 프런트 / 데이터 서비스와 vLLM이 분리되어 있다.
- [x] 현재 실행 중심은 `intent -> routing -> react_loop` 단일 에이전트 흐름이다.
- [x] `usage_guide`는 전용 수집/합성 흐름이 있으나, 나머지 intent는 공용 ReAct 비중이 높다.
- [x] 프런트는 채팅 중심 UX이고, workspace/admin 일부는 placeholder 상태다.
- [ ] 멀티 에이전트 시스템으로 보기 위한 `run/task/agent/artifact/approval` 모델은 아직 없다.
- [ ] 로컬 workspace에서 파일/터미널/svn/빌드 도구를 직접 다루는 `앱 런타임`은 아직 없다.

---

## 1. 시스템 아키텍처 큰 줄기

### 1.1 구성 형태 결정

- [ ] `순수 웹`이 아니라 `데스크톱 앱 + 로컬 에이전트 + 중앙 API` 구조로 확정한다.
- [ ] 사용자용 앱 화면만을 기준으로 전체 구조를 정리한다.
- [ ] 로컬에서만 가능한 기능과 서버에서만 가능한 기능을 경계로 나눈다.

### 1.2 시스템 계층 정리

- [ ] `로컬 실행 계층`: 파일 읽기, 검색, svn, 터미널, patch 적용, 테스트 실행, 빌드 도구 호출.
- [ ] `중앙 추론 계층`: intent 분류, 라우팅, LLM 추론, 중앙 정책.
- [ ] `지식 계층`: 문서 RAG, 코드 메타, workspace memory, prompt/policy store.
- [ ] `운영 계층`: 사용자/워크스페이스/권한/감사 로그/비용/모니터링.
- [ ] `표시 계층`: 사용자용 앱 UI.

### 1.3 모델 한계

- [ ] 현재 모델은 높은 수준의 장기 reasoning을 안정적으로 대체하지 못한다는 전제를 시스템 문서에 명시한다.
- [ ] 모델 단독 처리 금지 작업 목록을 만든다.
- [ ] 고난도 reasoning 작업은 `분해 -> 근거 수집 -> 검증 -> 인간 승인` 흐름으로만 처리한다.
- [ ] 증거 없는 확신형 응답보다 불확실성 보고를 우선하게 한다.
- [ ] 모델은 최종 의사결정자가 아니라 초안 작성자 / 분해 보조자로 위치시킨다.

#### 1.3.1 모델 단독으로 맡기지 않을 작업

- [ ] 대규모 아키텍처 방향 확정
- [ ] 난해한 성능 / 동시성 / 메모리 문제 최종 진단
- [ ] 파급 범위 큰 리팩터링 최종 승인
- [ ] DB / 데이터 마이그레이션 최종 실행
- [ ] 보안 예외 승인
- [ ] 규제 / 라이선스 / 계약 해석
- [ ] 프로덕션 장애의 근본 원인 단정

#### 1.3.2 인간 승인 필수 작업

- [ ] 프로덕션 배포
- [ ] 파괴적 파일 변경
- [ ] SVN commit / revert / 대량 수정
- [ ] 빌드 / 배포 / 인프라 설정 변경
- [ ] 전역 정책 / 프롬프트 / 모델 기본값 변경

---

## 2. 앱 / 로컬 런타임 TODO

### 2.1 로컬 workspace 연결

- [ ] 사용자가 현재 작업 중인 workspace를 앱에 연결할 수 있게 한다.
- [ ] workspace trust / allowlist / repo allowlist 정책을 만든다.
- [ ] 다중 repo / monorepo / submodule / symlink 케이스를 지원한다.
- [ ] 현재 열린 파일, 선택 영역, 최근 수정 파일, `svn status`, `svn diff`를 컨텍스트로 수집한다.
- [ ] 로컬 symbol index / file index / 최근 명령 로그를 유지한다.

### 2.2 로컬 도구 실행

- [ ] `read/search/glob` 외에 `svn status`, `svn diff`, `svn info`, `pytest`, `npm test`, `lint`를 앱 런타임에 붙인다.
- [ ] `msbuild`, `dotnet build`, `cmake --build`, `ninja`, 사용자 정의 빌드 스크립트 호출을 앱 런타임에 붙인다.
- [ ] 솔루션 / 프로젝트 / 타깃 / 구성별로 빌드 명령을 선택할 수 있게 한다.
- [ ] 위험 명령은 승인 없이 실행되지 않도록 approval gate를 둔다.
- [ ] 명령 실행 결과를 step artifact로 저장한다.
- [ ] 장시간 작업 취소 / 재시도 / resume를 지원한다.
- [ ] 실행 중인 task를 앱 종료 후 복구할 수 있게 한다.

### 2.3 앱 UX

- [ ] 채팅 UI가 아니라 `Run 중심 UI`로 재설계한다.
- [ ] 현재 어떤 agent가 무슨 step을 수행 중인지 timeline으로 보여준다.
- [ ] diff viewer, artifact viewer, terminal panel, approval inbox를 붙인다.
- [ ] build output panel과 빌드 실패 분석 뷰를 붙인다.
- [ ] 사용자가 특정 step부터 다시 실행할 수 있게 한다.
- [ ] 생성된 patch를 검토 후 적용/폐기할 수 있게 한다.

---

## 3. 멀티 에이전트 런타임 TODO

### 3.1 공통 모델

- [ ] `Conversation`과 `Run`을 분리한다.
- [ ] `Run -> Task -> Step -> Artifact -> Approval` 자료구조를 정의한다.
- [ ] agent별 `role`, `input contract`, `output contract`, `failure contract`를 정의한다.
- [ ] agent handoff payload 형식을 표준화한다.
- [ ] parallel step / sequential step / barrier step 개념을 넣는다.

### 3.2 에이전트 카탈로그

- [ ] `Planner Agent`를 둔다.
- [ ] `Retriever Agent`를 둔다.
- [ ] `Workspace Analyst Agent`를 둔다.
- [ ] `Executor Agent`를 둔다.
- [ ] `Reviewer Agent`를 둔다.
- [ ] `Security Agent`를 둔다.
- [ ] `Test Agent`를 둔다.
- [ ] `Migration Agent`를 둔다.
- [ ] `Presenter Agent`를 둔다.
- [ ] `Ops / Monitoring Agent`를 둘지 결정한다.

### 3.3 에이전트별 책임

- [ ] Planner는 요청을 task graph로 쪼갠다.
- [ ] Retriever는 문서/코드/예제를 수집하고 evidence bundle을 만든다.
- [ ] Workspace Analyst는 현재 repo 구조, 변경 파일, 관련 심볼을 요약한다.
- [ ] Executor는 실제 코드 수정/명령 실행/파일 생성 후보를 만든다.
- [ ] Reviewer는 회귀 위험, 품질, 누락 테스트를 잡는다.
- [ ] Security Agent는 비밀정보, 권한, 위험 명령, 데이터 유출 경로를 본다.
- [ ] Test Agent는 재현/검증/회귀 테스트를 설계하고 실행한다.
- [ ] Migration Agent는 버전 차이와 단계별 전환안을 만든다.
- [ ] Presenter는 최종 사용자 응답과 보고서를 정리한다.

---

## 4. Intent별 전용 작업 TODO

### 4.1 General

- [ ] 비용 낮은 가벼운 응답 lane을 만든다.
- [ ] clarification-first 정책을 넣는다.

### 4.2 Doc Lookup

- [ ] 문서 전용 retriever와 citation renderer를 붙인다.
- [ ] page/section/version 기준 근거 표시를 강화한다.

### 4.3 API Lookup

- [ ] 시그니처/파라미터/반환값/버전 차이를 구조화한다.
- [ ] minimal example과 compatibility note를 분리한다.

### 4.4 Usage Guide

- [ ] example cluster 선택 로직을 더 강화한다.
- [ ] setup -> initialization -> load -> render -> cleanup 흐름을 고정 포맷으로 만든다.
- [ ] grounded snippet contamination 방지기를 넣는다.

### 4.5 Code Explain

- [ ] 정의 위치, 호출 경로, 영향 범위를 함께 보여준다.
- [ ] related symbol graph를 시각화한다.

### 4.6 Code Generate

- [ ] 생성 전 preflight 단계에서 target file / style / test expectation을 수집한다.
- [ ] patch preview와 apply approval을 분리한다.

### 4.7 Bug Fix / Troubleshooting

- [ ] 재현 정보 수집 단계가 필요하다.
- [ ] 로그, 최근 diff, failing test, suspect file을 우선 수집한다.
- [ ] fix proposal과 verification plan을 별도 artifact로 만든다.

### 4.8 Code Review

- [ ] finding schema를 severity, confidence, file anchor 중심으로 고정한다.
- [ ] 요약보다 findings-first UX를 만든다.

### 4.9 Refactor / Compare / Migration / Design Review

- [ ] plan-first 흐름을 강제한다.
- [ ] 변경 영향 범위와 rollback 가능성을 필수로 표시한다.
- [ ] architecture / migration / compare는 planner + reviewer 병렬 구조로 바꾼다.

---

## 5. RAG 고도화 TODO

### 5.1 인제스트

- [ ] 문서 타입별 파서 전략을 분리한다.
- [ ] 안정 코퍼스(엔진 소스 / 공식 예제)는 symbol / file / example index를 우선 구축하고, 임베딩 병행 여부를 검토한다.
- [ ] 로컬 workspace 코드는 기본적으로 비임베딩으로 두고, tool search + 경량 구조 인덱스를 우선한다.
- [ ] AST / reference graph / call graph는 대표 사용 흐름 추적에 실제로 필요한 범위부터 단계적으로 추가를 검토한다.
- [ ] import 시 project/module/version/owner/ACL 메타를 강제한다.
- [ ] example file, reference file, generated file을 구분한다.
- [ ] 문서는 임베딩을 유지하고, 코드는 안정 코퍼스와 로컬 workspace를 분리해 ingest / retrieval 전략을 적용한다.

### 5.2 검색

- [ ] 안정 코퍼스는 dense + lexical + reranker + symbol search + example/path prior를 조합한 multi-signal retrieval로 확장한다.
- [ ] 로컬 workspace는 lexical + symbol + path + diff/recency prior를 기본으로 두고 필요 시 안정 코퍼스와 hybrid 결합한다.
- [ ] query decomposition / ambiguity resolution / fallback rewrite를 intent별, 코퍼스별로 넣는다.
- [ ] 실패한 retrieval 패턴을 intent별로 따로 튜닝한다.

### 5.3 컨텍스트 빌딩

- [ ] `정의`, `사용`, `예제`, `설정`, `주의사항`, `테스트`, `변경이력`, `공식 기준`, `로컬 상태` 슬롯 기반으로 context packer를 만든다.
- [ ] 안정 코퍼스 pack과 로컬 workspace pack을 따로 만든 뒤 merge하는 구조를 만든다.
- [ ] answer 유형별 컨텍스트 템플릿을 분리한다.
- [ ] 로컬 workspace 컨텍스트와 중앙 RAG 컨텍스트를 합치는 규칙을 만든다.

### 5.4 근거 정합성

- [ ] unsupported claim detector를 넣는다.
- [ ] 코드 블록 provenance check를 넣는다.
- [ ] citation span alignment를 넣는다.
- [ ] source contamination / assembly noise / unrelated example noise를 잡는 정제기를 넣는다.

### 5.5 피드백 루프

- [ ] 사용자 피드백을 retrieval rank/prompt/policy 개선에 반영한다.
- [ ] intent별 golden set을 운영한다.
- [ ] regression benchmark를 정기 실행한다.

---

## 6. 프런트 / 웹 콘솔 TODO

### 6.1 앱 UI

- [ ] agent timeline 뷰를 만든다.
- [ ] run list / run detail / artifact diff / source trace 패널을 만든다.
- [ ] patch apply UX를 만든다.
- [ ] workspace selector / repo binding UI를 만든다.

### 6.2 웹 콘솔

- [ ] knowledge 관리 UI를 실제 API와 연결한다.
- [ ] prompt 관리 UI를 실제 API와 연결한다.
- [ ] functions / tools 관리 UI를 만든다.
- [ ] 사용자 / 역할 / 워크스페이스 관리 UI를 만든다.
- [ ] 실행 로그 / 비용 / 성능 대시보드를 만든다.

### 6.3 품질

- [ ] 인코딩 깨짐, i18n, typography, accessibility를 정리한다.
- [ ] 긴 응답 / 긴 source list / large diff 성능을 개선한다.

---

## 7. 보안 / 정책 TODO

- [ ] `API_SESSION_TOKEN` 수준에서 `org/workspace/user/role` 모델로 확장한다.
- [ ] 문서 ACL / 코드 ACL / tool ACL을 실제로 적용한다.
- [ ] approval-required tool 목록을 만든다.
- [ ] secret redaction을 로컬 런타임에서 먼저 수행한다.
- [ ] 감사 로그를 남긴다.
- [ ] 데이터 유출 방지 정책을 만든다.

---

## 8. 유지보수 / 운영 TODO

- [ ] pipeline job을 in-memory thread에서 durable queue 기반으로 바꾼다.
- [ ] 설정을 workspace/profile/role 단위로 override 가능하게 한다.
- [ ] 프롬프트 / 정책 / tool schema를 버전 관리한다.
- [ ] 장애 시 run resume와 stale recovery를 강화한다.
- [ ] agent별 SLI/SLO와 alert를 만든다.
- [ ] canary rollout / rollback 전략을 만든다.

---

## 9. 평가 / 릴리즈 TODO

- [ ] intent별 benchmark 세트를 만든다.
- [ ] retrieval precision / citation correctness / patch quality / review quality를 측정한다.
- [ ] app/웹/로컬 런타임 통합 E2E를 만든다.
- [ ] 실제 사용자 피드백을 release gate에 반영한다.
- [ ] 최종 acceptance checklist를 만든다.

---

## 10. 최종 목표

- [ ] 사용자가 로컬 workspace를 연결한다.
- [ ] 앱이 현재 코드/파일/`svn status`/`svn diff` 상태를 읽는다.
- [ ] Planner가 작업을 여러 agent task로 분해한다.
- [ ] Retriever/Workspace Analyst가 근거를 모은다.
- [ ] Executor가 수정안/실행안을 만든다.
- [ ] Reviewer/Security/Test Agent가 검증한다.
- [ ] 사용자는 diff와 artifact를 보고 승인한다.
- [ ] Presenter가 최종 응답과 보고서를 정리한다.
- [ ] 웹 콘솔은 관리/모니터링/자산 운영을 담당한다.
