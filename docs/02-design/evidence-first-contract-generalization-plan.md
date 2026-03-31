# Evidence-First Contract Generalization Plan

## 1. 배경

현재 로컬 오버레이와 서버 라우팅은 `flow`, `설명`, `변경`, `diff` 같은 질문 텍스트 힌트에 크게 의존한다.
이 구조는 특정 질문군에는 잘 맞지만, 다음 문제가 반복된다.

- 질문 표현이 조금만 바뀌어도 계약 분류가 흔들린다.
- 같은 코드베이스라도 `flow` 질문에만 retrieval/renderer가 강하게 최적화된다.
- `review`, `change`, `failure analysis` 같은 다른 작업군은 같은 수준의 근거 수집과 답변 구조를 받지 못한다.
- 클라이언트가 워크스페이스 diff/status를 질문 키워드에 따라 선택적으로 보내므로, review/change 질의에 필요한 증거가 일관되게 전달되지 않는다.

이번 작업의 목표는 질문 키워드 기반 분기를 없애고, `명시적 요청 metadata + 실제 수집된 구조적 증거`를 기반으로 계약을 정하는 것이다.

## 2. 목표

### 2.1 1차 목표

- 질문 계약을 키워드/힌트 regex가 아니라 구조 기반 신호로 추론한다.
- 로컬 오버레이 payload가 질문 종류와 무관하게 안정적으로 diff/status/graph/read evidence를 전달한다.
- 로컬 anchor/primary symbol 선택이 broad term, flow term, handler name blacklist에 덜 의존하도록 바꾼다.
- 최소한 다음 계약군을 구조적으로 구분할 수 있게 만든다.
  - `code_flow_explanation`
  - `code_read`
  - `code_review`
  - `code_change`
  - `doc_reference`
  - `general`
- 기존 flow 품질을 유지하면서 다른 계약군도 동일한 evidence-first 경로를 타게 만든다.

### 2.2 2차 목표

- 이후 `failure_analysis`, `code_compare`, `state_change_analysis`를 같은 프레임에 올릴 수 있게 확장 지점을 남긴다.
- renderer/executor가 계약 기반으로 갈라질 수 있도록 contract schema를 일반화한다.

## 3. 비목표

- 이번 변경에서 모든 질문을 완전한 의미 이해로 분류하지는 않는다.
- 이번 변경에서 review/change의 최종 answer renderer를 flow renderer 수준으로 완성하지는 않는다.
- 이번 변경에서 멀티턴 planning agent를 추가하지는 않는다.

## 4. 현재 편향 지점

### 4.1 클라이언트

`desktop/src/renderer/App.svelte`

- 질문 텍스트 regex로 `workspace_status`, `workspace_diff` 첨부 여부를 결정한다.
- 결과적으로 review/change에 필요한 증거가 질문 문구에 따라 빠질 수 있다.

### 4.2 로컬 오버레이 러너

`desktop/src/main/local_agent_runner.cjs`

- `FLOW_QUESTION_RE`, `FLOW_META_TERMS`, `BROAD_ANCHOR_TERMS` 기반 질문 해석
- `outlineEntrySignalScore`, `outlineHandlerPenalty` 같은 이름 기반 편향
- broad flow 질문일 때 focus line을 무시하고 top-level orchestration만 밀어주는 특수 규칙
- same-file caller promotion에도 flow-specific guard가 걸려 있다.

### 4.3 서버 계약 분류

`backend/app/services/chat/question_contract.py`

- flow/doc/read를 정규식 기반 텍스트 힌트로 구분한다.
- local overlay의 `trace`, `workspace_graph`, `workspace_diff` 같은 실제 구조적 증거를 분류에 거의 쓰지 않는다.

`backend/app/services/chat/intent.py`

- coarse bucket도 주로 `task_type`, `tool_scope`, code-like token pattern에 의존한다.
- question contract는 상세해졌지만 분류 입력이 빈약하다.

## 5. 설계 원칙

### 5.1 질문보다 증거를 우선한다

질문 텍스트는 “사용자가 어떤 파일/심볼을 직접 언급했는가” 정도의 구조 신호만 사용한다.
계약 결정은 가능하면 아래 순서로 한다.

1. 명시적 request metadata
2. local overlay 구조 프로필
3. 코드 문맥 구조 프로필
4. 그래도 모호하면 보수적인 기본 계약

### 5.2 계약과 renderer/executor를 분리한다

- `response_type`는 coarse lane 선택용으로 유지한다.
- `question_contract.kind`가 실제 retrieval 정책과 renderer/executor 정책의 기준이 된다.

### 5.3 모든 질문에 같은 bootstrap을 준다

- 로컬 오버레이가 있으면 status/diff/trace/graph를 항상 첨부한다.
- 서버는 이를 요약해서 `overlay_structural_profile`로 만든다.

## 6. 목표 아키텍처

## 6.1 입력 계층

### Request metadata

- `task_type`
- `tool_scope`
- `approval_mode`
- `workspace_overlay_present`

### Overlay structural profile

클라이언트 첨부에서 서버가 계산한다.

- `direct_read_count`
- `executable_read_count`
- `workspace_graph_chain_count`
- `workspace_graph_frontier_count`
- `trace_relation_count`
- `selected_file_present`
- `workspace_status_present`
- `workspace_diff_present`
- `changed_path_count`
- `target_symbol_present`

### Message structure profile

텍스트 의미 키워드가 아니라 구조만 본다.

