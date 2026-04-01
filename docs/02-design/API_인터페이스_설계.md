# API 인터페이스 설계

> 목적: PIXLLM의 인터페이스를 `REST 질의 몇 개`가 아니라 `session / turn / task / approval / bridge / model` 계약으로 재정의

## 1. 인터페이스 원칙

- 사용자 인터페이스의 기본 단위는 `chat request`가 아니라 `session`과 `turn`입니다.
- 실행 결과는 단일 문자열이 아니라 `event stream + artifact`로 반환합니다.
- 장시간 실행은 `task`로 분리하고, 위험 작업은 `approval` 계약을 반드시 거칩니다.
- 모델 계약은 기존 `vLLM` OpenAI 호환 API를 그대로 유지합니다.

## 2. 공통 식별자

모든 계층에서 아래 식별자를 공유합니다.

| 필드 | 의미 |
|---|---|
| `session_id` | 사용자 작업 세션 |
| `turn_id` | 세션 안의 단일 요청 |
| `task_id` | 장시간 실행 단위 |
| `agent_id` | 실행 주체 |
| `artifact_id` | 로그, diff, 계획, 테스트 결과 등 산출물 |
| `approval_id` | 승인 요청 |
| `tool_call_id` | 개별 도구 호출 |

## 3. 표준 이벤트 Envelope

모든 스트리밍 응답은 아래 형식을 기본으로 합니다.

```json
{
  "type": "assistant_delta",
  "session_id": "sess_123",
  "turn_id": "turn_456",
  "agent_id": "primary",
  "timestamp": "2026-04-01T09:00:00Z",
  "payload": {}
}
```

대표 `type`:

- `assistant_delta`
- `tool_start`
- `tool_result`
- `task_update`
- `artifact_created`
- `approval_request`
- `approval_resolved`
- `warning`
- `final_response`

## 4. 주요 인터페이스 표면

| 구간 | 형태 | 용도 |
|---|---|---|
| Renderer -> Main | IPC | 세션 입력, 승인, 아티팩트 열기 |
| Main -> Session Kernel | in-process async contract | turn 실행, task 생성, 상태 변경 |
| Kernel -> Control Plane | HTTP + SSE/WebSocket | 세션 저장, task/event 동기화 |
| Kernel -> Bridge | HTTP polling + event ingress | 원격 세션 생성, 재연결, 중단 |
| Kernel -> Model Plane | HTTP | `/v1/models`, `/v1/chat/completions` |
| CLI/SDK Host -> Runtime | stdio / NDJSON | headless 실행, structured I/O |

## 5. Session API

권장 control-plane 계약:

- `POST /api/v2/sessions`
- `GET /api/v2/sessions/{session_id}`
- `POST /api/v2/sessions/{session_id}/turns`
- `GET /api/v2/sessions/{session_id}/stream`
- `POST /api/v2/sessions/{session_id}/resume`

`turn` 생성 시 입력 예시:

```json
{
  "message": "이 함수가 어디서 수정되는지 찾아줘",
  "cwd": "D:/repo",
  "selected_paths": ["src/foo.ts"],
  "selection": null,
  "requested_mode": "auto",
  "metadata": {
    "ui_surface": "desktop",
    "approval_mode": "default"
  }
}
```

## 6. Task API

긴 실행은 반드시 task로 승격합니다.

- `POST /api/v2/tasks`
- `GET /api/v2/tasks/{task_id}`
- `POST /api/v2/tasks/{task_id}/cancel`
- `POST /api/v2/tasks/{task_id}/retry`
- `GET /api/v2/tasks/{task_id}/artifacts`

대표 task 유형:

- `local_shell`
- `local_agent`
- `remote_agent`
- `verification`
- `team_run`

## 7. Approval API

위험 작업은 approval queue를 통과합니다.

- `GET /api/v2/approvals`
- `POST /api/v2/approvals/{approval_id}/resolve`

approval payload 예시:

```json
{
  "approval_id": "apr_1",
  "kind": "command_execution",
  "summary": "Run pytest against workspace",
  "risk_level": "medium",
  "target_paths": ["D:/repo/tests"],
  "command_preview": "pytest -q"
}
```

## 8. Artifact 계약

artifact는 단순 첨부가 아니라 구조화된 산출물입니다.

대표 `artifact_type`:

- `plan`
- `tool_log`
- `diff`
- `terminal_output`
- `test_report`
- `review_findings`
- `source_bundle`
- `bridge_session_log`

최종 응답은 가능하면 `answer + artifact references + next actions`를 함께 반환합니다.

## 9. Bridge API

원격 실행은 참고 소스의 bridge 구조를 따른 control-plane 계약으로 모델링합니다.

- `POST /api/v2/bridge/environments`
- `POST /api/v2/bridge/environments/{environment_id}/poll`
- `POST /api/v2/bridge/environments/{environment_id}/work/{work_id}/ack`
- `POST /api/v2/bridge/environments/{environment_id}/work/{work_id}/stop`
- `POST /api/v2/bridge/sessions/{session_id}/reconnect`

bridge는 아래를 책임집니다.

- 원격 세션 등록
- work item lease/poll
- 세션 재연결
- 원격 승인 전달
- 세션 heartbeat

## 10. 모델 계약

모델 평면은 변경하지 않습니다.

- `GET /v1/models`
- `POST /v1/chat/completions`

변경되는 부분은 모델 위 오케스트레이션이지, 모델 API 자체가 아닙니다.

## 11. 응답 완료 계약

`final_response`는 아래를 포함해야 합니다.

- `answer`
- `sources`
- `artifacts`
- `verification`
- `next_actions`
- `usage`

즉 API 인터페이스는 더 이상 "질문을 보내면 문자열이 오는 구조"가 아니라, `세션 기반 제어 API + 이벤트 스트림 + 산출물 API + 모델 게이트웨이`로 이해해야 합니다.
