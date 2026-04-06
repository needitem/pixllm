# Qwen Tool-Calling Evaluation

Date: 2026-04-02

## Goal

Keep the overall Claude Code loop shape, but evaluate whether the current model behaves similarly enough under that loop.

The concrete failure to explain was:

- user asks for code analysis
- the model answers with prose such as "I'll search..."
- no native tool call is emitted
- the turn is treated as a valid final answer

Claude Code can also end on plain assistant text when no `tool_use` arrives, but Anthropic models tend to emit native tool calls more reliably. This report checks whether the remaining gap is primarily model behavior.

## Relevant Implementation Points

Current PIXLLM desktop loop:

- [QueryEngine.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/QueryEngine.cjs)
- [query.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/query.cjs)
- [streamModelCompletion.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/services/model/streamModelCompletion.cjs)
- [processUserInput.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/utils/processUserInput/processUserInput.cjs)
- [ToolRuntime.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/services/tools/ToolRuntime.cjs)

Claude Code reference points:

- [query.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/query.ts)
- [QueryEngine.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/QueryEngine.ts)
- [queryHelpers.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/utils/queryHelpers.ts)
- [prompts.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/constants/prompts.ts)

## Method

The evaluation used the actual desktop runtime pieces that shape model behavior:

- real `QueryEngine`
- real `processUserInput`
- real `buildSystemPrompt`
- real active tool narrowing for turn 1
- real JSON tool schemas exported to the model

The model endpoint tested was the direct OpenAI-compatible server behind the stack:

- backend health said current model label was `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled`
- direct callable model name on the LLM server was `qwen3.5-27b`
- direct LLM URL was `http://192.168.2.212:8001`

This was a tool-emission experiment, not a full end-to-end desktop transcript replay. It tested whether the model emits native `tool_calls` under the current PIXLLM prompt/tool contract.

Raw outputs were saved to:

- [.tmp-model-tool-eval-20260402.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402.json)
- [.tmp-model-tool-eval-20260402-b.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402-b.json)
- [.tmp-model-tool-eval-20260402-c.json](/D:/Pixoneer_Source/PIX_RAG_Source/.tmp-model-tool-eval-20260402-c.json)

## Result Summary

### 1. `tool_choice=auto` is the main failure point

For workspace analysis/search prompts, the current model frequently does not emit native tool calls under `auto`.

Instead it emits plain text plus pseudo markup such as:

```text
I'll search for image registration related code in the codebase.

<tool_call>
{"name": "grep", "arguments": {...}}
</tool_call>
```

That means:

- OpenAI-compatible `tool_calls` array is empty
- finish reason is usually `stop`
- PIXLLM sees a normal assistant text reply
- Claude-like success semantics allow that reply to end the turn

This reproduces the exact symptom the user saw.

### 2. `tool_choice=required` fixes native tool emission reliably

Across the tested evidence-seeking prompts, `required` consistently changed the model behavior from pseudo markup to real native `tool_calls`.

Observed patterns:

- workspace search prompt:
  - `auto`: 0 native tool calls, pseudo `<tool_call>` text
  - `required`: 3-4 native calls like `grep(...)`, `glob(...)`
- specific file read prompt:
  - `auto`: pseudo `read_file`
  - `required`: native `read_file`
- `/reference` prompt:
  - `auto`: pseudo `company_reference_search`
  - `required`: native `company_reference_search`
- Korean analysis prompt:
  - `auto`: pseudo `grep`
  - `required`: native `grep`

### 3. `required` is too blunt as a global default

For trivial questions that do not need tools:

- prompt: `What is 2 + 2?`
- `auto`: plain correct answer `4`
- `required`: model forced a meaningless tool call such as `brief(message="2 + 2 = 4")`

So a blanket global switch to `required` would degrade simple Q&A behavior.

### 4. The model issue is real even when intent classification is correct

One possible explanation was that PIXLLM might simply be failing to detect analysis-like prompts.

That is partly true for some English phrasings:

- `Search the codebase ... explain the flow` did not set `wantsAnalysis=true`

But that is not the full story.

When the prompt was made explicit:

- `Analyze the image registration flow in this codebase.`

the request context correctly became:

- `wantsAnalysis=true`
- `analysisOnly=true`

and the model still produced plain text plus pseudo `<tool_call>` markup under `auto`.

So the root cause is not only request classification. The model itself is not reliably honoring native tool calling under `auto`.

### 5. `/reference` routing is working at the tool-activation level

After correcting the evaluation harness to call `ToolRuntime.beginRun({ prompt, selectedFilePath })` properly, `/reference` did narrow turn-1 tools correctly:

