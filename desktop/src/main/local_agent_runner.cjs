const {
  normalizePath,
  uniq,
  failedSteps,
  summarizeObservation,
  extractIdentifiers,
  pickRepresentativeEvidence,
  inferCodeRelations,
  grepItemsFromTrace,
  listFilesFromTrace,
  readWindowsFromTrace,
  readObservationsFromTrace,
  symbolOutlinesFromTrace,
} = require('./local_agent_trace.cjs');
const {
  grepWorkspace,
  listWorkspaceFiles,
  readWorkspaceFile,
  findSymbolInWorkspace,
  findCallersInWorkspace,
  findReferencesInWorkspace,
  readSymbolSpanInWorkspace,
  symbolNeighborhoodInWorkspace,
  symbolOutlineInWorkspace,
} = require('./workspace.cjs');

const LOCAL_TRACE_READ_CHAR_LIMIT = 16000;
const FILE_READ_CHAR_LIMIT = 24000;
const DEFAULT_FILE_READ_END_LINE = 2400;
const MAX_TRACE_STEPS = 40;
const MAX_ROOT_SYMBOLS = 4;
const MAX_SUPPORT_SYMBOLS = 4;
const MAX_FRONTIER_DEPTH = 2;
const MAX_FRONTIER_EXPANSIONS = 8;
const MAX_FRONTIER_QUEUE_SIZE = 12;
const MAX_GREP_LIMIT = 30;
const MAX_LIST_LIMIT = 5000;
const MAX_ROOT_QUERY_CANDIDATES = 4;
const MAX_ROOT_PATHS_PER_QUERY = 3;
const MAX_ROOT_FILE_CANDIDATES = 6;
const MAX_ROOT_FILE_INSPECTIONS = 3;
const MAX_ROOT_GREPHITS_PER_QUERY = 12;
const MAX_ROOT_GREP_SCAN_LIMIT = 80;
const MAX_CORE_FILES = 4;
const MAX_SUPPORT_FILES = 4;
const MAX_RELATED_FILES = 8;
const MAX_RELATED_OWNER_READS = 3;
const MAX_BROAD_FILE_READS = 4;
const FLOW_OUTLINE_LIMIT = 320;
const CALL_KEYWORDS = new Set([
  'if',
  'for',
  'foreach',
  'while',
  'switch',
  'return',
  'catch',
  'using',
  'nameof',
  'typeof',
  'default',
  'base',
  'this',
  'new',
]);
const MEMBER_CALL_RE = /\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.|::|->)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
const DIRECT_CALL_RE = /\b([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
const CONTROL_SIGNAL_RE = /\b(if|for|foreach|while|switch|catch|try|return|await)\b/g;
const ASSIGNMENT_SIGNAL_RE = /(?:[A-Za-z_][A-Za-z0-9_]*|\)|\])\s*(?:[+\-*/%]?=|\+\+|--)/g;
const COMMENT_ONLY_LINE_RE = /^\s*(?:\/\/|#|\/\*|\*|<!--)/;
const INLINE_BLOCK_COMMENT_RE = /\/\*.*?\*\//g;
const INLINE_LINE_COMMENT_RE = /\/\/.*$/g;
const STRING_LITERAL_RE = /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g;
const EXECUTABLE_FLOW_PATH_RE = /\.(?:cs|vb|c|cc|cpp|cxx|h|hh|hpp|hxx|py|js|cjs|mjs|ts|tsx|jsx)$/i;
const MARKUP_FLOW_PATH_RE = /\.(?:xaml|xml|resx|json|yaml|yml|toml|ini|config|txt|md|rst|html|htm|css|scss|less)$/i;
const PROJECT_METADATA_PATH_RE = /\.(?:sln|csproj|vcxproj|vbproj|fsproj|props|targets)$/i;
const KOREAN_QUERY_NOISE_TOKENS = new Set([
  '\uC124\uBA85',
  '\uC124\uBA85\uD574\uC918',
  '\uC815\uB9AC',
  '\uC815\uB9AC\uD574\uC918',
  '\uC54C\uB824\uC918',
  '\uBCF4\uC5EC\uC918',
  '\uADF8\uB0E5',
  '\uC5B4\uB5BB\uAC8C',
  '\uBB50\uC57C',
  '\uB54C\uBB38',
  '\uAE30\uC900',
  '\uC911\uC2EC',
  '\uAD00\uB828',
  '\uB300\uD574',
]);
const FLOW_QUESTION_RE = /\b(flow|path|caller|callee|call chain|workflow|pipeline|entry|sink)\b|(\uD750\uB984|\uACFC\uC815|\uD638\uCD9C|\uACBD\uB85C|\uC5B4\uB514|\uC9C4\uC785|\uCD9C\uAD6C)/i;
const FLOW_META_TERMS = new Set([
  'flow',
  'path',
  'caller',
  'callee',
  'workflow',
  'pipeline',
  'entry',
  'sink',
  'code',
  'explain',
  'analysis',
  'describe',
  '\uD750\uB984',
  '\uACFC\uC815',
  '\uD638\uCD9C',
  '\uACBD\uB85C',
  '\uC124\uBA85',
  '\uBD84\uC11D',
]);
const BROAD_ANCHOR_TERMS = new Set([
  'image',
  'images',
  'video',
  'file',
  'files',
  'data',
  'result',
  'results',
  'view',
  'screen',
  'ui',
  '\uC601\uC0C1',
  '\uC774\uBBF8\uC9C0',
  '\uD654\uBA74',
  '\uD30C\uC77C',
  '\uB370\uC774\uD130',
  '\uACB0\uACFC',
  '\uC815\uBCF4',
]);

function pathBasename(value) {
  const normalized = normalizePath(value);
  return normalized.split('/').pop() || normalized;
}

function pathStem(value) {
  return pathBasename(value).replace(/\.[^.]+$/, '');
}

function pathDirname(value) {
  const normalized = normalizePath(value);
  const lastSlash = normalized.lastIndexOf('/');
  return lastSlash >= 0 ? normalized.slice(0, lastSlash) : '';
}

function pathExtname(value) {
  const normalized = pathBasename(value).toLowerCase();
  const lastDot = normalized.lastIndexOf('.');
  return lastDot >= 0 ? normalized.slice(lastDot) : '';
}

function pathSegments(value) {
  return normalizePath(value)
    .split('/')
    .map((item) => String(item || '').trim())
    .filter(Boolean);
}

function sharedPrefixDepth(left, right) {
  const leftParts = pathSegments(left);
  const rightParts = pathSegments(right);
  let depth = 0;
  for (let index = 0; index < Math.min(leftParts.length, rightParts.length); index += 1) {
    if (leftParts[index].toLowerCase() !== rightParts[index].toLowerCase()) {
      break;
    }
    depth += 1;
  }
  return depth;
}

function splitSymbolParts(value) {
  return String(value || '')
    .trim()
    .split(/_|(?=[A-Z])/)
    .map((item) => String(item || '').trim())
    .filter(Boolean);
}

function extractNativeQuestionTerms(question) {
  const weights = new Map();
  for (const raw of String(question || '').match(/[\uAC00-\uD7A3]{2,}/g) || []) {
    const token = String(raw || '')
      .trim()
      .replace(/(?:\uD574\uC918|\uD574\uC694|\uD569\uB2C8\uB2E4)$/u, '');
    if (!token || KOREAN_QUERY_NOISE_TOKENS.has(token)) continue;
    const score = token.length;
    const current = weights.get(token) || 0;
    weights.set(token, Math.max(current, score));
  }
  return Array.from(weights.entries())
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0) || String(a[0] || '').localeCompare(String(b[0] || '')))
    .map(([token]) => token);
}

function extractAsciiQuestionTerms(question) {
  const weights = new Map();
  for (const raw of String(question || '').match(/[A-Za-z_][A-Za-z0-9_]{2,}/g) || []) {
    const rawToken = String(raw || '').trim();
    const token = rawToken.toLowerCase();
    if (!token) continue;
    const current = weights.get(token) || 0;
    weights.set(token, Math.max(current, token.length));
    for (const part of splitSymbolParts(rawToken)) {
      const normalized = String(part || '').trim().toLowerCase();
      if (normalized.length < 3) continue;
      const currentPart = weights.get(normalized) || 0;
      weights.set(normalized, Math.max(currentPart, normalized.length + 2));
    }
  }
  return Array.from(weights.entries())
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0) || String(a[0] || '').localeCompare(String(b[0] || '')))
    .map(([token]) => token);
}

function expandQuestionTermVariants(terms = []) {
  const weights = new Map();
  for (const raw of Array.isArray(terms) ? terms : []) {
    const token = String(raw || '').trim().toLowerCase();
    if (!token) continue;
    for (const part of splitSymbolParts(token)) {
      const normalized = String(part || '').trim().toLowerCase();
      if (normalized.length < 3) continue;
      const current = weights.get(normalized) || 0;
      weights.set(normalized, Math.max(current, normalized.length + 2));
    }
    if (/[_-]/.test(token)) {
      const compact = token.replace(/[_-]+/g, '');
      if (compact.length >= 4) {
        const current = weights.get(compact) || 0;
        weights.set(compact, Math.max(current, compact.length));
      }
    }
  }
  return Array.from(weights.entries())
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0) || String(a[0] || '').localeCompare(String(b[0] || '')))
    .map(([token]) => token);
}

function isFlowQuestion(question) {
  return FLOW_QUESTION_RE.test(String(question || '').trim());
}

function questionTermPriority(term) {
  const token = String(term || '').trim();
  if (!token) {
    return -100;
  }
  let score = token.length;
  if (/[\uAC00-\uD7A3]/.test(token)) score += 2;
  if (/[A-Z_]/.test(token)) score += 12;
  if (splitSymbolParts(token).length >= 2) score += 8;
  if (FLOW_META_TERMS.has(token.toLowerCase())) score -= 24;
  if (BROAD_ANCHOR_TERMS.has(token.toLowerCase())) score -= 10;
  return score;
}

function isBroadAnchorTerm(term) {
  const token = String(term || '').trim().toLowerCase();
  if (!token) return true;
  return FLOW_META_TERMS.has(token) || BROAD_ANCHOR_TERMS.has(token);
}

function hasSpecificQuestionTerms(questionTerms = []) {
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const raw = String(term || '').trim();
    const lowered = raw.toLowerCase();
    if (!lowered || isBroadAnchorTerm(lowered)) continue;
    if (/[\uAC00-\uD7A3]/.test(raw) && raw.length >= 4) return true;
    if (splitSymbolParts(raw).length >= 2) return true;
    if (/[A-Z_]/.test(raw)) return true;
    if (lowered.length >= 5) return true;
  }
  return false;
}

function normalizeQuestionTerms(question) {
  const nativeTerms = extractNativeQuestionTerms(question);
  const asciiTerms = extractAsciiQuestionTerms(question);
  const identifierTerms = extractIdentifiers(question)
    .map((item) => String(item || '').trim().toLowerCase())
    .filter(Boolean);
  return uniq([
    ...identifierTerms,
    ...asciiTerms,
    ...nativeTerms
      .map((item) => String(item || '').trim().toLowerCase())
      .filter(Boolean),
    ...expandQuestionTermVariants([...identifierTerms, ...asciiTerms, ...nativeTerms])
      .map((item) => String(item || '').trim().toLowerCase())
      .filter(Boolean),
  ]);
}

