# Evidence-First Contract Generalization Plan

> 상태: 미래 계획 문서이지만, 현재 코드와 현재 제품 방향에 맞게 범위를 다시 줄였습니다.

## 1. 배경

현재 PIXLLM은 이미 일부 evidence-first 성격을 갖고 있습니다.

- request context가 explicit path와 intent를 뽑습니다
- tool policy가 grounded path와 read-before-edit를 봅니다
- final answer guard가 trace에 없는 파일 언급을 막습니다

다만 결과 계약은 아직 `세션 메시지`, `localTrace`, `runSnapshot`, `task runtime`에 나뉘어 있습니다.

## 2. 목표

현재 방향의 목표는 아래입니다.

- 로컬 turn, tool result, terminal capture, run snapshot을 더 일관된 evidence 계약으로 정리
- 최종 응답이 단순 문자열만이 아니라 trace와 run 상태를 함께 가리키게 만들기
- renderer와 backend run inspector가 같은 evidence vocabulary를 쓰게 만들기

## 3. 현재 범위의 표준 계약

현재 제품 방향에서 표준화할 대상은 아래입니다.

| 필드 | 예시 값 |
|---|---|
| `kind` | `direct_answer`, `tool_loop`, `local_task`, `run_snapshot` |
| `evidence_policy` | `none`, `grounded`, `verified` |
| `mutation_policy` | `read_only`, `workspace_edit`, `command_execution` |
| `result_shape` | `reply_only`, `reply_with_trace`, `reply_with_run_snapshot`, `reply_with_question` |

현재 기준으로는 이 정도가 맞고, `team_execution`, `remote_execution` 같은 계약을 기본값으로 두는 것은 과합니다.

## 4. Evidence Pack 정리 방향

현재 정리해야 할 evidence 묶음은 아래입니다.

- `context_evidence`: workspace, selected file, explicit path, recent session state
- `tool_evidence`: search, read, symbol, edit, shell, build 결과
- `trace_evidence`: `localTrace`, status events, terminal captures
- `run_evidence`: backend tasks, approvals, artifacts
- `model_evidence`: usage, finish reason, grounding된 answer

MCP/open-world evidence는 현재 범위 밖입니다.

## 5. 적용 순서

### Phase 1

- local turn event shape 정리
- run snapshot shape 정리
- final response에서 trace/run 근거 연결 강화

### Phase 2

- terminal capture와 tool result의 공통 표현 정리
- session 저장 포맷과 renderer 표시 포맷 정리
- approval / artifact 표준 필드 정리

### Phase 3

- 필요하면 local task와 backend run을 더 직접적으로 연결
- 필요하면 verification summary를 별도 계약으로 승격

## 6. 비범위

현재 계획에서 제외하는 것:

- MCP/open-world evidence
- plugin/skill evidence plane
- bridge/remote session evidence
- team worker evidence 통합

## 7. 성공 기준

- 현재 세션의 답변이 어떤 trace와 run 정보 위에 서 있는지 UI에서 추적 가능하다
- tool result, terminal output, run artifact가 서로 다른 이름으로 중복 표현되지 않는다
- 현재 없는 team/remote/MCP 개념이 계약 표준의 필수가 아니다

이 계획의 초점은 `확장 실행면 generalization`이 아니라 `현재 single local runtime의 evidence vocabulary 정리`입니다.
