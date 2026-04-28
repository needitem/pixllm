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

function stepSucceeded(step) {
  return step?.observation?.ok !== false;
}

function successfulSteps(trace, tool) {
  return (Array.isArray(trace) ? trace : []).filter((step) => step.tool === tool && stepSucceeded(step));
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
  if (toolName === 'glob') {
    return {
      ok: Boolean(payload.ok),
      pattern: payload.pattern || '',
      items: Array.isArray(payload.items) ? payload.items.slice(0, 200) : [],
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
  if (toolName === 'edit') {
    const diffText = String(payload.diff || '');
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      occurrences: Number(payload.occurrences || 0),
      replace_all: Boolean(payload.replace_all),
      added: Number(payload.added || 0),
      removed: Number(payload.removed || 0),
      diff: diffText.slice(0, maxChars),
      diff_truncated: Boolean(payload.diff_truncated) || diffText.length > maxChars,
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'source_ls') {
    return {
      ok: payload.ok !== false,
      path: payload.path || '',
      total: Number(payload.total || 0),
      items: Array.isArray(payload.items) ? payload.items.slice(0, 200) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'source_glob') {
    return {
      ok: payload.ok !== false,
      pattern: payload.pattern || '',
      total: Number(payload.total || 0),
      matches: Array.isArray(payload.matches) ? payload.matches.slice(0, 200) : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'source_grep') {
    return {
      ok: payload.ok !== false,
      pattern: payload.pattern || '',
      path_glob: payload.path_glob || '',
      total: Number(payload.total || 0),
      matches: Array.isArray(payload.matches)
        ? payload.matches.slice(0, 30).map((item) => ({
          path: item?.path || '',
          line: Number(item?.line || 0),
          line_range: item?.line_range || '',
          line_text: String(item?.line_text || '').slice(0, 500),
          snippet: String(item?.snippet || '').slice(0, Math.min(1200, maxChars)),
        }))
        : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'source_symbol_search') {
    return {
      ok: payload.ok !== false,
      query: payload.query || '',
      total: Number(payload.total || 0),
      results: Array.isArray(payload.results)
        ? payload.results.slice(0, 30).map((item) => ({
          symbol: item?.symbol || '',
          type_name: item?.type_name || '',
          member_name: item?.member_name || '',
          declaration: String(item?.declaration || '').slice(0, 800),
          path: item?.path || '',
          source_refs: Array.isArray(item?.source_refs) ? item.source_refs.slice(0, 4) : [],
          score: Number(item?.score || 0),
        }))
        : [],
      error: payload.error || '',
      message: payload.message || '',
    };
  }
  if (toolName === 'source_read') {
    return {
      ok: Boolean(payload.ok),
      path: payload.path || '',
      title: payload.title || '',
      kind: payload.kind || '',
      line_range: String(payload.line_range || ''),
      content: String(payload.content || '').slice(0, Math.min(3200, maxChars)),
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
      line: Number(payload.line || 0),
      items,
      content,
      lineRange: Number(payload.line || 0) > 0
        ? `${Number(payload.line || 0)}-${Number(payload.line || 0)}`
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
  readObservationsFromTrace,
  summarizeObservation,
};