function identifierStructureScore(symbol) {
  const token = String(symbol || '').trim();
  if (!token) {
    return -100;
  }
  const parts = splitSymbolParts(token);
  let score = 0;

  if (token.length >= 5) score += Math.min(14, Math.floor(token.length / 2));
  if (parts.length >= 2) score += Math.min(18, parts.length * 6);
  if (parts.length >= 3) score += 6;
  if (token.includes('_')) score += 5;
  if (/[A-Z].*[A-Z]/.test(token)) score += 6;
  if (/^[A-Z]/.test(token)) score += 3;
  if (/\d/.test(token)) score += 2;

  if (parts.length <= 1 && token.length <= 4) score -= 26;
  if (parts.length <= 1 && token.toLowerCase() === token && token.length <= 8) score -= 12;

  return score;
}

function signalScore(symbol, { mode = 'anchor' } = {}) {
  const token = String(symbol || '').trim();
  if (!token) {
    return -100;
  }
  const parts = splitSymbolParts(token);
  let score = identifierStructureScore(token);
  if (mode === 'anchor' && parts.length >= 2) score += 4;
  if (mode === 'support' && parts.length >= 2) score += 2;
  return score;
}

function isLowSignalSymbol(symbol, { mode = 'anchor' } = {}) {
  return signalScore(symbol, { mode }) < -4;
}

function countMatches(text, regex) {
  const matches = String(text || '').match(regex);
  return Array.isArray(matches) ? matches.length : 0;
}

function isCommentOnlyLine(text) {
  return COMMENT_ONLY_LINE_RE.test(String(text || '').trim());
}

function stripInlineComments(text) {
  return String(text || '')
    .replace(INLINE_BLOCK_COMMENT_RE, ' ')
    .replace(INLINE_LINE_COMMENT_RE, ' ')
    .trim();
}

function stripStringLiterals(text) {
  return String(text || '').replace(STRING_LITERAL_RE, '""');
}

function countDistinctQuestionTerms(text, questionTerms) {
  const lowered = String(text || '').toLowerCase();
  const distinct = new Set();
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (lowered.includes(loweredTerm)) distinct.add(loweredTerm);
  }
  return distinct.size;
}

function pathFlowBias(pathValue, { preferFlow = false } = {}) {
  const normalized = normalizePath(pathValue).toLowerCase();
  if (!normalized) {
    return 0;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules|packages|\.tmp)\//i.test(normalized)) {
    return -48;
  }
  if (EXECUTABLE_FLOW_PATH_RE.test(normalized)) {
    return preferFlow ? 26 : 12;
  }
  if (PROJECT_METADATA_PATH_RE.test(normalized)) {
    return preferFlow ? -32 : -16;
  }
  if (MARKUP_FLOW_PATH_RE.test(normalized)) {
    return preferFlow ? -28 : -10;
  }
  return 0;
}

function buildCandidateReadWindow(candidate, { preferFlow = false } = {}) {
  const rankedHits = (Array.isArray(candidate?.grepHits) ? candidate.grepHits : [])
    .map((item) => ({
      ...item,
      __line: Number(item?.line || 0),
      __score: Number(item?.score || 0),
    }))
    .filter((item) => item.__line > 0)
    .sort((left, right) => Number(right.__score || 0) - Number(left.__score || 0) || Number(left.__line || 0) - Number(right.__line || 0));
  if (rankedHits.length === 0) {
    return {
      startLine: 1,
      endLine: preferFlow ? 800 : 400,
    };
  }
  const center = rankedHits[0].__line;
  const radius = preferFlow ? 120 : 80;
  return {
    startLine: Math.max(1, center - radius),
    endLine: Math.max(center + radius, center + 40),
  };
}

function dedupeBy(items, keySelector) {
  const out = [];
  const seen = new Set();
  for (const item of Array.isArray(items) ? items : []) {
    const key = String(keySelector(item) || '').trim().toLowerCase();
    if (!key || seen.has(key)) {
      continue;
    }
    seen.add(key);
    out.push(item);
  }
  return out;
}

function outlineLineProximityScore(lineValue, focusLines, kind) {
  const line = Number(lineValue || 0);
  const source = (Array.isArray(focusLines) ? focusLines : []).map((item) => Number(item || 0)).filter((item) => item > 0);
  if (!line || source.length === 0) {
    return 0;
  }
  const minDistance = Math.min(...source.map((item) => Math.abs(item - line)));
  if (!Number.isFinite(minDistance)) {
    return 0;
  }
  const isExecutableKind = ['method', 'function', 'event'].includes(String(kind || '').trim().toLowerCase());
  if (minDistance <= 40) return isExecutableKind ? 48 : 16;
  if (minDistance <= 120) return isExecutableKind ? 32 : 10;
  if (minDistance <= 240) return isExecutableKind ? 18 : 4;
  return isExecutableKind ? -8 : -16;
}

function outlineDirectTermHits(item, questionTerms) {
  const loweredName = String(item?.name || '').trim().toLowerCase();
  const loweredText = String(item?.text || '').trim().toLowerCase();
  let hits = 0;
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (loweredName.includes(loweredTerm) || loweredText.includes(loweredTerm)) hits += 1;
  }
  return hits;
}

function outlineVisibilityScore(text, kind, { preferFlow = false, directTermHits = 0 } = {}) {
  const lowered = String(text || '').trim().toLowerCase();
  const loweredKind = String(kind || '').trim().toLowerCase();
  const isExecutableKind = ['method', 'function', 'event'].includes(loweredKind);
  if (/\bpublic\b/.test(lowered)) {
    return isExecutableKind
      ? (preferFlow ? 28 : 14)
      : 8;
  }
  if (/\bprotected\b/.test(lowered) || /\binternal\b/.test(lowered)) {
    return isExecutableKind
      ? (preferFlow ? 12 : 6)
      : 4;
  }
  if (/\bprivate\b/.test(lowered)) {
    return isExecutableKind
      ? (preferFlow && directTermHits === 0 ? -18 : -8)
      : -4;
  }
  return 0;
}

function outlineTopLevelFlowScore(lineValue, kind, { preferFlow = false, focusLines = [] } = {}) {
  if (!preferFlow || (Array.isArray(focusLines) && focusLines.length > 0)) {
    return 0;
  }
  const line = Number(lineValue || 0);
  if (!line) {
    return 0;
  }
  const loweredKind = String(kind || '').trim().toLowerCase();
  const isExecutableKind = ['method', 'function', 'event'].includes(loweredKind);
  if (isExecutableKind) {
    if (line <= 400) return 34;
    if (line <= 900) return 24;
    if (line <= 1600) return 12;
    if (line <= 2400) return 0;
    return -18;
  }
  if (loweredKind === 'type') {
    return line <= 160 ? 6 : -6;
  }
  return 0;
}

function outlineEntrySignalScore(name, { preferFlow = false } = {}) {
  if (!preferFlow) {
    return 0;
  }
  const firstPart = splitSymbolParts(name)[0];
  const lowered = String(firstPart || '').trim().toLowerCase();
  if (!lowered) {
    return 0;
  }
  if (['select', 'load', 'handle', 'init', 'initialize', 'perform', 'start', 'open', 'update', 'refresh'].includes(lowered)) {
    return 22;
  }
  if (['generate', 'create', 'build', 'apply'].includes(lowered)) {
    return 8;
  }
  return 0;
}

function outlineHandlerPenalty(name, { preferFlow = false, focusLines = [] } = {}) {
  if (!preferFlow || (Array.isArray(focusLines) && focusLines.length > 0)) {
    return 0;
  }
  const token = String(name || '').trim();
  if (!token) {
    return 0;
  }
  if (/(?:^On[A-Z]|Click|Clicked|Render|Renders|Changed|Changing|Mouse|Key|Drag|Drop|Preview|Selection|Loaded|Closing|Opened|Ortho)/.test(token)) {
    return -26;
  }
  return 0;
}

function outlineCommentPenalty(text) {
  return /^\s*(?:\/\/|\/\*)/.test(String(text || '').trim()) ? -48 : 0;
}

function chooseBestOutlineItems(outlineItems, questionTerms, { focusLines = [], preferFlow = false } = {}) {
  const terms = new Set(Array.isArray(questionTerms) ? questionTerms : []);
  const effectiveFocusLines = preferFlow && !hasSpecificQuestionTerms(questionTerms) ? [] : focusLines;
  const candidates = (Array.isArray(outlineItems) ? outlineItems : [])
    .filter((item) => ['method', 'function', 'event', 'type'].includes(String(item?.kind || '').trim().toLowerCase()))
    .map((item) => {
      const name = String(item?.name || '').trim();
      const kind = String(item?.kind || '').trim().toLowerCase();
      const loweredName = name.toLowerCase();
      const directTermHits = outlineDirectTermHits(item, questionTerms);
      let score = signalScore(name, { mode: 'anchor' });
      if (kind === 'method') score += 30;
      if (kind === 'function') score += 28;
      if (kind === 'event') score += 24;
      if (kind === 'type') score += 16;
      score += outlineLineProximityScore(item?.line, effectiveFocusLines, kind);
      score += outlineVisibilityScore(item?.text, kind, { preferFlow, directTermHits });
      score += outlineTopLevelFlowScore(item?.line, kind, { preferFlow, focusLines: effectiveFocusLines });
      score += outlineEntrySignalScore(name, { preferFlow });
      score += outlineHandlerPenalty(name, { preferFlow, focusLines: effectiveFocusLines });
      score += outlineCommentPenalty(item?.text);
      for (const term of terms) {
        if (loweredName.includes(term)) score += 20;
        if (String(item?.text || '').toLowerCase().includes(term)) score += 8;
      }
      if (preferFlow && kind === 'type' && Array.isArray(effectiveFocusLines) && effectiveFocusLines.length > 0) score -= 16;
      if (isLowSignalSymbol(name, { mode: 'anchor' })) score -= 20;
      return { ...item, __score: score };
    })
    .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || Number(a.line || 0) - Number(b.line || 0));

  const filtered = candidates.filter((item) => !isLowSignalSymbol(item?.name, { mode: 'anchor' }));
  const source = filtered.length > 0 ? filtered : candidates;
  return dedupeBy(source, (item) => item?.name).slice(0, MAX_ROOT_SYMBOLS);
}

function extractCallTokens(content, { mode = 'support' } = {}) {
  const counts = new Map();
  const text = String(content || '');
  const push = (token) => {
    const normalized = String(token || '').trim();
    if (!normalized) return;
    const lowered = normalized.toLowerCase();
    if (CALL_KEYWORDS.has(lowered)) return;
    if (isLowSignalSymbol(normalized, { mode })) return;
    counts.set(normalized, (counts.get(normalized) || 0) + 1);
  };

  for (const match of text.matchAll(MEMBER_CALL_RE)) {
    push(match[2] || '');
  }
  for (const match of text.matchAll(DIRECT_CALL_RE)) {
    push(match[1] || '');
  }

  return Array.from(counts.entries())
    .map(([symbol, count]) => ({ symbol, count }))
    .sort((a, b) => Number(b.count || 0) - Number(a.count || 0) || String(a.symbol || '').localeCompare(String(b.symbol || '')));
}

function scoreReadWindow(window, outlineNames, questionTerms, selectedPath) {
  const symbol = String(window?.symbol || '').trim();
  const content = String(window?.content || '');
  const loweredContent = content.toLowerCase();
  const callTokens = extractCallTokens(content, { mode: 'anchor' });
  const questionSet = new Set(Array.isArray(questionTerms) ? questionTerms : []);
  let score = 0;

  score += signalScore(symbol, { mode: 'anchor' });
  score += callTokens.length * 10;
  score += callTokens.reduce((sum, item) => sum + Number(item.count || 0), 0) * 3;
  score += countMatches(content, CONTROL_SIGNAL_RE) * 2;
  score += countMatches(content, ASSIGNMENT_SIGNAL_RE) * 2;
  if (normalizePath(window?.path).toLowerCase() === normalizePath(selectedPath).toLowerCase()) {
    score += 24;
  }
  for (const term of questionSet) {
    if (String(symbol || '').toLowerCase().includes(term)) score += 22;
    if (loweredContent.includes(term)) score += 10;
  }
  for (const outlineName of Array.isArray(outlineNames) ? outlineNames : []) {
    const token = String(outlineName || '').trim();
    if (!token || token.toLowerCase() === String(symbol || '').toLowerCase()) continue;
    if (loweredContent.includes(token.toLowerCase())) score += 4;
  }
  return score;
}

