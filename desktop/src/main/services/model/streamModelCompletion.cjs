function toStringValue(value) {
  return String(value || '').trim();
}

function buildHeaders() {
  return {
    'Content-Type': 'application/json',
  };
}

function resolveMode(baseUrl = '') {
  const normalized = toStringValue(baseUrl).replace(/\/$/, '');
  if (/(?:^|\/)api$/i.test(normalized)) {
    return 'proxy';
  }
  return 'openai';
}

function normalizeBaseUrl(baseUrl = '') {
  return toStringValue(baseUrl).replace(/\/$/, '');
}

function buildRequestTarget(baseUrl = '', path = '') {
  return `${normalizeBaseUrl(baseUrl)}${path}`;
}

const DEBUG_TEXT_LIMIT = 12000;
const DEBUG_ARRAY_LIMIT = 24;

function clipDebugText(value = '', maxChars = DEBUG_TEXT_LIMIT) {
  const text = String(value || '');
  if (text.length <= maxChars) return text;
  return `${text.slice(0, Math.max(0, maxChars - 15))}\n...[truncated]`;
}

function sanitizeDebugValue(value, depth = 0) {
  if (depth > 4) {
    return '[depth-truncated]';
  }
  if (typeof value === 'string') {
    return clipDebugText(value);
  }
  if (Array.isArray(value)) {
    return value.slice(0, DEBUG_ARRAY_LIMIT).map((item) => sanitizeDebugValue(item, depth + 1));
  }
  if (value && typeof value === 'object') {
    const output = {};
    for (const [key, item] of Object.entries(value)) {
      output[key] = sanitizeDebugValue(item, depth + 1);
    }
    return output;
  }
  return value;
}

function buildDebugSnapshot({
  candidate = {},
  requestPath = '',
  requestBody = {},
  responseStatus = 0,
  responsePayload = null,
  responseText = '',
  meta = null,
} = {}) {
  return {
    request: {
      endpoint: buildRequestTarget(candidate.baseUrl, requestPath),
      mode: toStringValue(candidate.mode),
      label: toStringValue(candidate.label),
      body: sanitizeDebugValue(requestBody),
    },
    response: {
      status: Number(responseStatus || 0),
      payload: sanitizeDebugValue(responsePayload),
      rawText: typeof responseText === 'string' && responseText
        ? clipDebugText(responseText)
        : '',
    },
    meta: meta && typeof meta === 'object' ? sanitizeDebugValue(meta) : {},
  };
}

const DEFAULT_MAX_TOKENS = 1200;
const MIN_COMPLETION_TOKENS = 1;
const MAX_CONTEXT_OVERFLOW_RETRIES = 3;
const NON_EXACT_CONTEXT_RETRY_MARGIN = 32;

function normalizeMaxTokens(maxTokens = DEFAULT_MAX_TOKENS) {
  const value = Math.floor(Number(maxTokens || 0));
  if (Number.isFinite(value) && value >= MIN_COMPLETION_TOKENS) {
    return value;
  }
  return DEFAULT_MAX_TOKENS;
}

function shouldRetryWithFallback(status, payload, rawText = '') {
  const code = Number(status || 0);
  if ([404, 405, 501, 502, 503, 504].includes(code)) {
    return true;
  }
  const detail = typeof payload?.detail === 'string'
    ? payload.detail
    : typeof payload?.error?.message === 'string'
      ? payload.error.message
      : typeof payload?.message === 'string'
        ? payload.message
        : String(rawText || '');
  return /not found|no route|unsupported|unavailable/i.test(String(detail || ''));
}

function shouldFallbackAfterCaughtError(error) {
  const message = String(error instanceof Error ? error.message : error || '').toLowerCase();
  if (!message) {
    return false;
  }
  return /econnrefused|enotfound|networkerror|fetch failed|connection refused|no route|unsupported|unavailable|not found|http 404|http 405|http 501|http 502|http 503|http 504/.test(message);
}

