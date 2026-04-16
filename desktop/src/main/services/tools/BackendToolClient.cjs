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

function resolveWikiId(wikiId = '') {
  const explicit = normalizeWikiId(wikiId);
  if (explicit) return explicit;
  return 'engine';
}

async function lookupBackendWikiEvidence({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  userId = 'desktop-local',
  query = '',
  responseType = 'api_lookup',
  workflowFirst = false,
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
    buildRequestTarget(normalizedBaseUrl, '/v1/tool-api/orchestrate/lookup_sources_and_code'),
    {
      method: 'POST',
      headers: buildHeaders(apiToken),
      body: JSON.stringify({
        session_id: toStringValue(sessionId) || 'desktop-local-session',
        user_id: toStringValue(userId) || 'desktop-local',
        query: toStringValue(query),
        response_type: toStringValue(responseType || 'api_lookup') || 'api_lookup',
        workflow_first: Boolean(workflowFirst),
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

async function getBackendToolUserContext({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  userId = 'desktop-local',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/tool-api/user/acl/get_user_context',
    method: 'POST',
    body: {
      session_id: toStringValue(sessionId) || 'desktop-local-session',
      user_id: toStringValue(userId) || 'desktop-local',
    },
  });
}

async function listBackendRepoFiles({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  glob = '**/*',
  limit = 20,
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/tool-api/code/list_repo_files',
    method: 'POST',
    body: {
      session_id: toStringValue(sessionId) || 'desktop-local-session',
      glob: toStringValue(glob) || '**/*',
      limit: clampInt(limit, 1, 500, 20),
    },
  });
}

async function readBackendCode({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  path = '',
  startLine = 1,
  endLine = 120,
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/tool-api/code/read_code',
    method: 'POST',
    body: {
      session_id: toStringValue(sessionId) || 'desktop-local-session',
      path: toStringValue(path),
      start_line: clampInt(startLine, 1, 200000, 1),
      end_line: clampInt(endLine, 1, 200000, 120),
    },
  });
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

async function searchBackendWiki({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
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
      wiki_id: resolveWikiId(wikiId),
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
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/context',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
    },
  });
}

async function readBackendWikiPage({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  path = '',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/page/read',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
      path: toStringValue(path),
    },
  });
}

async function writeBackendWikiPage({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
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
      wiki_id: resolveWikiId(wikiId),
      path: toStringValue(path),
      content: String(content || ''),
      title: toStringValue(title),
      kind: toStringValue(kind),
      user_id: toStringValue(userId),
    },
  });
}

async function rebuildBackendWikiIndex({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/index/rebuild',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
    },
  });
}

async function lintBackendWiki({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  repair = false,
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/lint',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
      repair: Boolean(repair),
    },
  });
}

async function writebackBackendWikiPage({
  baseUrl = '',
  apiToken = '',
  wikiId = '',
  query = '',
  answer = '',
  title = '',
  category = 'analysis',
  path = '',
  sourcePaths = [],
} = {}) {
  return backendRequest({
    baseUrl,
    apiToken,
    requestPath: '/v1/wiki/writeback',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
      query: toStringValue(query),
      answer: String(answer || ''),
      title: toStringValue(title),
      category: toStringValue(category || 'analysis'),
      path: toStringValue(path),
      source_paths: Array.isArray(sourcePaths) ? sourcePaths.map((item) => toStringValue(item)).filter(Boolean) : [],
    },
  });
}

module.exports = {
  getBackendWikiContext,
  getBackendToolUserContext,
  lintBackendWiki,
  listBackendRepoFiles,
  lookupBackendWikiEvidence,
  readBackendCode,
  readBackendWikiPage,
  rebuildBackendWikiIndex,
  searchBackendWiki,
  writebackBackendWikiPage,
  writeBackendWikiPage,
};
