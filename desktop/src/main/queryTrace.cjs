const COMMON_CODE_TOKENS = new Set([
  'class', 'public', 'private', 'protected', 'internal', 'static', 'async', 'void', 'string',
  'int', 'bool', 'return', 'using', 'namespace', 'true', 'false', 'null', 'this', 'base',
  'var', 'new', 'get', 'set', 'line', 'path', 'items', 'content', 'query', 'limit',
  'list', 'ilist', 'ienumerable', 'icollection', 'dictionary', 'idictionary', 'task', 'tuple',
  'object', 'double', 'float', 'long', 'short', 'byte', 'char', 'decimal',
]);
const METHOD_NOISE_NAMES = new Set(['dispose', 'tostring', 'equals', 'gethashcode', 'invoke']);
const CALL_KEYWORD_TOKENS = new Set(['if', 'for', 'while', 'switch', 'catch', 'foreach', 'return', 'new', 'typeof', 'nameof', 'using', 'lock']);
const MAX_SNIPPET_CHARS = 280;

function normalizePath(value) {
  return String(value || '').trim().replace(/\\/g, '/');
}

function parseLineRange(value) {
  const raw = String(value || '').trim();
  const match = raw.match(/^(\d+)(?:\s*-\s*(\d+))?$/);
  if (!match) {
    return { startLine: 0, endLine: 0 };
  }
  const startLine = Math.max(1, Number(match[1] || 0));
  const endLine = Math.max(startLine, Number(match[2] || match[1] || 0));
  return { startLine, endLine };
}

function uniq(items) {
  const seen = new Set();
  const out = [];
  for (const item of items || []) {
    const normalized = normalizePath(item);
    if (!normalized) continue;
    const lowered = normalized.toLowerCase();
    if (seen.has(lowered)) continue;
    seen.add(lowered);
    out.push(normalized);
  }
  return out;
}

function stepSucceeded(step) {
  return Boolean(step?.observation?.ok);
}

function successfulSteps(trace, tool) {
  return (Array.isArray(trace) ? trace : []).filter((step) => step.tool === tool && stepSucceeded(step));
}

function failedSteps(trace) {
  return (Array.isArray(trace) ? trace : []).filter((step) => step.observation?.ok === false);
}

function isTraceCandidatePath(filePath) {
  const normalized = normalizePath(filePath);
  if (!normalized) return false;
  if (/^(?:\.git|\.svn|\.vs|\.vscode)(?:\/|$)/i.test(normalized)) return false;
  if (/\/(?:\.git|\.svn|\.vs|\.vscode|obj|bin|dist|build|out|node_modules)(?:\/|$)/i.test(normalized)) return false;
  return /\.(cs|xaml\.cs|cpp|c|cc|cxx|h|hh|hpp|hxx|py|ts|tsx|js|cjs|mjs|jsx|vb|json|xml|xaml|sql|bat|cmd|ps1|sh)$/i.test(normalized);
}

function grepQueriesFromTrace(trace) {
  return uniq(
    (Array.isArray(trace) ? trace : [])
      .filter((step) => ['grep', 'find_symbol', 'find_references', 'find_callers'].includes(step.tool))
      .map((step) => step?.input?.query || step?.input?.symbol || ''),
  );
}

function grepItemsFromTrace(trace) {
  const seen = new Set();
  const out = [];
  for (const step of (Array.isArray(trace) ? trace : []).filter((item) => ['grep', 'find_symbol', 'find_references', 'find_callers'].includes(item.tool) && stepSucceeded(item))) {
    for (const item of Array.isArray(step.observation?.items) ? step.observation.items : []) {
      const pathValue = normalizePath(item?.path);
      const text = String(item?.text || '');
      const key = `${pathValue}:${Number(item?.line || 0)}:${text}`.toLowerCase();
      if (!isTraceCandidatePath(pathValue) || seen.has(key)) continue;
      seen.add(key);
      out.push({
        path: pathValue,
        line: Number(item?.line || 0),
        text,
        source: String(item?.source || step.tool || ''),
        matchKind: String(item?.matchKind || item?.match_kind || ''),
        symbol: String(item?.symbol || step.observation?.symbol || ''),
      });
    }
  }
  return out;
}

