const { collectBackendEvidence } = require('../../services/tools/BackendToolClient.cjs');
const { defineLocalTool } = require('../../Tool.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  arraySchema,
  enumSchema,
} = require('../shared/schema.cjs');

function clampInt(value, low, high, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(low, Math.min(high, Math.floor(parsed)));
}

function isRemoteUrl(value) {
  return /^https?:\/\//i.test(toStringValue(value));
}

function normalizeReferencePath(value) {
  const candidate = toStringValue(value).replace(/\\/g, '/');
  if (!candidate || isRemoteUrl(candidate) || /^file:\/\//i.test(candidate)) {
    return '';
  }
  return candidate;
}

function parseStartLine(value) {
  const raw = toStringValue(value);
  const match = raw.match(/^(\d+)/);
  return match ? Math.max(1, Number(match[1] || 0)) : 0;
}

function normalizeReferenceMatch(item) {
  const lineRange = toStringValue(item?.line_range || item?.lineRange);
  return {
    path: normalizeReferencePath(item?.path),
    lineRange,
    line: parseStartLine(lineRange),
    text: toStringValue(item?.match || item?.text),
    symbol: toStringValue(item?.symbol),
    matchKind: toStringValue(item?.match_kind || item?.matchKind),
    evidenceType: toStringValue(item?.evidence_type || item?.evidenceType),
    source: 'company_reference_search',
  };
}

function normalizeReferenceWindow(item) {
  const lineRange = toStringValue(item?.line_range || item?.lineRange);
  return {
    path: normalizeReferencePath(item?.path),
    lineRange,
    startLine: parseStartLine(lineRange),
    endLine: (() => {
      const raw = toStringValue(lineRange);
      const match = raw.match(/-(\d+)$/);
      return match ? Math.max(parseStartLine(raw), Number(match[1] || 0)) : parseStartLine(raw);
    })(),
    content: String(item?.content || ''),
    truncated: Boolean(item?.truncated),
    matchKind: toStringValue(item?.match_kind || item?.matchKind),
    evidenceType: toStringValue(item?.evidence_type || item?.evidenceType),
  };
}

function normalizeDocEvidenceItem(item) {
  const sourceUrl = toStringValue(item?.source_url || item?.sourceUrl);
  const filePath = normalizeReferencePath(item?.file_path || item?.filePath || sourceUrl);
  return {
    chunk_id: toStringValue(item?.chunk_id || item?.chunkId),
    doc_id: toStringValue(item?.doc_id || item?.docId),
    source_url: sourceUrl,
    file_path: filePath,
    heading_path: toStringValue(item?.heading_path || item?.headingPath),
    paragraph_range: toStringValue(item?.paragraph_range || item?.paragraphRange),
    text: String(item?.text || '').slice(0, 1600),
    truncated: Boolean(item?.truncated),
  };
}

function normalizeCitationItem(item) {
  const sourceUrl = toStringValue(item?.source_url || item?.sourceUrl);
  return {
    kind: toStringValue(item?.kind || 'generic'),
    doc_id: toStringValue(item?.doc_id || item?.docId),
    chunk_id: toStringValue(item?.chunk_id || item?.chunkId),
    path: normalizeReferencePath(item?.path),
    line_range: toStringValue(item?.line_range || item?.lineRange),
    source_url: sourceUrl,
    note: toStringValue(item?.note),
  };
}

