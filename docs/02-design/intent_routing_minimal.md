# Minimal Intent Routing

## Summary

PIXLLM now treats intent routing as a small, fail-open hinting layer instead of a
strict classifier gate.

The goal is simple:

- keep broad engineering questions flowing through the code-first pipeline
- avoid request failures caused by invalid classifier labels
- reserve special response types for only a few explicit user signals

This policy is especially important for this project because most real user
traffic is code-oriented:

- code explanation
- flow / structure summaries
- usage walkthroughs
- debugging
- implementation or patch requests

In that environment, an aggressive multi-intent classifier creates more
instability than value.

## Current Policy

The front router is intentionally minimal and deterministic.

It now resolves a coarse routing bucket first:

- `read_code`
- `change_code`
- `doc_lookup`

Then it derives a compatible `response_type` hint for downstream routing.

Default fallback:

- broad engineering prompts -> `read_code` -> `code_explain`
- explicit document lookup -> `doc_lookup`
- explicit change intent or write-capable request metadata -> `change_code`

## Why We Minimized Intent Classification

The previous direction depended too much on a fine-grained intent classifier.
That caused several problems:

- invalid LLM output could block the request during prepare
- broad Korean prompts were hard to fit into narrow labels
- the classifier had to solve distinctions that retrieval can solve more safely
- latency and fragility increased without adding much routing value

Examples of prompts that should not fail at intent time:

- `영상 정합 흐름 정리해줘`
- `background map 로드 흐름 설명`
- `이 모듈 구조 설명해줘`

These are not high-risk classification problems. They are normal code-reading
questions and should proceed directly to code-first retrieval.

## Recommended Routing Model

Think of the system as using three layers:

1. Minimal front router
2. Runtime routing profile
3. Retrieval / ReAct loop

The front router should answer only:

- is this clearly docs-first?
- is this clearly a write / change request?
- otherwise: treat it as read-code

The runtime profile and retrieval loop do the real work:

- choose code vs docs priority
- gather evidence
- refine when evidence is weak
- generate the final answer style

## Design Rules

- Do not fail closed on invalid or low-confidence intent output.
- Do not use the intent layer as the main source of truth for code vs docs.
- Do not create large keyword tables that become a second classifier.
- Do prefer structured request metadata such as `task_type`, `tool_scope`, and `approval_mode`.
- Do keep a very small set of deterministic strong-signal checks.
- Do default broad technical prompts to `read_code`, which normally maps to `code_explain`.
- Do treat `response_type` primarily as a downstream presentation hint.

## Practical Effect

With this policy:

- `NXImageView usage guide` -> `read_code` -> `usage_guide`
- `NXImageView 문서 찾아줘` -> `doc_lookup`
- `영상 정합 흐름 정리해줘` -> `read_code` -> `code_explain`
- explicit write request metadata -> `change_code`

The important change is not the exact label.
The important change is that the request continues through the normal runtime
pipeline instead of failing during intent resolution.

## Implementation Notes

Relevant code:

- `backend/app/services/chat/intent.py`
- `backend/app/services/chat/runtime_profile.py`
- `backend/app/services/chat/retrieval/mode_policy.py`

Validation:

- `backend/tests/test_backend_helpers.py`
- `backend/tests/test_runtime_profile.py`