function extractErrorMessage(payload, rawText = '') {
  if (typeof payload === 'string') {
    return payload;
  }
  if (typeof payload?.detail === 'string') {
    return payload.detail;
  }
  if (typeof payload?.error?.message === 'string') {
    return payload.error.message;
  }
  if (typeof payload?.message === 'string') {
    return payload.message;
  }
  return String(rawText || '');
}

function parseAllowedCompletionTokens(errorMessage = '') {
  const message = toStringValue(errorMessage);
  if (!message) {
    return null;
  }
  const hasExactOutputBudget = /requested\s*\d+\s*output tokens/i.test(message);
  const patterns = [
    {
      expression: /maximum context length is\s*(\d+)\s*tokens\s*and your request has\s*(\d+)\s*input tokens/i,
      windowIndex: 1,
      inputIndex: 2,
    },
    {
      expression: /passed\s*(\d+)\s*input tokens[\s\S]*?context length is only\s*(\d+)\s*tokens/i,
      windowIndex: 2,
      inputIndex: 1,
    },
  ];
  for (const pattern of patterns) {
    const match = message.match(pattern.expression);
    if (!match) {
      continue;
    }
    const contextWindow = Number(match[pattern.windowIndex] || 0);
    const inputTokens = Number(match[pattern.inputIndex] || 0);
    if (!Number.isFinite(contextWindow) || !Number.isFinite(inputTokens)) {
      return null;
    }
    let allowed = contextWindow - inputTokens;
    if (!hasExactOutputBudget) {
      allowed -= NON_EXACT_CONTEXT_RETRY_MARGIN;
    }
    return Math.max(MIN_COMPLETION_TOKENS, Math.floor(allowed));
  }
  return null;
}

function resolveContextOverflowRetryMaxTokens(error, currentMaxTokens = DEFAULT_MAX_TOKENS) {
  const allowed = parseAllowedCompletionTokens(
    error instanceof Error ? error.message : String(error || ''),
  );
  const current = normalizeMaxTokens(currentMaxTokens);
  if (!Number.isFinite(allowed) || allowed == null) {
    return null;
  }
  const next = Math.max(MIN_COMPLETION_TOKENS, Math.floor(allowed));
  if (next >= current) {
    return null;
  }
  return next;
}

function buildCompletionRequestBody({
  mode = 'openai',
  model = '',
  messages = [],
  maxTokens = DEFAULT_MAX_TOKENS,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
  extraBody = null,
  stream = false,
} = {}) {
  return {
    model: toStringValue(model),
    messages: Array.isArray(messages) ? messages : [],
    max_tokens: normalizeMaxTokens(maxTokens),
    temperature: Number.isFinite(Number(temperature)) ? Number(temperature) : 0.2,
    ...(mode === 'proxy'
      ? toStringValue(responseFormat) && toStringValue(responseFormat).toLowerCase() !== 'text'
        ? { response_format: toStringValue(responseFormat) }
        : {}
      : responseFormat === 'json_object'
        ? { response_format: { type: 'json_object' } }
        : {}),
    ...(mode === 'openai' && stream ? { stream: true } : {}),
    stop: Array.isArray(stop) ? stop.map((item) => toStringValue(item)).filter(Boolean) : [],
    ...(extraBody && typeof extraBody === 'object' ? extraBody : {}),
  };
}

function normalizeTokenizePayload(payload = {}) {
  const tokenValues = Array.isArray(payload?.tokens)
    ? payload.tokens
    : Array.isArray(payload?.token_ids)
      ? payload.token_ids
      : Array.isArray(payload?.ids)
        ? payload.ids
        : [];
  let count = 0;
  for (const candidate of [payload?.count, payload?.token_count, payload?.prompt_tokens, tokenValues.length]) {
    const value = Number(candidate || 0);
    if (Number.isFinite(value) && value >= 0) {
      count = Math.floor(value);
      break;
    }
  }
  let maxModelLen = 0;
  for (const candidate of [payload?.max_model_len, payload?.max_model_len_tokens, payload?.model_max_length, payload?.maxModelLen]) {
    const value = Number(candidate || 0);
    if (Number.isFinite(value) && value > 0) {
      maxModelLen = Math.floor(value);
      break;
    }
  }
  return {
    count,
    maxModelLen,
    tokens: tokenValues,
  };
}