function CompanyReferenceSearchTool() {
  return defineLocalTool({
    name: 'company_reference_search',
    aliases: ['backend_reference_search', 'CompanyReferenceSearch'],
    kind: 'read',
    inputSchema: objectSchema({
      query: stringSchema('Search query for company engine source or internal reference docs'),
      mode: enumSchema(['auto', 'code', 'docs', 'hybrid'], 'Evidence collection mode'),
      response_type: stringSchema('Backend response type hint such as api_lookup or general'),
      top_k: integerSchema('Maximum number of document search results to consider', { minimum: 1 }),
      limit: integerSchema('Maximum number of code matches to consider', { minimum: 1 }),
      max_chars: integerSchema('Maximum total characters to read per code/doc window', { minimum: 200 }),
      max_line_span: integerSchema('Maximum code line span per opened window', { minimum: 1 }),
    }, ['query']),
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether evidence collection succeeded'),
        query: stringSchema('Original query'),
        requested_mode: stringSchema('Requested mode'),
        resolved_mode: stringSchema('Resolved mode'),
        matches: arraySchema(objectSchema({
          path: stringSchema('Matched file path'),
          lineRange: stringSchema('Matched line range'),
          line: integerSchema('Matched start line', { minimum: 0 }),
          text: stringSchema('Matched text snippet'),
          symbol: stringSchema('Matched symbol name'),
          matchKind: stringSchema('Match kind'),
          evidenceType: stringSchema('Evidence type such as declaration, implementation, or example'),
          source: stringSchema('Evidence source'),
        }), 'Code matches'),
        windows: arraySchema(objectSchema({
          path: stringSchema('Window file path'),
          lineRange: stringSchema('Window line range'),
          startLine: integerSchema('Window start line', { minimum: 0 }),
          endLine: integerSchema('Window end line', { minimum: 0 }),
          content: stringSchema('Window content'),
          truncated: booleanSchema('Whether the content was truncated'),
          matchKind: stringSchema('Window match kind'),
          evidenceType: stringSchema('Window evidence type such as declaration, implementation, or example'),
        }), 'Opened code windows'),
        doc_results: arraySchema(objectSchema({
          doc_id: stringSchema('Document id'),
          chunk_id: stringSchema('Chunk id'),
          file_path: stringSchema('Document file path'),
          source_url: stringSchema('Document source URL'),
          heading_path: stringSchema('Document heading path'),
          paragraph_range: stringSchema('Document paragraph range'),
          text: stringSchema('Document excerpt'),
          truncated: booleanSchema('Whether the excerpt was truncated'),
        }), 'Doc search results'),
        doc_chunks: arraySchema(objectSchema({
          doc_id: stringSchema('Document id'),
          chunk_id: stringSchema('Chunk id'),
          file_path: stringSchema('Document file path'),
          source_url: stringSchema('Document source URL'),
          heading_path: stringSchema('Document heading path'),
          paragraph_range: stringSchema('Document paragraph range'),
          text: stringSchema('Chunk text'),
          truncated: booleanSchema('Whether the chunk text was truncated'),
        }), 'Opened doc chunks'),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'search company engine source and internal reference docs through the backend evidence service',
    laneAffinity: ['read', 'flow', 'compare', 'review', 'failure'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: (observation) => {
      const windows = Array.isArray(observation?.windows) ? observation.windows : [];
      const docChunks = Array.isArray(observation?.doc_chunks) ? observation.doc_chunks : [];
      const hasInspection = windows.some((item) => toStringValue(item?.content))
        || docChunks.some((item) => toStringValue(item?.content));
      if (hasInspection) {
        return ['inspection', 'reference'];
      }
      const matches = Array.isArray(observation?.matches) ? observation.matches : [];
      const docResults = Array.isArray(observation?.doc_results) ? observation.doc_results : [];
      const citations = Array.isArray(observation?.citations) ? observation.citations : [];
      if (matches.length > 0 || docResults.length > 0 || citations.length > 0) {
        return ['discovery', 'reference'];
      }
      return ['reference'];
    },
    userFacingName: () => 'Company reference search',
    getToolUseSummary: (input) => `Search company reference: ${toStringValue(input?.query).slice(0, 80)}`,
    async description() {
      return 'Search backend-hosted company reference source code or internal docs and return read-only evidence windows';
    },
    async call(input, context) {
      const backendConfig = typeof context.getBackendConfig === 'function'
        ? context.getBackendConfig()
        : {};
      const baseUrl = toStringValue(backendConfig?.baseUrl || backendConfig?.serverBaseUrl);
      const apiToken = toStringValue(backendConfig?.apiToken || backendConfig?.serverApiToken);
      const query = toStringValue(input.query);
      if (!query) {
        return { ok: false, error: 'missing_query', message: 'query is required' };
      }
      if (!baseUrl) {
        return {
          ok: false,
          error: 'backend_reference_unavailable',
          message: 'Backend API base URL is not configured. Set serverBaseUrl before using company_reference_search.',
        };
      }

      try {
        const result = await collectBackendEvidence({
          baseUrl,
          apiToken,
          sessionId: toStringValue(context.sessionId),
          userId: 'desktop-local',
          query,
          mode: toStringValue(input.mode || 'code') || 'code',
          responseType: toStringValue(input.response_type || input.responseType || 'api_lookup') || 'api_lookup',
          topK: clampInt(input.top_k || input.topK, 1, 50, 8),
          limit: clampInt(input.limit, 1, 50, 8),
          maxChars: clampInt(input.max_chars || input.maxChars, 200, 12000, 12000),
          maxLineSpan: clampInt(input.max_line_span || input.maxLineSpan, 1, 500, 200),
        });
        const matches = (Array.isArray(result?.evidence?.code?.search?.matches) ? result.evidence.code.search.matches : [])
          .map((item) => normalizeReferenceMatch(item))
          .filter((item) => item.path);
        const windows = (Array.isArray(result?.evidence?.code?.windows) ? result.evidence.code.windows : [])
          .map((item) => normalizeReferenceWindow(item))
          .filter((item) => item.path);
        const docResults = (Array.isArray(result?.evidence?.docs?.search?.results) ? result.evidence.docs.search.results : [])
          .map((item) => normalizeDocEvidenceItem(item));
        const docChunks = (Array.isArray(result?.evidence?.docs?.chunks) ? result.evidence.docs.chunks : [])
          .map((item) => normalizeDocEvidenceItem(item));
        const citations = (Array.isArray(result?.citations) ? result.citations : [])
          .map((item) => normalizeCitationItem(item));
        const trace = Array.isArray(result?.trace) ? result.trace.slice(0, 16) : [];
        const messageParts = [];
        if (matches.length > 0) messageParts.push(`${matches.length} code matches`);
        if (windows.length > 0) messageParts.push(`${windows.length} code windows`);
        if (docResults.length > 0) messageParts.push(`${docResults.length} doc results`);
        if (docChunks.length > 0) messageParts.push(`${docChunks.length} doc chunks`);

        return {
          ok: true,
          query: toStringValue(result?.query || query),
          requested_mode: toStringValue(result?.requested_mode || input.mode || 'code'),
          resolved_mode: toStringValue(result?.resolved_mode || input.mode || 'code'),
          matches,
          windows,
          doc_results: docResults,
          doc_chunks: docChunks,
          citations,
          trace,
          policy: result?.policy && typeof result.policy === 'object' ? result.policy : {},
          message: messageParts.length > 0
            ? `Collected ${messageParts.join(', ')} from backend reference sources.`
            : 'No backend reference evidence matched the query.',
        };
      } catch (error) {
        return {
          ok: false,
          error: 'backend_reference_search_failed',
          message: error instanceof Error ? error.message : String(error),
          query,
        };
      }
    },
  });
}

module.exports = {
  CompanyReferenceSearchTool,
};
