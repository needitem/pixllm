const {
  getBackendToolUserContext,
  listBackendRepoFiles,
  lookupBackendWikiEvidence,
  readBackendCode,
} = require('../../services/tools/BackendToolClient.cjs');
const { defineLocalTool } = require('../../Tool.cjs');
const { extractCodeExamples, extractReferenceAnchors } = require('../../query/referenceArtifacts.cjs');
const { extractEngineApiFacts } = require('../../query/engineApiFacts.cjs');
const {
  toStringValue,
  objectSchema,
  stringSchema,
  integerSchema,
  booleanSchema,
  arraySchema,
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

function uniqueBy(items, keyFn) {
  const seen = new Set();
  const output = [];
  for (const item of Array.isArray(items) ? items : []) {
    const key = toStringValue(typeof keyFn === 'function' ? keyFn(item) : '');
    if (!key || seen.has(key)) continue;
    seen.add(key);
    output.push(item);
  }
  return output;
}

function anchorPriority(anchor) {
  const evidenceType = toStringValue(anchor?.evidenceType || anchor?.evidence_type).toLowerCase();
  if (evidenceType === 'implementation') return 0;
  if (evidenceType === 'declaration') return 1;
  return 2;
}

function normalizeSuffix(value) {
  return normalizeReferencePath(value).toLowerCase();
}

function chooseSuffixCandidate(anchorPath, files = []) {
  const suffix = normalizeSuffix(anchorPath);
  if (!suffix) return '';
  const candidates = (Array.isArray(files) ? files : [])
    .map((item) => toStringValue(item?.path || item))
    .filter(Boolean);
  const ranked = candidates
    .filter((item) => item.replace(/\\/g, '/').toLowerCase().endsWith(suffix))
    .sort((left, right) => left.length - right.length);
  return toStringValue(ranked[0]);
}

async function hydrateReferenceAnchors({
  baseUrl = '',
  apiToken = '',
  sessionId = '',
  anchors = [],
  maxChars = 4000,
  maxLineSpan = 120,
} = {}) {
  const uniqueAnchors = uniqueBy(
    (Array.isArray(anchors) ? anchors : [])
      .filter((item) => toStringValue(item?.path))
      .sort((left, right) => anchorPriority(left) - anchorPriority(right)),
    (item) => `${toStringValue(item?.path)}:${toStringValue(item?.lineRange)}`,
  ).slice(0, 8);
  if (uniqueAnchors.length === 0) return [];

  await getBackendToolUserContext({
    baseUrl,
    apiToken,
    sessionId,
  });

  const fileListsByLeaf = new Map();
  const windows = [];

  for (const anchor of uniqueAnchors) {
    const anchorPath = toStringValue(anchor?.path);
    const leafName = anchorPath.split('/').pop() || '';
    if (!leafName) continue;

    if (!fileListsByLeaf.has(leafName)) {
      const listed = await listBackendRepoFiles({
        baseUrl,
        apiToken,
        sessionId,
        glob: `**/${leafName}`,
        limit: 40,
      }).catch(() => ({ files: [] }));
      fileListsByLeaf.set(leafName, Array.isArray(listed?.files) ? listed.files : []);
    }

    const matchedPath = chooseSuffixCandidate(anchorPath, fileListsByLeaf.get(leafName));
    if (!matchedPath) continue;

    const startLine = Math.max(1, Number(anchor?.startLine || 1));
    const endLine = Math.max(startLine, Number(anchor?.endLine || startLine));
    const lineSpan = Math.max(1, Math.min(Number(maxLineSpan || 120), 240));
    const readStart = Math.max(1, startLine - Math.floor(lineSpan / 2));
    const readEnd = Math.max(readStart, Math.min(readStart + lineSpan - 1, endLine + Math.floor(lineSpan / 2)));
    const readResult = await readBackendCode({
      baseUrl,
      apiToken,
      sessionId,
      path: matchedPath,
      startLine: readStart,
      endLine: readEnd,
    }).catch(() => null);
    if (!readResult?.found) continue;

    windows.push({
      path: toStringValue(readResult?.path || matchedPath),
      lineRange: toStringValue(readResult?.line_range || `${readStart}-${readEnd}`),
      startLine: readStart,
      endLine: readEnd,
      content: String(readResult?.content || '').slice(0, Math.max(800, Number(maxChars || 4000))),
      truncated: Boolean(readResult?.truncated),
      matchKind: 'reference_anchor',
      evidenceType: toStringValue(anchor?.evidenceType || anchor?.evidence_type || 'reference'),
    });
  }

  return uniqueBy(windows, (item) => `${toStringValue(item?.path)}:${toStringValue(item?.lineRange)}`);
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
    text: String(item?.text || '').slice(0, 2400),
    truncated: Boolean(item?.truncated),
    title: toStringValue(item?.title),
    symbols: Array.isArray(item?.symbols) ? item.symbols.map((value) => toStringValue(value)).filter(Boolean).slice(0, 16) : [],
    tags: Array.isArray(item?.tags) ? item.tags.map((value) => toStringValue(value)).filter(Boolean).slice(0, 16) : [],
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

function normalizeApiFactItem(item) {
  return {
    kind: toStringValue(item?.kind),
    namespace: toStringValue(item?.namespace),
    typeName: toStringValue(item?.typeName),
    qualifiedType: toStringValue(item?.qualifiedType),
    memberName: toStringValue(item?.memberName),
    signature: toStringValue(item?.signature),
    stubSignature: toStringValue(item?.stubSignature),
    path: normalizeReferencePath(item?.path),
    lineRange: toStringValue(item?.lineRange || item?.line_range),
    evidenceType: toStringValue(item?.evidenceType || item?.evidence_type),
  };
}

function normalizeLookupSummaryItem(item) {
  return {
    qualifiedSymbol: toStringValue(item?.qualified_symbol || item?.qualifiedSymbol),
    typeName: toStringValue(item?.type_name || item?.typeName),
    memberName: toStringValue(item?.member_name || item?.memberName),
    sourceUrl: toStringValue(item?.source_url || item?.sourceUrl),
    headingPath: toStringValue(item?.heading_path || item?.headingPath),
  };
}

function WikiEvidenceSearchTool() {
  return defineLocalTool({
    name: 'wiki_evidence_search',
    aliases: ['backend_wiki_evidence_search', 'WikiEvidenceSearch'],
    kind: 'read',
    inputSchema: objectSchema({
      query: stringSchema('Search query for backend wiki evidence or reference docs'),
      response_type: stringSchema('Backend response type hint such as api_lookup or general'),
      top_k: integerSchema('Maximum number of document search results to consider', { minimum: 1 }),
      limit: integerSchema('Maximum number of code matches to consider', { minimum: 1 }),
      max_chars: integerSchema('Maximum total characters to read per code/doc window', { minimum: 200 }),
      max_line_span: integerSchema('Maximum code line span per opened window', { minimum: 1 }),
    }, ['query']),
    async backfillObservableInput(input) {
      if (input && typeof input === 'object' && !Array.isArray(input) && Object.prototype.hasOwnProperty.call(input, 'mode')) {
        delete input.mode;
      }
    },
    outputSchema: {
      type: 'object',
      properties: {
        ok: booleanSchema('Whether evidence collection succeeded'),
        query: stringSchema('Original query'),
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
        sources: arraySchema(objectSchema({
          doc_id: stringSchema('Document id'),
          chunk_id: stringSchema('Chunk id'),
          file_path: stringSchema('Document file path'),
          source_url: stringSchema('Document source URL'),
          title: stringSchema('Document title'),
          heading_path: stringSchema('Document heading path'),
          paragraph_range: stringSchema('Document paragraph range'),
          text: stringSchema('Chunk text'),
          truncated: booleanSchema('Whether the source text was truncated'),
          symbols: arraySchema(stringSchema('Relevant workflow or engine symbols'), 'Workflow or engine symbol hints'),
          tags: arraySchema(stringSchema('Relevant document tags'), 'Document tags'),
        }), 'Source excerpts'),
        reference_anchors: arraySchema(objectSchema({
          path: stringSchema('Anchored source path'),
          lineRange: stringSchema('Anchored line range'),
          startLine: integerSchema('Anchored start line', { minimum: 1 }),
          endLine: integerSchema('Anchored end line', { minimum: 1 }),
          evidenceType: stringSchema('Anchor evidence type such as declaration or implementation'),
          sourceUrl: stringSchema('Originating source URL'),
          filePath: stringSchema('Originating doc path'),
          headingPath: stringSchema('Originating heading path'),
          snippet: stringSchema('Source line snippet'),
        }), 'Extracted source anchors from reference docs'),
        examples: arraySchema(objectSchema({
          language: stringSchema('Code block language'),
          code: stringSchema('Reference code block'),
          truncated: booleanSchema('Whether the code block was truncated'),
          sourceUrl: stringSchema('Originating source URL'),
          filePath: stringSchema('Originating doc path'),
          headingPath: stringSchema('Originating heading path'),
        }), 'Extracted reference code blocks'),
        api_facts: arraySchema(objectSchema({
          kind: stringSchema('Fact kind such as type, method, property, constructor, or enum_member'),
          namespace: stringSchema('Type namespace'),
          typeName: stringSchema('Type name'),
          qualifiedType: stringSchema('Qualified type name'),
          memberName: stringSchema('Member name'),
          signature: stringSchema('Observed source signature'),
          stubSignature: stringSchema('Normalized C#-style stub signature'),
          path: stringSchema('Source path'),
          lineRange: stringSchema('Source line range'),
          evidenceType: stringSchema('Evidence type such as declaration or implementation'),
        }), 'Structured API facts extracted from source windows'),
        fact_sheet: stringSchema('Compact verified API fact sheet for model grounding'),
        known_types: arraySchema(objectSchema({
          qualifiedType: stringSchema('Qualified type name'),
          namespace: stringSchema('Type namespace'),
          typeName: stringSchema('Type name'),
          kind: stringSchema('Associated kind hint'),
        }), 'Known engine types observed in the reference results'),
        search_status: stringSchema('Search outcome such as exact_match, no_exact_match, or broad_match'),
        matched_api: objectSchema({
          qualifiedSymbol: stringSchema('Matched qualified API symbol'),
          typeName: stringSchema('Matched type name'),
          memberName: stringSchema('Matched member name'),
          sourceUrl: stringSchema('Matched source URL'),
          headingPath: stringSchema('Matched source heading path'),
        }),
        related_apis: arraySchema(objectSchema({
          qualifiedSymbol: stringSchema('Suggested related qualified API symbol'),
          typeName: stringSchema('Suggested related type name'),
          memberName: stringSchema('Suggested related member name'),
          sourceUrl: stringSchema('Suggested related source URL'),
          headingPath: stringSchema('Suggested related source heading path'),
        }), 'Related verified APIs'),
        workflow_bundle: objectSchema({
          required_slots: arraySchema(stringSchema('Workflow-first required slot'), 'Required slots'),
          filled_slots: arraySchema(stringSchema('Workflow-first filled slot'), 'Filled slots'),
          missing_slots: arraySchema(stringSchema('Workflow-first missing slot'), 'Missing slots'),
          slots_complete: booleanSchema('Whether workflow-first slots are fully satisfied'),
          workflow_paths: arraySchema(stringSchema('Workflow paths used'), 'Workflow paths'),
          method_paths: arraySchema(stringSchema('Method paths used'), 'Method paths'),
        }),
        negative_evidence: stringSchema('Explicit negative result when no exact API was found'),
        error: stringSchema('Error code'),
        message: stringSchema('Human-readable status'),
      },
    },
    searchHint: 'search backend wiki evidence and internal reference docs through the backend evidence service',
    laneAffinity: ['read', 'flow', 'compare', 'review', 'failure'],
    isReadOnly: () => true,
    isConcurrencySafe: () => true,
    getObservationEvidenceKinds: (observation) => {
      const windows = Array.isArray(observation?.windows) ? observation.windows : [];
      const sources = Array.isArray(observation?.sources) ? observation.sources : [];
      const citations = Array.isArray(observation?.citations) ? observation.citations : [];
      const hasCodeInspection = windows.some((item) => toStringValue(item?.content));
      if (hasCodeInspection) {
        return ['inspection', 'reference'];
      }
      if (sources.length > 0 || citations.length > 0) {
        return ['reference'];
      }
      return ['reference'];
    },
    userFacingName: () => 'Wiki evidence search',
    getToolUseSummary: (input) => `Search wiki evidence: ${toStringValue(input?.query).slice(0, 80)}`,
    async description() {
      return 'Search backend-hosted wiki evidence or internal docs and return read-only evidence windows';
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
          message: 'Backend API base URL is not configured. Set serverBaseUrl before using wiki_evidence_search.',
        };
      }

      try {
        const result = await lookupBackendWikiEvidence({
          baseUrl,
          apiToken,
          sessionId: toStringValue(context.sessionId),
          userId: 'desktop-local',
          query,
          responseType: toStringValue(input.response_type || input.responseType || 'api_lookup') || 'api_lookup',
          workflowFirst: Boolean(context?.requestContext?.workflowPlan?.preferWikiFirst),
          topK: clampInt(input.top_k || input.topK, 1, 50, 8),
          limit: clampInt(input.limit, 1, 50, 8),
          maxChars: clampInt(input.max_chars || input.maxChars, 200, 12000, 12000),
          maxLineSpan: clampInt(input.max_line_span || input.maxLineSpan, 1, 500, 200),
        });
        const windows = (Array.isArray(result?.code_windows) ? result.code_windows : [])
          .map((item) => normalizeReferenceWindow(item))
          .filter((item) => item.path);
        const sources = (Array.isArray(result?.sources) ? result.sources : [])
          .map((item) => normalizeDocEvidenceItem(item));
        const citations = (Array.isArray(result?.citations) ? result.citations : [])
          .map((item) => normalizeCitationItem(item));
        const lookupSummary = result?.lookup_summary && typeof result.lookup_summary === 'object'
          ? result.lookup_summary
          : {};
        const searchStatus = toStringValue(lookupSummary?.status || '');
        const matchedApi = normalizeLookupSummaryItem(lookupSummary?.matched_api || lookupSummary?.matchedApi);
        const relatedApis = Array.isArray(lookupSummary?.related_apis || lookupSummary?.relatedApis)
          ? (lookupSummary.related_apis || lookupSummary.relatedApis)
            .map((item) => normalizeLookupSummaryItem(item))
            .filter((item) => item.qualifiedSymbol)
          : [];
        const negativeEvidence = toStringValue(lookupSummary?.negative_evidence || lookupSummary?.negativeEvidence);
        const workflowBundle = result?.workflow_bundle && typeof result.workflow_bundle === 'object'
          ? result.workflow_bundle
          : {};
        const referenceAnchors = extractReferenceAnchors(sources);
        const examples = extractCodeExamples(sources, clampInt(input.max_chars || input.maxChars, 400, 8000, 4000));
        const shouldHydrateAnchors = !searchStatus && windows.length === 0 && referenceAnchors.length > 0;
        const hydratedWindows = shouldHydrateAnchors
          ? await hydrateReferenceAnchors({
            baseUrl,
            apiToken,
            sessionId: toStringValue(context.sessionId),
            anchors: referenceAnchors,
            maxChars: clampInt(input.max_chars || input.maxChars, 400, 8000, 4000),
            maxLineSpan: clampInt(input.max_line_span || input.maxLineSpan, 20, 240, 120),
          })
          : [];
        const mergedWindows = uniqueBy(
          [...windows, ...hydratedWindows],
          (item) => `${toStringValue(item?.path)}:${toStringValue(item?.lineRange)}`,
        );
        const factBundle = extractEngineApiFacts({
          query,
          windows: mergedWindows,
          sources,
        });
        const apiFacts = (Array.isArray(factBundle.apiFacts) ? factBundle.apiFacts : [])
          .map((item) => normalizeApiFactItem(item));
        const messageParts = [];
        if (mergedWindows.length > 0) messageParts.push(`${mergedWindows.length} code windows`);
        if (sources.length > 0) messageParts.push(`${sources.length} sources`);
        if (referenceAnchors.length > 0) messageParts.push(`${referenceAnchors.length} source anchors`);
        if (examples.length > 0) messageParts.push(`${examples.length} code examples`);
        if (apiFacts.length > 0) {
          messageParts.push(`${apiFacts.length} api facts`);
        }
        if (searchStatus === 'exact_match' && matchedApi.qualifiedSymbol) {
          messageParts.unshift(`Exact API match: ${matchedApi.qualifiedSymbol}`);
        } else if (searchStatus === 'no_exact_match') {
          if (negativeEvidence) {
            messageParts.unshift(negativeEvidence);
          }
          if (relatedApis.length > 0) {
            messageParts.push(`related APIs: ${relatedApis.map((item) => item.qualifiedSymbol).join(', ')}`);
          }
        }
        const statusMessage = searchStatus === 'exact_match'
          ? `Exact verified API match: ${matchedApi.qualifiedSymbol || query}`
          : searchStatus === 'no_exact_match'
            ? [
              negativeEvidence || 'No exact verified API match found.',
              relatedApis.length > 0
                ? `Related verified APIs: ${relatedApis.map((item) => item.qualifiedSymbol).join(', ')}.`
                : '',
            ].filter(Boolean).join(' ')
            : (
              messageParts.length > 0
                ? `Collected ${messageParts.join(', ')} from backend reference sources.`
                : 'No backend reference evidence matched the query.'
            );

        return {
          ok: true,
          query: toStringValue(result?.query || query),
          windows: mergedWindows,
          sources,
          citations,
          reference_anchors: referenceAnchors,
          examples,
          api_facts: apiFacts,
          fact_sheet: factBundle.factSheet,
          known_types: factBundle.knownTypes,
          search_status: searchStatus || 'broad_match',
          matched_api: matchedApi,
          related_apis: relatedApis,
          workflow_bundle: workflowBundle,
          negative_evidence: negativeEvidence,
          message: statusMessage,
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
  WikiEvidenceSearchTool,
};
