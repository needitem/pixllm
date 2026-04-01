# Evidence-First Contract Generalization Plan

상태: 미래 계획 문서. 현재 제품 방향과 맞는 범위로 다시 정리한다.

## 1. 배경

현재 PIXLLM은 이미 부분적인 evidence-first 성격을 가진다.

- request context가 explicit path와 intent를 잡는다.
- tool policy가 grounded path와 read-before-edit를 강제한다.
- final answer guard가 trace에 없는 source mention을 재검사한다.
- backend evidence가 `company_reference_search`로 transcript에 편입된다.

다만 evidence vocabulary는 아직 `messages`, `localTrace`, `runSnapshot`, `taskRuntime`, `tool_result`에 나뉘어 있다.

## 2. 목표

- local turn, tool result, terminal capture, run snapshot을 더 일관된 evidence contract로 정리
- 최종 응답이 어떤 trace/run state를 근거로 하는지 더 명확히 연결
- renderer와 run inspector가 같은 evidence vocabulary를 쓰게 만들기

## 3. 현재 범위의 계약

현재 제품 방향에서 다룰 대상:

| 필드 | 예시 |
|---|---|
| `kind` | `direct_answer`, `tool_loop`, `local_task`, `run_snapshot` |
| `evidence_policy` | `none`, `grounded`, `verified` |
| `mutation_policy` | `read_only`, `workspace_edit`, `command_execution` |
| `result_shape` | `reply_only`, `reply_with_trace`, `reply_with_run_snapshot`, `reply_with_question` |

`team_execution`, `remote_execution`, MCP/open-world evidence는 현재 기본값으로 두지 않는다.

## 4. evidence pack 방향

- `context_evidence`: workspace, selected file, explicit path, session state
- `tool_evidence`: search, read, symbol, edit, shell, build 결과
- `trace_evidence`: `localTrace`, status events, terminal captures
- `run_evidence`: backend tasks, approvals, artifacts
- `model_evidence`: usage, finish reason, grounding 상태

## 5. 적용 순서

### Phase 1

- local turn event shape 정리
- run snapshot shape 정리
- final response에서 trace/run 근거 연결 강화

### Phase 2

- terminal capture와 tool result의 공통 표현 정리
- session 저장 형식과 renderer 표현 형식 정리
- approval / artifact 필드 정리

### Phase 3

- 필요하면 local task와 backend run을 더 직접적으로 연결
- 필요하면 verification summary를 별도 계약으로 승격

## 6. 비범위

- MCP/open-world evidence
- plugin/skill evidence plane
- bridge/remote session evidence
- team worker evidence 통합

현재 이 계획의 초점은 `확장 실행면 일반화`가 아니라 `single local runtime의 evidence vocabulary 정리`다.
