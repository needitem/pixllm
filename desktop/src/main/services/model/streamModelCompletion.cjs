function toStringValue(value) {
  return String(value || '').trim();
}

function buildHeaders(apiToken = '') {
  const headers = {
    'Content-Type': 'application/json',
  };
  const token = toStringValue(apiToken);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
    headers['x-api-token'] = token;
  }
  return headers;
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

function buildEndpointCandidates({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
} = {}) {
  const primaryBaseUrl = normalizeBaseUrl(baseUrl);
  const fallbackBase = normalizeBaseUrl(fallbackBaseUrl);
  const candidates = [];
  if (primaryBaseUrl) {
    candidates.push({
      baseUrl: primaryBaseUrl,
      apiToken: toStringValue(apiToken),
      mode: resolveMode(primaryBaseUrl),
      label: 'primary',
    });
  }
  if (fallbackBase && fallbackBase !== primaryBaseUrl) {
    candidates.push({
      baseUrl: fallbackBase,
      apiToken: toStringValue(fallbackApiToken || apiToken),
      mode: resolveMode(fallbackBase),
      label: 'fallback',
    });
  }
  return candidates;
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
      return {
        id: toStringValue(item?.id),
        name: toStringValue(fn?.name || item?.name),
        arguments: typeof fn?.arguments === 'string'
          ? fn.arguments
          : typeof item?.arguments === 'string'
            ? item.arguments
            : '',
      };
    })
    .filter((item) => item.id || item.name || item.arguments);
}

async function callModelCompletion({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  messages = [],
  tools = [],
  toolChoice = 'auto',
  maxTokens = 1200,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
} = {}) {
  const candidates = buildEndpointCandidates({
    baseUrl,
    apiToken,
    fallbackBaseUrl,
    fallbackApiToken,
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
          ? buildRequestTarget(candidate.baseUrl, '/v1/llm/chat_completions')
          : buildRequestTarget(candidate.baseUrl, '/v1/chat/completions'),
        {
          method: 'POST',
          headers: buildHeaders(candidate.apiToken),
          body: JSON.stringify({
            model: toStringValue(model),
            messages: Array.isArray(messages) ? messages : [],
            ...(Array.isArray(tools) && tools.length > 0 ? { tools, tool_choice: toolChoice || 'auto' } : {}),
            max_tokens: Math.max(128, Number(maxTokens || 1200)),
            temperature: Number.isFinite(Number(temperature)) ? Number(temperature) : 0.2,
            ...(candidate.mode === 'proxy'
              ? toStringValue(responseFormat) && toStringValue(responseFormat).toLowerCase() !== 'text'
                ? { response_format: toStringValue(responseFormat) }
                : {}
              : responseFormat === 'json_object'
                ? { response_format: { type: 'json_object' } }
                : {}),
            stop: Array.isArray(stop) ? stop.map((item) => toStringValue(item)).filter(Boolean) : [],
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
          throw new Error(payload?.error?.message || payload?.message || `HTTP ${response.status}`);
        }
        return payload.data || {};
      }
      if (!response.ok) {
        if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
          continue;
        }
        throw new Error(payload?.error?.message || payload?.message || `HTTP ${response.status}`);
      }
      const choice = Array.isArray(payload?.choices) ? payload.choices[0] : null;
      const content =
        typeof choice?.message?.content === 'string'
          ? choice.message.content
          : Array.isArray(choice?.message?.content)
            ? choice.message.content.map((item) => String(item?.text || '')).join('')
            : '';
      return {
        text: content,
        tool_calls: normalizeOpenAiToolCalls(choice?.message?.tool_calls),
        finish_reason: toStringValue(choice?.finish_reason),
        usage: payload?.usage && typeof payload.usage === 'object' ? payload.usage : {},
      };
    } catch (error) {
      lastError = error;
      if (!hasFallback) {
        throw error;
      }
    }
  }
  throw lastError || new Error('LLM request failed');
}

async function streamModelCompletion({
  baseUrl = '',
  apiToken = '',
  fallbackBaseUrl = '',
  fallbackApiToken = '',
  model = '',
  messages = [],
  tools = [],
  toolChoice = 'auto',
  maxTokens = 1200,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
  signal = null,
  onToken = async () => {},
  onToolCalls = async () => {},
} = {}) {
  const candidates = buildEndpointCandidates({
    baseUrl,
    apiToken,
    fallbackBaseUrl,
    fallbackApiToken,
  });
  if (!candidates.length) {
    throw new Error('serverBaseUrl is required');
  }
  let lastError = null;
  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    const hasFallback = index < candidates.length - 1;
    try {
      const response = await fetch(candidate.mode === 'proxy'
        ? buildRequestTarget(candidate.baseUrl, '/v1/llm/chat_completions/stream')
        : buildRequestTarget(candidate.baseUrl, '/v1/chat/completions'), {
        method: 'POST',
        headers: buildHeaders(candidate.apiToken),
        body: JSON.stringify({
          model: toStringValue(model),
          messages: Array.isArray(messages) ? messages : [],
          ...(Array.isArray(tools) && tools.length > 0 ? { tools, tool_choice: toolChoice || 'auto' } : {}),
          max_tokens: Math.max(128, Number(maxTokens || 1200)),
          temperature: Number.isFinite(Number(temperature)) ? Number(temperature) : 0.2,
          ...(candidate.mode === 'proxy'
            ? toStringValue(responseFormat) && toStringValue(responseFormat).toLowerCase() !== 'text'
              ? { response_format: toStringValue(responseFormat) }
              : {}
            : responseFormat === 'json_object'
              ? { response_format: { type: 'json_object' } }
              : {}),
          ...(candidate.mode === 'openai' ? { stream: true } : {}),
          stop: Array.isArray(stop) ? stop.map((item) => toStringValue(item)).filter(Boolean) : [],
        }),
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
        if (hasFallback && shouldRetryWithFallback(response.status, payload, text)) {
          continue;
        }
        throw new Error(text || `HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let aggregated = '';
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
            const deltaToolCalls = Array.isArray(choice?.delta?.tool_calls) ? choice.delta.tool_calls : [];
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
            if (deltaToolCalls.length > 0) {
              void onToolCalls(normalizeOpenAiToolCalls(openAiToolCalls));
            }
            if (choice?.finish_reason) {
              donePayload = {
                text: aggregated,
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
        return {
          text: typeof donePayload.text === 'string' ? donePayload.text : aggregated,
          tool_calls: normalizeOpenAiToolCalls(donePayload.tool_calls || openAiToolCalls),
          finish_reason: toStringValue(donePayload.finish_reason),
          usage: donePayload.usage && typeof donePayload.usage === 'object' ? donePayload.usage : {},
        };
      }

      return {
        text: aggregated,
        tool_calls: normalizeOpenAiToolCalls(openAiToolCalls),
        finish_reason: '',
        usage: {},
      };
    } catch (error) {
      lastError = error;
      if (!hasFallback) {
        throw error;
      }
    }
  }
  throw lastError || new Error('LLM stream request failed');
}

module.exports = {
  callModelCompletion,
  streamModelCompletion,
  resolveMode,
};
