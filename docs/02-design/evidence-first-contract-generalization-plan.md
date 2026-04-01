# Evidence-First Contract Generalization Plan

## 1. 배경

새 운영 모델에서는 질문 문구보다 `실제로 수집된 evidence`, `실행 표면`, `승인 요구`, `태스크 상태`가 더 중요합니다.

따라서 계약도 `flow 질문`, `설명 질문` 같은 텍스트 분류가 아니라 아래 구조를 중심으로 일반화해야 합니다.

- 이 턴이 어느 실행 표면에서 처리되는가
- 어떤 수준의 evidence가 필요한가
- 파일 변경과 검증이 필요한가
- 결과를 단순 답변으로 끝낼지 artifact까지 남길지

## 2. 목표

- 모든 턴을 공통 `session / turn / task / agent / artifact / approval` 모델로 표현합니다.
- 도구 루프, 태스크, 팀 실행, 브리지 실행이 같은 이벤트 계약을 공유하게 합니다.
- 최종 응답이 문자열 중심이 아니라 `answer + evidence + artifact + verification` 중심이 되게 합니다.

## 3. 표준 실행 계약

각 턴은 아래 계약 필드를 가집니다.

| 필드 | 예시 값 |
|---|---|
| `kind` | `direct_answer`, `tool_loop`, `task_execution`, `team_execution`, `remote_execution` |
| `evidence_policy` | `none`, `minimal`, `grounded`, `verified` |
| `mutation_policy` | `read_only`, `workspace_edit`, `remote_edit` |
| `verification_policy` | `none`, `light`, `standard`, `strict` |
| `result_shape` | `reply_only`, `reply_with_artifacts`, `reply_after_approval` |

## 4. Evidence Pack 표준화

evidence는 아래 묶음으로 정리합니다.

- `context_evidence`: cwd, selected files, recent history
- `tool_evidence`: read/search/shell/MCP 결과
- `task_evidence`: test report, build log, plan, review findings
- `bridge_evidence`: remote session state, reconnect log
- `model_evidence`: sources, citations, usage

## 5. 적용 순서

### Phase 1

- turn router가 `kind`를 선택
- event envelope를 표준화
- final response에 verification 필드 추가

### Phase 2

- task/artifact schema를 공통화
- tool 결과와 task 결과를 같은 evidence buffer에 적재
- approval payload를 공통 구조로 통일

### Phase 3

- team worker 결과를 동일 계약으로 통합
- bridge/remote 세션도 동일 이벤트 타입 사용
- UI가 계약 종류별로 일관된 패널을 렌더링

## 6. 비목표

- 자연어 의미를 완벽하게 분류하는 일
- 모든 결과를 무조건 장문의 reasoning으로 만드는 일
- 계약 종류를 세분화해서 다시 거대한 intent taxonomy를 만드는 일

## 7. 성공 기준

- 직접 답변과 태스크 실행이 같은 세션 모델 아래에서 보입니다.
- 파일 변경 요청은 항상 approval, artifact, verification을 동반합니다.
- 원격 실행과 병렬 실행도 같은 UI 패턴으로 관찰 가능합니다.
- 모델 문구가 바뀌어도 계약 해석이 흔들리지 않습니다.
