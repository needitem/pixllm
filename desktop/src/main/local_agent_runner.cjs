const {
  normalizePath,
  uniq,
  failedSteps,
  summarizeObservation,
  extractIdentifiers,
  pickRepresentativeEvidence,
  inferCodeRelations,
  readWindowsFromTrace,
  readObservationsFromTrace,
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
const MAX_TRACE_STEPS = 12;
const MAX_ROOT_SYMBOLS = 4;
const MAX_SUPPORT_SYMBOLS = 4;
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

function chooseBestOutlineItems(outlineItems, questionTerms, { focusLines = [], preferFlow = false } = {}) {
  const terms = new Set(Array.isArray(questionTerms) ? questionTerms : []);
  const candidates = (Array.isArray(outlineItems) ? outlineItems : [])
    .filter((item) => ['method', 'function', 'event', 'type'].includes(String(item?.kind || '').trim().toLowerCase()))
    .map((item) => {
      const name = String(item?.name || '').trim();
      const kind = String(item?.kind || '').trim().toLowerCase();
      const loweredName = name.toLowerCase();
      let score = signalScore(name, { mode: 'anchor' });
      if (kind === 'method') score += 30;
      if (kind === 'function') score += 28;
      if (kind === 'event') score += 24;
      if (kind === 'type') score += 16;
      score += outlineLineProximityScore(item?.line, focusLines, kind);
      for (const term of terms) {
        if (loweredName.includes(term)) score += 20;
        if (String(item?.text || '').toLowerCase().includes(term)) score += 8;
      }
      if (preferFlow && kind === 'type' && Array.isArray(focusLines) && focusLines.length > 0) score -= 16;
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

function choosePrimaryWindow(trace, selectedPath, outlineItems, questionTerms) {
  const outlineNames = (Array.isArray(outlineItems) ? outlineItems : []).map((item) => String(item?.name || '').trim()).filter(Boolean);
  const windows = readWindowsFromTrace(trace)
    .filter((item) => String(item?.symbol || '').trim())
    .filter((item) => !isLowSignalSymbol(item?.symbol, { mode: 'anchor' }))
    .map((item) => ({
      ...item,
      __score: scoreReadWindow(item, outlineNames, questionTerms, selectedPath),
    }))
    .sort((a, b) => Number(b.__score || 0) - Number(a.__score || 0) || String(a.path || '').localeCompare(String(b.path || '')));
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
  if (trace.length >= MAX_TRACE_STEPS) {
    return { ok: false, error: 'local_trace_budget_exhausted' };
  }
  const observation = summarizeObservation(
    action,
    await executeTool(workspacePath, action, input || {}),
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

function scoreAnchorCandidateSeed(candidate, questionTerms) {
  const pathValue = normalizePath(candidate?.path);
  let score = scoreFileQuestionAlignment(pathValue, '', questionTerms);
  const grepHits = Array.isArray(candidate?.grepHits) ? candidate.grepHits : [];
  score += Math.min(20, grepHits.length * 6);
  score += Math.min(30, Math.max(0, ...grepHits.map((item) => Number(item?.score || 0))));
  const commentOnlyHits = grepHits.filter((item) => Boolean(item?.commentOnly)).length;
  if (grepHits.length > 0 && commentOnlyHits === grepHits.length) {
    score -= 28;
  }
  score += pathFlowBias(pathValue);
  if (candidate?.selected) {
    score += 8;
  }
  return score;
}

function scoreAnchorCandidateInspection(candidate, questionTerms, { preferFlow = false } = {}) {
  const content = String(candidate?.content || '');
  const outlineItems = Array.isArray(candidate?.outlineItems) ? candidate.outlineItems : [];
  const metrics = buildAnchorEvidenceMetrics(content, outlineItems);
  const alignment = buildQuestionAlignmentMetrics(candidate?.path, content, outlineItems, questionTerms);
  const focusLines = (Array.isArray(candidate?.grepHits) ? candidate.grepHits : [])
    .map((item) => Number(item?.line || 0))
    .filter((item) => item > 0);
  const outlineCandidates = chooseBestOutlineItems(outlineItems, questionTerms, { focusLines, preferFlow });
  let score = scoreAnchorCandidateSeed(candidate, questionTerms);
  score += scoreFileQuestionAlignment(candidate?.path, content, questionTerms);
  score += alignment.codeDistinctTerms * 18;
  score += alignment.outlineTermHits * 8;
  score += alignment.pathTermHits * 6;
  score += Math.min(12, alignment.codeTermHits * 2);
  score += Math.min(6, alignment.commentDistinctTerms * 3);
  score += Math.min(16, metrics.methodCount * 2);
  score += Math.min(12, metrics.callTokenCount * 3);
  score += Math.min(16, metrics.callMentionCount);
  score += Math.min(10, metrics.controlCount * 2);
  score += Math.min(8, metrics.assignmentCount / 2);
  score += pathFlowBias(candidate?.path, { preferFlow });
  if (outlineCandidates[0]) {
    score += 6;
  }
  if (preferFlow) {
    if (
      alignment.codeDistinctTerms > 0
      || alignment.outlineTermHits > 0
      || metrics.methodCount > 0
      || metrics.callTokenCount > 0
      || metrics.controlCount > 0
    ) {
      score += 8;
    }
    if (alignment.codeDistinctTerms === 0 && alignment.outlineTermHits === 0) {
      score -= 28;
    }
    if (metrics.declarationOnly) {
      score -= 18;
    }
    const grepHits = Array.isArray(candidate?.grepHits) ? candidate.grepHits : [];
    if (grepHits.length > 0 && grepHits.every((item) => Boolean(item?.commentOnly)) && alignment.codeDistinctTerms === 0) {
      score -= 18;
    }
  }
  return {
    score,
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
    .sort((left, right) => scoreAnchorCandidateSeed(right, questionTerms) - scoreAnchorCandidateSeed(left, questionTerms))
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
  const evaluation = scoreAnchorCandidateInspection(
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
  return {
    inspected,
    tuple: [
      preferFlow ? (executableFlow > 0 ? 1 : 0) : 0,
      preferFlow ? (declarationOnly ? 0 : 1) : 0,
      preferFlow ? (softQuestionCoverage > 0 ? 1 : 0) : 0,
      directQuestionCode ? 1 : 0,
      nearbyExecutable ? 1 : 0,
      Math.min(4, softQuestionCoverage),
      Math.min(4, nonCommentHits.length),
      Math.min(6, executableFlow),
      Number(inspected?.evaluation?.score || 0),
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
  return String(left?.inspected?.path || '').localeCompare(String(right?.inspected?.path || ''));
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
  score += pathFlowBias(pathValue, { preferFlow });
  if (rawQuery && codeText.includes(rawQuery)) score += 24;
  else if (rawQuery && loweredText.includes(rawQuery)) score += 4;
  if (rawQuery && loweredPath.includes(rawQuery)) score += 12;
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (codeText.includes(loweredTerm)) score += 10;
    else if (loweredText.includes(loweredTerm)) score += 2;
    if (loweredPath.includes(loweredTerm)) score += 6;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules|packages|\.tmp)\//i.test(pathValue)) score -= 40;
  if (commentOnly) score -= 28;
  if (/\b(class|interface|struct|enum|record|namespace|module)\b/i.test(text)) score += 4;
  if (/[A-Za-z_][A-Za-z0-9_]*\s*\(|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*\(|::\s*[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(text)) score += 8;
  if (/\b(if|for|foreach|while|switch|return|await|catch)\b/i.test(text)) score += 6;
  if (!commentOnly && /\b(case|public|private|protected|internal|new|return)\b/i.test(text)) score += 8;
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
  const readFiles = readObservationsFromTrace(trace);
  const relatedFiles = uniq([
    primaryPath,
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

  const chain = [];
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

  const graphState = {
    anchor_symbol: analysis.primarySymbol || '',
    focus_symbol: analysis.callerOwner?.symbol || analysis.primarySymbol || '',
    focus_path: primaryPath,
    chain,
    frontiers: [],
    frontier: {},
    closed: true,
    coverage_ratio: chain.length > 0 ? 1.0 : 0.0,
    covered_count: chain.length,
    discovered_count: chain.length,
    open_frontier_count: 0,
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

  const analysis = {
    selectedPath: normalizePath(selectedFilePath),
    rootPath,
    rootFocusLines,
    candidateSymbols: [],
    primarySymbol: '',
    primaryPath: rootPath,
    primaryWindow: null,
    callerOwner: null,
    supportReads: [],
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
    limit: isFlowQuestion(question) ? FLOW_OUTLINE_LIMIT : 120,
  });
  const outlineItems = Array.isArray(outlineObservation?.items) ? outlineObservation.items : [];
  const rootCandidates = chooseBestOutlineItems(outlineItems, anchorQuestionTerms, {
    focusLines: rootFocusLines,
    preferFlow: isFlowQuestion(question),
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

  const primaryWindow = choosePrimaryWindow(trace, rootPath, outlineItems, anchorQuestionTerms);
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
    const bestCaller = pickBestCallerHit(callerObservation?.items, rootPath);
    if (bestCaller) {
      const neighborhoodObservation = await pushTraceStep(trace, workspacePath, `inspect the enclosing local symbol around the ${analysis.primarySymbol} call site`, 'symbol_neighborhood', {
        path: bestCaller.path,
        symbol: analysis.primarySymbol,
        lineHint: Number(bestCaller.line || 0),
        limit: 12,
      });
      const owner = pickNeighborhoodOwner(neighborhoodObservation?.items, analysis.primarySymbol);
      if (owner) {
        const ownerSymbol = String(owner.name || owner.symbol || '').trim();
        if (hasReadSymbol(trace, bestCaller.path, ownerSymbol)) {
          analysis.callerOwner = {
            symbol: ownerSymbol,
            path: normalizePath(bestCaller.path),
            line: Number(owner.line || bestCaller.line || 0),
            read: false,
          };
        } else {
          const ownerSpan = await pushTraceStep(trace, workspacePath, `read the caller owner span for ${ownerSymbol}`, 'read_symbol_span', {
            path: bestCaller.path,
            symbol: ownerSymbol,
            lineHint: Number(owner.line || bestCaller.line || 0),
            maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
          });
          if (ownerSpan?.ok) {
            analysis.callerOwner = {
              symbol: ownerSymbol,
              path: normalizePath(bestCaller.path),
              line: Number(owner.line || bestCaller.line || 0),
              read: true,
            };
          }
        }
      }
    }

    if (!analysis.callerOwner) {
      const referenceObservation = await pushTraceStep(trace, workspacePath, `trace references of ${analysis.primarySymbol} when direct callers are absent`, 'find_references', {
        symbol: analysis.primarySymbol,
        limit: 24,
      });
      const bestReference = pickBestCallerHit(referenceObservation?.items, rootPath);
      if (bestReference) {
        const neighborhoodObservation = await pushTraceStep(trace, workspacePath, `inspect the enclosing local symbol around the ${analysis.primarySymbol} reference`, 'symbol_neighborhood', {
          path: bestReference.path,
          symbol: analysis.primarySymbol,
          lineHint: Number(bestReference.line || 0),
          limit: 12,
        });
        const owner = pickNeighborhoodOwner(neighborhoodObservation?.items, analysis.primarySymbol);
        if (owner) {
          const ownerSymbol = String(owner.name || owner.symbol || '').trim();
          if (hasReadSymbol(trace, bestReference.path, ownerSymbol)) {
            analysis.callerOwner = {
              symbol: ownerSymbol,
              path: normalizePath(bestReference.path),
              line: Number(owner.line || bestReference.line || 0),
              read: false,
            };
          } else {
          const ownerSpan = await pushTraceStep(trace, workspacePath, `read the reference owner span for ${ownerSymbol}`, 'read_symbol_span', {
            path: bestReference.path,
            symbol: ownerSymbol,
            lineHint: Number(owner.line || bestReference.line || 0),
            maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
          });
          if (ownerSpan?.ok) {
            analysis.callerOwner = {
              symbol: ownerSymbol,
              path: normalizePath(bestReference.path),
              line: Number(owner.line || bestReference.line || 0),
              read: true,
            };
          }
          }
        }
      }
    }
  }

  const callerWindow = analysis.callerOwner
    ? readWindowsFromTrace(trace).find((item) => {
      return normalizePath(item.path).toLowerCase() === normalizePath(analysis.callerOwner.path).toLowerCase()
        && String(item.symbol || '').trim().toLowerCase() === String(analysis.callerOwner.symbol || '').trim().toLowerCase();
    }) || null
    : null;
  const priorPrimaryWindow = analysis.primaryWindow;
  if (
    callerWindow
    && normalizePath(callerWindow.path).toLowerCase() === normalizePath(analysis.primaryPath).toLowerCase()
    && signalScore(analysis.callerOwner?.symbol || '', { mode: 'anchor' }) >= signalScore(analysis.primarySymbol || '', { mode: 'anchor' }) - 8
  ) {
    analysis.primarySymbol = String(analysis.callerOwner?.symbol || analysis.primarySymbol || '').trim();
    analysis.primaryPath = normalizePath(callerWindow.path || analysis.primaryPath);
    analysis.primaryWindow = callerWindow;
  }
  const supportSymbols = chooseSupportSymbols(
    analysis.primaryWindow,
    [callerWindow, priorPrimaryWindow].filter(Boolean),
    outlineItems,
    questionTerms,
    [analysis.primarySymbol, analysis.callerOwner?.symbol || ''],
  );

  for (const symbol of supportSymbols) {
    if (!symbol) continue;
    if (hasReadSymbol(trace, rootPath, symbol)) {
      const existing = readWindowsFromTrace(trace).find((item) => {
        return normalizePath(item.path).toLowerCase() === normalizePath(rootPath).toLowerCase()
          && String(item.symbol || '').trim().toLowerCase() === symbol.toLowerCase();
      });
      if (existing) {
        analysis.supportReads.push(existing);
      }
      continue;
    }

    const localOutlineMatch = outlineItems.find((item) => String(item?.name || '').trim().toLowerCase() === symbol.toLowerCase());
    if (localOutlineMatch) {
      const localSupport = await pushTraceStep(trace, workspacePath, `read the local support symbol span for ${symbol}`, 'read_symbol_span', {
        path: rootPath,
        symbol,
        lineHint: Number(localOutlineMatch.line || 0),
        maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
      });
      if (localSupport?.ok) {
        analysis.supportReads.push({
          path: normalizePath(localSupport.path || rootPath),
          symbol,
          startLine: Number(String(localSupport.lineRange || '').split('-')[0] || 0),
        });
      }
      continue;
    }

    const definitionObservation = await pushTraceStep(trace, workspacePath, `resolve the support symbol definition for ${symbol}`, 'find_symbol', {
      symbol,
      limit: 12,
    });
    const bestDefinition = pickBestDefinition(definitionObservation?.items, rootPath);
    if (!bestDefinition || hasReadSymbol(trace, bestDefinition.path, symbol)) {
      continue;
    }
    const definitionPrefixDepth = sharedPrefixDepth(bestDefinition.path, rootPath);
    const questionAligned = questionTerms.some((term) => symbol.toLowerCase().includes(String(term || '').toLowerCase()));
    if (definitionPrefixDepth < 1 && !questionAligned) {
      continue;
    }
    const supportSpan = await pushTraceStep(trace, workspacePath, `read the support symbol span for ${symbol}`, 'read_symbol_span', {
      path: bestDefinition.path,
      symbol,
      lineHint: Number(bestDefinition.line || 0),
      maxChars: LOCAL_TRACE_READ_CHAR_LIMIT,
    });
    if (supportSpan?.ok) {
      analysis.supportReads.push({
        path: normalizePath(supportSpan.path || bestDefinition.path),
        symbol,
        startLine: Number(String(supportSpan.lineRange || '').split('-')[0] || bestDefinition.line || 0),
      });
    }
  }

  analysis.supportReads = dedupeBy(analysis.supportReads, (item) => `${item.path}::${item.symbol}`);
  analysis.summary = analysis.primarySymbol
    ? `Collected local flow evidence around ${analysis.primarySymbol}${analysis.callerOwner?.symbol ? ` with caller ${analysis.callerOwner.symbol}` : ''}.`
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
    chooseBestOutlineItems,
    choosePrimaryWindow,
    chooseSupportSymbols,
    buildWorkspaceGraph,
    scoreFileQuestionAlignment,
  },
};
