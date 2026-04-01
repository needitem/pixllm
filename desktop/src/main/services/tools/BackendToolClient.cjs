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

function clampInt(value, low, high, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(low, Math.min(high, Math.floor(parsed)));
}

async function collectBackendEvidence({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  userId = 'desktop-local',
  query = '',
  mode = 'code',
  responseType = 'api_lookup',
  topK = 8,
  limit = 8,
  maxChars = 12000,
  maxLineSpan = 200,
} = {}) {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  if (!normalizedBaseUrl) {
    throw new Error('Backend API base URL is not configured');
  }

  const response = await fetch(
    buildRequestTarget(normalizedBaseUrl, '/v1/tool-api/orchestrate/collect_evidence'),
    {
      method: 'POST',
      headers: buildHeaders(apiToken),
      body: JSON.stringify({
        session_id: toStringValue(sessionId) || 'desktop-local-session',
        user_id: toStringValue(userId) || 'desktop-local',
        query: toStringValue(query),
        mode: toStringValue(mode || 'code') || 'code',
        response_type: toStringValue(responseType || 'api_lookup') || 'api_lookup',
        top_k: clampInt(topK, 1, 50, 8),
        limit: clampInt(limit, 1, 50, 8),
        max_chars: clampInt(maxChars, 200, 12000, 12000),
        max_line_span: clampInt(maxLineSpan, 1, 500, 200),
      }),
    },
  );

  const rawText = await response.text();
  let payload = null;
  try {
    payload = JSON.parse(rawText);
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
    throw new Error(toStringValue(payload?.error?.message) || 'Invalid backend evidence response');
  }

  return payload.data && typeof payload.data === 'object' ? payload.data : {};
}

module.exports = {
  collectBackendEvidence,
};