function choosePrimaryWindow(trace, selectedPath, outlineItems, questionTerms, { focusLines = [], preferFlow = false } = {}) {
  const outlineNames = (Array.isArray(outlineItems) ? outlineItems : []).map((item) => String(item?.name || '').trim()).filter(Boolean);
  const effectiveFocusLines = preferFlow && !hasSpecificQuestionTerms(questionTerms) ? [] : focusLines;
  const rankedOutlineItems = chooseBestOutlineItems(outlineItems, questionTerms, {
    focusLines: effectiveFocusLines,
    preferFlow,
  });
  if (preferFlow && !hasSpecificQuestionTerms(questionTerms)) {
    for (const candidate of rankedOutlineItems) {
      const candidateSymbol = String(candidate?.name || '').trim().toLowerCase();
      if (!candidateSymbol) continue;
      const matchedWindow = readWindowsFromTrace(trace).find((item) => {
        return normalizePath(item.path).toLowerCase() === normalizePath(selectedPath).toLowerCase()
          && String(item.symbol || '').trim().toLowerCase() === candidateSymbol;
      });
      if (matchedWindow) {
        return matchedWindow;
      }
    }
  }
  const outlineMetaByName = new Map();
  for (const item of Array.isArray(outlineItems) ? outlineItems : []) {
    const name = String(item?.name || '').trim();
    if (!name) continue;
    const key = name.toLowerCase();
    const current = outlineMetaByName.get(key);
    if (!current || Number(item?.line || 0) < Number(current?.line || 0)) {
      outlineMetaByName.set(key, item);
    }
  }
  const windows = readWindowsFromTrace(trace)
    .filter((item) => String(item?.symbol || '').trim())
    .filter((item) => !isLowSignalSymbol(item?.symbol, { mode: 'anchor' }))
    .map((item) => ({
      ...item,
      __score: (() => {
        let score = scoreReadWindow(item, outlineNames, questionTerms, selectedPath);
        const outlineMeta = outlineMetaByName.get(String(item?.symbol || '').trim().toLowerCase()) || null;
        if (outlineMeta) {
          const kind = String(outlineMeta?.kind || '').trim().toLowerCase();
          const directTermHits = outlineDirectTermHits(outlineMeta, questionTerms);
          score += outlineVisibilityScore(outlineMeta?.text, kind, { preferFlow, directTermHits });
          score += outlineTopLevelFlowScore(outlineMeta?.line, kind, { preferFlow, focusLines: effectiveFocusLines });
          score += outlineEntrySignalScore(outlineMeta?.name, { preferFlow });
          score += outlineHandlerPenalty(outlineMeta?.name, { preferFlow, focusLines: effectiveFocusLines });
          score += outlineCommentPenalty(outlineMeta?.text);
          const proximityScore = outlineLineProximityScore(outlineMeta?.line, effectiveFocusLines, kind);
          score += directTermHits > 0 ? proximityScore : Math.trunc(proximityScore / 2);
        }
        return score;
      })(),
    }))
    .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || Number(a.startLine || 0) - Number(b.startLine || 0) || String(a.path || '').localeCompare(String(b.path || '')));
  return windows[0] || null;
}

function chooseSupportSymbols(primaryWindow, extraWindows, outlineItems, questionTerms, exclusions = []) {
  const localSymbols = new Set(
    (Array.isArray(outlineItems) ? outlineItems : [])
      .map((item) => String(item?.name || '').trim())
      .filter(Boolean)
      .map((item) => item.toLowerCase()),
  );
  const excluded = new Set((Array.isArray(exclusions) ? exclusions : []).map((item) => String(item || '').trim().toLowerCase()).filter(Boolean));
  const questionSet = new Set(Array.isArray(questionTerms) ? questionTerms : []);
  const counts = new Map();

  for (const window of [primaryWindow, ...(Array.isArray(extraWindows) ? extraWindows : [])]) {
    if (!window) continue;
    for (const token of extractCallTokens(window.content || '', { mode: 'support' })) {
      const symbol = String(token.symbol || '').trim();
      const lowered = symbol.toLowerCase();
      if (!symbol || excluded.has(lowered)) continue;
      const localHit = localSymbols.has(lowered);
      const repeatedHit = Number(token.count || 0) >= 2;
      const questionHit = Array.from(questionSet).some((term) => lowered.includes(term));
      if (!localHit && !repeatedHit && !questionHit) continue;
      let score = Number(token.count || 0) * 10 + signalScore(symbol, { mode: 'support' });
      if (localHit) score += 18;
      for (const term of questionSet) {
        if (lowered.includes(term)) score += 10;
      }
      counts.set(symbol, Math.max(score, counts.get(symbol) || -999));
    }
  }

  return Array.from(counts.entries())
    .map(([symbol, score]) => ({ symbol, score }))
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.symbol || '').localeCompare(String(b.symbol || '')))
    .slice(0, MAX_SUPPORT_SYMBOLS)
    .map((item) => item.symbol);
}

function anchorTerms(question, pathValue) {
  return uniq([
    ...normalizeQuestionTerms(question),
    ...splitSymbolParts(pathStem(pathValue))
      .map((item) => item.toLowerCase())
      .filter((item) => item.length >= 3),
  ]);
}

function scoreFileQuestionAlignment(pathValue, content, questionTerms) {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  const stem = pathStem(pathValue).toLowerCase();
  const loweredContent = String(content || '').toLowerCase();
  let score = 0;

  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (stem.includes(loweredTerm)) score += 18;
    else if (normalizedPath.includes(loweredTerm)) score += 10;
    if (loweredContent.includes(loweredTerm)) score += /[\uac00-\ud7a3]/i.test(loweredTerm) ? 2 : 3;
    const matchCount = loweredContent.split(loweredTerm).length - 1;
    if (matchCount >= 2) score += 3;
  }

  return score;
}

function hasReadSymbol(trace, pathValue, symbol) {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  const normalizedSymbol = String(symbol || '').trim().toLowerCase();
  if (!normalizedPath || !normalizedSymbol) {
    return false;
  }
  return readWindowsFromTrace(trace).some((item) => {
    return normalizePath(item.path).toLowerCase() === normalizedPath
      && String(item.symbol || '').trim().toLowerCase() === normalizedSymbol;
  });
}

function pickBestCallerHit(items, selectedPath) {
  return (Array.isArray(items) ? items : [])
    .map((item) => {
      const pathValue = normalizePath(item?.path);
      let score = Number(item?.score || 0);
      if (selectedPath && pathValue.toLowerCase() === normalizePath(selectedPath).toLowerCase()) score += 24;
      score += sharedPrefixDepth(pathValue, selectedPath) * 4;
      return { ...item, __score: score };
    })
    .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || String(a.path || '').localeCompare(String(b.path || '')))[0] || null;
}

function pickNeighborhoodOwner(items, baseSymbol = '') {
  const preferred = (Array.isArray(items) ? items : [])
    .filter((item) => ['method', 'function', 'event', 'type'].includes(String(item?.kind || '').trim().toLowerCase()))
    .filter((item) => {
      const symbol = String(item?.name || '').trim();
      if (!symbol) return false;
      if (String(baseSymbol || '').trim().toLowerCase() === symbol.toLowerCase()) {
        return false;
      }
      return !isLowSignalSymbol(symbol, { mode: 'anchor' });
    });
  const source = preferred.length > 0 ? preferred : (Array.isArray(items) ? items : []);
  return source[0] || null;
}

function pickBestDefinition(items, selectedPath) {
  return (Array.isArray(items) ? items : [])
    .map((item) => {
      const pathValue = normalizePath(item?.path);
      let score = Number(item?.score || 0);
      if (selectedPath && pathValue.toLowerCase() === normalizePath(selectedPath).toLowerCase()) score += 20;
      score += sharedPrefixDepth(pathValue, selectedPath) * 4;
      return { ...item, __score: score };
    })
    .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || String(a.path || '').localeCompare(String(b.path || '')))[0] || null;
}

function rankRelatedOwnerHits(items, selectedPath) {
  return dedupeBy(
    (Array.isArray(items) ? items : [])
      .map((item) => {
        const pathValue = normalizePath(item?.path);
        let score = Number(item?.score || 0);
        if (selectedPath && pathValue.toLowerCase() === normalizePath(selectedPath).toLowerCase()) score += 24;
        score += sharedPrefixDepth(pathValue, selectedPath) * 4;
        if (Number(item?.line || 0) > 0) score += 2;
        return { ...item, __score: score };
      })
      .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || String(a.path || '').localeCompare(String(b.path || ''))),
    (item) => normalizePath(item?.path),
  );
}

function hasReadPath(trace, pathValue) {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  if (!normalizedPath) {
    return false;
  }
  return readWindowsFromTrace(trace).some((item) => normalizePath(item.path).toLowerCase() === normalizedPath);
}

function findReadWindow(trace, pathValue, symbol = '') {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  const normalizedSymbol = String(symbol || '').trim().toLowerCase();
  return readWindowsFromTrace(trace).find((item) => {
    if (normalizePath(item.path).toLowerCase() !== normalizedPath) {
      return false;
    }
    if (!normalizedSymbol) {
      return true;
    }
    return String(item.symbol || '').trim().toLowerCase() === normalizedSymbol;
  }) || null;
}

function relationPriority(relation) {
  const token = String(relation || '').trim().toLowerCase();
  if (token === 'anchor') return 4;
  if (token === 'caller_owner') return 3;
  if (token === 'related_owner') return 2;
  if (token === 'callee_definition') return 1;
  return 0;
}

function recordFlowNode(nodes, node) {
  if (!node?.path || !node?.symbol) {
    return;
  }
  const normalizedPath = normalizePath(node.path);
  const normalizedSymbol = String(node.symbol || '').trim();
  if (!normalizedPath || !normalizedSymbol) {
    return;
  }
  const key = `${normalizedPath}::${normalizedSymbol}`.toLowerCase();
  const existingIndex = (Array.isArray(nodes) ? nodes : []).findIndex((item) => {
    return `${normalizePath(item?.path)}::${String(item?.symbol || '').trim()}`.toLowerCase() === key;
  });
  const merged = {
    path: normalizedPath,
    symbol: normalizedSymbol,
    line: Number(node.line || 0),
    relation: String(node.relation || '').trim(),
    baseSymbol: String(node.baseSymbol || '').trim(),
    depth: Number(node.depth || 0),
    covered: node.covered !== false,
    discovered: node.discovered !== false,
    searchCompleted: node.searchCompleted !== false,
    reason: String(node.reason || '').trim(),
  };
  if (existingIndex < 0) {
    nodes.push(merged);
    return;
  }
  const current = nodes[existingIndex] || {};
  nodes[existingIndex] = {
    ...current,
    ...merged,
    relation: relationPriority(merged.relation) >= relationPriority(current.relation) ? merged.relation : current.relation,
    baseSymbol: merged.baseSymbol || current.baseSymbol || '',
    line: Number(merged.line || current.line || 0),
    depth: Math.min(
      Number.isFinite(Number(current.depth)) ? Number(current.depth) : Number(merged.depth || 0),
      Number(merged.depth || 0),
    ),
    covered: current.covered !== false || merged.covered !== false,
    discovered: current.discovered !== false || merged.discovered !== false,
    searchCompleted: current.searchCompleted !== false || merged.searchCompleted !== false,
    reason: merged.reason || current.reason || '',
  };
}