- active tool set became `company_reference_search` plus always-on runtime tools
- the model still used pseudo markup under `auto`
- the same prompt produced native `company_reference_search(...)` under `required`

So this particular issue is not caused by broken reference routing.

## Detailed Observations

### Workspace analysis

Prompt:

```text
Search the codebase for image registration related code and explain the flow.
```

Observed:

- `auto`: assistant prose + pseudo `grep` markup
- `required`: native `grep` and `glob`

### Specific file read

Prompt:

```text
Open the main QueryEngine implementation and summarize how tool execution works.
```

Observed:

- `auto`: pseudo `read_file`
- `required`: native `read_file`

### Company reference search

Prompt:

```text
/reference Search company reference code for image registration flow and summarize the design.
```

Observed:

- active tool set correctly narrowed to include `company_reference_search`
- `auto`: prose + pseudo `company_reference_search`
- `required`: native `company_reference_search`

### Korean prompt

Prompt:

```text
Korean prompt equivalent of: "Search the codebase for video/image registration related code and explain the flow."
```

Observed:

- `auto`: prose + pseudo `grep`
- `required`: native `grep`

This matters because the production user prompt was Korean. The failure is not limited to English wording.

## Comparison With Claude Code

Claude Code semantics are still important, but they do not fully save this situation.

Claude Code does:

- treat native `tool_use` as follow-up work
- keep looping when `tool_use` appears
- consider a plain assistant text result successful when no `tool_use` appears

Relevant references:

- [queryHelpers.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/utils/queryHelpers.ts)
- [query.ts](/D:/Pixoneer_Source/PIX_RAG_Source/claude-code-sourcemap/restored-src/src/query.ts)

That means exact Claude Code semantics assume the model is willing to emit native tool calls when tools are appropriate.

The current Qwen model is not reliable enough under `tool_choice=auto` to satisfy that assumption.

So the current failure is best understood as:

- loop semantics are now reasonably Claude-like
- the model is not Claude-like enough in native tool-calling behavior

## Conclusions

### Main conclusion

The remaining failure is primarily model-behavioral, not just loop-architectural.

With the current model:

- `auto` often yields pseudo tool markup in assistant text
- `required` reliably yields native tool calls

### Secondary conclusion

PIXLLM should keep the overall Claude Code loop shape, but add a model-adaptive forcing layer. That is the smallest change that preserves the architecture while making the current model usable.

## Recommended Direction

### Recommended policy

Keep the Claude-like loop, but make `toolChoice` adaptive:

- use `auto` by default
- upgrade to `required` on turn 1 when the request is evidence-seeking and there are relevant tools available
- drop back to `auto` after the first real tool result if needed

### Suggested triggers for `required`

Use `required` when all of the following are true:

- turn is 1
- active tool set contains meaningful read/discovery/reference tools
- request is evidence-seeking

Evidence-seeking should include at least:

- `wantsAnalysis`
- `/reference`, `/workspace`, `/hybrid`
- prompts asking to search, find, inspect, trace, explain a code flow, summarize implementation, or compare code behavior
- prompts that mention codebase/workspace/internal reference source

### Suggested exclusions

Do not force `required` for:

- trivial factual or arithmetic questions
- clearly conversational replies
- prompts where no meaningful tools are active
- follow-up turns after the model already has enough evidence

## Concrete Next Steps

1. Add a model-adaptive `toolChoice` policy in [QueryEngine.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/QueryEngine.cjs) or [streamModelCompletion.cjs](/D:/Pixoneer_Source/PIX_RAG_Source/desktop/src/main/services/model/streamModelCompletion.cjs).
2. Use `required` only for first-turn evidence-seeking prompts on models that show this pseudo-tool pattern.
3. Strengthen `processUserInput` classification so English prompts like `search ... and explain the flow` are recognized as analysis-like more consistently.
4. Keep the existing Claude-like transcript semantics rather than adding regex guards for phrases like `I'll search...`.

## Non-Recommendation

Do not solve this by adding phrase-based guards such as:

- if answer contains `I'll search`
- if answer contains `let me check`

That would diverge from the Claude Code design for the wrong reason. The real issue is native tool-call reliability, not wording.

## Bottom Line

If the product goal is:

- keep Claude Code's overall loop shape
- but make PIXLLM work well with the current model

then the right move is:

- keep the loop Claude-like
- adapt `toolChoice` to the model
- force tools only on first-turn evidence-seeking requests

For the current Qwen model, that is the highest-leverage fix supported by the experiments.
