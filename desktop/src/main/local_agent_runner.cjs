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
const MAX_CORE_FILES = 4;
const MAX_SUPPORT_FILES = 4;
const MAX_RELATED_FILES = 8;
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

function chooseBestOutlineItems(outlineItems, questionTerms) {
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
      for (const term of terms) {
        if (loweredName.includes(term)) score += 20;
        if (String(item?.text || '').toLowerCase().includes(term)) score += 8;
      }
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

async function resolveRootPath(workspacePath, question, selectedFilePath, trace) {
  const selectedPath = normalizePath(selectedFilePath);
  if (selectedPath) {
    return selectedPath;
  }

  const questionTerms = normalizeQuestionTerms(question);
  const listResult = await pushTraceStep(trace, workspacePath, 'enumerate workspace files to anchor the local investigation', 'list_files', {
    limit: MAX_LIST_LIMIT,
  });
  const items = Array.isArray(listResult?.items) ? listResult.items : [];
  if (questionTerms.length > 0) {
    const scored = items
      .map((item) => {
        const pathValue = normalizePath(item?.path);
        const lowered = pathValue.toLowerCase();
        let score = 0;
        for (const term of questionTerms) {
          const loweredTerm = String(term || '').trim().toLowerCase();
          if (!loweredTerm) continue;
          if (lowered.includes(loweredTerm)) score += 16;
          if (pathStem(pathValue).toLowerCase().includes(loweredTerm)) score += 12;
        }
        return { path: pathValue, score };
      })
      .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.path || '').localeCompare(String(b.path || '')));
    if (scored[0] && scored[0].score > 0) {
      return scored[0].path;
    }
  }

  const anchorQueries = buildAnchorQueries(question, questionTerms);
  for (const queryText of anchorQueries) {
    const grepObservation = await pushTraceStep(
      trace,
      workspacePath,
      `search workspace text to find a local anchor for ${queryText}`,
      'grep',
      {
        query: queryText,
        limit: MAX_GREP_LIMIT,
      },
    );
    const bestHit = pickBestGrepAnchor(grepObservation?.items, questionTerms, queryText);
    if (bestHit && Number(bestHit.score || 0) > 0) {
      return bestHit.path;
    }
  }
  return '';
}

function scoreGrepAnchorHit(item, questionTerms, queryText) {
  const pathValue = normalizePath(item?.path);
  const loweredPath = pathValue.toLowerCase();
  const text = String(item?.text || '').trim();
  const loweredText = text.toLowerCase();
  const rawQuery = String(queryText || '').trim().toLowerCase();
  let score = 0;

  if (!pathValue) {
    return 0;
  }
  if (rawQuery && loweredText.includes(rawQuery)) score += 24;
  if (rawQuery && loweredPath.includes(rawQuery)) score += 12;
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
    const loweredTerm = String(term || '').trim().toLowerCase();
    if (!loweredTerm) continue;
    if (loweredText.includes(loweredTerm)) score += 10;
    if (loweredPath.includes(loweredTerm)) score += 6;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(pathValue)) score -= 30;
  if (/\b(class|interface|struct|enum|record|namespace|module)\b/i.test(text)) score += 4;
  return score;
}

function pickBestGrepAnchor(items, questionTerms, queryText) {
  const bestByPath = new Map();
  for (const item of Array.isArray(items) ? items : []) {
    const pathValue = normalizePath(item?.path);
    if (!pathValue) continue;
    const candidate = {
      path: pathValue,
      score: scoreGrepAnchorHit(item, questionTerms, queryText),
      line: Number(item?.line || 0),
      text: String(item?.text || '').trim(),
    };
    const current = bestByPath.get(pathValue.toLowerCase());
    if (!current || Number(candidate.score || 0) > Number(current.score || 0)) {
      bestByPath.set(pathValue.toLowerCase(), candidate);
    }
  }
  return Array.from(bestByPath.values())
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.path || '').localeCompare(String(b.path || '')))[0] || null;
}

function buildAnchorQueries(question, questionTerms) {
  const rawQuestion = String(question || '').trim();
  const queries = [];
  for (const term of Array.isArray(questionTerms) ? questionTerms : []) {
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
  const primaryPath = normalizePath(analysis.primaryPath || selectedPath);
  const readFiles = readObservationsFromTrace(trace);
  const relatedFiles = uniq([
    primaryPath,
    analysis.callerOwner?.path || '',
    ...(analysis.supportReads || []).map((item) => item.path),
    ...readFiles.map((item) => item.path),
  ]).slice(0, MAX_RELATED_FILES);
  const coreFiles = uniq([
    selectedPath,
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
      root_path: selectedPath,
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
  const rootPath = await resolveRootPath(workspacePath, question, selectedFilePath, trace);
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
    candidateSymbols: [],
    primarySymbol: '',
    primaryPath: rootPath,
    primaryWindow: null,
    callerOwner: null,
    supportReads: [],
    summary: '',
  };

  await pushTraceStep(trace, workspacePath, 'read the selected file as the primary local anchor', 'read_file', {
    path: rootPath,
    maxChars: FILE_READ_CHAR_LIMIT,
    startLine: 1,
    endLine: DEFAULT_FILE_READ_END_LINE,
  });

  const outlineObservation = await pushTraceStep(trace, workspacePath, 'inspect local declarations in the anchor file', 'symbol_outline', {
    path: rootPath,
    limit: 120,
  });
  const outlineItems = Array.isArray(outlineObservation?.items) ? outlineObservation.items : [];
  const rootCandidates = chooseBestOutlineItems(outlineItems, questionTerms);
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

  const primaryWindow = choosePrimaryWindow(trace, rootPath, outlineItems, questionTerms);
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
  },
};