- `path_reference_count`
- `member_access_count`
- `call_like_count`
- `explicit_identifier_count`
- `code_fence_count`
- `symbol_candidates`
- `has_explicit_code_target`

## 6.2 계약 결정 규칙

### 명시적 metadata 우선

- `task_type/docs` 또는 docs-only `tool_scope` -> `doc_reference`
- write/build/execute 계열 `task_type`/`tool_scope` -> `code_change`
- review 계열 `task_type` -> `code_review`
- troubleshooting 계열 `task_type` -> `failure_analysis`

### overlay 구조 기반 자동 추론

- call chain / direct executable reads / graph frontier가 존재하면 `code_flow_explanation`
- flow 구조는 약하고 workspace diff 중심이면 `code_review`
- explicit code target 또는 grounded local reads가 있으면 `code_read`
- 둘 다 없으면 `general`

### 보수적 fallback

- 모르면 `code_read` 또는 `general`로 두고, retrieval은 넓게 시작한다.
- 특정 질문 문구만으로 `flow`나 `review`를 확정하지 않는다.

## 6.3 로컬 anchor 선택 규칙

질문 키워드 편향을 제거하고 아래 점수를 쓴다.

- 실행 가능성
  - method/function 여부
  - 호출/제어/대입 밀도
  - declaration-only 여부
- 위치 신호
  - 선택 파일과의 거리
  - focus line proximity
  - 동일 모듈/디렉터리 근접도
- 명시적 코드 타깃 정합성
  - 질문에서 직접 추출한 식별자와 symbol/path 정합
- 이미 읽힌 evidence 정합성
  - read_symbol_span 존재 여부
  - outline/read window 일치 여부

의도적으로 제외할 규칙:

- `flow`, `경로`, `호출` 같은 단어를 본 가산점
- `image`, `video`, `data`, `result` 같은 broad term blacklist
- `Select`, `Load`, `Handle` 같은 이름 prefix 가산점
- `Click`, `Render`, `Loaded` 같은 handler 이름 감점

## 6.4 계약별 품질 기준

### code_flow_explanation

- entry/caller
- focal processing
- downstream/open frontier

### code_read

- focal symbol/file
- grounded reads
- supporting references

### code_review

- changed surface
- grounded diff/status
- touched code reads
- findings-ready evidence

### code_change

- edit surface
- directly read target files
- verification target

## 7. 구현 범위

### 7.1 클라이언트

`desktop/src/renderer/App.svelte`

- workspace overlay에 status/diff를 질문과 무관하게 첨부
- changed path list를 metadata로 추가

### 7.2 로컬 오버레이 러너

`desktop/src/main/local_agent_runner.cjs`

- flow 질문 정규식 제거
- broad/meta term 편향 제거
- anchor/root selection을 구조 점수 기반으로 변경
- same-file caller promotion에서 flow 질문 의존 제거

### 7.3 서버 계약 분류

`backend/app/services/chat/question_contract.py`

- 텍스트 힌트 regex 제거
- overlay/message structural profile 도입
- `code_review`, `failure_analysis` 계약 도입

`backend/app/services/chat/intent.py`

- contract builder에 local overlay metadata 전달
- routing bucket과 answer style을 계약 중심으로 보정

`backend/app/services/chat/preparation.py`

- verify/prepare 단계에서 overlay metadata를 classifier로 전달

`backend/app/services/chat/runtime_profile.py`

- 새 contract kind를 code lane으로 포함

## 8. 테스트 전략

### 8.1 서버 단위 테스트

`backend/tests/test_codex_style_routing.py`

- flow keyword 없이도 overlay graph가 있으면 `code_flow_explanation`
- explicit review task_type이면 `code_review`
- explicit change task_type이면 `code_change`
- code-like identifier 질문은 `code_read`
- overlay diff만 있고 flow graph가 없으면 `code_review`
- fallback은 `general` 또는 `code_read`

### 8.2 로컬 러너 테스트

`desktop/src/main/local_agent_runner.test.cjs`

- broad flow term이 없어도 executable orchestrator가 우선 anchor가 되는지
- handler blacklist 없이도 구조적으로 top-level executable span이 선택되는지
- same-file caller promotion이 구조 점수 기준으로만 동작하는지
- unrelated external definition 추적 억제는 유지되는지

### 8.3 수동 확인

- `영상 정합 흐름 정리해줘`
- 명시적 코드 심볼 read 질문
- review task metadata가 붙은 요청
- change/write task metadata가 붙은 요청

## 9. 검증 명령

### 로컬 러너

```powershell
node --test desktop/src/main/local_agent_runner.test.cjs
```

### 서버 라우팅

```powershell
python -m pytest backend/tests/test_codex_style_routing.py -q
```

## 10. 롤아웃 체크리스트

- [ ] 계획 문서 작성
- [ ] App overlay payload 일반화
- [ ] question_contract 구조 프로필 도입
- [ ] intent/preparation wiring 반영
- [ ] local_agent_runner 편향 제거
- [ ] 테스트 보강
- [ ] 대상 스위트 실행
- [ ] 수동 샘플 질의 확인

## 11. 완료 기준

- flow/read/review/change 계약이 질문 키워드 regex 없이 결정된다.
- 로컬 오버레이는 질문 문구와 무관하게 diff/status를 항상 제공한다.
- 로컬 anchor 선택이 이름 prefix/handler blacklist 없이도 기존 flow 품질을 유지한다.
- 대상 테스트가 모두 통과한다.
