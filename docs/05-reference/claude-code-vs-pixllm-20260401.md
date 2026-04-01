# Claude Code vs PIXLLM

Date: 2026-04-01

## Scope

This comparison is based on the source trees currently available in this repository.

Compared paths:

- Claude Code source map: `D:\Pixoneer_Source\PIX_RAG_Source\claude-code-sourcemap\restored-src\src`
- PIXLLM source: `D:\Pixoneer_Source\PIX_RAG_Source`

Primary Claude Code files inspected:

- `claude-code-sourcemap/restored-src/src/QueryEngine.ts`
- `claude-code-sourcemap/restored-src/src/query.ts`
- `claude-code-sourcemap/restored-src/src/tools.ts`

Primary PIXLLM files inspected:

- `desktop/src/main/local_agent_service.cjs`
- `desktop/src/main/core/local_agent_engine.cjs`
- `desktop/src/main/core/local_agent_runtime.cjs`
- `desktop/src/main/core/local_request_context.cjs`
- `desktop/src/main/core/local_tool_policy.cjs`
- `desktop/src/main/core/local_tools.cjs`
- `desktop/src/main/core/local_model_client.cjs`
- `backend/app/routers/runs.py`
- `backend/app/routers/tool_runtime.py`

## High-Level Conclusion

PIXLLM has moved closer to Claude Code in structure, but the similarity is still partial.

Current PIXLLM strengths:

- explicit pre-loop request context
- central local tool permission gate
- grounded final answer checks
- structured local tool batch execution

Current PIXLLM gaps relative to Claude Code:

- no streaming-time tool execution
- no unified runtime across desktop and backend
- no built-in MCP/open-world path in the local agent loop
- no integrated team/sub-agent execution in the local agent path

## What Claude Code Does Differently

Claude Code still keeps more of the control loop inside one engine:

- `processUserInput` before the main loop
- `wrappedCanUseTool` for centralized permission checks
- streaming `tool_use` handling during generation
- interrupt cleanup with synthetic `tool_result`
- unified tool inventory in `tools.ts`

That means Claude Code is closer to a single integrated runtime than PIXLLM is today.

## What PIXLLM Now Implements

PIXLLM desktop local agent currently has:

- `LocalAgentService` as the stream/event surface
- `LocalAgentEngine` as the turn loop
- `LocalAgentRuntime` as the local orchestration layer
- `LocalToolCollection` as the tool registry
- `local_request_context` for explicit path and intent extraction
- `local_tool_policy` for path and execution gating

This is a real improvement over the older `engine only + tool collection` shape.

## Important Remaining Differences

### 1. Runtime split

PIXLLM still has a split between:

- desktop local agent runtime
- backend runs/tool-api/policy services

Claude Code keeps more of this inside one engine/runtime layer.

### 2. Tool timing

PIXLLM streams model text, collects `tool_calls`, and executes them after completion.

Claude Code can act on tool usage while the stream is still in progress.

### 3. Open-world scope

Claude Code includes MCP/open-world extension surfaces in its core tool model.

PIXLLM local agent path currently does not.

### 4. Recovery depth

PIXLLM has repeated batch prevention, interrupted tool results, and grounded answer retry, but Claude Code still has the more complete interrupt/transcript recovery model.

## What PIXLLM Should Learn from Claude Code

1. Keep tool orchestration as close to the engine loop as possible.
2. Preserve one central permission contract for every tool call.
3. Move toward streaming-time tool execution.
4. Reduce duplication between local runtime and backend runtime.

## What PIXLLM Should Not Copy Blindly

PIXLLM does not need to adopt every Claude Code concept.

- MCP/open-world integration is intentionally out of scope for the current local path.
- Team/remote abstractions should not be documented as current features until they are implemented.

## Current Recommended Roadmap

1. Unify desktop local runtime and backend tool/runtime policy.
2. Add streaming tool execution.
3. Keep expanding `LocalAgentRuntime` instead of spreading orchestration logic back across multiple files.
4. Only add team/remote/MCP layers after the single-agent runtime is stable.

## Bottom Line

Current PIXLLM is best described as:

- a desktop-first grounded coding assistant
- with a strengthened single local agent runtime
- plus optional backend operational APIs

It is not yet a full Claude Code-style unified agent platform, but it now has enough structure that the next refactors can move in that direction cleanly.