function listFilesFromTrace(trace) {
  return uniq(successfulSteps(trace, 'list_files').flatMap((step) => (Array.isArray(step.observation?.items) ? step.observation.items : []).map((item) => item.path).filter(isTraceCandidatePath)))
    .map((path) => ({ path }));
}

function readWindowsFromTrace(trace) {
  const keyed = new Map();
  for (const observation of (Array.isArray(trace) ? trace : [])
    .filter((step) => ['read_file', 'read_symbol_span'].includes(step.tool) && stepSucceeded(step))
    .map((step) => step.observation)
    .filter(Boolean)) {
    const pathValue = normalizePath(observation.path);
    if (!pathValue) continue;
    const lineRange = String(observation.lineRange || '').trim();
    const { startLine, endLine } = parseLineRange(lineRange);
    const key = `${pathValue}::${lineRange || 'head'}`.toLowerCase();
    const content = String(observation.content || '');
    const current = keyed.get(key);
    if (current && String(current.content || '').length >= content.length) {
      continue;
    }
    keyed.set(key, {
      ok: true,
      path: pathValue,
      content,
      lineRange,
      startLine,
      endLine,
      truncated: Boolean(observation.truncated),
      symbol: String(observation.symbol || ''),
      matchKind: String(observation.matchKind || observation.match_kind || ''),
    });
  }
  return Array.from(keyed.values());
}

function readObservationsFromTrace(trace) {
  const grouped = new Map();
  for (const window of readWindowsFromTrace(trace)) {
    const key = window.path.toLowerCase();
    if (!grouped.has(key)) {
      grouped.set(key, {
        ok: true,
        path: window.path,
        contentParts: [],
        lineRanges: [],
        totalChars: 0,
      });
    }
    const entry = grouped.get(key);
    if (window.lineRange && !entry.lineRanges.includes(window.lineRange)) {
      entry.lineRanges.push(window.lineRange);
    }
    const snippet = `${window.lineRange ? `// lines ${window.lineRange}\n` : ''}${String(window.content || '')}`.trim();
    if (!snippet) {
      continue;
    }
    const remaining = Math.max(0, 24000 - entry.totalChars);
    if (remaining <= 0) {
      continue;
    }
    const bounded = snippet.slice(0, remaining);
    entry.contentParts.push(bounded);
    entry.totalChars += bounded.length;
  }
  return Array.from(grouped.values()).map((entry) => ({
    ok: true,
    path: entry.path,
    content: entry.contentParts.join('\n\n'),
    lineRange: entry.lineRanges[0] || '',
    lineRanges: entry.lineRanges,
  }));
}

function symbolOutlinesFromTrace(trace) {
  return (Array.isArray(trace) ? trace : [])
    .filter((step) => ['symbol_outline', 'symbol_neighborhood'].includes(step.tool) && stepSucceeded(step))
    .map((step) => ({
      path: normalizePath(step?.observation?.path),
      symbol: String(step?.observation?.symbol || ''),
      backend: String(step?.observation?.backend || ''),
      lineHint: Number(step?.observation?.lineHint || 0),
      items: Array.isArray(step?.observation?.items) ? step.observation.items.slice(0, 40) : [],
    }))
    .filter((item) => item.path);
}

