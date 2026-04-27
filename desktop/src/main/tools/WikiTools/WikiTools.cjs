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

function normalizeEvidencePage(item = {}) {
  return {
    path: toStringValue(item?.path),
    title: toStringValue(item?.title),
    kind: toStringValue(item?.kind),
    relation: toStringValue(item?.relation),
    summary: toStringValue(item?.summary),
    content: String(item?.content || ''),
    workflow_family: toStringValue(item?.workflow_family),
    output_shape: toStringValue(item?.output_shape),
    required_symbols: Array.isArray(item?.required_symbols)
      ? item.required_symbols.map((value) => toStringValue(value)).filter(Boolean)
      : [],
  };
}

function normalizeSourceRef(item = {}) {
  return {
    path: toStringValue(item?.path),
    line_range: toStringValue(item?.line_range),
  };
}

function normalizeSourceSnippet(item = {}) {
  return {
    path: toStringValue(item?.path),
    line_range: toStringValue(item?.line_range),
    role: toStringValue(item?.role),
    content: String(item?.content || ''),
  };
}

function normalizeGroundingFact(item = {}) {
  return {
    symbol: toStringValue(item?.symbol),
    declaration: toStringValue(item?.declaration),
    source_refs: Array.isArray(item?.source_refs)
      ? item.source_refs.map((value) => normalizeSourceRef(value)).filter((value) => value.path)
      : [],
    source_snippets: Array.isArray(item?.source_snippets)
      ? item.source_snippets.map((value) => normalizeSourceSnippet(value)).filter((value) => value.path || value.content)
      : [],
  };
}

function normalizeAnswerGrounding(item = {}) {
  if (!item || typeof item !== 'object' || Array.isArray(item)) {
    return null;
  }
  return {
    must: Array.isArray(item?.must) ? item.must.map((value) => toStringValue(value)).filter(Boolean) : [],
    should: Array.isArray(item?.should) ? item.should.map((value) => toStringValue(value)).filter(Boolean) : [],
    may: Array.isArray(item?.may) ? item.may.map((value) => toStringValue(value)).filter(Boolean) : [],
    facts: Array.isArray(item?.facts)
      ? item.facts.map((value) => normalizeGroundingFact(value)).filter((value) => value.symbol || value.declaration)
      : [],
  };
}

function compactSymbol(value = '') {
  return toStringValue(value).toLowerCase().replace(/[^a-z0-9_.]+/g, '');
}

function requiredSymbolRank(symbol = '', requiredSymbols = []) {
  const compact = compactSymbol(symbol);
  if (!compact) {
    return 9999;
  }
  const index = (Array.isArray(requiredSymbols) ? requiredSymbols : [])
    .map((item) => compactSymbol(item))
    .findIndex((item) => item && (compact === item || compact.endsWith(`.${item}`)));
  return index >= 0 ? index : 9999;
}

function prioritizeEvidencePack(pack = {}) {
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    return null;
  }
  const requiredSymbols = Array.isArray(pack?.workflow?.required_symbols) ? pack.workflow.required_symbols : [];
  const sortByRequiredSymbols = (items = []) => (Array.isArray(items) ? items : [])
    .map((item, index) => ({ item, index }))
    .sort((a, b) => (
      requiredSymbolRank(a.item?.symbol || a.item?.title, requiredSymbols)
      - requiredSymbolRank(b.item?.symbol || b.item?.title, requiredSymbols)
    ) || (a.index - b.index))
    .map((entry) => entry.item);

  pack.method_declarations = sortByRequiredSymbols(pack.method_declarations);
  if (pack.answer_grounding && typeof pack.answer_grounding === 'object' && !Array.isArray(pack.answer_grounding)) {
    const facts = Array.isArray(pack.answer_grounding.facts) ? pack.answer_grounding.facts : [];
    const seen = new Set(facts.map((item) => compactSymbol(item?.symbol)).filter(Boolean));
    const augmentedFacts = [...facts];
    for (const item of pack.method_declarations || []) {
      const symbol = compactSymbol(item?.symbol);
      if (!symbol || seen.has(symbol)) {
        continue;
      }
      seen.add(symbol);
      augmentedFacts.push({
        symbol: toStringValue(item?.symbol),
        declaration: toStringValue(item?.declaration),
        source_refs: Array.isArray(item?.source_refs) ? item.source_refs : [],
        source_snippets: Array.isArray(item?.source_snippets) ? item.source_snippets : [],
      });
    }
    pack.answer_grounding.facts = sortByRequiredSymbols(augmentedFacts);
  }
  return pack;
}

