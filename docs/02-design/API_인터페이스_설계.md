# API 인터페이스 설계

기준일: 2026-04-01

이 문서는 현재 코드에 구현된 인터페이스를 기준으로 설명합니다. 과거 문서에 있던 `/api/v2/sessions` 같은 control-plane API는 현재 desktop local agent 경로의 구현 기준이 아닙니다.

## 1. 현재 인터페이스 층

현재 PIXLLM의 주요 인터페이스는 세 층입니다.

| 구간 | 현재 방식 | 역할 |
|---|---|---|
| Renderer -> preload | Electron context bridge | 데스크톱 메서드 노출 |
| preload -> Electron main | IPC invoke / event | 세션, 워크스페이스, 로컬 에이전트 스트림 |
| Electron main -> backend | HTTP | health, runs, approvals, LLM endpoint |

## 2. 현재 preload surface

`window.pixllmDesktop`가 현재 데스크톱 인터페이스입니다.

주요 메서드:

- settings: `loadSettings`, `saveSettings`
- sessions: `listSessions`, `getSession`, `createSession`, `saveSession`
- local agent: `agentChatStreamStart`, `agentChatStreamCancel`, `answerAgentQuestion`
- backend runs: `apiHealth`, `apiRuns`, `apiRun`, `apiCancelRun`, `apiResumeRun`, `apiApproveRun`, `apiRejectRun`
- workspace: `chooseWorkspace`, `svnInfo`, `svnStatus`, `svnDiff`, `listWorkspaceFiles`, `readWorkspaceFile`, `writeWorkspaceFile`, `grepWorkspace`, `runBuild`

## 3. 현재 로컬 에이전트 스트림 이벤트

renderer는 `onAgentStreamEvent`로 `agent:stream-event`를 구독합니다.

현재 방출되는 이벤트 타입:

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

## 4. `done` payload

현재 로컬 에이전트 완료 이벤트는 아래 필드를 포함합니다.

- `answer`
- `local_trace`
- `local_transcript`
- `local_summary`
- `local_overlay`
- `primary_file_path`
- `primary_file_content`

`local_overlay`에는 현재 데스크톱 로컬 런타임 메타데이터가 들어갑니다.

- `engine`
- `session_id`
- `usage`
- `primary_file_path`
- `runtime`

## 5. 현재 backend HTTP API

데스크톱이 실제로 호출하는 backend API:

- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs/{run_id}/cancel`
- `POST /api/v1/runs/{run_id}/resume`
- `GET /api/v1/runs/{run_id}/approvals`
- `POST /api/v1/runs/{run_id}/approvals/{approval_id}/approve`
- `POST /api/v1/runs/{run_id}/approvals/{approval_id}/reject`

현재 `/api/v1/tool-api`는 존재하지만, desktop local agent의 기본 tool loop는 이를 직접 사용하지 않습니다.

## 6. 현재 LLM 인터페이스

로컬 에이전트는 두 종류의 LLM endpoint를 지원합니다.

- OpenAI 호환: `POST /v1/chat/completions`
- proxy 모드: `POST /v1/llm/chat_completions`

streaming 호출도 같은 두 축을 사용합니다.

- OpenAI 호환 stream
- proxy stream `/v1/llm/chat_completions/stream`

현재 구현에서는 streaming 중 tool call을 즉시 실행하지 않고, 스트림이 끝난 뒤 수집된 `tool_calls`를 실행합니다.

## 7. 현재 구현되지 않은 인터페이스

현재 코드 기준으로 아직 구현되지 않았거나 로컬 채팅 루프의 표준 인터페이스가 아닌 것:

- `/api/v2/sessions/*`
- bridge / remote environment control API
- team worker orchestration API
- CLI/SDK host용 stdio runtime
- MCP tool/resource transport

따라서 현재 PIXLLM의 핵심 인터페이스는 `Electron IPC + local agent stream + backend /api/v1/runs + LLM endpoint`로 이해하는 것이 맞습니다.
