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

function normalizeWikiId(value = '') {
  const raw = toStringValue(value).toLowerCase();
  if (!raw) return '';
  return raw.replace(/[^a-z0-9._-]+/g, '-').replace(/^[._-]+|[._-]+$/g, '').slice(0, 80);
}

function deriveWikiId({ wikiId = '', workspacePath = '' } = {}) {
  const explicit = normalizeWikiId(wikiId);
  if (explicit) return explicit;
  const normalizedPath = toStringValue(workspacePath).replace(/\\/g, '/').replace(/\/+$/, '');
  const tail = normalizedPath.split('/').filter(Boolean).pop() || 'shared';
  return normalizeWikiId(tail) || 'shared';
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

async function backendRequest({
  baseUrl = '',
  apiToken = '',
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
    headers: buildHeaders(apiToken),
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

async function bootstrapBackendWiki({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
  name = '',
  description = '',
  overwrite = false,
  userId = 'desktop-local',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/bootstrap',
    method: 'POST',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
      name: toStringValue(name),
      description: toStringValue(description),
      overwrite: Boolean(overwrite),
      user_id: toStringValue(userId),
    },
  });
}

async function searchBackendWiki({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
  query = '',
  limit = 12,
  includeContent = false,
  kind = '',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/search',
    method: 'POST',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
      query: toStringValue(query),
      limit: clampInt(limit, 1, 50, 12),
      include_content: Boolean(includeContent),
      kind: toStringValue(kind),
    },
  });
}

async function getBackendWikiContext({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/context',
    method: 'POST',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
    },
  });
}

async function readBackendWikiPage({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
  path = '',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/page/read',
    method: 'POST',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
      path: toStringValue(path),
    },
  });
}

async function writeBackendWikiPage({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
  path = '',
  content = '',
  title = '',
  kind = '',
  userId = 'desktop-local',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/page',
    method: 'PUT',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
      path: toStringValue(path),
      content: String(content || ''),
      title: toStringValue(title),
      kind: toStringValue(kind),
      user_id: toStringValue(userId),
    },
  });
}

async function appendBackendWikiLog({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  workspacePath = '',
  title = '',
  bodyLines = [],
  kind = 'update',
  userId = 'desktop-local',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/log/append',
    method: 'POST',
    body: {
      wiki_id: deriveWikiId({ wikiId, workspacePath }),
      title: toStringValue(title),
      body_lines: Array.isArray(bodyLines) ? bodyLines.map((item) => toStringValue(item)).filter(Boolean) : [],
      kind: toStringValue(kind || 'update'),
      user_id: toStringValue(userId),
    },
  });
}

module.exports = {
  appendBackendWikiLog,
  bootstrapBackendWiki,
  collectBackendEvidence,
  deriveWikiId,
  getBackendWikiContext,
  readBackendWikiPage,
  searchBackendWiki,
  writeBackendWikiPage,
};