function recordOpenFrontier(frontiers, node) {
  if (!node?.symbol) {
    return;
  }
  const normalizedPath = normalizePath(node.path || '');
  const normalizedSymbol = String(node.symbol || '').trim();
  if (!normalizedSymbol) {
    return;
  }
  const key = `${normalizedPath}::${normalizedSymbol}`.toLowerCase();
  if ((Array.isArray(frontiers) ? frontiers : []).some((item) => {
    return `${normalizePath(item?.path || '')}::${String(item?.symbol || '').trim()}`.toLowerCase() === key;
  })) {
    return;
  }
  frontiers.push({
    path: normalizedPath,
    symbol: normalizedSymbol,
    line: Number(node.line || 0),
    relation: String(node.relation || '').trim(),
    baseSymbol: String(node.baseSymbol || '').trim(),
    depth: Number(node.depth || 0),
    covered: false,
    discovered: true,
    searchCompleted: false,
    reason: String(node.reason || '').trim(),
  });
}

function enqueueFrontierNode(queue, queuedKeys, frontiers, node) {
  if (!node?.path || !node?.symbol) {
    return false;
  }
  const normalizedPath = normalizePath(node.path);
  const normalizedSymbol = String(node.symbol || '').trim();
  if (!normalizedPath || !normalizedSymbol) {
    return false;
  }
  const key = `${normalizedPath}::${normalizedSymbol}`.toLowerCase();
  if (queuedKeys.has(key)) {
    return false;
  }
  if ((Array.isArray(queue) ? queue : []).length >= MAX_FRONTIER_QUEUE_SIZE) {
    recordOpenFrontier(frontiers, { ...node, reason: node.reason || 'queue_limit' });
    return false;
  }
  queuedKeys.add(key);
  queue.push({
    ...node,
    path: normalizedPath,
    symbol: normalizedSymbol,
  });
  return true;
}

function getOutlineItemsForPath(trace, pathValue) {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  const outlines = symbolOutlinesFromTrace(trace)
    .filter((item) => normalizePath(item.path).toLowerCase() === normalizedPath)
    .sort((left, right) => {
      const leftCount = Array.isArray(left?.items) ? left.items.length : 0;
      const rightCount = Array.isArray(right?.items) ? right.items.length : 0;
      return rightCount - leftCount;
    });
  return Array.isArray(outlines[0]?.items) ? outlines[0].items : [];
}

async function ensureOutlineItems(trace, workspacePath, pathValue, { preferFlow = false } = {}) {
  const existing = getOutlineItemsForPath(trace, pathValue);
  if (existing.length > 0) {
    return existing;
  }
  const outlineObservation = await pushTraceStep(
    trace,
    workspacePath,
    `inspect local declarations in ${pathBasename(pathValue)}`,
    'symbol_outline',
    {
      path: pathValue,
      limit: preferFlow ? FLOW_OUTLINE_LIMIT : 120,
    },
  );
  return Array.isArray(outlineObservation?.items) ? outlineObservation.items : [];
}

function shouldFollowDefinition(pathValue, {
  rootPath,
  currentPath,
  questionTerms = [],
  symbol = '',
  preferFlow = false,
} = {}) {
  const normalizedPath = normalizePath(pathValue);
  if (!normalizedPath) {
    return false;
  }
  const rootPrefix = sharedPrefixDepth(normalizedPath, rootPath);
  const currentPrefix = sharedPrefixDepth(normalizedPath, currentPath);
  const questionAligned = (Array.isArray(questionTerms) ? questionTerms : []).some((term) => {
    return String(symbol || '').toLowerCase().includes(String(term || '').toLowerCase());
  });
  const nearestPrefix = Math.max(rootPrefix, currentPrefix);
  let score = 0;
  score += pathFlowBias(normalizedPath, { preferFlow });
  score += rootPrefix * 6;
  score += currentPrefix * 6;
  score += Math.min(18, scoreFileQuestionAlignment(normalizedPath, '', questionTerms));
  if (pathDirname(normalizedPath).toLowerCase() === pathDirname(currentPath).toLowerCase()) score += 12;
  if (pathExtname(normalizedPath) === pathExtname(currentPath)) score += 4;
  if (questionAligned) score += 8;
  if (nearestPrefix === 0) {
    return questionAligned && score >= (preferFlow ? 28 : 20);
  }
  if (preferFlow && nearestPrefix < 2 && !questionAligned) {
    return score >= 24;
  }
  return score >= (preferFlow ? 16 : 10);
}

async function resolveSupportSymbolRead(trace, workspacePath, symbol, {
  rootPath,
  currentPath,
  currentSymbol,
  outlineItems = [],
  questionTerms = [],
  preferFlow = false,
  relation = 'callee_definition',
  depth = 1,
} = {}) {
  const normalizedSymbol = String(symbol || '').trim();
  if (!normalizedSymbol) {
    return { node: null, frontier: null };
  }
  const localOutlineMatch = (Array.isArray(outlineItems) ? outlineItems : []).find((item) => {
    return String(item?.name || '').trim().toLowerCase() === normalizedSymbol.toLowerCase();
  });
  if (localOutlineMatch) {
    if (!hasReadSymbol(trace, currentPath, normalizedSymbol)) {
      await pushTraceStep(trace, workspacePath, `read the local support symbol span for ${normalizedSymbol}`, 'read_symbol_span', {
        path: currentPath,
        symbol: normalizedSymbol,
        lineHint: Number(localOutlineMatch.line || 0),
        maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
      });
    }
    const localWindow = findReadWindow(trace, currentPath, normalizedSymbol);
    if (localWindow) {
      return {
        node: {
          path: normalizePath(localWindow.path || currentPath),
          symbol: normalizedSymbol,
          line: Number(localWindow.startLine || localOutlineMatch.line || 0),
          relation,
          baseSymbol: currentSymbol,
          depth,
        },
        frontier: null,
      };
    }
  }

  const definitionObservation = await pushTraceStep(trace, workspacePath, `resolve the support symbol definition for ${normalizedSymbol}`, 'find_symbol', {
    symbol: normalizedSymbol,
    limit: 12,
  });
  const bestDefinition = pickBestDefinition(definitionObservation?.items, currentPath || rootPath);
  if (!bestDefinition || !bestDefinition.path) {
    return {
      node: null,
      frontier: {
        path: '',
        symbol: normalizedSymbol,
        relation,
        baseSymbol: currentSymbol,
        depth,
        reason: 'definition_not_found',
      },
    };
  }
  if (!shouldFollowDefinition(bestDefinition.path, {
    rootPath,
    currentPath,
    questionTerms,
    symbol: normalizedSymbol,
    preferFlow,
  })) {
    return {
      node: null,
      frontier: {
        path: normalizePath(bestDefinition.path),
        symbol: normalizedSymbol,
        relation,
        baseSymbol: currentSymbol,
        depth,
        line: Number(bestDefinition.line || 0),
        reason: 'definition_low_relevance',
      },
    };
  }
  if (!hasReadSymbol(trace, bestDefinition.path, normalizedSymbol)) {
    await pushTraceStep(trace, workspacePath, `read the support symbol span for ${normalizedSymbol}`, 'read_symbol_span', {
      path: bestDefinition.path,
      symbol: normalizedSymbol,
      lineHint: Number(bestDefinition.line || 0),
      maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
    });
  }
  const supportWindow = findReadWindow(trace, bestDefinition.path, normalizedSymbol);
  if (!supportWindow) {
    return {
      node: null,
      frontier: {
        path: normalizePath(bestDefinition.path),
        symbol: normalizedSymbol,
        relation,
        baseSymbol: currentSymbol,
        depth,
        line: Number(bestDefinition.line || 0),
        reason: 'definition_read_failed',
      },
    };
  }
  return {
    node: {
      path: normalizePath(supportWindow.path || bestDefinition.path),
      symbol: normalizedSymbol,
      line: Number(supportWindow.startLine || bestDefinition.line || 0),
      relation,
      baseSymbol: currentSymbol,
      depth,
    },
    frontier: null,
  };
}

async function expandFlowFrontierNode(trace, workspacePath, node, {
  rootPath,
  questionTerms,
  preferFlow = false,
} = {}) {
  const currentWindow = findReadWindow(trace, node.path, node.symbol);
  if (!currentWindow?.content) {
    return { children: [], frontiers: [] };
  }
  const outlineItems = await ensureOutlineItems(trace, workspacePath, node.path, { preferFlow });
  const nextSymbols = chooseSupportSymbols(
    currentWindow,
    [],
    outlineItems,
    questionTerms,
    [node.symbol, node.baseSymbol || ''],
  );
  const children = [];
  const frontiers = [];

  for (const symbol of nextSymbols) {
    if (!symbol) continue;
    if (node.depth >= MAX_FRONTIER_DEPTH) {
      frontiers.push({
        path: node.path,
        symbol,
        relation: 'callee_definition',
        baseSymbol: node.symbol,
        depth: node.depth + 1,
        reason: 'depth_limit',
      });
      continue;
    }
    const resolved = await resolveSupportSymbolRead(trace, workspacePath, symbol, {
      rootPath,
      currentPath: node.path,
      currentSymbol: node.symbol,
      outlineItems,
      questionTerms,
      preferFlow,
      relation: 'callee_definition',
      depth: node.depth + 1,
    });
    if (resolved.node) {
      children.push(resolved.node);
      continue;
    }
    if (resolved.frontier) {
      frontiers.push(resolved.frontier);
    }
  }

  return { children, frontiers };
}