function normalizeEvidencePack(pack = {}) {
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    return null;
  }
  const workflow = pack.workflow && typeof pack.workflow === 'object'
    ? normalizeEvidencePage(pack.workflow)
    : null;
  return prioritizeEvidencePack({
    version: Number(pack.version || 1),
    query: toStringValue(pack.query),
    workflow,
    bundle_pages: Array.isArray(pack.bundle_pages)
      ? pack.bundle_pages.map((item) => normalizeEvidencePage(item)).filter((item) => item.path || item.content)
      : [],
    method_declarations: Array.isArray(pack.method_declarations)
      ? pack.method_declarations.map((item) => ({
        symbol: toStringValue(item?.symbol),
        member_name: toStringValue(item?.member_name),
        type_name: toStringValue(item?.type_name),
        title: toStringValue(item?.title),
        path: toStringValue(item?.path),
        reason: toStringValue(item?.reason),
        score: Number(item?.score || 0),
        declaration: toStringValue(item?.declaration),
        source_refs: Array.isArray(item?.source_refs)
          ? item.source_refs.map((value) => normalizeSourceRef(value)).filter((value) => value.path)
          : [],
        source_snippets: Array.isArray(item?.source_snippets)
          ? item.source_snippets.map((value) => normalizeSourceSnippet(value)).filter((value) => value.path || value.content)
          : [],
        declarations: Array.isArray(item?.declarations)
          ? item.declarations.map((value) => toStringValue(value)).filter(Boolean)
          : [],
        content: String(item?.content || ''),
      })).filter((item) => item.symbol || item.path || item.content)
      : [],
    source_anchors: Array.isArray(pack.source_anchors)
      ? pack.source_anchors.map((value) => toStringValue(value)).filter(Boolean)
      : [],
    answer_grounding: normalizeAnswerGrounding(pack.answer_grounding),
  });
}

const GENERIC_QUERY_TERMS = new Set([
  '파일',
  '로드',
  '화면',
  '방법',
  '사용',
  '이용',
  '도시',
  '알려줘',
  '에서',
  '으로',
  '하는',
]);

function queryTerms(value = '') {
  const terms = Array.from(new Set(
    String(value || '')
      .toLowerCase()
      .match(/[a-z][a-z0-9_]{1,}|[가-힣]{2,}/g) || [],
  )).filter((term) => term.length >= 2 && term !== 'c' && !GENERIC_QUERY_TERMS.has(term));
  return terms.map((term) => ({
    term,
    weight: /^[a-z][a-z0-9_]{2,}$/.test(term) ? 5 : 2,
  }));
}

function workflowRelevanceScore(result = {}, terms = []) {
  const haystack = [
    result?.path,
    result?.title,
    result?.summary,
    result?.excerpt,
    result?.content,
  ].map((value) => String(value || '').toLowerCase()).join('\n');
  if (!haystack) {
    return 0;
  }
  return (Array.isArray(terms) ? terms : [])
    .reduce((score, item) => score + (item?.term && haystack.includes(item.term) ? Number(item.weight || 1) : 0), 0);
}

function workflowPath(result = {}) {
  const pathValue = toStringValue(result?.path).replace(/\\/g, '/');
  return pathValue.startsWith('workflows/') && pathValue.endsWith('.md') ? pathValue : '';
}

