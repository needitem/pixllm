const { defineLocalTool } = require('../../Tool.cjs');
const {
  getBackendWikiContext,
  readBackendWikiPage,
  searchBackendWiki,
} = require('../../services/tools/BackendToolClient.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
} = require('../shared/schema.cjs');

function backendWikiContext(context = {}) {
  const backendConfig = typeof context.getBackendConfig === 'function'
    ? context.getBackendConfig()
    : {};
  return {
    baseUrl: toStringValue(backendConfig?.baseUrl || backendConfig?.serverBaseUrl),
    wikiId: toStringValue(backendConfig?.wikiId),
    llmBaseUrl: toStringValue(backendConfig?.llmBaseUrl || backendConfig?.baseUrl || backendConfig?.serverBaseUrl),
    fallbackBaseUrl: toStringValue(backendConfig?.serverBaseUrl || backendConfig?.baseUrl),
    model: toStringValue(backendConfig?.model),
  };
}

function wikiBackendUnavailable() {
  return {
    ok: false,
    error: 'backend_wiki_unavailable',
    message: 'Backend API base URL is not configured. Set serverBaseUrl before using wiki tools.',
  };
}

function normalizeSearchResult(item = {}) {
  return {
    path: toStringValue(item?.path),
    title: toStringValue(item?.title),
    kind: toStringValue(item?.kind),
    summary: toStringValue(item?.summary),
    excerpt: toStringValue(item?.excerpt),
    content: toStringValue(item?.content),
    updated_at: toStringValue(item?.updated_at),
    rank: Number(item?.rank || 0),
  };
}

function uniqStrings(items = [], limit = 8) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const normalized = toStringValue(item);
    if (!normalized) continue;
    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(normalized);
    if (output.length >= limit) break;
  }
  return output;
}

function hasHangul(value = '') {
  return /[\u3131-\u318E\uAC00-\uD7A3]/.test(String(value || ''));
}

function normalizeReadPage(item = {}) {
  return {
    path: toStringValue(item?.path),
    title: toStringValue(item?.title),
    kind: toStringValue(item?.kind),
    summary: toStringValue(item?.summary),
    content: toStringValue(item?.content),
    updated_at: toStringValue(item?.updated_at),
    relation: toStringValue(item?.relation),
  };
}

function WikiSearchTool() {
  return defineLocalTool({
    name: 'wiki_search',
    aliases: ['shared_wiki_search', 'WikiSearch'],
    kind: 'read',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
      query: stringSchema('Search query. Leave empty to inspect coordination pages'),
      limit: integerSchema('Maximum number of results', { minimum: 1 }),
      include_content: booleanSchema('Include full content in results'),
      kind: stringSchema('Optional page kind filter'),
    }),
    searchHint: 'search the backend-managed wiki',
    laneAffinity: ['read', 'review'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['discovery'],
    async description() {
      return 'Search the backend wiki by title, path, summary, or content.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const query = toStringValue(input?.query);
      if (!query) {
        const wikiContext = await getBackendWikiContext({
          baseUrl: backend.baseUrl,
          wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        });
        const pages = Array.isArray(wikiContext?.coordination_pages)
          ? wikiContext.coordination_pages
          : Array.isArray(wikiContext?.pages)
            ? wikiContext.pages
            : [];
        return {
          ok: true,
          wiki_id: toStringValue(wikiContext?.wiki?.id),
          total: pages.length,
          results: pages
            .slice(0, Math.max(1, Math.min(Number(input?.limit || 8), 20)))
            .map((item) => normalizeSearchResult(item)),
        };
      }
      const requestedKind = toStringValue(input?.kind);
      const workflowFirst = !requestedKind || requestedKind === 'workflow';
      const mergedResults = [];
      const seenPaths = new Set();
      const appendResults = (items = []) => {
        for (const item of Array.isArray(items) ? items : []) {
          const normalized = normalizeSearchResult(item);
          const key = toStringValue(normalized.path).toLowerCase();
          if (!key || seenPaths.has(key)) continue;
          seenPaths.add(key);
          mergedResults.push(normalized);
          if (mergedResults.length >= Number(input?.limit || 12)) {
            break;
          }
        }
      };

      if (workflowFirst) {
        const workflowResult = await searchBackendWiki({
          baseUrl: backend.baseUrl,
          wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
          query,
          limit: Number(input?.limit || 12),
          includeContent: Boolean(input?.include_content),
          kind: 'workflow',
        });
        appendResults(workflowResult?.results);
        if (mergedResults.length > 0) {
          return {
            ok: true,
            wiki_id: toStringValue(workflowResult?.wiki_id) || toStringValue(input?.wiki_id) || backend.wikiId,
            query,
            total: mergedResults.length,
            results: mergedResults,
          };
        }
      }

      const fallbackResult = await searchBackendWiki({
        baseUrl: backend.baseUrl,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        query,
        limit: Number(input?.limit || 12),
        includeContent: Boolean(input?.include_content),
        kind: requestedKind,
      });
      appendResults(fallbackResult?.results);
      return {
        ok: true,
        wiki_id: toStringValue(fallbackResult?.wiki_id),
        query,
        total: mergedResults.length > 0 ? mergedResults.length : Number(fallbackResult?.total || 0),
        results: mergedResults,
      };
    },
  });
}

function WikiReadTool() {
  return defineLocalTool({
    name: 'wiki_read',
    aliases: ['shared_wiki_read', 'wiki_open', 'WikiRead'],
    kind: 'read',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
      path: stringSchema('Wiki page path such as SCHEMA.md or pages/home.md'),
    }, ['path']),
    searchHint: 'read one markdown page from the backend wiki',
    laneAffinity: ['read', 'review'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['inspection'],
    async description() {
      return 'Read a single markdown page from the backend wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await readBackendWikiPage({
        baseUrl: backend.baseUrl,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        path: toStringValue(input?.path),
      });
      return {
        ok: true,
        wiki_id: toStringValue(page?.wiki_id),
        path: toStringValue(page?.path),
        title: toStringValue(page?.title),
        kind: toStringValue(page?.kind),
        content: String(page?.content || ''),
        summary: toStringValue(page?.summary),
        updated_at: toStringValue(page?.updated_at),
        related_pages: Array.isArray(page?.related_pages) ? page.related_pages.map((item) => normalizeReadPage(item)) : [],
        related_paths: Array.isArray(page?.related_paths) ? page.related_paths.map((item) => toStringValue(item)).filter(Boolean) : [],
      };
    },
  });
}

module.exports = {
  WikiReadTool,
  WikiSearchTool,
};
