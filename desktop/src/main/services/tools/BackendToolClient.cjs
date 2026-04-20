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

async function searchBackendWiki({
  baseUrl = '',
  wikiId = '',
  query = '',
  limit = 12,
  includeContent = false,
  kind = '',
} = {}) {
  return backendRequest({
    baseUrl,
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
  wikiId = '',
} = {}) {
  return backendRequest({
    baseUrl,
    requestPath: '/v1/wiki/context',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
    },
  });
}

async function readBackendWikiPage({
  baseUrl = '',
  wikiId = '',
  path = '',
} = {}) {
  return backendRequest({
    baseUrl,
    requestPath: '/v1/wiki/page/read',
    method: 'POST',
    body: {
      wiki_id: resolveWikiId(wikiId),
      path: toStringValue(path),
    },
  });
}

module.exports = {
  getBackendWikiContext,
  readBackendWikiPage,
  searchBackendWiki,
};
