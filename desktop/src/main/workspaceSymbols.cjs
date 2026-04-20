const path = require('node:path');

const MATCHER_CACHE = new Map();
const MAX_MATCHER_CACHE_ENTRIES = 128;

function escapeRegExp(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function capitalizeIdentifier(value) {
  const text = String(value || '').trim();
  if (!text) {
    return '';
  }
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function getSymbolMatchers(symbol) {
  const key = String(symbol || '').trim();
  if (!key) {
    return {
      symbolText: '',
      symbolLower: '',
      escapedSymbol: '',
      definitionMatchers: [],
      newRegex: /$^/,
      memberCallRegex: /$^/,
      bareRegex: /$^/,
      stateUpdateRegex: /$^/,
      suffixCallRegex: /$^/,
    };
  }
  const cached = MATCHER_CACHE.get(key);
  if (cached) {
    return cached;
  }
  const symbolText = key;
  const symbolLower = key.toLowerCase();
  const escapedSymbol = escapeRegExp(symbolText);
  const symbolSuffix = capitalizeIdentifier(symbolText);
  const definitionMatchers = [
    {
      kind: 'type_declaration',
      regex: new RegExp(`\\b(?:class|struct|interface|enum|record|typedef|using)\\s+${escapedSymbol}\\b`, 'i'),
      baseScore: 24,
    },
    {
      kind: 'method_declaration',
      regex: new RegExp(`\\b(?:public|private|protected|internal|static|async|virtual|override|sealed|partial|abstract|extern|unsafe|new|required|readonly|\\s)+[A-Za-z_<>,\\[\\]?]+\\s+${escapedSymbol}\\s*\\(`, 'i'),
      baseScore: 20,
    },
    {
      kind: 'function_declaration',
      regex: new RegExp(`\\b(?:export\\s+)?(?:async\\s+)?function\\s+${escapedSymbol}\\s*\\(`, 'i'),
      baseScore: 21,
    },
    {
      kind: 'function_assignment',
      regex: new RegExp(`\\b(?:export\\s+)?(?:const|let|var)\\s+${escapedSymbol}\\s*=\\s*(?:async\\s*)?(?:function\\b|\\([^)]*\\)\\s*=>|[A-Za-z_][A-Za-z0-9_]*\\s*=>)`, 'i'),
      baseScore: 18,
    },
    {
      kind: 'property_or_field',
      regex: new RegExp(`\\b(?:public|private|protected|internal|static|virtual|override|sealed|partial|abstract|new|required|readonly|\\s)+[A-Za-z_<>,\\[\\]?]+\\s+${escapedSymbol}\\s*(?:\\{|=>|=|;)`, 'i'),
      baseScore: 17,
    },
  ];
  const resolved = {
    symbolText,
    symbolLower,
    escapedSymbol,
    definitionMatchers,
    newRegex: new RegExp(`\\bnew\\s+${escapeRegExp(symbolLower)}\\b`, 'i'),
    memberCallRegex: new RegExp(`\\.${escapeRegExp(symbolLower)}\\s*\\(`, 'i'),
    bareRegex: new RegExp(`\\b${escapeRegExp(symbolLower)}\\b`, 'i'),
    stateUpdateRegex: new RegExp(`(?:\\b|\\.|->)(?:this\\.|self\\.|state\\.|model\\.|ctx\\.|context\\.)?${escapedSymbol}\\s*(?:[+\\-*/%]?=|\\+\\+|--)`, 'i'),
    suffixCallRegex: symbolSuffix ? new RegExp(`\\b[A-Za-z_][A-Za-z0-9_]*${escapeRegExp(symbolSuffix)}\\s*\\(`, 'i') : /$^/,
  };
  MATCHER_CACHE.set(key, resolved);
  while (MATCHER_CACHE.size > MAX_MATCHER_CACHE_ENTRIES) {
    const oldestKey = MATCHER_CACHE.keys().next().value;
    if (oldestKey === undefined) break;
    MATCHER_CACHE.delete(oldestKey);
  }
  return resolved;
}

function hasStateUpdateSignal(text, symbol) {
  const line = String(text || '').trim();
  const symbolInfo = getSymbolMatchers(symbol);
  if (!line || !symbolInfo.symbolText) {
    return false;
  }
  if (symbolInfo.stateUpdateRegex.test(line)) {
    return true;
  }
  if (symbolInfo.suffixCallRegex.test(line)) {
    return true;
  }
  return /\b[A-Za-z_][A-Za-z0-9_]*\s*\(/.test(line)
    && symbolInfo.bareRegex.test(line)
    && /(?:[-+*/%]?=|\+\+|--)/.test(line);
}

function pathMatchesFilter(pathValue, pathFilter = '') {
  const filterValue = String(pathFilter || '').trim().replace(/\\/g, '/').toLowerCase();
  if (!filterValue) {
    return true;
  }
  return String(pathValue || '').replace(/\\/g, '/').toLowerCase().includes(filterValue);
}

function isDefinitionLikeText(text, symbol) {
  const line = String(text || '').trim();
  return getSymbolMatchers(symbol).definitionMatchers.some((item) => item.regex.test(line));
}

function scoreDefinitionHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const lowered = line.toLowerCase();
  const symbolInfo = getSymbolMatchers(symbol);
  let score = 0;
  for (const matcher of symbolInfo.definitionMatchers) {
    if (matcher.regex.test(line)) {
      score = Math.max(score, matcher.baseScore);
      if (matcher.kind === 'type_declaration') break;
    }
  }
  if (!score) {
    return 0;
  }
  if (/\b(class|struct|interface|enum|record)\b/i.test(line)) score += 4;
  if (/\b(public|private|protected|internal|static|async|virtual|override)\b/i.test(line)) score += 2;
  if (/=>/.test(line)) score -= 1;
  if (symbolInfo.newRegex.test(lowered)) score -= 6;
  if (symbolInfo.memberCallRegex.test(lowered)) score -= 6;
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  const fileStem = path.basename(String(item?.path || ''), path.extname(String(item?.path || ''))).toLowerCase();
  if (fileStem === symbolInfo.symbolLower || fileStem.includes(symbolInfo.symbolLower)) score += 4;
  return score;
}

function scoreReferenceHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const lowered = line.toLowerCase();
  const symbolInfo = getSymbolMatchers(symbol);
  let score = 8;
  if (!symbolInfo.bareRegex.test(lowered)) {
    return 0;
  }
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  if (isDefinitionLikeText(line, symbol)) score -= 6;
  if (symbolInfo.newRegex.test(lowered)) score += 6;
  if (symbolInfo.memberCallRegex.test(lowered)) score += 6;
  if (hasStateUpdateSignal(line, symbol)) score += 4;
  if (/\b(?:if|for|while|switch|return|await|=>)\b/.test(line)) score += 1;
  return score;
}

function scoreCallerHit(item, symbol) {
  const line = String(item?.text || '').trim();
  const symbolInfo = getSymbolMatchers(symbol);
  if (!symbolInfo.symbolText) {
    return 0;
  }
  if (!new RegExp(`(?:\\.|\\b)${symbolInfo.escapedSymbol}\\s*\\(`, 'i').test(line)) {
    return 0;
  }
  if (isDefinitionLikeText(line, symbolInfo.symbolText)) {
    return 0;
  }
  let score = 18;
  if (/\/(?:obj|bin|dist|build|out|node_modules)\//i.test(String(item?.path || ''))) score -= 15;
  if (/await\s+/.test(line)) score += 2;
  if (/return\s+/.test(line)) score += 1;
  return score;
}

function buildOutlineItemsFromContent(content, symbol = '', limit = 40) {
  const lines = String(content || '').split(/\r?\n/);
  const items = [];
  const symbolLower = String(symbol || '').trim().toLowerCase();
  const patterns = [
    { kind: 'type', regex: /\b(?:class|struct|interface|enum|record)\s+([A-Za-z_][A-Za-z0-9_]*)/g },
    { kind: 'function', regex: /\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g },
    { kind: 'function', regex: /\b(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_][A-Za-z0-9_]*\s*=>)/g },
    { kind: 'method', regex: /\b(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g },
    { kind: 'property', regex: /\b(?:public|private|protected|internal)\s+[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*(?:get|set)/g },
    { kind: 'event', regex: /\bevent\s+[A-Za-z_<>,\[\]?]+\s+([A-Za-z_][A-Za-z0-9_]*)/g },
  ];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    for (const pattern of patterns) {
      for (const match of line.matchAll(pattern.regex)) {
        const name = String(match[1] || '').trim();
        if (!name) continue;
        items.push({
          name,
          kind: pattern.kind,
          line: index + 1,
          text: line.trim(),
          score: symbolLower && (name.toLowerCase().includes(symbolLower) || line.toLowerCase().includes(symbolLower)) ? 10 : 1,
        });
      }
    }
  }

  return items
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || Number(a.line || 0) - Number(b.line || 0))
    .slice(0, Math.max(1, Math.min(Number(limit || 40), 80)));
}

function buildSymbolNeighborhoodItems(items, lineHint = 0, limit = 12) {
  const hint = Math.max(0, Number(lineHint || 0));
  const safeLimit = Math.max(1, Math.min(Number(limit || 12), 40));
  const kindPriority = {
    function: 0,
    method: 0,
    type: 1,
    event: 2,
    property: 3,
  };
  return (Array.isArray(items) ? items : [])
    .map((item) => ({
      ...item,
      distance: hint > 0 ? Math.abs(Number(item.line || 0) - hint) : Number(item.line || 0),
      beforeHint: hint > 0 && Number(item.line || 0) <= hint,
      kindRank: Number(kindPriority[String(item?.kind || '').trim().toLowerCase()] ?? 4),
    }))
    .sort((a, b) => {
      if (hint > 0) {
        if (a.beforeHint !== b.beforeHint) return a.beforeHint ? -1 : 1;
        if (a.distance !== b.distance) return a.distance - b.distance;
      }
      if (a.kindRank !== b.kindRank) return a.kindRank - b.kindRank;
      return Number(a.line || 0) - Number(b.line || 0) || String(a.name || '').localeCompare(String(b.name || ''));
    })
    .slice(0, safeLimit)
    .map(({ distance, beforeHint, kindRank, ...item }) => item);
}

function chooseDefinitionCandidate(candidates, lineHint = 0) {
  const hint = Math.max(0, Number(lineHint || 0));
  return [...(Array.isArray(candidates) ? candidates : [])]
    .sort((a, b) => {
      if (hint > 0) {
        const delta = Math.abs(Number(a.line || 0) - hint) - Math.abs(Number(b.line || 0) - hint);
        if (delta !== 0) return delta;
      }
      return Number(b.score || 0) - Number(a.score || 0) || Number(a.line || 0) - Number(b.line || 0);
    })[0] || null;
}

function collectDefinitionCandidates(lines, symbol) {
  const out = [];
  for (let index = 0; index < lines.length; index += 1) {
    const text = String(lines[index] || '');
    for (const matcher of getSymbolMatchers(symbol).definitionMatchers) {
      if (!matcher.regex.test(text)) {
        continue;
      }
      out.push({
        line: index + 1,
        kind: matcher.kind,
        score: matcher.baseScore,
        text,
      });
    }
  }
  return out;
}

function countChar(text, char) {
  return String(text || '').split(char).length - 1;
}

function expandSymbolSpan(lines, candidateLine) {
  let startLine = Math.max(1, Number(candidateLine || 1));
  let endLine = startLine;

  while (startLine > 1) {
    const prev = String(lines[startLine - 2] || '').trim();
    if (!prev) break;
    if (/^(?:\[|\/\/\/|\/\/|\/\*|\*|\#)/.test(prev)) {
      startLine -= 1;
      continue;
    }
    break;
  }

  let braceDepth = 0;
  let seenBrace = false;
  for (let index = startLine - 1; index < lines.length && index < startLine + 160; index += 1) {
    const line = String(lines[index] || '');
    endLine = index + 1;
    braceDepth += countChar(line, '{');
    if (countChar(line, '{') > 0) seenBrace = true;
    braceDepth -= countChar(line, '}');
    const trimmed = line.trim();
    if (!seenBrace && index >= startLine - 1 && /(?:=>|;)\s*$/.test(trimmed)) {
      break;
    }
    if (seenBrace && braceDepth <= 0 && index > startLine - 1) {
      break;
    }
    if (!trimmed && index > startLine - 1 && !seenBrace) {
      break;
    }
  }

  return {
    startLine,
    endLine: Math.max(startLine, endLine),
  };
}

function dedupeRankedItems(items, limit) {
  const byKey = new Map();
  for (const item of Array.isArray(items) ? items : []) {
    const key = `${String(item?.path || '').toLowerCase()}:${Number(item?.line || 0)}:${String(item?.matchKind || item?.match_kind || '').toLowerCase()}`;
    const current = byKey.get(key);
    if (!current || Number(item?.score || 0) > Number(current?.score || 0)) {
      byKey.set(key, item);
    }
  }
  return Array.from(byKey.values())
    .sort((a, b) => Number(b.score || 0) - Number(a.score || 0) || String(a.path || '').localeCompare(String(b.path || '')))
    .slice(0, Math.max(1, Math.min(Number(limit || 50), 200)));
}

function createWorkspaceSymbolApis({ grepWorkspace, safeResolve, isAllowedWorkbenchFile, fs }) {
  async function findSymbolInWorkspace(workspacePath, symbol, options = {}) {
    const normalizedSymbol = String(symbol || '').trim();
    if (!normalizedSymbol) {
      return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
    }
    const pathFilter = String(options.pathFilter || '').trim();
    const limit = Math.max(1, Math.min(Number(options.limit || 8), 50));
    const searchLimit = Math.max(40, Math.min(limit * 20, 200));
    const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
    if (!grepResult.ok) {
      return {
        ok: false,
        symbol: normalizedSymbol,
        items: [],
        error: grepResult.error || 'symbol_search_failed',
      };
    }

    const items = [];
    for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
      if (!pathMatchesFilter(item.path, pathFilter)) {
        continue;
      }
      const score = scoreDefinitionHit(item, normalizedSymbol);
      if (score <= 0) {
        continue;
      }
      items.push({
        path: String(item.path || '').replace(/\\/g, '/'),
        line: Number(item.line || 0),
        text: String(item.text || ''),
        matchKind: 'symbol_definition',
        symbol: normalizedSymbol,
        score,
        source: 'find_symbol',
      });
    }

    return {
      ok: true,
      symbol: normalizedSymbol,
      items: dedupeRankedItems(items, limit),
      backend: grepResult.backend || 'search_code',
    };
  }

  async function findReferencesInWorkspace(workspacePath, symbol, options = {}) {
    const normalizedSymbol = String(symbol || '').trim();
    if (!normalizedSymbol) {
      return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
    }
    const pathFilter = String(options.pathFilter || '').trim();
    const limit = Math.max(1, Math.min(Number(options.limit || 20), 100));
    const searchLimit = Math.max(60, Math.min(limit * 12, 200));
    const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
    if (!grepResult.ok) {
      return {
        ok: false,
        symbol: normalizedSymbol,
        items: [],
        error: grepResult.error || 'reference_search_failed',
      };
    }

    const items = [];
    for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
      if (!pathMatchesFilter(item.path, pathFilter)) {
        continue;
      }
      const score = scoreReferenceHit(item, normalizedSymbol);
      if (score <= 0) {
        continue;
      }
      items.push({
        path: String(item.path || '').replace(/\\/g, '/'),
        line: Number(item.line || 0),
        text: String(item.text || ''),
        matchKind: isDefinitionLikeText(item.text, normalizedSymbol) ? 'symbol_definition' : 'reference',
        symbol: normalizedSymbol,
        score,
        source: 'find_references',
      });
    }

    return {
      ok: true,
      symbol: normalizedSymbol,
      items: dedupeRankedItems(items, limit),
      backend: grepResult.backend || 'search_code',
    };
  }

  async function findCallersInWorkspace(workspacePath, symbol, options = {}) {
    const normalizedSymbol = String(symbol || '').trim();
    if (!normalizedSymbol) {
      return { ok: false, symbol: '', items: [], error: 'empty_symbol' };
    }
    const pathFilter = String(options.pathFilter || '').trim();
    const limit = Math.max(1, Math.min(Number(options.limit || 20), 100));
    const searchLimit = Math.max(60, Math.min(limit * 12, 200));
    const grepResult = await grepWorkspace(workspacePath, normalizedSymbol, searchLimit);
    if (!grepResult.ok) {
      return {
        ok: false,
        symbol: normalizedSymbol,
        items: [],
        error: grepResult.error || 'caller_search_failed',
      };
    }

    const items = [];
    for (const item of Array.isArray(grepResult.items) ? grepResult.items : []) {
      if (!pathMatchesFilter(item.path, pathFilter)) {
        continue;
      }
      const score = scoreCallerHit(item, normalizedSymbol);
      if (score <= 0) {
        continue;
      }
      items.push({
        path: String(item.path || '').replace(/\\/g, '/'),
        line: Number(item.line || 0),
        text: String(item.text || ''),
        matchKind: 'caller',
        symbol: normalizedSymbol,
        score,
        source: 'find_callers',
      });
    }

    return {
      ok: true,
      symbol: normalizedSymbol,
      items: dedupeRankedItems(items, limit),
      backend: grepResult.backend || 'search_code',
    };
  }

  async function symbolOutlineInWorkspace(workspacePath, relativePath = '', options = {}) {
    const requestedPath = String(relativePath || '').trim();
    const symbol = String(options.symbol || '').trim();
    let resolvedPath = requestedPath;

    if (!resolvedPath && symbol) {
      const symbolResult = await findSymbolInWorkspace(workspacePath, symbol, { limit: 1, pathFilter: options.pathFilter || '' });
      resolvedPath = String(symbolResult.items?.[0]?.path || '').trim();
    }
    if (!resolvedPath) {
      return { ok: false, path: '', symbol, items: [], error: 'path_or_symbol_required' };
    }

    try {
      const fullPath = await safeResolve(workspacePath, resolvedPath);
      const content = await fs.promises.readFile(fullPath, 'utf-8');
      return {
        ok: true,
        path: resolvedPath.replace(/\\/g, '/'),
        symbol,
        backend: 'heuristic_outline',
        items: buildOutlineItemsFromContent(content, symbol, options.limit || 40),
      };
    } catch (error) {
      return {
        ok: false,
        path: resolvedPath.replace(/\\/g, '/'),
        symbol,
        items: [],
        error: String(error && error.message ? error.message : error || 'symbol_outline_failed'),
      };
    }
  }

  async function symbolNeighborhoodInWorkspace(workspacePath, relativePath = '', options = {}) {
    const outline = await symbolOutlineInWorkspace(workspacePath, relativePath, {
      ...options,
      limit: 400,
    });
    if (!outline.ok) {
      return outline;
    }
    const lineHint = Math.max(0, Number(options.lineHint || options.line_hint || 0));
    return {
      ok: true,
      path: outline.path,
      symbol: outline.symbol,
      backend: outline.backend,
      lineHint,
      items: buildSymbolNeighborhoodItems(outline.items, lineHint, options.limit || 12),
    };
  }

  async function readSymbolSpanInWorkspace(workspacePath, relativePath = '', symbol = '', options = {}) {
    const normalizedSymbol = String(symbol || '').trim();
    let resolvedPath = String(relativePath || '').trim();
    const lineHint = Math.max(0, Number(options.lineHint || options.startLine || options.start_line || 0));
    const maxChars = Math.max(200, Math.min(Number(options.maxChars || options.max_chars || 12000), 100000));

    if (!normalizedSymbol) {
      return { ok: false, path: resolvedPath, symbol: '', content: '', error: 'empty_symbol' };
    }
    if (!resolvedPath) {
      const symbolResult = await findSymbolInWorkspace(workspacePath, normalizedSymbol, { limit: 1, pathFilter: options.pathFilter || '' });
      resolvedPath = String(symbolResult.items?.[0]?.path || '').trim();
    }
    if (!resolvedPath) {
      return { ok: false, path: '', symbol: normalizedSymbol, content: '', error: 'symbol_definition_not_found' };
    }

    try {
      const fullPath = await safeResolve(workspacePath, resolvedPath);
      if (!isAllowedWorkbenchFile(path.basename(fullPath))) {
        return { ok: false, path: resolvedPath, symbol: normalizedSymbol, content: '', error: 'unsupported_file_type' };
      }
      const content = await fs.promises.readFile(fullPath, 'utf-8');
      const lines = content.split(/\r?\n/);
      const candidates = collectDefinitionCandidates(lines, normalizedSymbol);
      const chosen = chooseDefinitionCandidate(candidates, lineHint);
      if (!chosen) {
        return { ok: false, path: resolvedPath, symbol: normalizedSymbol, content: '', error: 'symbol_definition_not_found' };
      }
      const span = expandSymbolSpan(lines, chosen.line);
      const selected = lines.slice(span.startLine - 1, span.endLine);
      const bounded = selected.join('\n').slice(0, maxChars);
      return {
        ok: true,
        path: resolvedPath.replace(/\\/g, '/'),
        symbol: normalizedSymbol,
        matchKind: chosen.kind,
        lineRange: `${span.startLine}-${span.endLine}`,
        content: bounded,
        truncated: bounded.length < selected.join('\n').length,
      };
    } catch (error) {
      return {
        ok: false,
        path: resolvedPath.replace(/\\/g, '/'),
        symbol: normalizedSymbol,
        content: '',
        error: String(error && error.message ? error.message : error || 'read_symbol_span_failed'),
      };
    }
  }

  return {
    findCallersInWorkspace,
    findReferencesInWorkspace,
    findSymbolInWorkspace,
    readSymbolSpanInWorkspace,
    symbolNeighborhoodInWorkspace,
    symbolOutlineInWorkspace,
  };
}

module.exports = {
  createWorkspaceSymbolApis,
};