function scoreRelatedFileCandidate(pathValue, {
  rootPath,
  selectedPath,
  questionTerms,
  grepHits = [],
  preferFlow = false,
} = {}) {
  const normalizedPath = normalizePath(pathValue);
  if (!normalizedPath) {
    return -100;
  }
  const normalizedRootPath = normalizePath(rootPath);
  if (normalizedPath.toLowerCase() === normalizedRootPath.toLowerCase()) {
    return -100;
  }

  const normalizedSelectedPath = normalizePath(selectedPath || rootPath);
  const normalizedDir = pathDirname(normalizedPath).toLowerCase();
  const rootDir = pathDirname(normalizedRootPath).toLowerCase();
  const selectedDir = pathDirname(normalizedSelectedPath).toLowerCase();
  const rootParentDir = pathDirname(rootDir).toLowerCase();
  const rootStemParts = splitSymbolParts(pathStem(normalizedRootPath))
    .map((item) => String(item || '').trim().toLowerCase())
    .filter((item) => item.length >= 3);
  const stem = pathStem(normalizedPath).toLowerCase();
  let score = 0;

  score += pathFlowBias(normalizedPath, { preferFlow });
  score += Math.min(24, scoreFileQuestionAlignment(normalizedPath, '', questionTerms));
  score += sharedPrefixDepth(normalizedPath, normalizedRootPath) * 4;

  if (normalizedDir && normalizedDir === rootDir) score += preferFlow ? 26 : 18;
  if (normalizedDir && normalizedDir === selectedDir) score += 10;
  if (rootParentDir && normalizedDir.startsWith(rootParentDir)) score += 4;
  if (pathExtname(normalizedPath) && pathExtname(normalizedPath) === pathExtname(normalizedRootPath)) score += 4;

  for (const token of rootStemParts) {
    if (stem.includes(token)) score += 4;
  }

  if (Array.isArray(grepHits) && grepHits.length > 0) {
    score += 14;
    score += Math.min(18, grepHits.length * 6);
    if (grepHits.some((item) => /[A-Za-z_][A-Za-z0-9_]*\s*\(|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*\(|::\s*[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(String(item?.text || '')))) {
      score += 6;
    }
  }

  return score;
}

function chooseBroadReadCandidates(fileItems, trace, {
  rootPath,
  selectedPath,
  questionTerms,
  preferFlow = false,
} = {}) {
  const readPaths = new Set(
    readObservationsFromTrace(trace)
      .map((item) => normalizePath(item.path).toLowerCase())
      .filter(Boolean),
  );
  const grepByPath = new Map();
  for (const hit of grepItemsFromTrace(trace)) {
    const pathValue = normalizePath(hit?.path);
    if (!pathValue) continue;
    const key = pathValue.toLowerCase();
    if (!grepByPath.has(key)) {
      grepByPath.set(key, []);
    }
    grepByPath.get(key).push({
      line: Number(hit?.line || 0),
      text: String(hit?.text || ''),
      score: Number(hit?.score || 0),
    });
  }

  const inventoryPaths = [
    ...(Array.isArray(fileItems) ? fileItems : []).map((item) => normalizePath(item?.path || item)),
    ...listFilesFromTrace(trace).map((item) => normalizePath(item?.path || item)),
  ];

  const candidates = dedupeBy(
    inventoryPaths
      .filter(Boolean)
      .map((pathValue) => {
        const grepHits = grepByPath.get(pathValue.toLowerCase()) || [];
        return {
          path: pathValue,
          grepHits,
          score: scoreRelatedFileCandidate(pathValue, {
            rootPath,
            selectedPath,
            questionTerms,
            grepHits,
            preferFlow,
          }),
        };
      })
      .filter((item) => !readPaths.has(normalizePath(item.path).toLowerCase()))
      .filter((item) => Number(item.score || 0) >= (preferFlow ? 18 : 14))
      .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.path || '').localeCompare(String(b.path || ''))),
    (item) => item?.path,
  );

  return candidates.slice(0, MAX_BROAD_FILE_READS);
}

function buildBroadReadInput(candidate, { preferFlow = false } = {}) {
  const readWindow = buildCandidateReadWindow(candidate, { preferFlow });
  return {
    path: candidate.path,
    startLine: readWindow.startLine,
    endLine: readWindow.endLine,
    maxChars: FILE_READ_CHAR_LIMIT,
  };
}

function buildNodeRole(pathValue, primaryPath, coreSet, supportSet) {
  const normalized = normalizePath(pathValue).toLowerCase();
  if (normalized === normalizePath(primaryPath).toLowerCase()) return 'focus';
  if (coreSet.has(normalized)) return 'core';
  if (supportSet.has(normalized)) return 'support';
  return 'support';
}

function nextRound(trace) {
  return (Array.isArray(trace) ? trace.length : 0) + 1;
}

function appendTraceObservation(trace, thought, action, input, rawObservation) {
  if (trace.length >= MAX_TRACE_STEPS) {
    return { ok: false, error: 'local_trace_budget_exhausted' };
  }
  const observation = summarizeObservation(
    action,
    rawObservation,
    LOCAL_TRACE_READ_CHAR_LIMIT,
  );
  trace.push({
    round: nextRound(trace),
    thought: String(thought || '').trim(),
    tool: action,
    input: input || {},
    observation,
  });
  return observation;
}

async function executeTool(workspacePath, toolName, input) {
  if (toolName === 'list_files') return listWorkspaceFiles(workspacePath, { limit: input.limit || MAX_LIST_LIMIT });
  if (toolName === 'grep') return grepWorkspace(workspacePath, input.query || '', input.limit || MAX_GREP_LIMIT);
  if (toolName === 'find_symbol') return findSymbolInWorkspace(workspacePath, input.symbol || input.query || '', {
    limit: input.limit || 12,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'find_callers') return findCallersInWorkspace(workspacePath, input.symbol || input.query || '', {
    limit: input.limit || 20,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'find_references') return findReferencesInWorkspace(workspacePath, input.symbol || input.query || '', {
    limit: input.limit || 24,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'read_symbol_span') return readSymbolSpanInWorkspace(workspacePath, input.path || '', input.symbol || '', {
    lineHint: input.lineHint || input.line_hint || 0,
    maxChars: input.maxChars || LOCAL_TRACE_READ_CHAR_LIMIT,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'symbol_outline') return symbolOutlineInWorkspace(workspacePath, input.path || '', {
    symbol: input.symbol || '',
    limit: input.limit || 120,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'symbol_neighborhood') return symbolNeighborhoodInWorkspace(workspacePath, input.path || '', {
    symbol: input.symbol || '',
    lineHint: input.lineHint || input.line_hint || 0,
    limit: input.limit || 12,
    pathFilter: input.pathFilter || input.path_filter || '',
  });
  if (toolName === 'read_file') return readWorkspaceFile(workspacePath, input.path || '', {
    maxChars: input.maxChars || FILE_READ_CHAR_LIMIT,
    startLine: input.startLine || input.start_line || 1,
    endLine: input.endLine || input.end_line || DEFAULT_FILE_READ_END_LINE,
  });
  return { ok: false, error: `tool_not_allowed_in_local_loop:${toolName}` };
}

async function pushTraceStep(trace, workspacePath, thought, action, input) {
  return appendTraceObservation(
    trace,
    thought,
    action,
    input,
    await executeTool(workspacePath, action, input || {}),
  );
}

async function collectOwnerSpanReads(trace, workspacePath, hits, primarySymbol, {
  selectedPath = '',
  relationLabel = 'call site',
} = {}) {
  const owners = [];
  for (const hit of rankRelatedOwnerHits(hits, selectedPath).slice(0, MAX_RELATED_OWNER_READS)) {
    const hitPath = normalizePath(hit?.path);
    if (!hitPath) continue;
    const neighborhoodObservation = await pushTraceStep(
      trace,
      workspacePath,
      `inspect the enclosing local symbol around the ${primarySymbol} ${relationLabel}`,
      'symbol_neighborhood',
      {
        path: hitPath,
        symbol: primarySymbol,
        lineHint: Number(hit?.line || 0),
        limit: 12,
      },
    );
    const owner = pickNeighborhoodOwner(neighborhoodObservation?.items, primarySymbol);
    if (!owner) {
      continue;
    }
    const ownerSymbol = String(owner.name || owner.symbol || '').trim();
    if (!ownerSymbol) {
      continue;
    }
    const ownerLine = Number(owner.line || hit?.line || 0);
    if (hasReadSymbol(trace, hitPath, ownerSymbol)) {
      owners.push({
        symbol: ownerSymbol,
        path: hitPath,
        line: ownerLine,
        read: false,
      });
      continue;
    }
    const ownerSpan = await pushTraceStep(
      trace,
      workspacePath,
      `read the local owner span for ${ownerSymbol}`,
      'read_symbol_span',
      {
        path: hitPath,
        symbol: ownerSymbol,
        lineHint: ownerLine,
        maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
      },
    );
    if (ownerSpan?.ok) {
      owners.push({
        symbol: ownerSymbol,
        path: hitPath,
        line: ownerLine,
        read: true,
      });
    }
  }
  return dedupeBy(owners, (item) => `${item.path}::${item.symbol}`);
}

function buildAnchorEvidenceMetrics(content, outlineItems) {
  const text = String(content || '');
  const callTokens = extractCallTokens(text, { mode: 'anchor' });
  const callMentionCount = callTokens.reduce((sum, item) => sum + Number(item.count || 0), 0);
  const controlCount = countMatches(text, CONTROL_SIGNAL_RE);
  const assignmentCount = countMatches(text, ASSIGNMENT_SIGNAL_RE);
  const outlineRows = Array.isArray(outlineItems) ? outlineItems : [];
  const methodCount = outlineRows.filter((item) => ['method', 'function', 'event'].includes(String(item?.kind || '').trim().toLowerCase())).length;
  const typeCount = outlineRows.filter((item) => String(item?.kind || '').trim().toLowerCase() === 'type').length;
  const declarationOnly = typeCount > 0 && methodCount === 0 && controlCount === 0 && callTokens.length <= 1;
  return {
    callTokenCount: callTokens.length,
    callMentionCount,
    controlCount,
    assignmentCount,
    methodCount,
    typeCount,
    declarationOnly,
  };
}

function buildQuestionAlignmentMetrics(pathValue, content, outlineItems, questionTerms) {
  const normalizedPath = normalizePath(pathValue).toLowerCase();
  const lines = String(content || '').split(/\r?\n/);
  let codeTermHits = 0;
  let commentTermHits = 0;
  let codeDistinctTerms = 0;
  let commentDistinctTerms = 0;
  let outlineTermHits = 0;
  let pathTermHits = 0;
  const codeDistinct = new Set();
  const commentDistinct = new Set();

  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (normalizedPath.includes(loweredTerm)) pathTermHits += 1;
    for (const item of Array.isArray(outlineItems) ? outlineItems : []) {
      const outlineText = `${String(item?.name || '')} ${String(item?.text || '')}`.toLowerCase();
      if (outlineText.includes(loweredTerm)) {
        outlineTermHits += 1;
        break;
      }
    }
    for (const line of lines) {
      const rawLine = String(line || '');
      const loweredLine = rawLine.toLowerCase();
      if (!loweredLine.includes(loweredTerm)) continue;
      if (isCommentOnlyLine(rawLine)) {
        commentTermHits += 1;
        commentDistinct.add(loweredTerm);
        continue;
      }
      const strippedLine = stripInlineComments(stripStringLiterals(rawLine)).toLowerCase();
      if (strippedLine.includes(loweredTerm)) {
        codeTermHits += 1;
        codeDistinct.add(loweredTerm);
      } else {
        commentTermHits += 1;
        commentDistinct.add(loweredTerm);
      }
    }
  }

  codeDistinctTerms = codeDistinct.size;
  commentDistinctTerms = commentDistinct.size;
  return {
    pathTermHits,
    outlineTermHits,
    codeTermHits,
    commentTermHits,
    codeDistinctTerms,
    commentDistinctTerms,
    totalDistinctTerms: new Set([...codeDistinct, ...commentDistinct]).size,
  };
}

function bucketSignal(value, thresholds) {
  let bucket = 0;
  const numericValue = Number(value || 0);
  for (const threshold of Array.isArray(thresholds) ? thresholds : []) {
    if (numericValue >= Number(threshold || 0)) {
      bucket += 1;
    }
  }
  return bucket;
}

function buildSeedCandidateDecision(candidate, questionTerms, { preferFlow = false } = {}) {
  const pathValue = normalizePath(candidate?.path);
  const grepHits = Array.isArray(candidate?.grepHits) ? candidate.grepHits : [];
  const nonCommentHits = grepHits.filter((item) => !Boolean(item?.commentOnly));
  const specificTerms = (Array.isArray(questionTerms) ? questionTerms : []).filter((item) => !isBroadAnchorTerm(item));
  const candidateQueries = new Set(
    (Array.isArray(candidate?.queries) ? candidate.queries : [])
      .map((item) => String(item || '').trim().toLowerCase())
      .filter(Boolean),
  );
  const queryMatches = specificTerms.filter((item) => candidateQueries.has(String(item || '').trim().toLowerCase())).length;
  const executableHitCount = nonCommentHits.filter((item) => {
    const text = String(item?.text || '');
    return /[A-Za-z_][A-Za-z0-9_]*\s*\(|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*\(|::\s*[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(text)
      || /\b(if|for|foreach|while|switch|return|await|catch)\b/i.test(text);
  }).length;
  const alignmentBucket = bucketSignal(scoreFileQuestionAlignment(pathValue, '', questionTerms), [8, 18, 30]);
  const grepStrength = bucketSignal(
    Math.max(0, ...nonCommentHits.map((item) => Number(item?.score || 0))),
    [1, 4, 7],
  );
  return {
    candidate,
    tuple: [
      candidate?.selected ? 1 : 0,
      queryMatches > 0 ? 1 : 0,
      nonCommentHits.length > 0 ? 1 : 0,
      preferFlow ? (executableHitCount > 0 ? 1 : 0) : 0,
      alignmentBucket,
      bucketSignal(nonCommentHits.length, [1, 2, 4]),
      bucketSignal(pathFlowBias(pathValue, { preferFlow }), [1, 4]),
      grepStrength,
    ],
  };
}

function buildAnchorCandidateInspection(candidate, questionTerms, { preferFlow = false } = {}) {
  const content = String(candidate?.content || '');
  const outlineItems = Array.isArray(candidate?.outlineItems) ? candidate.outlineItems : [];
  const metrics = buildAnchorEvidenceMetrics(content, outlineItems);
  const alignment = buildQuestionAlignmentMetrics(candidate?.path, content, outlineItems, questionTerms);
  const focusLines = (Array.isArray(candidate?.grepHits) ? candidate.grepHits : [])
    .map((item) => Number(item?.line || 0))
    .filter((item) => item > 0);
  const outlineCandidates = chooseBestOutlineItems(outlineItems, questionTerms, { focusLines, preferFlow });
  return {
    metrics,
    alignment,
    outlineCandidates,
  };
}

function mergeAnchorCandidate(candidates, payload) {
  const pathValue = normalizePath(payload?.path);
  if (!pathValue) {
    return;
  }
  const key = pathValue.toLowerCase();
  const current = candidates.get(key) || {
    path: pathValue,
    selected: false,
    grepHits: [],
    queries: [],
    source: '',
  };
  if (payload?.selected) {
    current.selected = true;
  }
  if (payload?.query) {
    const queryText = String(payload.query || '').trim();
    if (queryText && !current.queries.includes(queryText)) {
      current.queries.push(queryText);
    }
  }
  if (payload?.hit) {
    current.grepHits.push({
      query: String(payload.query || '').trim(),
      line: Number(payload.hit?.line || 0),
      text: String(payload.hit?.text || '').trim(),
      commentOnly: Boolean(payload?.commentOnly),
      score: Number(payload?.hitScore || 0),
    });
    current.grepHits.sort((left, right) => Number(right.score || 0) - Number(left.score || 0));
    current.grepHits = current.grepHits.slice(0, MAX_ROOT_PATHS_PER_QUERY);
  }
  current.source = current.grepHits.length > 0 ? 'grep' : (current.selected ? 'selected' : (payload?.source || current.source || 'candidate'));
  candidates.set(key, current);
}

async function collectAnchorCandidates(workspacePath, question, selectedPath, questionTerms) {
  const candidates = new Map();
  const preferFlow = isFlowQuestion(question);
  const specificQuestionTerms = (Array.isArray(questionTerms) ? questionTerms : []).filter((item) => !isBroadAnchorTerm(item));
  if (selectedPath) {
    mergeAnchorCandidate(candidates, { path: selectedPath, selected: true, source: 'selected' });
  }

  const anchorQueries = buildAnchorQueries(question, questionTerms).slice(0, MAX_ROOT_QUERY_CANDIDATES);
  for (const queryText of anchorQueries) {
    const token = String(queryText || '').trim();
    if (!token) continue;
    const observation = await grepWorkspace(workspacePath, token, MAX_ROOT_GREP_SCAN_LIMIT);
    if (!observation?.ok) continue;
    const rankedHits = (Array.isArray(observation?.items) ? observation.items : [])
      .map((hit) => ({
        ...hit,
        __score: scoreGrepAnchorHit(hit, questionTerms, token, { preferFlow }),
        __commentOnly: isCommentOnlyLine(hit?.text),
      }))
      .sort((left, right) => Number(right.__score || 0) - Number(left.__score || 0) || String(left.path || '').localeCompare(String(right.path || '')))
      .slice(0, MAX_ROOT_GREPHITS_PER_QUERY);
    const uniqueHits = dedupeBy(rankedHits, (item) => item?.path).slice(0, MAX_ROOT_PATHS_PER_QUERY);
    for (const hit of uniqueHits) {
      mergeAnchorCandidate(candidates, {
        path: hit?.path,
        query: token,
        hit,
        source: 'grep',
        hitScore: hit?.__score,
        commentOnly: hit?.__commentOnly,
      });
    }
  }

  if (candidates.size === 0) {
    const fileList = await listWorkspaceFiles(workspacePath, { limit: MAX_LIST_LIMIT });
    const ranked = (Array.isArray(fileList?.items) ? fileList.items : [])
      .map((item) => ({
        path: normalizePath(item?.path),
        score: scoreFileQuestionAlignment(item?.path, '', questionTerms),
      }))
      .filter((item) => item.path && Number(item.score || 0) > 0)
      .sort((left, right) => Number(right.score || 0) - Number(left.score || 0) || String(left.path || '').localeCompare(String(right.path || '')))
      .slice(0, 2);
    for (const item of ranked) {
      mergeAnchorCandidate(candidates, { path: item.path, source: 'list_files' });
    }
  }

  const candidateList = Array.from(candidates.values())
    .filter((candidate) => {
      if (specificQuestionTerms.length === 0) {
        return true;
      }
      const candidateQueries = new Set((Array.isArray(candidate?.queries) ? candidate.queries : []).map((item) => String(item || '').trim().toLowerCase()).filter(Boolean));
      return specificQuestionTerms.some((term) => candidateQueries.has(String(term || '').trim().toLowerCase()));
    });

  return (candidateList.length > 0 ? candidateList : Array.from(candidates.values()))
    .map((candidate) => buildSeedCandidateDecision(candidate, questionTerms, { preferFlow }))
    .sort(compareDecisionTuples)
    .map((item) => item.candidate)
    .slice(0, MAX_ROOT_FILE_CANDIDATES);
}

async function inspectAnchorCandidate(workspacePath, candidate, questionTerms, { preferFlow = false } = {}) {
  const readWindow = buildCandidateReadWindow(candidate, { preferFlow });
  const readObservation = await readWorkspaceFile(workspacePath, candidate.path, {
    maxChars: Math.min(FILE_READ_CHAR_LIMIT, 6000),
    startLine: readWindow.startLine,
    endLine: readWindow.endLine,
  });
  const content = readObservation?.ok ? String(readObservation.content || '') : '';
  const outlineObservation = readObservation?.ok
    ? await symbolOutlineInWorkspace(workspacePath, candidate.path, { limit: preferFlow ? FLOW_OUTLINE_LIMIT : 120 })
    : { ok: false, items: [] };
  const outlineItems = Array.isArray(outlineObservation?.items) ? outlineObservation.items : [];
  const evaluation = buildAnchorCandidateInspection(
    {
      ...candidate,
      content,
      outlineItems,
    },
    questionTerms,
    { preferFlow },
  );
  return {
    ...candidate,
    readObservation,
    content,
    outlineItems,
    evaluation,
  };
}

function buildObservedAnchorDecision(inspected, { preferFlow = false } = {}) {
  const alignment = inspected?.evaluation?.alignment && typeof inspected.evaluation.alignment === 'object'
    ? inspected.evaluation.alignment
    : {};
  const metrics = inspected?.evaluation?.metrics && typeof inspected.evaluation.metrics === 'object'
    ? inspected.evaluation.metrics
    : {};
  const grepHits = Array.isArray(inspected?.grepHits) ? inspected.grepHits : [];
  const nonCommentHits = grepHits.filter((item) => !Boolean(item?.commentOnly));
  const declarationOnly = Boolean(metrics.declarationOnly);
  const distinctCoverage = Number(alignment.codeDistinctTerms || 0) + Number(alignment.outlineTermHits || 0);
  const softQuestionCoverage = distinctCoverage + Number(alignment.commentDistinctTerms || 0);
  const executableFlow = Number(metrics.methodCount || 0) + Number(metrics.callTokenCount || 0) + Number(metrics.controlCount || 0);
  const directQuestionCode = Number(alignment.codeDistinctTerms || 0) > 0;
  const nearbyExecutable = Array.isArray(inspected?.evaluation?.outlineCandidates) && inspected.evaluation.outlineCandidates.length > 0;
  const selectedExecutable = inspected?.selected && (executableFlow > 0 || nearbyExecutable);
  return {
    inspected,
    tuple: [
      selectedExecutable ? 1 : 0,
      preferFlow ? (executableFlow > 0 ? 1 : 0) : 0,
      preferFlow ? (declarationOnly ? 0 : 1) : 0,
      preferFlow ? (softQuestionCoverage > 0 ? 1 : 0) : 0,
      directQuestionCode ? 1 : 0,
      nearbyExecutable ? 1 : 0,
      Math.min(4, softQuestionCoverage),
      Math.min(4, nonCommentHits.length),
      Math.min(6, executableFlow),
      bucketSignal(Number(alignment.pathTermHits || 0), [1, 2, 3]),
      inspected?.selected ? 1 : 0,
    ],
  };
}

function compareDecisionTuples(left, right) {
  const leftTuple = Array.isArray(left?.tuple) ? left.tuple : [];
  const rightTuple = Array.isArray(right?.tuple) ? right.tuple : [];
  const width = Math.max(leftTuple.length, rightTuple.length);
  for (let index = 0; index < width; index += 1) {
    const delta = Number(rightTuple[index] || 0) - Number(leftTuple[index] || 0);
    if (delta !== 0) {
      return delta;
    }
  }
  const leftPath = normalizePath(left?.inspected?.path || left?.candidate?.path || '');
  const rightPath = normalizePath(right?.inspected?.path || right?.candidate?.path || '');
  return String(leftPath || '').localeCompare(String(rightPath || ''));
}

async function selectRootAnchorCandidate(workspacePath, question, selectedPath, questionTerms) {
  const preferFlow = isFlowQuestion(question);
  const candidates = await collectAnchorCandidates(workspacePath, question, selectedPath, questionTerms);
  const inspectedCandidates = [];
  for (const candidate of candidates.slice(0, MAX_ROOT_FILE_INSPECTIONS)) {
    const inspected = await inspectAnchorCandidate(workspacePath, candidate, questionTerms, { preferFlow });
    inspectedCandidates.push(inspected);
  }
  if (inspectedCandidates.length === 0) {
    return null;
  }
  const ranked = inspectedCandidates
    .map((item) => buildObservedAnchorDecision(item, { preferFlow }))
    .sort(compareDecisionTuples);
  return ranked[0]?.inspected || null;
}

async function resolveRootPath(workspacePath, question, selectedFilePath, trace) {
  const selectedPath = normalizePath(selectedFilePath);
  const questionTerms = normalizeQuestionTerms(question);
  const bestAnchor = await selectRootAnchorCandidate(workspacePath, question, selectedPath, questionTerms);
  if (!bestAnchor?.path) {
    return { path: selectedPath || '', focusLines: [] };
  }
  if (String(bestAnchor.source || '').trim().toLowerCase() === 'grep' && Array.isArray(bestAnchor.queries) && bestAnchor.queries[0]) {
    const grepObservation = await pushTraceStep(
      trace,
      workspacePath,
      `search workspace text to find a local anchor for ${bestAnchor.queries[0]}`,
      'grep',
      {
        query: bestAnchor.queries[0],
        limit: MAX_GREP_LIMIT,
      },
    );
    if (!grepObservation?.ok) {
      return {
        path: bestAnchor.path,
        focusLines: (Array.isArray(bestAnchor.grepHits) ? bestAnchor.grepHits : []).map((item) => Number(item?.line || 0)).filter((item) => item > 0),
      };
    }
  } else if (String(bestAnchor.source || '').trim().toLowerCase() === 'list_files') {
    await pushTraceStep(trace, workspacePath, 'enumerate workspace files to anchor the local investigation', 'list_files', {
      limit: MAX_LIST_LIMIT,
    });
  }
  return {
    path: bestAnchor.path,
    focusLines: (Array.isArray(bestAnchor.grepHits) ? bestAnchor.grepHits : []).map((item) => Number(item?.line || 0)).filter((item) => item > 0),
  };
}

function scoreGrepAnchorHit(item, questionTerms, queryText, { preferFlow = false } = {}) {
  const pathValue = normalizePath(item?.path);
  const loweredPath = pathValue.toLowerCase();
  const text = String(item?.text || '').trim();
  const loweredText = text.toLowerCase();
  const codeText = stripInlineComments(stripStringLiterals(text)).toLowerCase();
  const rawQuery = String(queryText || '').trim().toLowerCase();
  let score = 0;

  if (!pathValue) {
    return 0;
  }
  const commentOnly = isCommentOnlyLine(text);
  score += bucketSignal(pathFlowBias(pathValue, { preferFlow }), [1, 4]);
  if (rawQuery && codeText.includes(rawQuery)) score += 3;
  else if (rawQuery && loweredText.includes(rawQuery)) score += 1;
  if (rawQuery && loweredPath.includes(rawQuery)) score += 2;
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (codeText.includes(loweredTerm)) score += 2;
    else if (loweredText.includes(loweredTerm)) score += 1;
    if (loweredPath.includes(loweredTerm)) score += 1;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules|packages|\.tmp)\//i.test(pathValue)) score -= 4;
  if (commentOnly) score -= 3;
  if (/\b(class|interface|struct|enum|record|namespace|module)\b/i.test(text)) score += 1;
  if (/[A-Za-z_][A-Za-z0-9_]*\s*\(|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*\(|::\s*[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(text)) score += 2;
  if (/\b(if|for|foreach|while|switch|return|await|catch)\b/i.test(text)) score += 1;
  if (!commentOnly && /\b(case|public|private|protected|internal|new|return)\b/i.test(text)) score += 1;
  return score;
}

function buildAnchorQueries(question, questionTerms) {
  const rawQuestion = String(question || '').trim();
  const queries = [];
  const orderedTerms = uniq(Array.isArray(questionTerms) ? questionTerms : [])
    .sort((left, right) => questionTermPriority(right) - questionTermPriority(left) || String(left || '').localeCompare(String(right || '')));
  for (const term of orderedTerms) {
    const token = String(term || '').trim();
    if (!token) continue;
    queries.push(token);
    if (queries.length >= 10) break;
  }
  if (rawQuestion) {
    queries.push(rawQuestion);
  }
  return uniq(queries);
}

function summarizeTraceTargets(trace) {
  return readWindowsFromTrace(trace)
    .map((item) => `${item.path}${item.symbol ? `::${item.symbol}` : ''}${item.lineRange ? `@${item.lineRange}` : ''}`)
    .slice(0, 10);
}

function buildWorkspaceGraph(question, trace, analysis) {
  const selectedPath = normalizePath(analysis.selectedPath || analysis.rootPath || '');
  const rootPath = normalizePath(analysis.rootPath || selectedPath);
  const primaryPath = normalizePath(analysis.primaryPath || rootPath || selectedPath);
  const selectedMatchesPrimary = Boolean(selectedPath) && selectedPath.toLowerCase() === primaryPath.toLowerCase();
  const flowNodes = dedupeBy(
    Array.isArray(analysis.flowNodes) ? analysis.flowNodes : [],
    (item) => `${normalizePath(item?.path)}::${String(item?.symbol || '').trim()}`,
  );
  const openFrontier = dedupeBy(
    Array.isArray(analysis.openFrontier) ? analysis.openFrontier : [],
    (item) => `${normalizePath(item?.path || '')}::${String(item?.symbol || '').trim()}`,
  );
  const relatedOwners = dedupeBy(
    Array.isArray(analysis.relatedOwners) ? analysis.relatedOwners : [],
    (item) => `${normalizePath(item?.path)}::${String(item?.symbol || '').trim()}`,
  );
  const readFiles = readObservationsFromTrace(trace);
  const relatedFiles = uniq([
    primaryPath,
    ...flowNodes.map((item) => item.path),
    ...relatedOwners.map((item) => item.path),
    analysis.callerOwner?.path || '',
    ...(analysis.supportReads || []).map((item) => item.path),
    ...readFiles.map((item) => item.path),
  ]).slice(0, MAX_RELATED_FILES);
  const coreFiles = uniq([
    selectedMatchesPrimary ? selectedPath : '',
    primaryPath,
    analysis.callerOwner?.path || '',
  ]).filter(Boolean).slice(0, MAX_CORE_FILES);
  const supportFiles = uniq([
    ...relatedOwners.map((item) => item.path),
    ...(analysis.supportReads || []).map((item) => item.path),
    ...relatedFiles.filter((pathValue) => !coreFiles.some((item) => item.toLowerCase() === pathValue.toLowerCase())),
  ]).filter(Boolean).slice(0, MAX_SUPPORT_FILES);
  const coreSet = new Set(coreFiles.map((item) => item.toLowerCase()));
  const supportSet = new Set(supportFiles.map((item) => item.toLowerCase()));
  const edges = inferCodeRelations(readFiles, relatedFiles).slice(0, 12);
  const primaryContent = String(
    analysis.primaryWindow?.content
    || readFiles.find((item) => normalizePath(item.path).toLowerCase() === primaryPath.toLowerCase())?.content
    || ''
  );
  const nodes = relatedFiles.map((pathValue, index) => {
    const candidate = readFiles.find((item) => normalizePath(item.path).toLowerCase() === normalizePath(pathValue).toLowerCase()) || {
      path: pathValue,
      content: '',
      lineRanges: [],
    };
    return {
      id: pathValue,
      path: pathValue,
      role: buildNodeRole(pathValue, primaryPath, coreSet, supportSet),
      read_order: index + 1,
      score: index === 0 ? 100 : Math.max(10, 60 - index * 8),
      representative_evidence: pickRepresentativeEvidence(
        {
          path: pathValue,
          grepItems: [],
          readObservation: candidate,
        },
        question,
      ),
      reasons: [
        pathValue.toLowerCase() === primaryPath.toLowerCase() ? 'primary_flow' : '',
        pathValue.toLowerCase() === selectedPath.toLowerCase() ? 'selected_file' : '',
        analysis.callerOwner?.path && normalizePath(analysis.callerOwner.path).toLowerCase() === normalizePath(pathValue).toLowerCase() ? 'caller_owner' : '',
        (analysis.supportReads || []).some((item) => normalizePath(item.path).toLowerCase() === normalizePath(pathValue).toLowerCase()) ? 'support_definition' : '',
      ].filter(Boolean),
      grounded: true,
      read_spans: (candidate.lineRanges || []).slice(0, 4),
    };
  });

  const chain = flowNodes.length > 0
    ? flowNodes.map((item) => ({
      relation: String(item.relation || '').trim() || 'support',
      symbol: String(item.symbol || '').trim(),
      path: normalizePath(item.path),
      line: Number(item.line || 0),
      covered: item.covered !== false,
      discovered: item.discovered !== false,
      search_completed: item.searchCompleted !== false,
      base_symbol: String(item.baseSymbol || '').trim(),
    }))
    : [];
  if (chain.length === 0) {
    if (analysis.primarySymbol) {
      chain.push({
        relation: 'anchor',
        symbol: analysis.primarySymbol,
        path: primaryPath,
        line: Number(analysis.primaryWindow?.startLine || 0),
        covered: true,
        discovered: true,
        search_completed: true,
        base_symbol: '',
      });
    }
    if (analysis.callerOwner?.symbol) {
      chain.push({
        relation: 'caller_owner',
        symbol: analysis.callerOwner.symbol,
        path: analysis.callerOwner.path,
        line: Number(analysis.callerOwner.line || 0),
        covered: true,
        discovered: true,
        search_completed: true,
        base_symbol: analysis.primarySymbol,
      });
    }
    for (const owner of relatedOwners) {
      if (!owner?.symbol || !owner?.path) continue;
      if (
        analysis.callerOwner
        && normalizePath(owner.path).toLowerCase() === normalizePath(analysis.callerOwner.path).toLowerCase()
        && String(owner.symbol || '').trim().toLowerCase() === String(analysis.callerOwner.symbol || '').trim().toLowerCase()
      ) {
        continue;
      }
      chain.push({
        relation: 'related_owner',
        symbol: owner.symbol,
        path: owner.path,
        line: Number(owner.line || 0),
        covered: true,
        discovered: true,
        search_completed: true,
        base_symbol: analysis.primarySymbol,
      });
    }
    for (const support of analysis.supportReads || []) {
      chain.push({
        relation: 'callee_definition',
        symbol: support.symbol,
        path: support.path,
        line: Number(support.startLine || 0),
        covered: true,
        discovered: true,
        search_completed: true,
        base_symbol: analysis.primarySymbol,
      });
    }
  }
  const frontierNodes = openFrontier.map((item) => ({
    relation: String(item.relation || '').trim() || 'frontier',
    symbol: String(item.symbol || '').trim(),
    path: normalizePath(item.path || ''),
    line: Number(item.line || 0),
    covered: false,
    discovered: true,
    search_completed: false,
    base_symbol: String(item.baseSymbol || '').trim(),
    reason: String(item.reason || '').trim(),
  }));
  const discoveredCount = chain.length + frontierNodes.length;
  const coveredCount = chain.filter((item) => item.covered !== false).length;
  const graphClosed = analysis.graphClosed === true
    ? frontierNodes.length === 0
    : !Boolean(frontierNodes.length);

  const graphState = {
    anchor_symbol: analysis.primarySymbol || '',
    focus_symbol: analysis.callerOwner?.symbol || analysis.primarySymbol || '',
    focus_path: primaryPath,
    chain,
    frontiers: frontierNodes,
    frontier: frontierNodes[0] || {},
    closed: graphClosed,
    coverage_ratio: discoveredCount > 0 ? (coveredCount / discoveredCount) : 0.0,
    covered_count: coveredCount,
    discovered_count: discoveredCount,
    open_frontier_count: frontierNodes.length,
  };

  const summary = analysis.summary
    || (analysis.primarySymbol
      ? `Collected local flow evidence around ${analysis.primarySymbol}.`
      : primaryPath
        ? `Collected local file evidence from ${primaryPath}.`
        : 'No local workspace anchor was available.');
  const contextText = JSON.stringify(
    {
      question,
      root_path: rootPath,
      selected_path: selectedPath,
      primary_path: primaryPath,
      primary_symbol: analysis.primarySymbol || '',
      candidate_symbols: analysis.candidateSymbols || [],
      caller_owner: analysis.callerOwner || null,
      support_symbols: (analysis.supportReads || []).map((item) => item.symbol),
      related_files: relatedFiles,
      open_frontier: frontierNodes.map((item) => ({
        path: item.path,
        symbol: item.symbol,
        relation: item.relation,
        reason: item.reason,
      })),
      trace_targets: summarizeTraceTargets(trace),
      trace_length: trace.length,
    },
    null,
    2,
  );

  return {
    summary,
    contextText,
    primaryFilePath: primaryPath,
    primaryFileContent: primaryContent,
    selectedFiles: relatedFiles,
    workspaceGraph: {
      version: 3,
      question,
      focus_file: primaryPath,
      core_files: coreFiles,
      supporting_files: supportFiles,
      local_summary: summary,
      target_symbol: analysis.primarySymbol || '',
      graph_closed: graphClosed,
      graph_state: graphState,
      nodes,
      edges,
    },
  };
}

async function runLocalToolLoop({
  workspacePath,
  question,
  selectedFilePath = '',
}) {
  const trace = [];
  const rootAnchor = await resolveRootPath(workspacePath, question, selectedFilePath, trace);
  const rootPath = normalizePath(rootAnchor?.path || '');
  const rootFocusLines = Array.isArray(rootAnchor?.focusLines) ? rootAnchor.focusLines : [];
  const anchorQuestionTerms = normalizeQuestionTerms(question);
  const questionTerms = anchorTerms(question, rootPath);
  const preferFlow = isFlowQuestion(question);
  const hasSpecificFlowTerms = hasSpecificQuestionTerms(anchorQuestionTerms);
  if (!rootPath) {
    return {
      trace,
      summary: 'No local file anchor was available.',
      contextText: JSON.stringify({ question, root_path: '' }, null, 2),
      error: 'No local file anchor was available.',
      primaryFilePath: '',
      primaryFileContent: '',
      selectedFiles: [],
      workspaceGraph: {},
    };
  }

  const inventory = await listWorkspaceFiles(workspacePath, { limit: MAX_LIST_LIMIT });
  appendTraceObservation(
    trace,
    'enumerate workspace files to widen the initial local evidence set',
    'list_files',
    { limit: MAX_LIST_LIMIT },
    inventory,
  );

  const analysis = {
    selectedPath: normalizePath(selectedFilePath),
    rootPath,
    rootFocusLines,
    candidateSymbols: [],
    primarySymbol: '',
    primaryPath: rootPath,
    primaryWindow: null,
    callerOwner: null,
    relatedOwners: [],
    supportReads: [],
    flowNodes: [],
    openFrontier: [],
    graphClosed: false,
    summary: '',
  };

  await pushTraceStep(trace, workspacePath, 'read the chosen local anchor file', 'read_file', {
    path: rootPath,
    maxChars: FILE_READ_CHAR_LIMIT,
    startLine: 1,
    endLine: DEFAULT_FILE_READ_END_LINE,
  });

  const outlineObservation = await pushTraceStep(trace, workspacePath, 'inspect local declarations in the anchor file', 'symbol_outline', {
    path: rootPath,
    limit: preferFlow ? FLOW_OUTLINE_LIMIT : 120,
  });
  const outlineItems = Array.isArray(outlineObservation?.items) ? outlineObservation.items : [];
  const rootCandidates = chooseBestOutlineItems(outlineItems, anchorQuestionTerms, {
    focusLines: rootFocusLines,
    preferFlow,
  });
  analysis.candidateSymbols = rootCandidates.map((item) => String(item?.name || '').trim()).filter(Boolean);

  for (const item of rootCandidates) {
    const symbol = String(item?.name || '').trim();
    if (!symbol || hasReadSymbol(trace, rootPath, symbol)) {
      continue;
    }
    await pushTraceStep(trace, workspacePath, `read the local symbol span for ${symbol}`, 'read_symbol_span', {
      path: rootPath,
      symbol,
      lineHint: Number(item?.line || 0),
      maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
    });
  }

  const primaryWindow = choosePrimaryWindow(trace, rootPath, outlineItems, anchorQuestionTerms, {
    focusLines: rootFocusLines,
    preferFlow,
  });
  if (primaryWindow) {
    analysis.primaryWindow = primaryWindow;
    analysis.primarySymbol = String(primaryWindow.symbol || '').trim();
    analysis.primaryPath = normalizePath(primaryWindow.path || rootPath);
  } else if (analysis.candidateSymbols[0]) {
    analysis.primarySymbol = analysis.candidateSymbols[0];
  }

  if (analysis.primarySymbol) {
    const callerObservation = await pushTraceStep(trace, workspacePath, `trace callers of ${analysis.primarySymbol}`, 'find_callers', {
      symbol: analysis.primarySymbol,
      limit: 20,
    });
    analysis.relatedOwners = await collectOwnerSpanReads(
      trace,
      workspacePath,
      callerObservation?.items,
      analysis.primarySymbol,
      {
        selectedPath: rootPath,
        relationLabel: 'call site',
      },
    );
    analysis.callerOwner = analysis.relatedOwners[0] || null;

    if (!analysis.callerOwner) {
      const referenceObservation = await pushTraceStep(trace, workspacePath, `trace references of ${analysis.primarySymbol} when direct callers are absent`, 'find_references', {
        symbol: analysis.primarySymbol,
        limit: 24,
      });
      analysis.relatedOwners = await collectOwnerSpanReads(
        trace,
        workspacePath,
        referenceObservation?.items,
        analysis.primarySymbol,
        {
          selectedPath: rootPath,
          relationLabel: 'reference',
        },
      );
      analysis.callerOwner = analysis.relatedOwners[0] || null;
    }
  }

  const callerWindows = (Array.isArray(analysis.relatedOwners) ? analysis.relatedOwners : [])
    .map((owner) => {
      return readWindowsFromTrace(trace).find((item) => {
        return normalizePath(item.path).toLowerCase() === normalizePath(owner.path).toLowerCase()
          && String(item.symbol || '').trim().toLowerCase() === String(owner.symbol || '').trim().toLowerCase();
      }) || null;
    })
    .filter(Boolean);
  const callerWindow = callerWindows[0] || null;
  if (
    callerWindow
    && normalizePath(callerWindow.path).toLowerCase() === normalizePath(analysis.primaryPath).toLowerCase()
    && (!preferFlow || hasSpecificFlowTerms)
    && signalScore(analysis.callerOwner?.symbol || '', { mode: 'anchor' }) >= signalScore(analysis.primarySymbol || '', { mode: 'anchor' }) - 8
  ) {
    analysis.primarySymbol = String(analysis.callerOwner?.symbol || analysis.primarySymbol || '').trim();
    analysis.primaryPath = normalizePath(callerWindow.path || analysis.primaryPath);
    analysis.primaryWindow = callerWindow;
  }
  const frontierQueue = [];
  const queuedKeys = new Set();
  const expandedKeys = new Set();

  if (analysis.primaryWindow && analysis.primarySymbol) {
    const anchorNode = {
      path: normalizePath(analysis.primaryWindow.path || analysis.primaryPath || rootPath),
      symbol: analysis.primarySymbol,
      line: Number(analysis.primaryWindow.startLine || 0),
      relation: 'anchor',
      baseSymbol: '',
      depth: 0,
    };
    recordFlowNode(analysis.flowNodes, anchorNode);
    enqueueFrontierNode(frontierQueue, queuedKeys, analysis.openFrontier, anchorNode);
  }

  for (const owner of analysis.relatedOwners) {
    if (!owner?.path || !owner?.symbol) continue;
    const relation = (
      analysis.callerOwner
      && normalizePath(owner.path).toLowerCase() === normalizePath(analysis.callerOwner.path).toLowerCase()
      && String(owner.symbol || '').trim().toLowerCase() === String(analysis.callerOwner.symbol || '').trim().toLowerCase()
    ) ? 'caller_owner' : 'related_owner';
    const ownerNode = {
      path: normalizePath(owner.path),
      symbol: String(owner.symbol || '').trim(),
      line: Number(owner.line || 0),
      relation,
      baseSymbol: analysis.primarySymbol,
      depth: 0,
    };
    recordFlowNode(analysis.flowNodes, ownerNode);
    if (findReadWindow(trace, ownerNode.path, ownerNode.symbol)) {
      enqueueFrontierNode(frontierQueue, queuedKeys, analysis.openFrontier, ownerNode);
    }
  }

  let expansionCount = 0;
  while (frontierQueue.length > 0 && expansionCount < MAX_FRONTIER_EXPANSIONS) {
    const node = frontierQueue.shift();
    const nodeKey = `${normalizePath(node?.path)}::${String(node?.symbol || '').trim()}`.toLowerCase();
    if (!node?.path || !node?.symbol || expandedKeys.has(nodeKey)) {
      continue;
    }
    expandedKeys.add(nodeKey);
    expansionCount += 1;
    const expansion = await expandFlowFrontierNode(trace, workspacePath, node, {
      rootPath: analysis.primaryPath || rootPath,
      questionTerms,
      preferFlow,
    });
    for (const child of expansion.children || []) {
      recordFlowNode(analysis.flowNodes, child);
      analysis.supportReads.push({
        path: normalizePath(child.path),
        symbol: String(child.symbol || '').trim(),
        startLine: Number(child.line || 0),
      });
      enqueueFrontierNode(frontierQueue, queuedKeys, analysis.openFrontier, child);
    }
    for (const frontierNode of expansion.frontiers || []) {
      recordOpenFrontier(analysis.openFrontier, frontierNode);
    }
  }

  while (frontierQueue.length > 0) {
    const node = frontierQueue.shift();
    recordOpenFrontier(analysis.openFrontier, {
      ...node,
      reason: 'expansion_budget_exhausted',
    });
  }

  analysis.supportReads = dedupeBy(analysis.supportReads, (item) => `${item.path}::${item.symbol}`);
  analysis.graphClosed = analysis.openFrontier.length === 0;

  for (const candidate of chooseBroadReadCandidates(
    Array.isArray(inventory?.items) ? inventory.items : [],
    trace,
    {
      rootPath: analysis.primaryPath || rootPath,
      selectedPath: analysis.selectedPath || rootPath,
      questionTerms,
      preferFlow,
    },
  )) {
    if (hasReadPath(trace, candidate.path)) {
      continue;
    }
    await pushTraceStep(
      trace,
      workspacePath,
      `ground the related local file ${pathBasename(candidate.path)} to widen the workspace context`,
      'read_file',
      buildBroadReadInput(candidate, { preferFlow }),
    );
  }

  analysis.summary = analysis.primarySymbol
    ? `Collected local flow evidence around ${analysis.primarySymbol}${analysis.callerOwner?.symbol ? ` with caller ${analysis.callerOwner.symbol}` : ''}${analysis.openFrontier.length > 0 ? ` and ${analysis.openFrontier.length} open frontier nodes` : ''}.`
    : `Collected local file evidence from ${analysis.primaryPath}.`;

  const summaryBundle = buildWorkspaceGraph(question, trace, analysis);
  const failedStep = failedSteps(trace)[0];
  return {
    trace,
    summary: summaryBundle.summary,
    contextText: summaryBundle.contextText,
    error: failedStep ? String(failedStep.observation?.error || 'local_tool_loop_failed') : '',
    primaryFilePath: summaryBundle.primaryFilePath,
    primaryFileContent: summaryBundle.primaryFileContent,
    selectedFiles: summaryBundle.selectedFiles,
    workspaceGraph: summaryBundle.workspaceGraph,
  };
}

module.exports = {
  runLocalToolLoop,
  __test: {
    signalScore,
    buildObservedAnchorDecision,
    compareDecisionTuples,
    chooseBestOutlineItems,
    choosePrimaryWindow,
    chooseSupportSymbols,
    shouldFollowDefinition,
    resolveSupportSymbolRead,
    rankRelatedOwnerHits,
    chooseBroadReadCandidates,
    buildBroadReadInput,
    buildWorkspaceGraph,
    scoreFileQuestionAlignment,
  },
};
