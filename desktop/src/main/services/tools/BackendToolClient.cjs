function toStringValue(value) {
  return String(value || '').trim();
}

function buildHeaders() {
  return {
    'Content-Type': 'application/json',
  };
}

function normalizeBaseUrl(baseUrl = '') {
  return toStringValue(baseUrl).replace(/\/$/, '');
}

function buildRequestTarget(baseUrl = '', requestPath = '') {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  const normalizedPath = toStringValue(requestPath);
  if (/(?:^|\/)api\/v1$/i.test(normalizedBaseUrl) && /^\/v1\//i.test(normalizedPath)) {
    return `${normalizedBaseUrl}${normalizedPath.slice(3)}`;
  }
  return `${normalizedBaseUrl}${normalizedPath}`;
}

function clampInt(value, low, high, defaultValue) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return defaultValue;
  return Math.max(low, Math.min(high, Math.floor(parsed)));
}

async function backendRequest({
  baseUrl = '',
  requestPath = '',
  method = 'POST',
  body = null,
} = {}) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  if (!normalizedBaseUrl) {
    throw new Error('Backend API base URL is not configured');
  }

  const response = await fetch(buildRequestTarget(normalizedBaseUrl, requestPath), {
    method,
    headers: buildHeaders(),
    body: body === null ? null : JSON.stringify(body),
  });

  const rawText = await response.text();
  let payload = null;
  try {
    payload = rawText ? JSON.parse(rawText) : null;
  } catch {
    throw new Error(rawText || `HTTP ${response.status}`);
  }

  if (!response.ok) {
    throw new Error(
      toStringValue(payload?.error?.message)
      || toStringValue(payload?.message)
      || `HTTP ${response.status}`,
    );
  }
  if (!payload || payload.ok !== true) {
    throw new Error(toStringValue(payload?.error?.message) || 'Invalid backend response');
  }
  return payload.data && typeof payload.data === 'object' ? payload.data : {};
}

async function answerBackendSource({
  baseUrl = '',
  prompt = '',
  llmBaseUrl = '',
  model = '',
  sessionId = '',
  maxTokens = 4096,
  maxLlmCalls = 12,
  enableThinking = false,
} = {}) {
  return backendRequest({
    baseUrl,
    requestPath: '/v1/source/answer',
    method: 'POST',
    body: {
      prompt: toStringValue(prompt),
      llm_base_url: toStringValue(llmBaseUrl),
      model: toStringValue(model),
      session_id: toStringValue(sessionId),
      max_tokens: clampInt(maxTokens, 256, 16384, 4096),
      max_llm_calls: clampInt(maxLlmCalls, 1, 40, 12),
      enable_thinking: Boolean(enableThinking),
    },
  });
}

module.exports = {
  answerBackendSource,
};
