const { defineLocalTool } = require('../../Tool.cjs');
const {
  appendBackendWikiLog,
  bootstrapBackendWiki,
  deriveWikiId,
  getBackendWikiContext,
  readBackendWikiPage,
  searchBackendWiki,
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
    wikiId: toStringValue(backendConfig?.sharedWikiId || backendConfig?.wikiId),
    workspacePath: toStringValue(context.workspacePath),
  };
}

function wikiBackendUnavailable() {
  return {
    ok: false,
    error: 'backend_wiki_unavailable',
    message: 'Backend API base URL is not configured. Set serverBaseUrl before using shared wiki tools.',
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

function WikiBootstrapTool() {
  return defineLocalTool({
    name: 'wiki_bootstrap',
    aliases: ['wiki_init', 'wiki_scaffold', 'WikiBootstrap'],
    kind: 'write',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional shared wiki id override'),
      name: stringSchema('Optional human-readable shared wiki name'),
      description: stringSchema('Optional shared wiki description'),
      overwrite: booleanSchema('Overwrite existing coordination pages'),
    }),
    searchHint: 'initialize a backend-managed shared wiki for multiple users',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Create the shared backend wiki scaffold with schema, index, log, pages, and raw source folders.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const result = await bootstrapBackendWiki({
        ...backend,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        name: toStringValue(input?.name),
        description: toStringValue(input?.description),
        overwrite: Boolean(input?.overwrite),
      });
      const resolvedWikiId = deriveWikiId({
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        workspacePath: backend.workspacePath,
      });
      return {
        ok: true,
        wiki_id: resolvedWikiId,
        wiki_name: toStringValue(result?.wiki?.name || resolvedWikiId),
        created_paths: Array.isArray(result?.created_paths) ? result.created_paths : [],
        updated_paths: Array.isArray(result?.updated_paths) ? result.updated_paths : [],
        skipped_paths: Array.isArray(result?.skipped_paths) ? result.skipped_paths : [],
        message: `Shared wiki ${resolvedWikiId} is ready on the backend.`,
      };
    },
  });
}

function WikiSearchTool() {
  return defineLocalTool({
    name: 'wiki_search',
    aliases: ['shared_wiki_search', 'WikiSearch'],
    kind: 'read',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional shared wiki id override'),
      query: stringSchema('Search query. Leave empty to inspect coordination pages'),
      limit: integerSchema('Maximum number of results', { minimum: 1 }),
      include_content: booleanSchema('Include full content in results'),
      kind: stringSchema('Optional page kind filter'),
    }),
    searchHint: 'search the backend-managed shared wiki',
    laneAffinity: ['read', 'review', 'flow'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['discovery'],
    async description() {
      return 'Search the shared backend wiki by title, path, summary, or content.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const query = toStringValue(input?.query);
      if (!query) {
        const wikiContext = await getBackendWikiContext({
          ...backend,
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
        ...backend,
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
      wiki_id: stringSchema('Optional shared wiki id override'),
      path: stringSchema('Wiki page path such as SCHEMA.md or pages/home.md'),
    }, ['path']),
    searchHint: 'read one markdown page from the shared backend wiki',
    laneAffinity: ['read', 'review', 'flow'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: () => ['inspection'],
    async description() {
      return 'Read a single markdown page from the shared backend wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await readBackendWikiPage({
        ...backend,
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
      wiki_id: stringSchema('Optional shared wiki id override'),
      path: stringSchema('Wiki page path such as pages/topics/auth-model.md'),
      content: stringSchema('Full markdown content to store'),
      title: stringSchema('Optional explicit title'),
      kind: stringSchema('Optional page kind'),
    }, ['path', 'content']),
    searchHint: 'create or update a markdown page in the shared backend wiki',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Write or replace a markdown page in the shared backend wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await writeBackendWikiPage({
        ...backend,
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

function WikiAppendLogTool() {
  return defineLocalTool({
    name: 'wiki_append_log',
    aliases: ['shared_wiki_log', 'WikiAppendLog'],
    kind: 'write',
    inputSchema: objectSchema({
      wiki_id: stringSchema('Optional shared wiki id override'),
      title: stringSchema('Short log title'),
      kind: stringSchema('Log entry kind such as ingest, query, lint, or update'),
      body_lines: arraySchema(stringSchema('Log bullet line'), 'Log bullet lines'),
    }, ['title']),
    searchHint: 'append an operation entry to the shared backend wiki log',
    laneAffinity: ['change', 'review'],
    isReadOnly: () => false,
    isConcurrencySafe: () => false,
    async description() {
      return 'Append a structured entry to log.md in the shared backend wiki.';
    },
    async call(input, context) {
      const backend = backendWikiContext(context);
      if (!backend.baseUrl) {
        return wikiBackendUnavailable();
      }
      const page = await appendBackendWikiLog({
        ...backend,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        title: toStringValue(input?.title),
        kind: toStringValue(input?.kind || 'update'),
        bodyLines: Array.isArray(input?.body_lines) ? input.body_lines : [],
      });
      return {
        ok: true,
        wiki_id: toStringValue(page?.wiki_id),
        path: toStringValue(page?.path),
        updated_at: toStringValue(page?.updated_at),
        version: Number(page?.version || 0),
      };
    },
  });
}

module.exports = {
  WikiAppendLogTool,
  WikiBootstrapTool,
  WikiReadTool,
  WikiSearchTool,
  WikiWriteTool,
};
