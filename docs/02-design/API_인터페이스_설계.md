# API 인터페이스 설계

기준일: 2026-04-06

이 문서는 현재 구현된 desktop IPC, local agent stream, backend HTTP surface를 정리한다.

## 1. 인터페이스 층

현재 PIXLLM의 실행 인터페이스는 세 층이다.

| 구간 | 현재 방식 | 역할 |
|---|---|---|
| renderer -> preload | Electron context bridge | UI에서 안전한 desktop surface 호출 |
| preload -> main | IPC invoke / event | 세션, workspace, local agent stream 제어 |
| main -> backend | HTTP | health, runs, approvals, evidence, LLM/proxy endpoint |

## 2. preload surface

`window.pixllmDesktop`가 현재 renderer가 쓰는 주 surface다.

핵심 메서드:

- settings: `loadSettings`, `saveSettings`
- sessions: `listSessions`, `getSession`, `createSession`, `saveSession`
- local agent: `agentChatStreamStart`, `agentChatStreamCancel`, `answerAgentQuestion`
- backend runs: `apiHealth`, `apiRuns`, `apiRun`, `apiCancelRun`, `apiResumeRun`, `apiApproveRun`, `apiRejectRun`
- workspace: `chooseWorkspace`, `listWorkspaceFiles`, `readWorkspaceFile`, `writeWorkspaceFile`, `grepWorkspace`, `runBuild`, `svnInfo`, `svnStatus`, `svnDiff`

## 3. local agent stream events

renderer는 `agent:stream-event`를 구독한다.

현재 event 종류:

- `request_start`
- `session_restored`
- `status`
- `model`
- `assistant_message`
- `tool_use`
- `tool_result`
- `transition`
- `tool_batch_start`
- `tool_batch_end`
- `terminal`
- `user_question`
- `brief`
- `token`
- `done`
- `cancelled`
- `error`

공통 envelope:

```json
{
  "requestId": "uuid",
  "event": "tool_result",
  "payload": {}
}
```

중요:

- `transition`에는 compaction, continuation, grounding retry, next-speaker continuation 같은 내부 제어 흐름이 기록된다.
- Qwen textual protocol 자체는 `assistant_message`, `tool_use`, `tool_result` 이벤트로 재구성되어 renderer에 전달된다.

## 4. done payload

`done` event는 아래 필드를 반환한다.

- `answer`
- `local_trace`
- `local_transcript`
- `local_summary`
- `local_overlay`
- `primary_file_path`
- `primary_file_content`

`local_overlay`는 desktop local runtime 메타데이터다.

- `engine`
- `session_id`
- `usage`
- `primary_file_path`
- `runtime`

## 5. backend HTTP surface

desktop이 직접 호출하는 backend API:

- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs/{run_id}/cancel`
- `POST /api/v1/runs/{run_id}/resume`
- `GET /api/v1/runs/{run_id}/approvals`
- `POST /api/v1/runs/{run_id}/approvals/{approval_id}/approve`
- `POST /api/v1/runs/{run_id}/approvals/{approval_id}/reject`
- `POST /api/v1/tool-api/orchestrate/lookup_sources_and_code`

현재 `/api/v1/tool-api/orchestrate/lookup_sources_and_code`는 `company_reference_search`가 사용한다. 이 호출은 회사 엔진 소스나 내부 문서를 read-only evidence로 수집하는 용도다.

## 6. LLM 인터페이스

desktop local agent는 두 종류의 transport surface를 쓸 수 있다.

- OpenAI-compatible direct call: `POST /v1/chat/completions`
- proxy mode: `POST /v1/llm/chat_completions`

streaming도 같은 축을 따른다.

- OpenAI-compatible SSE
- proxy stream `/v1/llm/chat_completions/stream`

하지만 현재 application-level contract는 transport와 다르다.

- transport는 OpenAI-compatible일 수 있다.
- transcript와 tool protocol은 Qwen textual contract가 기준이다.
  - assistant -> `<tool_call>...</tool_call>`
  - user/tool result -> `<tool_response>...</tool_response>`

native `tool_calls`는 tolerated fallback이지 기본 flattening 경로가 아니다.

## 7. compaction과 user query 보존

Qwen server는 flattened messages 안에 user query가 사라지면 `400 No user query found in messages`를 반환할 수 있다.

현재 desktop runtime은:

- message compaction 시 첫 substantive user message를 보존하고
- flattened payload에 user query가 없으면 fallback `User request:` 메시지를 다시 주입한다.

이 보정은 현재 LLM 인터페이스 설계의 중요한 일부다.

## 8. streaming tool execution 상태

현재 상태는 다음과 같다.

- 스트리밍 중 parse 가능한 tool call은 선실행을 시작할 수 있다.
- turn 종료 시 `ToolRuntime`이 prefetched result를 claim해서 재사용한다.
- cancel 또는 model error 시 unclaimed tool call은 drain하거나 synthetic result로 transcript를 복구한다.
- 같은 스트림 안에서 `tool_result`를 모델에 즉시 재주입하지는 않는다.

## 9. 현재 범위 밖 인터페이스

현재 코드 기준으로 기본 경로가 아닌 것:

- `/api/v2/sessions/*`
- remote bridge control API
- team worker orchestration API
- MCP transport
- plugin/skill host transport

현재 PIXLLM의 인터페이스는 `Electron IPC + local agent stream + backend /api/v1/runs + backend evidence + Qwen-compatible LLM endpoint`로 이해하는 게 맞다.