function referencePathsFromTrace(trace) {
  const paths = [];
  for (const step of successfulSteps(trace, 'company_reference_search')) {
    const observation = step?.observation && typeof step.observation === 'object' ? step.observation : {};
    for (const item of Array.isArray(observation.matches) ? observation.matches : []) {
      paths.push(item?.path);
    }
    for (const item of Array.isArray(observation.windows) ? observation.windows : []) {
      paths.push(item?.path);
    }
    for (const item of Array.isArray(observation.doc_results) ? observation.doc_results : []) {
      paths.push(item?.file_path);
    }
    for (const item of Array.isArray(observation.doc_chunks) ? observation.doc_chunks : []) {
      paths.push(item?.file_path);
    }
    for (const item of Array.isArray(observation.citations) ? observation.citations : []) {
      paths.push(item?.path);
    }
  }
  return uniq(
    paths.filter((item) => {
      const normalized = normalizePath(item);
      if (!normalized) return false;
      if (/^(?:https?|file):\/\//i.test(normalized)) return false;
      return isTraceCandidatePath(normalized);
    }),
  );
}

function summarizeObservation(toolName, observation, maxChars = 16000) {
  const payload = observation || {};
  if (toolName === 'list_files') {
    return {
      ok: payload.ok !== false,
      total: payload.total || 0,
      items: Array.isArray(payload.items) ? payload.items.slice(0, 500) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'glob' || toolName === 'glob_files') {
    return {
      ok: Boolean(payload.ok),
      pattern: payload.pattern || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 200) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'todo_read' || toolName === 'todo_write') {
    return {
      ok: Boolean(payload.ok),
      total: Number(payload.total || 0),
      items: Array.isArray(payload.items) ? payload.items.slice(0, 100) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'grep') {
    return {
      ok: Boolean(payload.ok),
      query: payload.query || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 20) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'find_symbol' || toolName === 'find_references') {
    return {
      ok: Boolean(payload.ok),
      symbol: payload.symbol || payload.query || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 20) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'find_callers') {
    return {
      ok: Boolean(payload.ok),
      symbol: payload.symbol || payload.query || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 20) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'read_file' || toolName === 'read_symbol_span') {
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      truncated: Boolean(payload.truncated),
      content: String(payload.content || '').slice(0, maxChars),
      error: payload.error || '',
      message: payload.message || '',
      lineRange: String(payload.lineRange || ''),
      symbol: String(payload.symbol || ''),
      matchKind: String(payload.matchKind || payload.match_kind || ''),
    };
  }
  if (toolName === 'write' || toolName === 'write_file') {
    const diffText = String(payload.diff || '');
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      bytes: Number(payload.bytes || 0),
      added: Number(payload.added || 0),
      removed: Number(payload.removed || 0),
      diff: diffText.slice(0, maxChars),
      diff_truncated: Boolean(payload.diff_truncated) || diffText.length > maxChars,
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'edit' || toolName === 'replace_in_file') {
    const diffText = String(payload.diff || '');
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      occurrences: Number(payload.occurrences || 0),
      replace_all: Boolean(payload.replace_all || payload.replaceAll),
      added: Number(payload.added || 0),
      removed: Number(payload.removed || 0),
      diff: diffText.slice(0, maxChars),
      diff_truncated: Boolean(payload.diff_truncated) || diffText.length > maxChars,
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'run_build') {
    return {
      ok: Boolean(payload.ok),
      tool: payload.tool || '',
      code: Number(payload.code || 0),
      stdout: String(payload.stdout || '').slice(0, maxChars),
      stderr: String(payload.stderr || '').slice(0, maxChars),
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'bash' || toolName === 'run_shell' || toolName === 'powershell') {
    return {
      ok: Boolean(payload.ok),
      command: payload.command || '',
      code: Number(payload.code || 0),
      stdout: String(payload.stdout || '').slice(0, maxChars),
      stderr: String(payload.stderr || '').slice(0, maxChars),
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'company_reference_search') {
    return {
      ok: Boolean(payload.ok),
      query: payload.query || '',
      requested_mode: payload.requested_mode || '',
      resolved_mode: payload.resolved_mode || '',
      matches: Array.isArray(payload.matches)
        ? payload.matches.slice(0, 20).map((item) => ({
          path: item?.path || '',
          lineRange: item?.lineRange || item?.line_range || '',
          line: Number(item?.line || 0),
          text: String(item?.text || item?.match || '').slice(0, 240),
          symbol: item?.symbol || '',
          matchKind: item?.matchKind || item?.match_kind || '',
        }))
        : [],
      windows: Array.isArray(payload.windows)
        ? payload.windows.slice(0, 6).map((item) => ({
          path: item?.path || '',
          lineRange: item?.lineRange || item?.line_range || '',
          truncated: Boolean(item?.truncated),
          content: String(item?.content || '').slice(0, Math.min(1800, maxChars)),
        }))
        : [],
      doc_results: Array.isArray(payload.doc_results)
        ? payload.doc_results.slice(0, 8).map((item) => ({
          doc_id: item?.doc_id || '',
          chunk_id: item?.chunk_id || '',
          file_path: item?.file_path || '',
          source_url: item?.source_url || '',
          heading_path: item?.heading_path || '',
          paragraph_range: item?.paragraph_range || '',
          text: String(item?.text || '').slice(0, 240),
        }))
        : [],
      doc_chunks: Array.isArray(payload.doc_chunks)
        ? payload.doc_chunks.slice(0, 6).map((item) => ({
          doc_id: item?.doc_id || '',
          chunk_id: item?.chunk_id || '',
          file_path: item?.file_path || '',
          source_url: item?.source_url || '',
          heading_path: item?.heading_path || '',
          paragraph_range: item?.paragraph_range || '',
          text: String(item?.text || '').slice(0, 360),
          truncated: Boolean(item?.truncated),
        }))
        : [],
      citations: Array.isArray(payload.citations) ? payload.citations.slice(0, 12) : [],
      trace: Array.isArray(payload.trace) ? payload.trace.slice(0, 12) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'symbol_outline') {
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      symbol: payload.symbol || '',
      backend: payload.backend || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 40) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'symbol_neighborhood') {
    const items = Array.isArray(payload.items) ? payload.items.slice(0, 20) : [];
    const content = items
      .map((item) => {
        const line = Number(item?.line || 0);
        const name = String(item?.name || '').trim();
        const kind = String(item?.kind || '').trim();
        const text = String(item?.text || '').trim();
        const prefix = [line > 0 ? String(line) : '', kind, name].filter(Boolean).join(':');
        return [prefix, text].filter(Boolean).join(' ');
      })
      .filter(Boolean)
      .join('\n')
      .slice(0, maxChars);
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      symbol: payload.symbol || '',
      backend: payload.backend || '',
      lineHint: Number(payload.lineHint || payload.line_hint || 0),
      items,
      content,
      lineRange: Number(payload.lineHint || payload.line_hint || 0) > 0
        ? `${Number(payload.lineHint || payload.line_hint || 0)}-${Number(payload.lineHint || payload.line_hint || 0)}`
        : '',
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  return {
    ...payload,
    message: payload.message || '',
  };
}

function extractIdentifiers(text) {
  const matches = String(text || '').match(/\b[A-Za-z_][A-Za-z0-9_]{3,}\b/g) || [];
  const weighted = [];
  for (const raw of matches) {
    const token = String(raw || '').trim();
    const lowered = token.toLowerCase();
    if (!token || COMMON_CODE_TOKENS.has(lowered) || token.startsWith('_')) continue;
    let score = token.length;
    if (/[A-Z]/.test(token)) score += 6;
    if (/[A-Z][a-z0-9]+[A-Z]/.test(token)) score += 8;
    weighted.push([score, token]);
  }
  weighted.sort((a, b) => b[0] - a[0] || String(a[1]).localeCompare(String(b[1])));
  const seen = new Set();
  const out = [];
  for (const [, token] of weighted) {
    const lowered = token.toLowerCase();
    if (seen.has(lowered)) continue;
    seen.add(lowered);
    out.push(token);
    if (out.length >= 12) break;
  }
  return out;
}

function pickRepresentativeEvidence(candidate, question = '') {
  const questionTerms = extractIdentifiers(question);
  const snippets = [];
  for (const item of candidate.grepItems || []) {
    const text = String(item.text || '').trim();
    if (!text) continue;
    snippets.push({
      text: `${candidate.path}:${Number(item.line || 0)}: ${text}`,
      score: questionTerms.reduce((sum, term) => sum + (text.toLowerCase().includes(term.toLowerCase()) ? 4 : 0), 0) + 3,
    });
  }
  if (candidate.readObservation?.content) {
    for (const line of String(candidate.readObservation.content).split(/\r?\n/).map((value) => String(value || '').trim()).filter(Boolean)) {
      let score = 0;
      score += questionTerms.reduce((sum, term) => sum + (line.toLowerCase().includes(term.toLowerCase()) ? 5 : 0), 0);
      if (/[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(line)) score += 2;
      if (/\b(class|interface|enum|struct|property|field|command|handler|event|draw|render|overlay|layer|process|request|response|state)\b/i.test(line)) score += 1;
      snippets.push({ text: line, score });
    }
  }
  snippets.sort((a, b) => b.score - a.score || a.text.localeCompare(b.text));
  return String(snippets[0]?.text || '').slice(0, MAX_SNIPPET_CHARS);
}

function pushRelationEdge(edges, seen, from, to, relation, via = '') {
  const source = normalizePath(from);
  const target = normalizePath(to);
  const relationKey = String(relation || '').trim();
  const viaKey = String(via || '').trim();
  if (!source || !target || !relationKey || source === target) return;
  const key = `${source}::${target}::${relationKey}::${viaKey}`.toLowerCase();
  if (seen.has(key)) return;
  seen.add(key);
  edges.push({ from: source, to: target, relation: relationKey, via: viaKey });
}

function decapitalizeToken(token) {
  const text = String(token || '').trim();
  if (!text) return '';
  return text.charAt(0).toLowerCase() + text.slice(1);
}

function collectDefinedTypes(content, fallbackName = '') {
  const tokens = [
    ...Array.from(String(content || '').matchAll(/\b(?:class|interface|struct|enum|record|namespace|module|type)\s+([A-Za-z_][A-Za-z0-9_]*)/g)).map((match) => match[1] || fallbackName),
  ];
  if (fallbackName) {
    tokens.push(fallbackName);
  }
  return uniq(tokens.filter(Boolean));
}

function collectDefinedMethods(content) {
  const tokens = [
    ...Array.from(String(content || '').matchAll(/\b(?:public|private|protected|internal|static|export|async|virtual|override)\s+(?:static\s+)?(?:async\s+)?[A-Za-z_<>\[\],?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/gm)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/^\s*(?:async\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\([^)\n;]*\)\s*\{/gm)).map((match) => match[1] || ''),
  ];
  return uniq(tokens.filter((token) => token && !CALL_KEYWORD_TOKENS.has(String(token).toLowerCase())));
}

function collectDefinedProperties(content) {
  const tokens = [
    ...Array.from(String(content || '').matchAll(/\b(?:public|private|protected|internal)\s+[A-Za-z_<>\[\],?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*(?:get|set)/g)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/^\s*(?:public|private|protected|readonly|static|declare|export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=;\n]+)?(?:=|;)\s*$/gm)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/\b(?:this|self|state|model|ctx|context)\.([A-Za-z_][A-Za-z0-9_]*)\s*(?:[+\-*/%]?=|=|\+\+|--)/g)).map((match) => match[1] || ''),
  ];
  return uniq(tokens.filter((token) => token && !COMMON_CODE_TOKENS.has(String(token).toLowerCase())));
}

function extractUpdatedPropertyTokens(content) {
  const tokens = [
    ...Array.from(String(content || '').matchAll(/\b(?:this|self|state|model|ctx|context)\.([A-Za-z_][A-Za-z0-9_]*)\s*(?:[+\-*/%]?=|\+\+|--)/g)).map((match) => match[1] || ''),
    ...Array.from(String(content || '').matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:[+\-*/%]?=|\+\+|--)/g)).map((match) => match[1] || ''),
  ];
  return uniq(tokens.filter((token) => {
    const lowered = String(token || '').toLowerCase();
    return lowered && !COMMON_CODE_TOKENS.has(lowered) && !CALL_KEYWORD_TOKENS.has(lowered);
  }));
}

function inferCodeRelations(readObservations, relatedFiles) {
  const relatedSet = new Set(uniq(relatedFiles).map((item) => item.toLowerCase()));
  const entries = (readObservations || []).map((observation) => ({ path: normalizePath(observation.path), content: String(observation.content || '') }))
    .filter((entry) => relatedSet.has(entry.path.toLowerCase()));
  const typeIndex = new Map();
  const methodIndex = new Map();
  const propertyIndex = new Map();
  const entriesByPath = new Map();

  for (const entry of entries) {
    const stem = entry.path.split('/').pop()?.replace(/\.[^.]+$/, '') || '';
    const definedTypes = collectDefinedTypes(entry.content, stem);
    const definedMethods = collectDefinedMethods(entry.content);
    const definedProperties = collectDefinedProperties(entry.content);
    entriesByPath.set(entry.path, { definedTypes, definedMethods, definedProperties });
    for (const token of definedTypes) if (!typeIndex.has(String(token).toLowerCase())) typeIndex.set(String(token).toLowerCase(), entry.path);
    for (const token of definedMethods) if (!methodIndex.has(String(token).toLowerCase())) methodIndex.set(String(token).toLowerCase(), entry.path);
    for (const token of definedProperties) if (!propertyIndex.has(String(token).toLowerCase())) propertyIndex.set(String(token).toLowerCase(), entry.path);
  }

  const edges = [];
  const seen = new Set();
  for (const entry of entries) {
    const defs = entriesByPath.get(entry.path) || { definedTypes: [], definedMethods: [], definedProperties: [] };
    const own = new Set([...defs.definedTypes, ...defs.definedMethods, ...defs.definedProperties].map((item) => String(item).toLowerCase()));
    for (const token of extractIdentifiers(entry.content).filter((item) => /^[A-Z]/.test(item) && !own.has(String(item).toLowerCase()))) {
      const target = typeIndex.get(String(token).toLowerCase());
      if (target && !METHOD_NOISE_NAMES.has(String(token).toLowerCase())) pushRelationEdge(edges, seen, entry.path, target, 'uses_type', token);
    }
    for (const match of entry.content.matchAll(/(?:\.|\b)([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)) {
      const token = String(match[1] || '').trim();
      const lowered = token.toLowerCase();
      if (!token || CALL_KEYWORD_TOKENS.has(lowered) || METHOD_NOISE_NAMES.has(lowered)) continue;
      const target = methodIndex.get(lowered);
      if (target) pushRelationEdge(edges, seen, entry.path, target, 'calls_method', token);
    }
    for (const token of extractUpdatedPropertyTokens(entry.content)) {
      const target = propertyIndex.get(String(token).toLowerCase());
      if (target && !METHOD_NOISE_NAMES.has(String(token).toLowerCase())) pushRelationEdge(edges, seen, entry.path, target, 'updates_state', token);
    }
  }
  return edges;
}

module.exports = {
  normalizePath,
  parseLineRange,
  uniq,
  stepSucceeded,
  successfulSteps,
  failedSteps,
  isTraceCandidatePath,
  grepQueriesFromTrace,
  grepItemsFromTrace,
  listFilesFromTrace,
  readWindowsFromTrace,
  readObservationsFromTrace,
  symbolOutlinesFromTrace,
  referencePathsFromTrace,
  summarizeObservation,
  extractIdentifiers,
  pickRepresentativeEvidence,
  inferCodeRelations,
};