function buildEndpointCandidates({
  baseUrl = '',
  fallbackBaseUrl = '',
} = {}) {
  const primaryBaseUrl = normalizeBaseUrl(baseUrl);
  const fallbackBase = normalizeBaseUrl(fallbackBaseUrl);
  const candidates = [];
  if (primaryBaseUrl) {
    candidates.push({
      baseUrl: primaryBaseUrl,
      mode: resolveMode(primaryBaseUrl),
      label: 'primary',
    });
  }
  if (fallbackBase && fallbackBase !== primaryBaseUrl) {
    candidates.push({
      baseUrl: fallbackBase,
      mode: resolveMode(fallbackBase),
      label: 'fallback',
    });
  }
  return candidates;
}

async function countPromptTokens({
  baseUrl = '',
  fallbackBaseUrl = '',
  model = '',
  messages = [],
  signal = null,
} = {}) {
  const candidates = buildEndpointCandidates({
    baseUrl,
    fallbackBaseUrl,
  });
  if (!candidates.length) {
    throw new Error('serverBaseUrl is required');
  }
  let lastError = null;
  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    const hasFallback = index < candidates.length - 1;
    try {
      const response = await fetch(
        candidate.mode === 'proxy'
          ? buildRequestTarget(candidate.baseUrl, '/v1/llm/tokenize')
          : buildRequestTarget(candidate.baseUrl, '/tokenize'),
        {
          method: 'POST',
          headers: buildHeaders(),
          signal: signal || undefined,
          body: JSON.stringify({
            model: toStringValue(model),
            messages: Array.isArray(messages) ? messages : [],
            return_token_strs: false,
          }),
        },
      );
      const text = await response.text();
      let payload = null;
      try {
        payload = JSON.parse(text);
      } catch {
        if (hasFallback && shouldRetryWithFallback(response.status, null, text)) {
          continue;
        }
        throw new Error(text || `HTTP ${response.status}`);
      }
      if (candidate.mode === 'proxy') {
        if (!response.ok || !payload?.ok) {
          if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
            continue;
          }
          throw new Error(extractErrorMessage(payload, text) || `HTTP ${response.status}`);
        }
        return normalizeTokenizePayload(payload.data || {});
      }
      if (!response.ok) {
        if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
          continue;
        }
        throw new Error(extractErrorMessage(payload, text) || `HTTP ${response.status}`);
      }
      return normalizeTokenizePayload(payload || {});
    } catch (error) {
      lastError = error;
      if (!hasFallback || !shouldFallbackAfterCaughtError(error)) {
        throw error;
      }
    }
  }
  throw lastError || new Error('LLM tokenize request failed');
}

function parseSseChunk(buffer, onEvent) {
  let nextBuffer = buffer;
  let index = -1;
  while ((index = nextBuffer.indexOf('\n\n')) >= 0) {
    const rawChunk = nextBuffer.slice(0, index);
    nextBuffer = nextBuffer.slice(index + 2);
    const lines = rawChunk.split('\n').map((line) => line.trim()).filter(Boolean);
    let eventName = 'message';
    const dataLines = [];
    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim() || 'message';
      } else if (line.startsWith('data:')) {
        dataLines.push(line.slice(5).trim());
      }
    }
    const rawPayload = dataLines.join('\n').trim();
    if (!rawPayload) continue;
    let payload = rawPayload;
    try {
      payload = JSON.parse(rawPayload);
    } catch {
      // keep raw payload
    }
    onEvent(eventName, payload);
  }
  return nextBuffer;
}

