# Qwen Tool-Calling Evaluation

Date: 2026-04-06

## Status

이 문서는 현재 설계 문서가 아니라, 2026-04-02 시점의 stopgap 실험을 기록한 참고 문서다.

현재 runtime은 이 문서의 권고를 그대로 따르지 않는다. 이후 구현은 아래 방향으로 바뀌었다.

- `tool_choice=required` 중심 stopgap에서 벗어남
- `QwenAdapter` 기반 textual tool protocol 수용
- malformed tool-call recovery 강화
- `QwenQueryRewrite` 기반 한국어/mixed prompt search hint 추가
- `nextSpeakerCheck` 기반 continuation 추가
- 공식 `Qwen/Qwen3.5-27B` 기본 설정으로 전환

즉 이 문서는 `왜 Qwen 전용 adapter가 필요했는지`를 설명하는 과거 실험 보고서로 읽어야 맞다.

## 당시 문제

실험 당시 concrete failure는 아래였다.

- user asks for code analysis
- model answers with prose such as `"I'll search..."`
- native tool call은 비거나 약함
- turn이 유효 final answer처럼 닫힐 수 있음

Claude Code도 `tool_use`가 없으면 plain assistant text를 성공으로 볼 수 있지만, Anthropic 모델은 native tool use를 더 잘 냈다. 이 문서는 그 차이가 model behavior인지 확인하려고 작성됐다.

## 당시 관찰 결과

당시 실험 결론은 단순했다.

1. `tool_choice=auto`에서 pseudo tool markup이 자주 나왔다.
2. `tool_choice=required`는 tool emission을 늘렸지만 너무 거칠었다.
3. 한국어 prompt도 같은 문제를 보였다.
4. 따라서 `required`는 유용한 진단 도구였지만, 최종 구조로는 적절하지 않았다.

예시 패턴:

```text
I'll search for image registration related code in the codebase.

<tool_call>
{"name": "grep", "arguments": {...}}
</tool_call>
```

이 패턴은 native `tool_calls`가 아니라 textual pseudo markup이기 때문에, adapter 없는 loop에서는 쉽게 놓친다.

## 왜 현재 구조가 바뀌었는가

이 실험의 가장 중요한 교훈은 `tool_choice forcing`보다 `Qwen 출력 적응층`이 더 본질적이라는 점이었다.

현재 runtime은 이 실험을 바탕으로 다음처럼 바뀌었다.

- model boundary에 `QwenAdapter.cjs` 추가
- Qwen textual `<tool_call>` / `<tool_response>`를 1급 프로토콜로 승격
- malformed JSON-like payload 복구
- `reasoning_content` / `reasoning` 기반 recovery
- `QwenQueryRewrite.cjs`로 한국어 prompt를 search/symbol hint로 재작성
- prose-only intermediate answer에 `nextSpeakerCheck.cjs` 적용

## 현재 읽는 방법

이 문서를 읽을 때는 아래처럼 해석해야 한다.

- `tool_choice=required`는 현재 기본 설계가 아님
- `required` 실험은 Qwen이 native transport보다 textual protocol에 더 자연스럽게 반응한다는 근거였음
- 현재 구현은 forcing 대신 adapter, rewrite, continuation으로 이동했음

## 현재 참고해야 할 문서

현재 구조를 보려면 이 문서를 기준으로 삼지 말고 아래를 먼저 본다.

- [Qwen_출력_적응_설계.md](/D:/Pixoneer_Source/PIX_RAG_Source/docs/02-design/Qwen_출력_적응_설계.md)
- [LLM서빙_상세_설계.md](/D:/Pixoneer_Source/PIX_RAG_Source/docs/02-design/LLM서빙_상세_설계.md)
- [desktop_layered_tool_loop_architecture.md](/D:/Pixoneer_Source/PIX_RAG_Source/docs/02-design/desktop_layered_tool_loop_architecture.md)

## Raw outputs

원 실험 결과는 아래 파일에 남아 있다.

- [.tmp-model-tool-eval-20260402.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402.json)
- [.tmp-model-tool-eval-20260402-b.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402-b.json)
- [.tmp-model-tool-eval-20260402-c.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402-c.json)

## Bottom Line

이 문서의 현재 의미는 하나다.

- `tool_choice forcing`은 임시 진단 도구로는 유효했지만
- 최종 해법은 `Qwen-first adapter architecture`였고
- 현재 PIXLLM은 그 방향으로 이미 이동했다
