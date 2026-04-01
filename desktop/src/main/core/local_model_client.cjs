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
  model = '',
  messages = [],
  tools = [],
  toolChoice = 'auto',
  maxTokens = 1200,
  temperature = 0.2,
  responseFormat = 'text',
  stop = [],
} = {}) {
  const normalizedBase = toStringValue(baseUrl).replace(/\/$/, '');
  if (!normalizedBase) {
    throw new Error('serverBaseUrl is required');
  }
  const mode = resolveMode(normalizedBase);
  const response = await fetch(
    mode === 'proxy'
      ? `${normalizedBase}/v1/llm/chat_completions`
      : `${normalizedBase}/v1/chat/completions`,
    {
    method: 'POST',
    headers: buildHeaders(apiToken),
    body: JSON.stringify({
      model: toStringValue(model),
      messages: Array.isArray(messages) ? messages : [],
      ...(Array.isArray(tools) && tools.length > 0 ? { tools, tool_choice: toolChoice || 'auto' } : {}),
      max_tokens: Math.max(128, Number(maxTokens || 1200)),
      temperature: Number.isFinite(Number(temperature)) ? Number(temperature) : 0.2,
      ...(mode === 'proxy'
        ? toStringValue(responseFormat) && toStringValue(responseFormat).toLowerCase() !== 'text'
          ? { response_format: toStringValue(responseFormat) }
          : {}
        : responseFormat === 'json_object'
          ? { response_format: { type: 'json_object' } }
          : {}),
      stop: Array.isArray(stop) ? stop.map((item) => toStringValue(item)).filter(Boolean) : [],
    }),
  });
  const text = await response.text();
  let payload = null;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error(text || `HTTP ${response.status}`);
  }
  if (mode === 'proxy') {
    if (!response.ok || !payload?.ok) {
      throw new Error(payload?.error?.message || payload?.message || `HTTP ${response.status}`);
    }
    return payload.data || {};
  }
  if (!response.ok) {
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
}

async function streamModelCompletion({
  baseUrl = '',
  apiToken = '',
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
} = {}) {
  const normalizedBase = toStringValue(baseUrl).replace(/\/$/, '');
  if (!normalizedBase) {
    throw new Error('serverBaseUrl is required');
  }
  const mode = resolveMode(normalizedBase);

  const response = await fetch(mode === 'proxy'
    ? `${normalizedBase}/v1/llm/chat_completions/stream`
    : `${normalizedBase}/v1/chat/completions`, {
    method: 'POST',
    headers: buildHeaders(apiToken),
    body: JSON.stringify({
      model: toStringValue(model),
      messages: Array.isArray(messages) ? messages : [],
      ...(Array.isArray(tools) && tools.length > 0 ? { tools, tool_choice: toolChoice || 'auto' } : {}),
      max_tokens: Math.max(128, Number(maxTokens || 1200)),
      temperature: Number.isFinite(Number(temperature)) ? Number(temperature) : 0.2,
      ...(mode === 'proxy'
        ? toStringValue(responseFormat) && toStringValue(responseFormat).toLowerCase() !== 'text'
          ? { response_format: toStringValue(responseFormat) }
          : {}
        : responseFormat === 'json_object'
          ? { response_format: { type: 'json_object' } }
          : {}),
      ...(mode === 'openai' ? { stream: true } : {}),
      stop: Array.isArray(stop) ? stop.map((item) => toStringValue(item)).filter(Boolean) : [],
    }),
    signal: signal || undefined,
  });

  if (!response.ok || !response.body) {
    const text = await response.text();
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
      if (mode === 'openai') {
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
          const index = Number(deltaToolCall?.index || 0);
          if (!openAiToolCalls[index]) {
            openAiToolCalls[index] = {
              id: '',
              name: '',
              arguments: '',
            };
          }
          if (typeof deltaToolCall?.id === 'string') {
            openAiToolCalls[index].id = deltaToolCall.id;
          }
          const fn = deltaToolCall?.function && typeof deltaToolCall.function === 'object'
            ? deltaToolCall.function
            : {};
          if (typeof fn?.name === 'string' && fn.name) {
            openAiToolCalls[index].name = fn.name;
          }
          if (typeof fn?.arguments === 'string' && fn.arguments) {
            openAiToolCalls[index].arguments += fn.arguments;
          }
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
}

module.exports = {
  callModelCompletion,
  streamModelCompletion,
  resolveMode,
};