function normalizeOpenAiToolCalls(toolCalls) {
  return (Array.isArray(toolCalls) ? toolCalls : [])
    .map((item) => {
      const fn = item?.function && typeof item.function === 'object' ? item.function : {};
      const rawInput = item?.input && typeof item.input === 'object' && !Array.isArray(item.input)
        ? item.input
        : null;
      const argumentsText = rawInput
        ? JSON.stringify(rawInput)
        : typeof fn?.arguments === 'string'
          ? fn.arguments
          : typeof item?.arguments === 'string'
            ? item.arguments
            : '';
      if (!toStringValue(fn?.name || item?.name) || !/[}\]]\s*$/.test(toStringValue(argumentsText))) {
        return null;
      }
      try {
        const parsed = rawInput || JSON.parse(argumentsText);
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
          return null;
        }
      } catch {
        return null;
      }
      return {
        id: toStringValue(item?.id),
        name: toStringValue(fn?.name || item?.name),
        arguments: argumentsText,
      };
    })
    .filter(Boolean);
}

function coerceOpenAiText(value) {
  if (typeof value === 'string') {
    return value;
  }
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object') {
          if (typeof item.text === 'string') return item.text;
          if (typeof item.content === 'string') return item.content;
        }
        return '';
      })
      .join('');
  }
  return '';
}

function buildExtraBody({
  model = '',
} = {}) {
  const normalizedModel = toStringValue(model).toLowerCase();
  if (/qwen/i.test(normalizedModel)) {
    return {
      chat_template_kwargs: {
        enable_thinking: true,
      },
      top_k: 20,
    };
  }
  return null;
}

