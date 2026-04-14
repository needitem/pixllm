# Qwen 출력 적응 설계

기준일: 2026-04-06

목적: 현재 PIXLLM이 Qwen 계열 모델 출력을 어떻게 받아서 tool loop로 연결하는지 설명한다.

## 1. 왜 별도 적응층이 필요한가

현재 desktop runtime은 Qwen을 Claude나 OpenAI native function-calling과 동일하게 취급하지 않는다.

이유:

- Qwen은 `<tool_call>...</tool_call>` 같은 textual tool protocol을 자주 사용한다.
- `reasoning_content` 또는 `reasoning` 안에 tool intent가 들어갈 수 있다.
- tool을 쓰려던 의도는 있지만 block이 prose 안에 섞여 나오거나 reasoning 안으로 밀릴 수 있다.

따라서 현재 구조는 `Claude transport를 유지한 채 parser만 조금 보강`하는 방식이 아니라, `Qwen 전용 적응층을 둔 local tool loop`에 가깝다.

## 2. 현재 구성 요소

| 구성 요소 | 역할 |
|---|---|
| `QwenAdapter.cjs` | textual tool-call parsing, limited recovery, transcript flattening, system prompt/tool catalog 생성 |
| `streamModelCompletion.cjs` | direct/proxy transport, `reasoning_content` 수집, Qwen extra body 적용 |
| `QueryEngine.cjs` | streaming recovery, next speaker continuation, create-request verification, compaction-safe user query 보존 |
| `nextSpeakerCheck.cjs` | prose-only 응답 뒤에 model이 계속 말해야 하는지 판정 |

## 3. 현재 모델 프로토콜

현재 모델에 노출하는 기본 규약은 아래다.

- tool catalog는 OpenAI-style function schema JSON으로 system prompt 안에 나열한다.
- 실제 tool invocation은 plain text block으로 받는다.

```text
<tool_call>
{"name":"grep","arguments":{"query":"image registration","limit":10}}
</tool_call>
```

tool result는 user message 안의 textual block으로 되돌린다.

```text
<tool_response>
Tool: grep
Status: ok
Result:
...
</tool_response>
```

즉 transport는 OpenAI-compatible chat completion일 수 있어도, application-level contract는 Qwen textual protocol이다.

## 4. parser가 현재 복구하는 패턴

`QwenAdapter.cjs`는 아래를 현재 복구한다.

- 완전히 닫힌 `<tool_call>...</tool_call>`, `<tool_code>...</tool_code>`, `<tool_use>...</tool_use>` block
- `reasoning_content` 또는 `reasoning` 안에 들어간 동일 형식의 tool block
- bash fence 안의 명확한 read/search intent
- complete JSON 인자를 가진 native `tool_calls` fallback
- `user_prompt`, `active_tool_names`, `symbol_hints`를 활용한 제한적 prompt recovery

반대로 닫히지 않은 마지막 block이나 불완전한 JSON 인자는 더 이상 실제 tool call로 승격하지 않는다.

## 5. 한국어 입력 처리

현재 한국어 지원은 하드코딩된 용어집에 기대지 않는다.

흐름:

1. `processUserInput`가 `languageProfile`을 계산한다.
2. `processUserInput`가 필요한 `symbolHints`와 initial tool scope를 request context에 넣는다.
3. `QueryEngine`이 `user_prompt`, `active_tool_names`, `symbol_hints`를 recovery context로 전달한다.
4. `QwenAdapter` recovery는 이 정보를 사용해 제한적으로 tool call을 보정한다.

중요:

- `영상 정합 -> image registration` 같은 repo/domain 하드코딩은 현재 기본 설계가 아니다.
- 별도 bilingual rewrite helper는 현재 기본 경로가 아니다.

## 6. prose-only 응답 대응

Qwen은 tool result를 본 뒤에도 중간 prose로 멈출 수 있다. 현재 PIXLLM은 이 문제를 heavy finalization contract로 막지 않는다.

대신:

- turn이 prose-only로 끝나면
- `QueryEngine`이 `nextSpeakerCheck.cjs`를 호출한다.
- 결과가 `model`이면 meta user message `Please continue.`를 넣고 다음 turn으로 넘긴다.

이 설계는 문장 패턴 하드코딩보다 약하지만, Qwen Code와 비슷하게 `다음 화자 결정`으로 continuation을 처리한다.

## 7. compaction-safe user query 보존

Qwen 서버는 flattened messages 안에 실질 user query가 사라지면 `400 No user query found in messages`를 반환할 수 있다.

현재 방어는 두 겹이다.

1. `compactMessages()`가 첫 번째 substantive user message를 보존한다.
2. `_modelMessages()`가 flattened payload에 user query가 없으면 아래 형식으로 fallback user message를 다시 주입한다.

```text
User request:
...
```

이 보정은 message compaction 뒤에도 Qwen server가 다음 turn을 계속 처리할 수 있게 한다.

## 8. 현재 한계

- same-stream tool result reinjection은 아직 없다.
- parser는 강하지만 완전히 깨진 문법을 100% 복구하진 못한다.
- tool intent가 전혀 없는 일반 답변은 `nextSpeakerCheck`와 tool surface 설계의 영향을 더 많이 받는다.
- 모델 adapter는 Qwen 전용으로 단순화됐기 때문에 Claude-style provider parity는 현재 목표가 아니다.

## 9. 문서상 표현 원칙

현재 PIXLLM을 설명할 때는 아래처럼 쓰는 것이 정확하다.

- `Qwen-first desktop coding runtime`
- `textual tool-call protocol`
- `tolerant parser + rewrite hints + next-speaker continuation`
- `desktop single loop + backend evidence plane`