async function loadRelatedWorkflowEvidencePacks({
  backend = {},
  wikiId = '',
  query = '',
  results = [],
  primaryPack = null,
  maxPacks = 5,
} = {}) {
  const packs = [];
  const seen = new Set();
  const addPack = (pack) => {
    const normalized = normalizeEvidencePack(pack);
    const pathValue = toStringValue(normalized?.workflow?.path).toLowerCase();
    if (!normalized || !pathValue || seen.has(pathValue)) {
      return;
    }
    seen.add(pathValue);
    packs.push(normalized);
  };
  addPack(primaryPack);

  const terms = queryTerms(query);
  const candidates = (Array.isArray(results) ? results : [])
    .map((result, index) => ({
      path: workflowPath(result),
      score: workflowRelevanceScore(result, terms),
      index,
    }))
    .filter((item) => item.path && !seen.has(item.path.toLowerCase()))
    .sort((a, b) => (b.score - a.score) || (a.index - b.index));

  for (const candidate of candidates) {
    if (packs.length >= Math.max(1, Number(maxPacks || 3))) {
      break;
    }
    if (candidate.score <= 0 && packs.length > 0) {
      continue;
    }
    try {
      const page = await readBackendWikiPage({
        baseUrl: backend.baseUrl,
        wikiId,
        path: candidate.path,
      });
      addPack(page?.evidence_pack);
    } catch {
      // Search must still be useful when one related workflow page is stale.
    }
  }
  return packs;
}

function WikiSearchTool() {
  return defineLocalTool({
    name: 'wiki_search',
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
          const evidencePack = normalizeEvidencePack(workflowResult?.evidence_pack);
          const evidencePacks = await loadRelatedWorkflowEvidencePacks({
            backend,
            wikiId: toStringValue(workflowResult?.wiki_id) || toStringValue(input?.wiki_id) || backend.wikiId,
            query,
            results: mergedResults,
            primaryPack: evidencePack,
          });
          return {
            ok: true,
            wiki_id: toStringValue(workflowResult?.wiki_id) || toStringValue(input?.wiki_id) || backend.wikiId,
            query,
            total: mergedResults.length,
            results: mergedResults,
            evidence_pack: evidencePack,
            evidence_packs: evidencePacks,
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
      const evidencePack = normalizeEvidencePack(fallbackResult?.evidence_pack);
      const evidencePacks = await loadRelatedWorkflowEvidencePacks({
        backend,
        wikiId: toStringValue(fallbackResult?.wiki_id) || toStringValue(input?.wiki_id) || backend.wikiId,
        query,
        results: mergedResults,
        primaryPack: evidencePack,
      });
      return {
        ok: true,
        wiki_id: toStringValue(fallbackResult?.wiki_id),
        query,
        total: mergedResults.length > 0 ? mergedResults.length : Number(fallbackResult?.total || 0),
        results: mergedResults,
        evidence_pack: evidencePack,
        evidence_packs: evidencePacks,
      };
    },
  });
}

function WikiReadTool() {
  return defineLocalTool({
    name: 'wiki_read',
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
      const pagePath = toStringValue(input?.path);
      if (/^source[\\/]/i.test(pagePath) || /\.(?:h|hpp|cpp|cxx|cc|cs)$/i.test(pagePath)) {
        return {
          ok: false,
          error: 'wiki_read_requires_wiki_page_path',
          message: 'wiki_read accepts backend wiki page paths from wiki_search results, not source_refs paths. Use the source_refs as citations or search for the matching workflow/page.',
          path: pagePath,
        };
      }
      const page = await readBackendWikiPage({
        baseUrl: backend.baseUrl,
        wikiId: toStringValue(input?.wiki_id) || backend.wikiId,
        path: pagePath,
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
        evidence_pack: normalizeEvidencePack(page?.evidence_pack),
      };
    },
  });
}

module.exports = {
  WikiReadTool,
  WikiSearchTool,
};