async function callModelCompletion({
  baseUrl = '',
  fallbackBaseUrl = '',
  model = '',
  messages = [],
  maxTokens = 1200,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
  extraBody = null,
  signal = null,
} = {}) {
  const candidates = buildEndpointCandidates({
    baseUrl,
    fallbackBaseUrl,
  });
  if (!candidates.length) {
    throw new Error('serverBaseUrl is required');
  }
  let lastError = null;
  const debugAttempts = [];
  const defaultExtraBody = buildExtraBody({ model });
  const resolvedExtraBody = extraBody && typeof extraBody === 'object'
    ? extraBody
    : defaultExtraBody;
  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    const hasFallback = index < candidates.length - 1;
    let requestedMaxTokens = normalizeMaxTokens(maxTokens);
    let contextOverflowRetries = 0;
    while (true) {
      try {
        const requestPath = candidate.mode === 'proxy'
          ? '/v1/llm/chat_completions'
          : '/v1/chat/completions';
        const endpoint = buildRequestTarget(candidate.baseUrl, requestPath);
        const requestBody = buildCompletionRequestBody({
          mode: candidate.mode,
          model,
          messages,
          maxTokens: requestedMaxTokens,
          temperature,
          responseFormat,
          stop,
          extraBody: resolvedExtraBody,
        });
        const response = await fetch(
          buildRequestTarget(candidate.baseUrl, requestPath),
          {
            method: 'POST',
            headers: buildHeaders(),
            signal: signal || undefined,
            body: JSON.stringify(requestBody),
          },
        );
        const text = await response.text();
        let payload = null;
        try {
          payload = JSON.parse(text);
        } catch {
          debugAttempts.push({
            kind: 'response_parse_error',
            label: candidate.label,
            mode: candidate.mode,
            endpoint,
            maxTokens: requestedMaxTokens,
            status: response.status,
          });
          if (hasFallback && shouldRetryWithFallback(response.status, null, text)) {
            debugAttempts.push({
              kind: 'fallback',
              label: candidate.label,
              mode: candidate.mode,
              endpoint,
              reason: 'response_parse_error',
              status: response.status,
            });
            break;
          }
          throw new Error(text || `HTTP ${response.status}`);
        }
        if (candidate.mode === 'proxy') {
          if (!response.ok || !payload?.ok) {
            debugAttempts.push({
              kind: 'response_error',
              label: candidate.label,
              mode: candidate.mode,
              endpoint,
              maxTokens: requestedMaxTokens,
              status: response.status,
              message: extractErrorMessage(payload, text),
            });
            if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
              debugAttempts.push({
                kind: 'fallback',
                label: candidate.label,
                mode: candidate.mode,
                endpoint,
                reason: 'proxy_error',
                status: response.status,
              });
              break;
            }
            throw new Error(extractErrorMessage(payload, text) || `HTTP ${response.status}`);
          }
          debugAttempts.push({
            kind: 'success',
            label: candidate.label,
            mode: candidate.mode,
            endpoint,
            maxTokens: requestedMaxTokens,
            status: response.status,
          });
          return {
            ...(payload.data || {}),
            debug: buildDebugSnapshot({
              candidate,
              requestPath,
              requestBody,
              responseStatus: response.status,
              responsePayload: payload,
              responseText: text,
              meta: { attempts: debugAttempts },
            }),
          };
        }
        if (!response.ok) {
          debugAttempts.push({
            kind: 'response_error',
            label: candidate.label,
            mode: candidate.mode,
            endpoint,
            maxTokens: requestedMaxTokens,
            status: response.status,
            message: extractErrorMessage(payload, text),
          });
          if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
            debugAttempts.push({
              kind: 'fallback',
              label: candidate.label,
              mode: candidate.mode,
              endpoint,
              reason: 'openai_error',
              status: response.status,
            });
            break;
          }
          throw new Error(extractErrorMessage(payload, text) || `HTTP ${response.status}`);
        }
        const choice = Array.isArray(payload?.choices) ? payload.choices[0] : null;
        const content = coerceOpenAiText(choice?.message?.content);
        const reasoningContent = coerceOpenAiText(
          choice?.message?.reasoning_content || choice?.message?.reasoning,
        );
        debugAttempts.push({
          kind: 'success',
          label: candidate.label,
          mode: candidate.mode,
          endpoint,
          maxTokens: requestedMaxTokens,
          status: response.status,
          finishReason: toStringValue(choice?.finish_reason),
        });
        return {
          text: content,
          reasoning_content: reasoningContent,
          tool_calls: normalizeOpenAiToolCalls(choice?.message?.tool_calls),
          finish_reason: toStringValue(choice?.finish_reason),
          usage: payload?.usage && typeof payload.usage === 'object' ? payload.usage : {},
          debug: buildDebugSnapshot({
            candidate,
            requestPath,
            requestBody,
            responseStatus: response.status,
            responsePayload: payload,
            responseText: text,
            meta: { attempts: debugAttempts },
          }),
        };
      } catch (error) {
        lastError = error;
        const retryMaxTokens = resolveContextOverflowRetryMaxTokens(error, requestedMaxTokens);
        if (
          retryMaxTokens != null
          && contextOverflowRetries < MAX_CONTEXT_OVERFLOW_RETRIES
        ) {
          debugAttempts.push({
            kind: 'context_retry',
            label: candidate.label,
            mode: candidate.mode,
            maxTokens: requestedMaxTokens,
            nextMaxTokens: retryMaxTokens,
            message: error instanceof Error ? error.message : String(error || ''),
          });
          requestedMaxTokens = retryMaxTokens;
          contextOverflowRetries += 1;
          continue;
        }
        debugAttempts.push({
          kind: 'request_error',
          label: candidate.label,
          mode: candidate.mode,
          maxTokens: requestedMaxTokens,
          message: error instanceof Error ? error.message : String(error || ''),
        });
        if (error && typeof error === 'object') {
          error.debugMeta = sanitizeDebugValue({ attempts: debugAttempts });
        }
        if (!hasFallback || !shouldFallbackAfterCaughtError(error)) {
          throw error;
        }
        break;
      }
    }
  }
  throw lastError || new Error('LLM request failed');
}

