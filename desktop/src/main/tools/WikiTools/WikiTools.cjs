const { defineLocalTool } = require('../../Tool.cjs');
const {
  getBackendWikiContext,
  lintBackendWiki,
  readBackendWikiPage,
  rebuildBackendWikiIndex,
  searchBackendWiki,
  writebackBackendWikiPage,
  writeBackendWikiPage,
} = require('../../services/tools/BackendToolClient.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  arraySchema,
} = require('../shared/schema.cjs');

function backendWikiContext(context = {}) {
  const backendConfig = typeof context.getBackendConfig === 'function'
    ? context.getBackendConfig()
    : {};
  return {
    baseUrl: toStringValue(backendConfig?.baseUrl || backendConfig?.serverBaseUrl),
    apiToken: toStringValue(backendConfig?.apiToken || backendConfig?.serverApiToken),
    wikiId: toStringValue(backendConfig?.wikiId),
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
    score: Number(item?.score || 0),
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
    searchHint: 'search the backend-managed LLM wiki',
    laneAffinity: ['read', 'review', 'flow'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['discovery'],
    async description() {
      return 'Search the backend LLM wiki by title, path, summary, or content.';
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
          apiToken: backend.apiToken,
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
          results: pages.slice(0, Math.max(1, Math.min(Number(input?.limit || 8), 20))).map((item) => normalizeSearchResult(item)),
        };
      }
      const result = await searchBackendWiki({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        query,
        limit: Number(input?.limit || 12),
        includeContent: Boolean(input?.include_content),
        kind: toStringValue(input?.kind),
      });
      return {
        ok: true,
        wiki_id: toStringValue(result?.wiki_id),
        query,
        total: Number(result?.total || 0),
        results: Array.isArray(result?.results) ? result.results.map((item) => normalizeSearchResult(item)) : [],
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
    searchHint: 'read one markdown page from the backend LLM wiki',
    laneAffinity: ['read', 'review', 'flow'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['inspection'],
    async description() {
      return 'Read a single markdown page from the backend LLM wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await readBackendWikiPage({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
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
      };
    },
  });
}

function WikiWriteTool() {
  return defineLocalTool({
    name: 'wiki_write',
    aliases: ['shared_wiki_write', 'WikiWrite'],
    kind: 'write',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
      path: stringSchema('Wiki page path such as pages/topics/auth-model.md'),
      content: stringSchema('Full markdown content to store'),
      title: stringSchema('Optional explicit title'),
      kind: stringSchema('Optional page kind'),
    }, ['path', 'content']),
    searchHint: 'create or update a markdown page in the backend LLM wiki',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Write or replace a markdown page in the backend LLM wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await writeBackendWikiPage({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        path: toStringValue(input?.path),
        content: String(input?.content || ''),
        title: toStringValue(input?.title),
        kind: toStringValue(input?.kind),
      });
      return {
        ok: true,
        wiki_id: toStringValue(page?.wiki_id),
        path: toStringValue(page?.path),
        title: toStringValue(page?.title),
        kind: toStringValue(page?.kind),
        summary: toStringValue(page?.summary),
        updated_at: toStringValue(page?.updated_at),
        version: Number(page?.version || 0),
      };
    },
  });
}

function WikiRebuildIndexTool() {
  return defineLocalTool({
    name: 'wiki_rebuild_index',
    aliases: ['WikiRebuildIndex'],
    kind: 'write',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
    }),
    searchHint: 'rebuild the backend wiki index page',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Rebuild index.md for the backend LLM wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) return wikiBackendUnavailable();
      const page = await rebuildBackendWikiIndex({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
      });
      return {
        ok: true,
        wiki_id: toStringValue(page?.wiki_id),
        path: toStringValue(page?.path),
        title: toStringValue(page?.title),
        updated_at: toStringValue(page?.updated_at),
      };
    },
  });
}

function WikiLintTool() {
  return defineLocalTool({
    name: 'wiki_lint',
    aliases: ['WikiLint'],
    kind: 'read',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
      repair: booleanSchema('Whether to run low-risk repair actions'),
    }),
    searchHint: 'lint the backend wiki for broken links, orphan pages, and missing provenance',
    laneAffinity: ['read', 'review', 'change'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Lint the backend LLM wiki and optionally repair low-risk issues.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) return wikiBackendUnavailable();
      const result = await lintBackendWiki({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        repair: Boolean(input?.repair),
      });
      return {
        ok: true,
        wiki_id: toStringValue(result?.wiki_id),
        repair: Boolean(result?.repair),
        finding_count: Number(result?.finding_count || 0),
        findings: Array.isArray(result?.findings) ? result.findings : [],
      };
    },
  });
}

function WikiWritebackTool() {
  return defineLocalTool({
    name: 'wiki_writeback',
    aliases: ['WikiWriteback'],
    kind: 'write',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional wiki id override'),
      query: stringSchema('Original query to save'),
      answer: stringSchema('Answer markdown to persist'),
      title: stringSchema('Optional page title'),
      category: stringSchema('Target category such as analysis or decision'),
      path: stringSchema('Optional explicit output path'),
      source_paths: arraySchema(stringSchema('Related wiki paths'), 'Related wiki source paths'),
    }, ['query', 'answer']),
    searchHint: 'save a useful answer back into the backend LLM wiki',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Persist a query answer as a curated page in the backend LLM wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) return wikiBackendUnavailable();
      const result = await writebackBackendWikiPage({
        baseUrl: backend.baseUrl,
        apiToken: backend.apiToken,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        query: toStringValue(input?.query),
        answer: String(input?.answer || ''),
        title: toStringValue(input?.title),
        category: toStringValue(input?.category || 'analysis'),
        path: toStringValue(input?.path),
        sourcePaths: Array.isArray(input?.source_paths) ? input.source_paths : [],
      });
      const page = result?.page && typeof result.page === 'object' ? result.page : {};
      return {
        ok: true,
        wiki_id: toStringValue(page?.wiki_id),
        path: toStringValue(page?.path),
        title: toStringValue(page?.title),
        kind: toStringValue(page?.kind),
        updated_at: toStringValue(page?.updated_at),
      };
    },
  });
}

module.exports = {
  WikiLintTool,
  WikiReadTool,
  WikiRebuildIndexTool,
  WikiSearchTool,
  WikiWritebackTool,
  WikiWriteTool,
};
