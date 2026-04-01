# Desktop Layered Tool Loop Architecture

기준일: 2026-04-01

이 문서는 현재 desktop 로컬 agent loop를 계층별로 설명한다.

## 1. 현재 핵심 개념

현재 중심 구조는 `QueryEngine + ToolRuntime + tools/*`다.

- `QueryEngine`이 모델 turn loop를 관리한다.
- `processUserInput`이 pre-loop에서 request context를 만든다.
- `ToolRuntime`이 active tools, permission, grounding, tool batch execution을 관리한다.
- `StreamingToolExecutor`가 스트리밍 중 parse 가능한 tool call의 선실행과 drain/recovery를 담당한다.
- `tools/*`는 실제 file, shell, build, reference, task tool 구현이다.

현재 구조는 `single local tool loop`다. team, remote, MCP, plugin registry는 기본 경로가 아니다.

## 2. 레이어 정의

| 레이어 | 이름 | 현재 역할 |
|---|---|---|
| L0 | Desktop Event Surface | renderer와 main 사이의 요청/이벤트 전달 |
| L1 | Pre-loop Context | intent, directives, explicit path, evidence mode, initial tool scope 계산 |
| L2 | Query Loop | model call, parse, retry, compaction, grounding retry |
| L3 | Streaming Tool Prefetch | tool delta sync, parseable tool call 선실행, claim/drain |
| L4 | Permission and Grounding | deny-by-default gate, read-before-edit, backend-reference 분리 |
| L5 | Tool Execution | workspace, task runtime, backend evidence API 호출 |
| L6 | Transcript and Persistence | trace, transcript, file cache, session state 갱신 |

## 3. 현재 흐름

```mermaid
flowchart TD
    A["User request"] --> B["processUserInput"]
    B --> C["QueryEngine model call"]
    C --> D["assistant blocks parse"]
    D -->|text only| E["grounding check"]
    D -->|tool calls| F["StreamingToolExecutor sync"]
    F --> G["ToolRuntime executeToolBatch"]
    G --> H["tool_result blocks + trace"]
    H --> C
    E --> I["persist + done event"]
```

## 4. pre-loop

`processUserInput`가 현재 계산하는 것:

- intent: analysis, change, execution, compare
- directives: `/reference`, `/workspace`, `/hybrid`, `/exec`, `/change`, `/analysis`, `/config`
- explicit path candidate
- allowed direct paths
- evidence preference: `workspace`, `reference`, `hybrid`
- initial tool names

이 단계는 claude-code의 `processUserInput`보다 얕지만, 현재 desktop loop의 핵심 진입점이다.

## 5. tool policy

현재 policy는 deny-by-default다.

주요 규칙:

- 이번 turn에 enable되지 않은 tool은 거절
- unknown path는 바로 `read/edit/write`하지 않음
- edit/write 전에 read가 필요함
- backend reference path는 local file tool이 아니라 `company_reference_search`로 읽어야 함
- shell/build/task mutation은 execution intent 또는 충분한 grounded context가 있어야 함
- 새 tool이 명시 policy 없이 추가되면 `tool_policy_missing`으로 막힘

## 6. tool 범주

현재 registry의 주 범주:

- session/runtime: `todo_*`, `task_*`, `brief`, `ask_user_question`, `terminal_capture`
- workspace discovery: `list_files`, `glob`, `grep`, `project_context_search`, `find_symbol`, `find_callers`, `find_references`
- file/code read: `read_file`, `read_symbol_span`, `symbol_outline`, `symbol_neighborhood`, `lsp`
- mutation: `write`, `edit`, `notebook_edit`
- execution: `run_build`, `bash`, `powershell`
- backend reference: `company_reference_search`
- config: `config`

`web_search`, `web`, MCP/open-world registry는 현재 기본 경로에 없다.

## 7. streaming executor의 현재 수준

현재 구현은 완전한 claude-code식 same-stream reinjection은 아니다.

- tool call delta가 충분히 parse되면 바로 실행을 시작한다.
- concurrency-safe가 아닌 tool은 turn 종료 후 batch에서 실행한다.
- batch 단계에서 prefetched result를 claim해 재사용한다.
- cancel, parse failure, model error 시 `drainUnclaimed()`로 transcript 정합성을 복구한다.

즉 현재는 `streaming prefetch + claim/recovery` 구조다.

## 8. grounding과 recovery

현재 recovery 장치:

- parse retry
- output token cutoff recovery
- message/tool_result compaction
- repeated tool batch 제한
- no-progress retry
- ungrounded final answer retry
- interrupted tool result synthetic recovery
- stale-read 방어와 content hash fallback

## 9. 현재 한계

- same-stream tool_result 재주입 없음
- per-tool module 분리는 진행 중이지만 아직 일부 registry helper가 `tools.cjs`에 남아 있음
- claude-code 수준의 깊은 pre-loop 전처리까지는 아님
- desktop runtime과 backend ops plane은 분리되어 있음

현재 PIXLLM을 설명할 때는 `desktop single loop를 강화한 grounded tool architecture`라고 표현하는 것이 가장 정확하다.