async function streamModelCompletion({
  baseUrl = '',
  fallbackBaseUrl = '',
  model = '',
  messages = [],
  maxTokens = 1200,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
  signal = null,
  onToken = async () => {},
  onReasoningToken = async () => {},
  onToolCalls = async () => {},
  extraBody = null,
} = {}) {
  const candidates = buildEndpointCandidates({
    baseUrl,
    fallbackBaseUrl,
  });
  if (!candidates.length) {
    throw new Error('serverBaseUrl is required');
  }
  let lastError = null;
  const debugAttempts = [];
  const defaultExtraBody = buildExtraBody({ model });
  const resolvedExtraBody = extraBody && typeof extraBody === 'object'
    ? extraBody
    : defaultExtraBody;
  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    const hasFallback = index < candidates.length - 1;
    let requestedMaxTokens = normalizeMaxTokens(maxTokens);
    let contextOverflowRetries = 0;
    while (true) {
      try {
        const requestPath = candidate.mode === 'proxy'
          ? '/v1/llm/chat_completions/stream'
          : '/v1/chat/completions';
        const endpoint = buildRequestTarget(candidate.baseUrl, requestPath);
        const requestBody = buildCompletionRequestBody({
          mode: candidate.mode,
          model,
          messages,
          maxTokens: requestedMaxTokens,
          temperature,
          responseFormat,
          stop,
          extraBody: resolvedExtraBody,
          stream: candidate.mode === 'openai',
        });
        const response = await fetch(candidate.mode === 'proxy'
          ? buildRequestTarget(candidate.baseUrl, requestPath)
          : buildRequestTarget(candidate.baseUrl, requestPath), {
          method: 'POST',
          headers: buildHeaders(),
          body: JSON.stringify(requestBody),
          signal: signal || undefined,
        });

        if (!response.ok || !response.body) {
          const text = await response.text();
          let payload = null;
          try {
            payload = JSON.parse(text);
          } catch {
            payload = null;
          }
          debugAttempts.push({
            kind: 'response_error',
            label: candidate.label,
            mode: candidate.mode,
            endpoint,
            maxTokens: requestedMaxTokens,
            status: response.status,
            message: extractErrorMessage(payload, text),
          });
          if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
            debugAttempts.push({
              kind: 'fallback',
              label: candidate.label,
              mode: candidate.mode,
              endpoint,
              reason: 'stream_response_error',
              status: response.status,
            });
            break;
          }
          throw new Error(extractErrorMessage(payload, text) || `HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let aggregated = '';
        let aggregatedReasoning = '';
        let donePayload = null;
        const openAiToolCalls = [];

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          buffer = parseSseChunk(buffer, (eventName, payload) => {
            if (candidate.mode === 'openai') {
              if (eventName === 'message' && payload === '[DONE]') {
                donePayload = donePayload || { text: aggregated, finish_reason: '', usage: {} };
                return;
              }
              const choice = Array.isArray(payload?.choices) ? payload.choices[0] : null;
              const deltaText =
                typeof choice?.delta?.content === 'string'
                  ? choice.delta.content
                  : Array.isArray(choice?.delta?.content)
                    ? choice.delta.content.map((item) => String(item?.text || '')).join('')
                    : '';
              const deltaReasoning = coerceOpenAiText(
                choice?.delta?.reasoning_content || choice?.delta?.reasoning,
              );
              const deltaToolCalls = Array.isArray(choice?.delta?.tool_calls) ? choice.delta.tool_calls : [];
              if (deltaReasoning) {
                aggregatedReasoning += deltaReasoning;
                void onReasoningToken(deltaReasoning, aggregatedReasoning);
              }
              if (deltaText) {
                aggregated += deltaText;
                void onToken(deltaText, aggregated);
              }
              for (const deltaToolCall of deltaToolCalls) {
                const slot = Number(deltaToolCall?.index || 0);
                if (!openAiToolCalls[slot]) {
                  openAiToolCalls[slot] = { id: '', name: '', arguments: '' };
                }
                if (typeof deltaToolCall?.id === 'string') {
                  openAiToolCalls[slot].id = deltaToolCall.id;
                }
                const fn = deltaToolCall?.function && typeof deltaToolCall.function === 'object'
                  ? deltaToolCall.function
                  : {};
                if (typeof fn?.name === 'string' && fn.name) {
                  openAiToolCalls[slot].name = fn.name;
                }
                if (typeof fn?.arguments === 'string' && fn.arguments) {
                  openAiToolCalls[slot].arguments += fn.arguments;
                }
              }
              if (choice?.finish_reason) {
                donePayload = {
                  text: aggregated,
                  reasoning_content: aggregatedReasoning,
                  tool_calls: normalizeOpenAiToolCalls(openAiToolCalls),
                  finish_reason: toStringValue(choice.finish_reason),
                  usage: payload?.usage && typeof payload.usage === 'object' ? payload.usage : {},
                };
              }
              return;
            }
            if (eventName === 'token') {
              const tokenText =
                typeof payload === 'string'
                  ? payload
                  : typeof payload?.content === 'string'
                    ? payload.content
                    : '';
              if (!tokenText) return;
              aggregated += tokenText;
              void onToken(tokenText, aggregated);
              return;
            }
            if (eventName === 'error') {
              const messageText =
                typeof payload === 'string'
                  ? payload
                  : typeof payload?.message === 'string'
                    ? payload.message
                    : 'Unknown model streaming error';
              throw new Error(messageText);
            }
            if (eventName === 'done') {
              donePayload = payload;
            }
          });
        }

        if (donePayload && typeof donePayload === 'object') {
          debugAttempts.push({
            kind: 'success',
            label: candidate.label,
            mode: candidate.mode,
            endpoint,
            maxTokens: requestedMaxTokens,
            status: response.status,
            finishReason: toStringValue(donePayload.finish_reason),
          });
          return {
            text: typeof donePayload.text === 'string' ? donePayload.text : aggregated,
            reasoning_content: typeof donePayload.reasoning_content === 'string' ? donePayload.reasoning_content : aggregatedReasoning,
            tool_calls: normalizeOpenAiToolCalls(donePayload.tool_calls || openAiToolCalls),
            finish_reason: toStringValue(donePayload.finish_reason),
            usage: donePayload.usage && typeof donePayload.usage === 'object' ? donePayload.usage : {},
            debug: buildDebugSnapshot({
              candidate,
              requestPath,
              requestBody,
              responseStatus: response.status,
              responsePayload: donePayload,
              responseText: aggregated,
              meta: { attempts: debugAttempts },
            }),
          };
        }

        debugAttempts.push({
          kind: 'success',
          label: candidate.label,
          mode: candidate.mode,
          endpoint,
          maxTokens: requestedMaxTokens,
          status: response.status,
          finishReason: '',
        });
        return {
          text: aggregated,
          reasoning_content: aggregatedReasoning,
          tool_calls: normalizeOpenAiToolCalls(openAiToolCalls),
          finish_reason: '',
          usage: {},
          debug: buildDebugSnapshot({
            candidate,
            requestPath,
            requestBody,
            responseStatus: response.status,
            responsePayload: {
              text: aggregated,
              reasoning_content: aggregatedReasoning,
              tool_calls: normalizeOpenAiToolCalls(openAiToolCalls),
              finish_reason: '',
              usage: {},
            },
            responseText: aggregated,
            meta: { attempts: debugAttempts },
          }),
        };
      } catch (error) {
        lastError = error;
        const retryMaxTokens = resolveContextOverflowRetryMaxTokens(error, requestedMaxTokens);
        if (
          retryMaxTokens != null
          && contextOverflowRetries < MAX_CONTEXT_OVERFLOW_RETRIES
        ) {
          debugAttempts.push({
            kind: 'context_retry',
            label: candidate.label,
            mode: candidate.mode,
            maxTokens: requestedMaxTokens,
            nextMaxTokens: retryMaxTokens,
            message: error instanceof Error ? error.message : String(error || ''),
          });
          requestedMaxTokens = retryMaxTokens;
          contextOverflowRetries += 1;
          continue;
        }
        debugAttempts.push({
          kind: 'request_error',
          label: candidate.label,
          mode: candidate.mode,
          maxTokens: requestedMaxTokens,
          message: error instanceof Error ? error.message : String(error || ''),
        });
        if (error && typeof error === 'object') {
          error.debugMeta = sanitizeDebugValue({ attempts: debugAttempts });
        }
        if (!hasFallback || !shouldFallbackAfterCaughtError(error)) {
          throw error;
        }
        break;
      }
    }
  }
  throw lastError || new Error('LLM stream request failed');
}

module.exports = {
  callModelCompletion,
  countPromptTokens,
  streamModelCompletion,
};
