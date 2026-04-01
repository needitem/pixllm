# Claude Code vs PIXLLM

Date: 2026-04-01

## Scope

This comparison is based on the source trees currently present in this repository.

Compared paths:

- Claude Code source map: `D:\Pixoneer_Source\PIX_RAG_Source\claude-code-sourcemap\restored-src\src`
- PIXLLM source: `D:\Pixoneer_Source\PIX_RAG_Source`

Primary Claude Code files inspected:

- `claude-code-sourcemap/restored-src/src/QueryEngine.ts`
- `claude-code-sourcemap/restored-src/src/query.ts`
- `claude-code-sourcemap/restored-src/src/Tool.ts`
- `claude-code-sourcemap/restored-src/src/services/tools/StreamingToolExecutor.ts`
- `claude-code-sourcemap/restored-src/src/utils/processUserInput/processUserInput.ts`

Primary PIXLLM files inspected:

- `desktop/src/main/QueryEngine.cjs`
- `desktop/src/main/query.cjs`
- `desktop/src/main/Tool.cjs`
- `desktop/src/main/tools.cjs`
- `desktop/src/main/services/tools/ToolRuntime.cjs`
- `desktop/src/main/services/tools/StreamingToolExecutor.cjs`
- `desktop/src/main/utils/processUserInput/processUserInput.cjs`
- `desktop/src/main/hooks/useCanUseTool.cjs`
- `desktop/src/main/services/tools/BackendToolClient.cjs`
- `backend/app/services/tools/doc_runtime.py`

## High-Level Conclusion

PIXLLM is much closer to Claude Code than it was before the refactor, but it is still not the same runtime model.

Current PIXLLM strengths:

- desktop-centered single agent loop
- explicit pre-loop request context
- deny-by-default central tool policy
- per-tool modules for core file and shell tools
- streaming-time tool prefetch with drain/recovery
- backend evidence integration through a bounded read-only tool

Current PIXLLM gaps relative to Claude Code:

- no same-stream reinjection of `tool_result` into the model
- shallower `processUserInput`
- fewer per-tool permission/rendering contracts
- backend control plane still separate from the desktop main loop

## What Claude Code Still Does Better

Claude Code keeps more of the control loop inside one integrated engine:

- deeper `processUserInput`
- tool decisions and permissions tightly attached to the engine loop
- streaming `tool_use` execution with immediate `tool_result` feedback
- richer per-tool contracts in individual modules
- more complete interrupt/transcript recovery

## What PIXLLM Now Does

Current PIXLLM desktop runtime is best described as:

- `QueryEngine.cjs` for the main loop
- `processUserInput.cjs` for pre-loop request shaping
- `ToolRuntime.cjs` for tool authorization and batch execution
- `StreamingToolExecutor.cjs` for streaming prefetch and recovery
- `tools/*` for actual tool implementations
- `company_reference_search` for backend-hosted reference evidence

This is no longer the older `LocalAgentEngine + LocalAgentRuntime + core/local_*` structure.

## Important Remaining Differences

### 1. Streaming tool loop depth

PIXLLM can start tool executions during streaming, but still consumes results on the next batch/turn boundary.

Claude Code is closer to a real streaming executor that can feed completed `tool_result` blocks back into the same loop immediately.

### 2. Pre-loop depth

PIXLLM computes intent, directives, explicit path, evidence mode, and initial tool scope.

Claude Code still handles more in pre-processing: attachments, images, slash commands, hooks, mentions, model/effort changes, and richer tool allowlists.

### 3. Per-tool completeness

PIXLLM now has stronger fail-closed defaults and several real tool modules, but Claude Code still has deeper contracts on a per-tool basis.

### 4. Backend role

PIXLLM intentionally keeps backend as an evidence and control plane, not as a second agent loop.

This is a product choice, not just a missing feature.

## What PIXLLM Should Learn from Claude Code

1. Keep pushing logic out of monolithic registry files and into per-tool modules.
2. Deepen pre-loop input shaping so the active tool set is narrower from turn one.
3. Move from streaming prefetch toward true same-stream tool result reinjection.
4. Keep permission checks explicit and fail-closed for every new tool.

## What PIXLLM Should Not Copy Blindly

- MCP/open-world integration is intentionally out of scope for the current product path.
- Remote bridge and team worker abstractions should not be documented as current features.
- Backend should remain a bounded evidence plane unless the product explicitly decides to build a second execution loop.

## Bottom Line

Current PIXLLM is best described as:

- a desktop-first grounded coding assistant
- with one local agent loop
- plus backend evidence and control services

It is now structurally closer to Claude Code, but still intentionally narrower in scope.
