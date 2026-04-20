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
  return step?.observation?.ok !== false;
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

function isTraceReferencePath(filePath) {
  const normalized = normalizePath(filePath);
  if (!normalized) return false;
  if (/^(?:https?|file):\/\//i.test(normalized)) return false;
  if (/^[A-Za-z]:\//.test(normalized)) return false;
  if (normalized === '..' || normalized.startsWith('../')) return false;
  return /[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,12}$/i.test(normalized);
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
  for (const step of successfulSteps(trace, 'wiki_search')) {
    const observation = step?.observation && typeof step.observation === 'object' ? step.observation : {};
    for (const item of Array.isArray(observation.results) ? observation.results : []) {
      paths.push(item?.path);
      paths.push(item?.file_path);
    }
  }
  for (const step of successfulSteps(trace, 'wiki_read')) {
    const observation = step?.observation && typeof step.observation === 'object' ? step.observation : {};
    paths.push(observation?.path);
    for (const item of Array.isArray(observation.related_pages) ? observation.related_pages : []) {
      paths.push(item?.path);
      paths.push(item?.file_path);
    }
  }
  return uniq(
    paths.filter((item) => {
      const normalized = normalizePath(item);
      return isTraceReferencePath(normalized);
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
  if (toolName === 'wiki_search') {
    return {
      ok: Boolean(payload.ok),
      query: payload.query || '',
      total: Number(payload.total || 0),
      results: Array.isArray(payload.results)
        ? payload.results.slice(0, 12).map((item) => ({
          path: item?.path || '',
          title: item?.title || '',
          kind: item?.kind || '',
          summary: String(item?.summary || item?.excerpt || '').slice(0, 240),
        }))
        : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'wiki_read') {
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      title: payload.title || '',
      kind: payload.kind || '',
      summary: String(payload.summary || '').slice(0, 320),
      content: String(payload.content || '').slice(0, Math.min(3200, maxChars)),
      related_pages: Array.isArray(payload.related_pages)
        ? payload.related_pages.slice(0, 4).map((item) => ({
            path: item?.path || '',
            title: item?.title || '',
            kind: item?.kind || '',
            relation: item?.relation || '',
            summary: String(item?.summary || '').slice(0, 220),
            content: String(item?.content || '').slice(0, Math.min(1200, maxChars)),
          }))
        : [],
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

module.exports = {
  failedSteps,
  grepItemsFromTrace,
  listFilesFromTrace,
  readObservationsFromTrace,
  symbolOutlinesFromTrace,
  referencePathsFromTrace,
  summarizeObservation,
};
